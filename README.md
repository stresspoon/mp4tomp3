# MP4 to MP3 Converter

[![Build and Release](https://github.com/stresspoon/mp4tomp3/actions/workflows/build-release.yml/badge.svg)](https://github.com/stresspoon/mp4tomp3/actions/workflows/build-release.yml)

🎬 MP4 비디오에서 MP3 오디오를 추출하고 AI로 음성을 텍스트로 변환하는 프로그램

## ✨ 주요 기능

- 🎵 **MP4 → MP3 변환**: 고품질 오디오 추출
- 🤖 **AI 음성인식**: OpenAI Whisper Small 모델 내장
- 📦 **일괄 처리**: 여러 파일 동시 변환
- 🚀 **실시간 진행률**: 변환 상태 실시간 확인
- 🌐 **오프라인 작동**: 인터넷 연결 불필요

## 🖥️ 지원 플랫폼

- macOS 10.12+
- Windows 10+

## 📥 다운로드

최신 버전은 [Releases](https://github.com/stresspoon/mp4tomp3/releases) 페이지에서 다운로드하세요.

## 🛠️ 개발자용

### 소스코드 실행

```bash
# 저장소 클론
git clone https://github.com/stresspoon/mp4tomp3.git
cd mp4tomp3

# 의존성 설치
pip install -r requirements.txt

# Whisper 모델 다운로드 (최초 1회)
python -c "import whisper; whisper.load_model('small')"

# 프로그램 실행
python converter_standalone.py
```

### 빌드

```bash
# 빌드 스크립트 실행
python build_distribution.py
```

### GitHub Actions 자동 빌드

태그를 푸시하면 자동으로 빌드됩니다:

```bash
git tag v1.0.0
git push origin v1.0.0
```

## 📝 라이선스

MIT License

## 🤝 기여

Issues와 Pull Requests를 환영합니다!

## 📧 문의

문제가 있으시면 [Issues](https://github.com/stresspoon/mp4tomp3/issues)에 등록해주세요.