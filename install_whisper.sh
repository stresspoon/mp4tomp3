#!/bin/bash

echo "================================="
echo "Whisper STT 설치 스크립트"
echo "================================="
echo ""

# Python 버전 확인
echo "Python 버전 확인..."
python3 --version

# pip 업그레이드
echo ""
echo "pip 업그레이드..."
python3 -m pip install --upgrade pip

# Whisper 및 관련 패키지 설치
echo ""
echo "Whisper 및 관련 패키지 설치 중..."
echo "이 과정은 몇 분 정도 걸릴 수 있습니다..."
echo ""

# macOS에서는 CPU 버전으로 설치
python3 -m pip install openai-whisper

# 추가 필요 패키지
python3 -m pip install psutil

echo ""
echo "설치 확인 중..."
python3 -c "import whisper; print('✅ Whisper 설치 완료')" 2>/dev/null || echo "❌ Whisper 설치 실패"

echo ""
echo "================================="
echo "설치 완료!"
echo "================================="
echo ""
echo "테스트 실행:"
echo "python3 -c \"import whisper; model = whisper.load_model('tiny'); print('✅ Whisper 정상 작동')\""
echo ""