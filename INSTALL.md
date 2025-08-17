# MP4 to MP3 Converter - 설치 가이드

## 🚀 빠른 설치

### macOS
1. `MP4toMP3_macOS.dmg` 다운로드
2. DMG 파일 열기
3. MP4toMP3 앱을 Applications 폴더로 드래그
4. 첫 실행 시 "개발자 확인되지 않음" 경고가 나타나면:
   - 시스템 환경설정 > 보안 및 개인정보 보호
   - "확인 없이 열기" 클릭

### Windows
1. `MP4toMP3_Setup.exe` 다운로드
2. 설치 프로그램 실행
3. 설치 마법사 따라가기
4. 바탕화면 바로가기 자동 생성

## 📦 포함된 기능

- **MP4 to MP3 변환**: 고품질 오디오 추출
- **AI 음성인식 (STT)**: Small 모델 내장
- **일괄 처리**: 여러 파일 동시 변환
- **실시간 진행률**: 변환 상태 확인

## 🎯 시스템 요구사항

### 최소 사양
- **macOS**: 10.12 Sierra 이상
- **Windows**: Windows 10 이상
- **RAM**: 4GB
- **저장공간**: 1GB

### 권장 사양
- **RAM**: 8GB (STT 사용 시)
- **저장공간**: 2GB
- **프로세서**: Intel i5 또는 Apple M1 이상

## 🔧 문제 해결

### macOS - "손상된 앱" 오류
```bash
xattr -cr /Applications/MP4toMP3.app
```

### Windows - DLL 오류
Visual C++ 재배포 가능 패키지 설치:
https://aka.ms/vs/17/release/vc_redist.x64.exe

### ffmpeg 오류
앱에 ffmpeg가 포함되어 있지만, 시스템 ffmpeg를 사용하려면:
- macOS: `brew install ffmpeg`
- Windows: https://ffmpeg.org/download.html

## 📝 사용법

1. **파일 선택**: 드래그 앤 드롭 또는 클릭
2. **STT 옵션**: 음성을 텍스트로 변환 (선택)
3. **변환 시작**: 변환 버튼 클릭
4. **결과**: MP3와 TXT 파일 생성

## 🆘 지원

문제가 있으신가요?
- GitHub Issues: https://github.com/yourusername/mp4tomp3/issues
- Email: support@mp4tomp3.com

## 📄 라이선스

본 소프트웨어는 MIT 라이선스로 배포됩니다.
Whisper 모델은 OpenAI의 라이선스를 따릅니다.