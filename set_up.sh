#!/bin/bash
set -e

# ... 기존 시스템 업데이트 ...
echo "시스템 업데이트 진행 중..."
sudo apt-get update

# Tesseract 설치 (한국어 지원 포함)
echo "Tesseract 및 한국어 패키지 설치 중..."
sudo apt-get install -y tesseract-ocr tesseract-ocr-kor

# pip 최신 버전 업데이트 및 의존성 설치
echo "pip 업데이트 및 의존성 설치 중..."
pip install --upgrade pip
pip install -r requirements.txt

echo "설치 완료되었습니다."
