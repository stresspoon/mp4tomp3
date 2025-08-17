# 🚀 배포 가이드

## 1. GitHub 저장소 설정

### 1.1 저장소 생성
```bash
# 1. GitHub에서 새 저장소 생성 (mp4tomp3)

# 2. 로컬 저장소 초기화
git init
git add .
git commit -m "Initial commit"

# 3. 원격 저장소 연결
git remote add origin https://github.com/stresspoon/mp4tomp3.git
git branch -M main
git push -u origin main
```

### 1.2 필수 파일 확인
```
mp4tomp3/
├── .github/
│   └── workflows/
│       └── build-release.yml    # 자동 빌드 워크플로우
├── converter_standalone.py      # 메인 프로그램
├── whisper_manager.py           # Whisper 관리
├── custom_widgets.py            # UI 위젯
├── requirements.txt             # Python 의존성
├── README.md                    # 프로젝트 설명
├── .gitignore                   # Git 제외 파일
└── DEPLOY_GUIDE.md             # 이 파일
```

## 2. 자동 빌드 설정 (GitHub Actions)

### 2.1 Actions 활성화
1. GitHub 저장소 → Settings → Actions
2. "Allow all actions" 선택
3. Save

### 2.2 릴리스 자동 생성
```bash
# 버전 태그 생성 및 푸시
git tag v1.0.0
git push origin v1.0.0

# GitHub Actions가 자동으로:
# 1. Windows .exe 빌드
# 2. macOS .dmg 빌드
# 3. Release 페이지에 업로드
```

## 3. 수동 빌드 (로컬)

### 3.1 Windows 빌드
```bash
# Windows에서 실행
pip install pyinstaller
python build_distribution.py
# → dist/MP4toMP3.exe 생성
```

### 3.2 macOS 빌드
```bash
# macOS에서 실행
pip install pyinstaller
python build_distribution.py
# → dist/MP4toMP3.app 생성

# DMG 생성
hdiutil create -volname "MP4toMP3" -srcfolder dist/MP4toMP3.app -ov -format UDZO MP4toMP3.dmg
```

## 4. 배포 체크리스트

### 릴리스 전 확인사항
- [ ] 코드 테스트 완료
- [ ] 버전 번호 업데이트
- [ ] README.md 업데이트
- [ ] 불필요한 파일 제거 (`python cleanup.py`)

### 릴리스 과정
1. **코드 커밋**
   ```bash
   git add .
   git commit -m "Release v1.0.0"
   git push
   ```

2. **태그 생성**
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

3. **자동 빌드 확인**
   - GitHub Actions 탭에서 빌드 진행 확인
   - 약 10-15분 소요

4. **릴리스 확인**
   - Releases 페이지에서 자동 생성된 릴리스 확인
   - 다운로드 링크 테스트

## 5. 배포 URL

빌드가 완료되면 다음 URL에서 다운로드 가능:
```
https://github.com/stresspoon/mp4tomp3/releases/latest
```

### 직접 다운로드 링크
- Windows: `https://github.com/stresspoon/mp4tomp3/releases/latest/download/MP4toMP3.exe`
- macOS: `https://github.com/stresspoon/mp4tomp3/releases/latest/download/MP4toMP3.dmg`

## 6. 업데이트 프로세스

### 새 버전 릴리스
1. 코드 수정
2. 버전 번호 증가 (예: v1.0.0 → v1.0.1)
3. 변경사항 문서화
4. 새 태그로 푸시

### 사용자 알림
- GitHub Releases 페이지 자동 업데이트
- 사용자는 새 버전 다운로드

## 7. 문제 해결

### Actions 빌드 실패
- Actions 탭에서 로그 확인
- requirements.txt 의존성 확인
- Python 버전 확인 (3.10 권장)

### 파일 크기 문제
- GitHub 파일 크기 제한: 100MB
- Large File Storage (LFS) 사용 고려
- 또는 외부 호스팅 사용

## 8. 마케팅 및 배포

### 배포 채널
1. **GitHub Releases**: 개발자 대상
2. **웹사이트**: 일반 사용자 대상
3. **소셜 미디어**: 홍보용

### 다운로드 페이지 예시
```html
<!DOCTYPE html>
<html>
<head>
    <title>MP4 to MP3 Converter</title>
</head>
<body>
    <h1>MP4 to MP3 Converter 다운로드</h1>
    <a href="https://github.com/stresspoon/mp4tomp3/releases/latest/download/MP4toMP3.exe">
        Windows 다운로드
    </a>
    <a href="https://github.com/stresspoon/mp4tomp3/releases/latest/download/MP4toMP3.dmg">
        macOS 다운로드
    </a>
</body>
</html>
```

## 완료! 🎉

이제 GitHub에 푸시하고 태그를 생성하면 자동으로 빌드되어 배포됩니다!