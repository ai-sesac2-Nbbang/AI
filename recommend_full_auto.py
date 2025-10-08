import os
import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
import matplotlib.pyplot as plt
import seaborn as sns
from geopy.distance import great_circle
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

# -------------------------------------------------------------------
# 1. 한글 깨짐 방지 설정
# -------------------------------------------------------------------
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False
print("✅ 한글 폰트('맑은 고딕') 설정을 완료했습니다.")

# -------------------------------------------------------------------
# 2. 경로 설정 및 데이터 불러오기
# -------------------------------------------------------------------
print("\n🔄 STEP 1: 데이터 파일을 불러옵니다...")
BASE_DIR = r"C:\dev\agent\더미데이터2000명"
USERS_CSV = os.path.join(BASE_DIR, "dummy_data_2000_users.csv") 
POSTS_CSV = os.path.join(BASE_DIR, "dummy_data_2000_posts.csv")
PARTICIPATIONS_CSV = os.path.join(BASE_DIR, "dummy_data_2000_participations.csv")

try:
    users_original = pd.read_csv(USERS_CSV, encoding='utf-8-sig')
    posts_original = pd.read_csv(POSTS_CSV, encoding='utf-8-sig')
    participations = pd.read_csv(PARTICIPATIONS_CSV, encoding='utf-8-sig')
    print("✅ 3개의 CSV 파일을 성공적으로 불러왔습니다.")
except Exception as e:
    print(f"🚨 오류: CSV 파일을 불러오는 중 문제가 발생했습니다. ({e})")
    exit()

# -------------------------------------------------------------------
# 3. 데이터 정제 및 이름 변경
# -------------------------------------------------------------------
print("\n🔄 STEP 2: 데이터를 깔끔하게 정리정돈합니다...")
users_original.columns = users_original.columns.str.strip()
posts_original.columns = posts_original.columns.str.strip()
participations.columns = participations.columns.str.strip()

# 원본 데이터는 복사해서 사용 (나중에 정보를 합칠 때 원본이 필요함)
users = users_original.copy()
posts = posts_original.copy()

users.rename(columns={'id':'사용자ID', 'name':'사용자명', 'nickname':'닉네임', 'age_group':'연령대', 'gender':'성별', 'household_size':'가구규모'}, inplace=True)
posts.rename(columns={'id':'게시물ID', 'user_id':'작성자ID', 'name':'게시물제목', 'category':'카테고리', 'target_count':'목표인원', 'created_at':'작성일', 'mogu_spot':'좌표'}, inplace=True)
participations.rename(columns={'user_id':'사용자ID', 'mogu_post_id':'게시물ID'}, inplace=True)
participations['참여여부'] = 1
print("✅ 데이터 컬럼을 알기 쉬운 한글 이름으로 변경하고 정리했습니다.")

# -------------------------------------------------------------------
# 4. ✨✨ 신규 특징(Feature) 생성 (핵심 업그레이드) ✨✨
# -------------------------------------------------------------------
print("\n🔄 STEP 3: AI에게 더 많은 힌트(위치, 시간, 인기도)를 주기 위한 특징을 생성합니다...")

# 4-1. 위치 특징: 사용자에게 '동네' 및 실제 위도/경도 부여
seoul_neighborhoods = {
    '종로구 (광화문)': (37.575, 126.977), '중구 (명동)': (37.563, 126.983), '용산구 (이태원)': (37.534, 126.994), '성동구 (성수동)': (37.544, 127.056),
    '광진구 (건대입구)': (37.540, 127.069), '동대문구 (청량리)': (37.580, 127.047), '중랑구 (상봉동)': (37.596, 127.093), '성북구 (성신여대입구)': (37.591, 127.016),
    '강북구 (수유동)': (37.638, 127.026), '도봉구 (창동)': (37.653, 127.047), '노원구 (중계동 은행사거리)': (37.649, 127.072), '은평구 (연신내)': (37.619, 126.921),
    '서대문구 (신촌)': (37.559, 126.942), '마포구 (홍대입구)': (37.556, 126.923), '양천구 (목동)': (37.527, 126.866), '강서구 (마곡)': (37.560, 126.826),
    '구로구 (신도림)': (37.509, 126.891), '금천구 (가산디지털단지)': (37.481, 126.895), '영등포구 (여의도)': (37.525, 126.925), '동작구 (노량진)': (37.513, 126.942),
    '관악구 (서울대입구)': (37.478, 126.951), '서초구 (강남역)': (37.498, 127.028), '강남구 (삼성역)': (37.509, 127.063), '송파구 (잠실)': (37.514, 127.104),
    '강동구 (천호동)': (37.538, 127.124)
}
np.random.seed(42)
users['동네'] = np.random.choice(list(seoul_neighborhoods.keys()), len(users))
coords = users['동네'].map(seoul_neighborhoods)
users['사용자_위도'] = coords.apply(lambda x: x[0]) + np.random.normal(0, 0.005, len(users))
users['사용자_경도'] = coords.apply(lambda x: x[1]) + np.random.normal(0, 0.005, len(users))

posts[['게시물_경도', '게시물_위도']] = posts['좌표'].str.extract(r'POINT\(([\d.-]+) ([\d.-]+)\)').astype(float)


# 4-2. 시간 특징: '게시물_경과일' 생성
posts['작성일'] = pd.to_datetime(posts['작성일'])
posts['게시물_경과일'] = (datetime.now() - posts['작성일']).dt.days

# 4-3. 인기도 특징: '사용자별_총참여수', '게시물별_인기도' 생성
user_activity = participations.groupby('사용자ID')['게시물ID'].count().reset_index()
user_activity.rename(columns={'게시물ID': '사용자별_총참여수'}, inplace=True)
users = users.merge(user_activity, on='사용자ID', how='left').fillna(0)

post_popularity = participations.groupby('게시물ID')['사용자ID'].count().reset_index()
post_popularity.rename(columns={'사용자ID': '게시물별_인기도'}, inplace=True)
posts = posts.merge(post_popularity, on='게시물ID', how='left').fillna(0)

print("✅ '게시물 경과일', '사용자별 총참여수', '게시물별 인기도' 등 새로운 특징을 추가했습니다.")

# -------------------------------------------------------------------
# 5. AI 학습 데이터 생성
# -------------------------------------------------------------------
print("\n🔄 STEP 4: AI가 학습할 데이터를 생성합니다 (모든 사용자-게시물 조합)...")
all_combinations = pd.MultiIndex.from_product([users['사용자ID'], posts['게시물ID']], names=['사용자ID','게시물ID']).to_frame(index=False)
training_data = all_combinations.merge(participations, on=['사용자ID','게시물ID'], how='left')
training_data['참여여부'] = training_data['참여여부'].fillna(0)
print(f"✅ 총 {len(training_data):,}개의 학습 데이터를 생성했습니다.")

# -------------------------------------------------------------------
# 6. 전체 특징(Feature) 데이터 결합
# -------------------------------------------------------------------
print("\n🔄 STEP 5: 모든 특징(위치, 시간, 인기도 등)을 하나로 합칩니다...")
# 사용자 특징 (기본정보 + 동네 + 활동성 + 위치)
users_features_base = users[['사용자ID', '사용자별_총참여수', '사용자_위도', '사용자_경도']]
users_dummies = pd.get_dummies(users[['연령대', '성별', '가구규모', '동네']], drop_first=True, dtype=int)
users_features = pd.concat([users_features_base, users_dummies], axis=1)

# 게시물 특징 (기본정보 + 인기도 + 시간 + 위치)
posts_features_base = posts[['게시물ID', '게시물별_인기도', '게시물_경과일', '게시물_위도', '게시물_경도']]
posts_dummies = pd.get_dummies(posts[['카테고리']], prefix='카테고리', drop_first=True, dtype=int)
posts_features = pd.concat([posts_features_base, posts_dummies], axis=1)

features = training_data.merge(users_features, on='사용자ID', how='left')
features = features.merge(posts_features, on='게시물ID', how='left')

print("... '사용자-게시물' 간 거리를 계산 중입니다 (시간이 조금 걸릴 수 있습니다)...")
features['거리(km)'] = features.apply(lambda row: great_circle((row['사용자_위도'], row['사용자_경도']), (row['게시물_위도'], row['게시물_경도'])).kilometers, axis=1)
print("✅ 모든 특징 데이터 생성을 완료했습니다.")

y = features['참여여부']
X = features.drop(columns=['참여여부', '사용자ID', '게시물ID', '사용자_위도', '사용자_경도', '게시물_위도', '게시물_경도'])

# -------------------------------------------------------------------
# 7. LightGBM 모델 학습
# -------------------------------------------------------------------
print("\n🚀 STEP 6: 모든 정보를 총동원하여 최종 AI 모델 학습을 시작합니다...")
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
train_data = lgb.Dataset(X_train, label=y_train)
val_data = lgb.Dataset(X_val, label=y_val)
params = {'objective': 'binary', 'metric': 'auc', 'verbosity': -1, 'seed': 42}
model = lgb.train(params, train_data, num_boost_round=100, valid_sets=[val_data], callbacks=[lgb.log_evaluation(period=20), lgb.early_stopping(stopping_rounds=10)])

# -------------------------------------------------------------------
# 8. 모델 성능 검증 및 중요 특징 시각화
# -------------------------------------------------------------------
print("\n📊 STEP 7: 모델 성능을 평가하고 결과를 시각화합니다...")
y_pred = model.predict(X_val)
auc = roc_auc_score(y_val, y_pred)
print(f"✅ 모델 성능 (AUC 점수): {auc:.4f} (1에 가까울수록 좋습니다)")
plt.figure(figsize=(10, 8)); lgb.plot_importance(model, max_num_features=20, ax=plt.gca()); plt.title("추천에 영향을 많이 준 상위 20개 특징", fontsize=15); plt.show()

# -------------------------------------------------------------------
# 9. 랜덤 사용자 1명에게 Top 10 상품 추천
# -------------------------------------------------------------------
print("\n🎁 STEP 8: 랜덤 사용자 1명에게 '최종 진화된' 맞춤 상품을 추천합니다...")
random_user_id = users['사용자ID'].sample(1).values[0]
random_user_info = users[users['사용자ID'] == random_user_id]

print(f"\n--- [추천 대상] ---")
print(f"  - 사용자ID: {random_user_info['사용자ID'].iloc[0]}")
print(f"  - 닉네임: {random_user_info['닉네임'].iloc[0]}")
print(f"  - 특징: {random_user_info['연령대'].iloc[0]}, {random_user_info['성별'].iloc[0]}, {random_user_info['가구규모'].iloc[0]}")
print(f"  - 동네: {random_user_info['동네'].iloc[0]}")
print("--------------------")

user_data = features[features['사용자ID'] == random_user_id]
user_preds = model.predict(user_data.drop(columns=['참여여부', '사용자ID', '게시물ID', '사용자_위도', '사용자_경도', '게시물_위도', '게시물_경도']))
user_data['추천점수'] = user_preds

already_participated = participations[participations['사용자ID'] == random_user_id]['게시물ID']
recommendations = user_data[~user_data['게시물ID'].isin(already_participated)]
top_10 = recommendations.sort_values('추천점수', ascending=False).head(10)

final_recommendations = top_10[['사용자ID', '게시물ID', '추천점수', '거리(km)']].merge(posts[['게시물ID', '게시물제목', '카테고리', '작성자ID']], on='게시물ID', how='left')
creator_info = users_original[['id', 'nickname']].rename(columns={'id': '작성자ID', 'nickname': '작성자닉네임'})
final_recommendations = final_recommendations.merge(creator_info, on='작성자ID', how='left')

final_recommendations['거리(km)'] = final_recommendations['거리(km)'].round(2)
final_recommendations = final_recommendations[['사용자ID', '게시물ID', '게시물제목', '카테고리', '작성자닉네임', '거리(km)', '추천점수']]

csv_path = os.path.join(BASE_DIR, "recommend_top10_final_upgraded.csv")
final_recommendations.to_csv(csv_path, index=False, encoding='utf-8-sig')
print(f"\n✅ '{random_user_info['닉네임'].iloc[0]}'님을 위한 최종 업그레이드 추천 목록을 CSV 파일로 저장했습니다: \n   {csv_path}")

final_recommendations['표시될제목'] = final_recommendations.apply(lambda row: f"{row['게시물제목']} (by {row['작성자닉네임']}) - {row['거리(km)']}km", axis=1)
plt.figure(figsize=(12, 8)); sns.barplot(data=final_recommendations, x='추천점수', y='표시될제목', palette="plasma"); plt.title(f"'{random_user_info['닉네임'].iloc[0]}'님을 위한 최종 추천 Top 10", fontsize=16, pad=20); plt.xlabel("AI가 예측한 참여 확률 (추천 점수)", fontsize=12); plt.ylabel("게시물 (작성자) - 거리", fontsize=12); plt.xticks(fontsize=10); plt.yticks(fontsize=10); plt.grid(axis='x', linestyle='--', alpha=0.6); plt.tight_layout(); plt.show()
print("\n🎉 모든 과정이 성공적으로 완료되었습니다!")

