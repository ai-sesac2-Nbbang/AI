import pandas as pd
from faker import Faker
import numpy as np
import uuid
import random
from datetime import datetime, timedelta
import os

# --- ✨ Seed 고정 ✨ ---
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
Faker.seed(SEED)

# --- ✨✨ 설정 부분 ✨✨ ---
NUM_USERS = 2000
NUM_POSTS = 800
SAVE_PATH = r"C:\dev\agent\더미데이터2000명"


def generate_final_master_data():
    """
    '동네' 정보를 포함한 모든 기능이 집약된 최종 데이터를 생성합니다.
    """
    print("⚙️ [최종 통합본] '동네' 정보가 포함된 데이터 생성을 시작합니다...")
    
    fake = Faker('ko_KR'); os.makedirs(SAVE_PATH, exist_ok=True)
    SEOUL_BOUNDS = {"min_lat": 37.43, "max_lat": 37.70, "min_lon": 126.73, "max_lon": 127.18}
    def generate_random_point_in_seoul():
        r_lat = random.uniform(SEOUL_BOUNDS["min_lat"], SEOUL_BOUNDS["max_lat"]); r_lon = random.uniform(SEOUL_BOUNDS["min_lon"], SEOUL_BOUNDS["max_lon"])
        return f"POINT({r_lon:.6f} {r_lat:.6f})"

    print(f"👨‍👩‍👧‍👦 {NUM_USERS}명의 사용자 데이터를 생성 중...")
    
    # ★★★★★★★★★★★★★★★★★★★★★★★★★★★★
    #       '동네' 정보를 추가하기 위한 동네 목록
    # ★★★★★★★★★★★★★★★★★★★★★★★★★★★★
    seoul_neighborhoods = [
        '종로구 (광화문)', '중구 (명동)', '용산구 (이태원)', '성동구 (성수동)',
        '광진구 (건대입구)', '동대문구 (청량리)', '중랑구 (상봉동)', '성북구 (성신여대입구)',
        '강북구 (수유동)', '도봉구 (창동)', '노원구 (중계동 은행사거리)', '은평구 (연신내)',
        '서대문구 (신촌)', '마포구 (홍대입구)', '양천구 (목동)', '강서구 (마곡)',
        '구로구 (신도림)', '금천구 (가산디지털단지)', '영등포구 (여의도)', '동작구 (노량진)',
        '관악구 (서울대입구)', '서초구 (강남역)', '강남구 (삼성역)', '송파구 (잠실)',
        '강동구 (천호동)'
    ]
    
    users_data = []
    for i in range(NUM_USERS):
        birth_date = fake.date_of_birth(minimum_age=20, maximum_age=55); age = (datetime.now().date() - birth_date).days // 365
        if 20 <= age < 30: age_group = '20대'
        elif 30 <= age < 40: age_group = '30대'
        else: age_group = '40대 이상'
        
        # ★★★★★★★★★★★★★★★★★★★★★★★★★★★★
        #    사용자 생성 시 '동네' 컬럼을 바로 추가합니다.
        # ★★★★★★★★★★★★★★★★★★★★★★★★★★★★
        users_data.append({
            'id': str(uuid.uuid4()),
            'name': fake.name(),
            'nickname': f"{fake.user_name()}_{i}",
            'age_group': age_group,
            'gender': np.random.choice(['male','female']),
            'household_size': np.random.choice(['1인 가구','2인 가구','3인 이상 가구'],p=[0.6,0.25,0.15]),
            '동네': random.choice(seoul_neighborhoods)
        })
    df_users = pd.DataFrame(users_data)
    
    # --- 🛒 1-2. 게시글 데이터 생성 (아이템 목록은 이전과 동일) ---
    print(f"🛒 {NUM_POSTS}개의 다양한 게시글 데이터를 생성 중...")
    post_samples = {
        # 식품/간식 (대폭 추가)
        "코스트코 소불고기 (4kg)": "식품/간식", "신라면 40개입 1박스": "식품/간식", "제주 삼다수 2L 12병": "식품/간식",
        "하림 냉동 닭가슴살 2kg": "식품/간식", "비비고 왕교자 1.5kg x 2개": "식품/간식", "햇반 24개입 1박스": "식품/간식",
        "커클랜드 아몬드 1.13kg": "식품/간식", "필라델피아 크림치즈 1.36kg": "식품/간식", "상하목장 유기농우유 24팩": "식품/간식",
        "네스프레소 호환캡슐 100개입": "식품/간식", "곰표 밀가루 10kg": "식품/간식", "스팸 클래식 8개 묶음": "식품/간식",
        "서울우유 체다치즈 100매": "식품/간식", "매일 바이오 플레인 요거트 24개": "식품/간식", "오뚜기 3분카레 10개입": "식품/간식",

        # 생활용품 (대폭 추가)
        "크리넥스 3겹 화장지 30롤": "생활용품", "베베숲 물티슈 캡형 10팩": "생활용품", "다우니 섬유유연제 4L 리필": "생활용품",
        "하기스 매직컴포트 4단계 1박스": "생활용품", "로얄캐닌 강아지사료 8kg": "생활용품", "리스테린 1L x 2개": "생활용품",
        "페브리즈 1L 리필 x 2개": "생활용품", "종량제봉투 100L 100매": "생활용품", "듀라셀 건전지 AA 40개입": "생활용품",
        "질레트 퓨전 면도날 8개입": "생활용품", "코디 키친타올 12롤": "생활용품", "지퍼락 냉동용 대형 50매": "생활용품",
        "깨끗한나라 순수 200매 10개입": "생활용품", "퍼실 세탁세제 3L": "생활용품", "캣츠랑 고양이사료 10kg": "생활용품",

        # 패션/잡화 (대폭 추가)
        "나이키 스포츠 양말 6족 세트": "패션/잡화", "유니클로 에어리즘 3팩": "패션/잡화", "무신사 스탠다드 기본티 5장": "패션/잡화",
        "크록스 지비츠 세트 (20개입)": "패션/잡화", "캘빈클라인 드로즈 3팩": "패션/잡화", "피카소 칫솔 20개입": "패션/잡화",
        "컨버스 척 70 클래식": "패션/잡화", "잔스포츠 백팩": "패션/잡화", "샤오미 미밴드 스트랩 5종": "패션/잡화",
        "카카오프렌즈 볼펜 10자루 세트": "패션/잡화", "다이소 네트망 5개": "패션/잡화", "겨울용 수면양말 10족": "패션/잡화",

        # 뷰티/헬스케어 (대폭 추가)
        "닥터지 선크림 1+1 기획세트": "뷰티/헬스케어", "고려은단 비타민C 300정": "뷰티/헬스케어",
        "KF94 마스크 200매 박스": "뷰티/헬스케어", "메디힐 마스크팩 30매 박스": "뷰티/헬스케어",
        "세타필 대용량 로션 591ml": "뷰티/헬스케어", "종근당 락토핏 골드 180포": "뷰티/헬스케어",
        "아베다 샴푸 1L": "뷰티/헬스케어", "바이오가이아 유산균": "뷰티/헬스케어", "일리윤 세라마이드 아토 로션 500ml": "뷰티/헬스케어",
        "센카 퍼펙트휩 클렌징폼 5개": "뷰티/헬스케어", "실크테라피 헤어에센스 150ml": "뷰티/헬스케어", "덴티스테 치약 200g 3개": "뷰티/헬스케어"
    }
    posts_data = []
    for _ in range(NUM_POSTS):
        item_name = random.choice(list(post_samples.keys())); created_time = fake.date_time_between(start_date='-2M')
        posts_data.append({'id': str(uuid.uuid4()),'user_id': random.choice(df_users['id'].tolist()),'name': item_name,'category': post_samples[item_name],'target_count': random.randint(3,8),'created_at': created_time, 'mogu_spot': generate_random_point_in_seoul()})
    df_posts = pd.DataFrame(posts_data)

    # (페르소나 기반 참여 데이터 생성 및 파일 저장 로직은 이전과 동일)
    print("⭐ 페르소나 기반으로 현실적인 참여 데이터를 생성 중...")
    participations_data = []; user_info = df_users.set_index('id').to_dict('index')
    for index, post in df_posts.iterrows():
        num_participants = random.randint(2, post['target_count']); potential_participants_ids = [pid for pid in df_users['id'] if pid != post['user_id']];
        if len(potential_participants_ids) < num_participants: continue
        weights = []
        for pid in potential_participants_ids:
            user = user_info[pid]; weight = 1.0
            if post['category'] == '뷰티/헬스케어':
                if user['gender'] == 'female': weight *= 4.0
                else: weight *= 0.5
            if post['category'] == '패션/잡화':
                if user['age_group'] == '20대': weight *= 3.0
                elif user['age_group'] == '40대 이상': weight *= 0.5
            if post['category'] == '생활용품':
                if user['household_size'] == '3인 이상 가구': weight *= 1.5
            weights.append(weight)
        
        # 가중치 합계가 0인 경우 방지
        if sum(weights) == 0: continue
            
        prob_dist = np.array(weights) / sum(weights)
        selected_participants = np.random.choice(potential_participants_ids, size=num_participants, replace=False, p=prob_dist)
        for user_id in selected_participants:
            participations_data.append({'user_id': user_id,'mogu_post_id': post['id']})
    df_participations = pd.DataFrame(participations_data)
    print("✅ 데이터 생성 완료!")

    print(f"\n⚙️ PART 2: 생성된 최종 데이터 파일을 '{SAVE_PATH}' 경로에 저장합니다...")
    df_users.to_csv(os.path.join(SAVE_PATH, f'dummy_data_{NUM_USERS}_users.csv'), index=False, encoding='utf-8-sig')
    df_posts.to_csv(os.path.join(SAVE_PATH, f'dummy_data_{NUM_USERS}_posts.csv'), index=False, encoding='utf-8-sig')
    df_participations.to_csv(os.path.join(SAVE_PATH, f'dummy_data_{NUM_USERS}_participations.csv'), index=False, encoding='utf-8-sig')
    print("✅ 저장 완료!")


if __name__ == "__main__":
    generate_final_master_data()

# 동네 컬럼 추가 완료
# 상품 목록 대폭 추가