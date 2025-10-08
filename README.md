MoguMogu - AI 기반 공동구매 추천 플랫폼

<!-- 필요하면 로고 이미지 경로 추가 -->

🚀 프로젝트 개요

프로젝트 명: 모구모구 (MoguMogu)

목적: 사용자 데이터와 게시물 정보를 분석하여, AI 기반으로 개인 맞춤 공동구매를 추천하는 웹 애플리케이션 개발

주요 기능:

콘텐츠 기반 추천: 게시물 제목과 내용을 분석하여 유사 게시물 추천

협업 필터링: 사용자 참여 기록 기반으로 취향 맞춤 추천

인터랙티브 지도 시각화: 지도에서 게시물 위치 확인 및 클러스터링

📂 프로젝트 구성
/AI
│
├─ recommend_full_auto.py          # 핵심 AI 추천 스크립트 (단일 실행 가능)
├─ dummy_data2000                  # 더미 데이터 폴더 (users, posts, participations CSV)
│   ├─ dummy_data_2000_users.csv
│   ├─ dummy_data_2000_posts.csv
│   └─ dummy_data_2000_participations.csv
├─ generate_dummy_data.py          # 더미 데이터 생성 스크립트
├─ requirements.txt                # Python 의존성 패키지
└─ README.md                       # 프로젝트 소개


⚠️ 지도 시각화, HTML UI 관련 코드는 현재 제거. AI 추천 엔진 중심으로 최소 환경 구성.

💻 설치 및 실행
1. 환경 준비

Python 3.10 이상 권장

Anaconda 환경 사용 권장

conda create -n mogu python=3.10
conda activate mogu

2. 의존성 설치
pip install -r requirements.txt


requirements.txt 예시:

pandas
numpy
scikit-learn
scipy
surprise
faker

3. 더미 데이터 생성 (선택 사항)
python generate_dummy_data.py


dummy_data2000 폴더에 CSV 파일이 생성됩니다.

4. AI 추천 실행
python recommend_full_auto.py


스크립트 실행 시:

CSV 데이터 로딩

콘텐츠 기반 추천 + 협업 필터링 학습

추천 결과 CSV 파일 생성 (예: recommend_top10_final_upgraded.csv)

📈 데이터 구조
1. Users (dummy_data_2000_users.csv)
컬럼	설명
id	사용자 고유 ID
name	사용자 이름
nickname	닉네임
age_group	연령대 (20대, 30대, 40대 이상)
gender	성별
household_size	가구 구성
2. Posts (dummy_data_2000_posts.csv)
컬럼	설명
id	게시물 ID
user_id	작성자 ID
name	상품명
category	카테고리 (식품/생활용품/패션/뷰티 등)
target_count	목표 참여자 수
created_at	생성 날짜
mogu_spot	게시물 위치 (POINT(lon lat))
3. Participations (dummy_data_2000_participations.csv)
컬럼	설명
user_id	참여 사용자 ID
mogu_post_id	참여 게시물 ID
⚙️ 프로젝트 특징

AI 추천 엔진 ‘모구링’

콘텐츠 기반 추천: TF-IDF + 코사인 유사도

협업 필터링: SVD 기반 잠재 요인 모델 (surprise 라이브러리)

현실적인 참여 시뮬레이션: 성별, 연령대, 가구 정보 기반 페르소나 가중치

데이터 생성 자동화: Faker 라이브러리를 활용해 2000명 사용자, 800개 게시물, 참여 데이터 생성

📌 주의 사항

현재 지도 시각화는 제거됨. 순수 AI 추천 기능 중심

CSV 데이터가 반드시 dummy_data2000 폴더 내 존재해야 함

Windows 환경 기준 경로 설정 (C:\dev\agent\더미데이터2000명)

📝 참고

GitHub 저장소: https://github.com/ai-sesac2-Nbbang/AI

문의: sesac2@ai.com
 (예시)
