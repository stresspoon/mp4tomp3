#!/usr/bin/env python3
"""
Whisper 설치 및 작동 테스트 스크립트
"""

import sys
import os

print("="*50)
print("Whisper STT 테스트")
print("="*50)
print()

# 1. Whisper import 테스트
try:
    import whisper
    print("✅ Whisper 라이브러리 import 성공")
    print(f"   버전 정보: {whisper.__version__ if hasattr(whisper, '__version__') else 'unknown'}")
except ImportError as e:
    print(f"❌ Whisper 라이브러리 import 실패: {e}")
    print("\n설치 방법:")
    print("pip install openai-whisper")
    sys.exit(1)

print()

# 2. 모델 로드 테스트
try:
    print("모델 로드 테스트 (tiny 모델)...")
    model = whisper.load_model("tiny")
    print("✅ 모델 로드 성공")
except Exception as e:
    print(f"❌ 모델 로드 실패: {e}")
    sys.exit(1)

print()

# 3. 간단한 음성 인식 테스트 (MP3 파일이 있을 경우)
test_files = []
for ext in ['*.mp3', '*.mp4', '*.wav']:
    import glob
    files = glob.glob(ext)
    if files:
        test_files.extend(files[:1])  # 첫 번째 파일만

if test_files:
    test_file = test_files[0]
    print(f"테스트 파일로 전사 시도: {test_file}")
    try:
        result = model.transcribe(test_file, language='ko', fp16=False)
        text = result.get('text', '').strip()
        print(f"✅ 전사 성공! (텍스트 길이: {len(text)} 글자)")
        if text:
            print(f"   첫 100자: {text[:100]}...")
    except Exception as e:
        print(f"❌ 전사 실패: {e}")
else:
    print("테스트할 음성 파일이 없습니다.")

print()
print("="*50)
print("테스트 완료!")
print("="*50)