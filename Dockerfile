FROM python:3.11-slim

# 컨테이너 작업 디렉토리
WORKDIR /app

# requirements.txt만 먼저 복사 → 캐시 활용
COPY requirements.txt ./

# 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 나머지 소스 전체 복사
COPY . .

# 필요하면 실행 커맨드
# CMD ["python", "main.py"]
