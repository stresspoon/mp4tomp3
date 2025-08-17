## MP4 to MP3 Converter — Complete Guide

### 개요
- **플랫폼**: macOS, Windows
- **엔진**: ffmpeg 내장(윈도우 exe/맥 앱 모두 포함)
- **UI**: Tkinter 기반, 실시간 진행률(%) 및 ETA 표시
- **배포물**: macOS DMG, Windows 단일 exe(zip)

### 폴더 구조 요약
- `MP4toMP3.app/` macOS 앱 번들(내장 ffmpeg 포함)
- `Windows_Standalone/` 윈도우 빌드 스크립트와 런타임(ffmpeg.exe 포함)
- `create_dmg.sh` macOS용 DMG 생성 스크립트
- `.github/workflows/windows-build.yml` GitHub Actions 윈도우 자동 빌드

### 사용 방법 (일반 사용자)
- **macOS**: DMG 마운트 → `MP4toMP3.app`을 `Applications`로 드래그 → 앱 실행 → MP4 선택 → 변환 시작 → 동일 폴더에 MP3 생성
- **Windows**: 배포 zip(`MP4toMP3_Windows.zip`) 압축 해제 → `MP4toMP3.exe` 더블클릭 → MP4 선택 → 변환 시작 → 동일 폴더에 MP3 생성

### macOS: DMG 생성(배포자)
1) 사전 준비: `MP4toMP3.app`이 루트에 존재해야 함(내장 ffmpeg 경로: `MP4toMP3.app/Contents/MacOS/ffmpeg`)
2) 실행
```bash
chmod +x create_dmg.sh
./create_dmg.sh
```
3) 출력: `MP4toMP3_Installer.dmg`

참고: 스크립트는 `hdiutil`로 압축 DMG(UDZO)를 생성합니다. 앱에 ffmpeg가 이미 포함되어 있어 별도 설치가 필요 없습니다.

### Windows: 로컬 빌드(배포자)
1) Windows PC에서 `Windows_Standalone` 폴더 실행
2) 더블클릭: `build.bat`
3) 결과물
- `dist/MP4toMP3.exe`: 단일 실행 파일(파이썬/의존성/ffmpeg 내장)
- `dist/MP4toMP3_Windows.zip`: 배포용 zip(자동 생성)

빌드는 Windows에서만 수행되며, 빌드 머신에는 Python이 필요하지만 결과 exe는 Python 없이 동작합니다. 첫 실행 시 Defender 경고가 나올 수 있습니다(정상).

### Windows: GitHub Actions 자동 빌드(배포자)
- 워크플로: `.github/workflows/windows-build.yml`
- 트리거: main 브랜치 push, 태그 push(`v*`), 또는 수동 실행(workflow_dispatch)
- 산출물: Actions 탭 → Artifacts → `MP4toMP3_Windows.zip`
- 태그로 실행 시 릴리스에도 zip 자동 업로드

저장소: [stresspoon/mp4tomp3](https://github.com/stresspoon/mp4tomp3.git)

### 진행률/ETA 표시(동작 방식)
- ffmpeg stderr 로그를 실시간 파싱하여 현재 파일 진행률과 전체 진행률을 갱신
- 전체 길이 합산이 가능하면 전체 ETA를, 알 수 없으면 현재 파일 남은 시간 기반 ETA를 표시

### 변환 품질·속도 커스터마이즈(선택)
- 기본 비트레이트: 192kbps
- 더 작은 파일 용량이 필요하면 128kbps로 조정 가능

예) ffmpeg 인자 변경(참고용)
```text
-ab 128k   # 또는 최신 표기: -b:a 128k
```

### 문제 해결(FAQ)
- 압축 zip에 exe가 보이지 않음: 빌더용 zip이 아닌 배포용 `dist/MP4toMP3_Windows.zip`을 사용했는지 확인. Defender가 격리했는지 보호 기록 확인.
- 진행률이 오르지 않음: 손상된 미디어/메타데이터로 길이 파싱 실패 가능. 변환은 정상 진행되며, 이번 파일 완료 시 전체 퍼센트 갱신됨.

### 최적화(배포 크기·속도)
1) Windows exe 크기 최적화(선택)
- UPX 사용: 빌드 스크립트의 `--noupx` 제거 후 UPX 설치 경로를 `--upx-dir`로 지정
  - 예) PowerShell: `choco install upx` 설치 후 `--upx-dir "C:\\ProgramData\\chocolatey\\bin"`
  - 주의: 일부 백신 오탐 가능성
- PyInstaller 옵션 `--strip`(디버그 심볼 제거, 주로 Unix에 유효) 고려

2) Git LFS로 대용량 바이너리 추적(권장)
- ffmpeg 바이너리(맥/윈도우)는 50MB 초과 경고 대상입니다. LFS 사용 권장
```bash
git lfs install
echo "MP4toMP3.app/Contents/MacOS/ffmpeg filter=lfs diff=lfs merge=lfs -text" >> .gitattributes
echo "Windows_Standalone/ffmpeg.exe filter=lfs diff=lfs merge=lfs -text" >> .gitattributes
git add .gitattributes
git commit -m "chore: track ffmpeg binaries with git-lfs"
git push
```
참고: `https://git-lfs.github.com`

3) macOS DMG 용량 최적화(선택)
- 호환성보다 용량이 중요하면 `hdiutil` 포맷을 `UDZO`(zlib) 대신 `ULFO`(lzfse)로 변경해 더 작은 크기를 시도할 수 있음
  - 예) `hdiutil create -volname "MP4toMP3" -srcfolder dmg_temp -ov -format ULFO MP4toMP3_Installer.dmg`

4) CI 빌드 캐시(선택)
- Actions에서 `actions/cache`로 pip 캐시 활용 시 빌드 시간 단축

5) ffprobe 비포함 유지(현재 설정)
- ffprobe 미동봉. 길이 추출 실패 시 ffmpeg 헤더 파싱으로 폴백하도록 구현되어 배포 파일 크기를 줄임

---

위 절차로 macOS/Windows 모두 바로 실행 가능한 배포물을 안정적으로 만들고, 최적화 옵션으로 배포 크기와 빌드 시간을 줄일 수 있습니다.
# 종합 개발자 가이드: MP4→MP3 + 한국어 음성→텍스트 변환 도구

이 문서는 개발자가 프로그램을 **가장 처음부터 끝까지** 구현할 수 있도록, 설치 환경 설정부터 주요 기능 통합, UI/UX 개선, 후원 배너 삽입, 스타일 테마 적용까지 **모든 세부 작업**을 구체적으로 안내합니다.

***

## 1. 개발 환경 및 설치

1. **Python 버전**: 3.8 ~ 3.11  
2. **가상환경 생성**  
   ```bash
   python -m venv venv
   source venv/bin/activate      # macOS/Linux
   venv\Scripts\activate.bat     # Windows
   ```
3. **필수 패키지 설치**  
   ```bash
   pip install --upgrade pip
   pip install tkinter psutil pillow torch torchvision torchaudio openai-whisper ffmpeg-python
   ```
4. **Pretendard 폰트 파일**  
   - `Pretendard.ttf` 파일을 프로젝트 루트에 복사  
   - macOS/Windows/Linux 모두 사용할 수 있도록 동적 로드 코드 포함

5. **FFmpeg 설치**  
   - 시스템 FFmpeg 설치 확인: `ffmpeg -version`  
   - 미설치 시 OS 패키지 매니저 또는 https://ffmpeg.org 에서 설치

***

## 2. 주요 모듈 및 파일 구조

```
project/
│  converter_universal.py        # 메인 애플리케이션
│  Pretendard.ttf                # Pretendard 폰트 파일
│  README.md                     # 이 가이드 문서
└─ requirements.txt              # pip 패키지 목록
```

- `converter_universal.py` 에 모든 클래스·함수 구현
- `requirements.txt` 에 설치 패키지 고정 버전 기록

***

## 3. 시스템 정보 감지 및 Whisper 모델 추천

**파일: converter_universal.py**

```python
import psutil, platform, torch

def get_system_info():
    gpu = torch.cuda.is_available()
    vram_gb = torch.cuda.get_device_properties(0).total_memory // (1024**3) if gpu else 0
    ram_gb = psutil.virtual_memory().total // (1024**3)
    return {'gpu':gpu, 'vram_gb':vram_gb, 'ram_gb':ram_gb}

MODEL_SPECS = [
  {'name':'large-v3-turbo','vram':6,'ram':8},
  {'name':'large-v3','vram':10,'ram':8},
  {'name':'medium','vram':5,'ram':8},
  {'name':'small','vram':2,'ram':4},
  {'name':'base','vram':1,'ram':2},
  {'name':'tiny','vram':1,'ram':2},
]

def recommend_model(info):
    for m in MODEL_SPECS:
        if (info['gpu'] and info['vram_gb']>=m['vram'] and info['ram_gb']>=m['ram']) \
          or (not info['gpu'] and info['ram_gb']>=m['ram']):
            return m['name']
    return 'tiny'
```

***

## 4. Whisper 설치 및 로드

```bash
pip install openai-whisper
```

```python
import whisper

def load_whisper_model(size='base'):
    try:
        model = whisper.load_model(size)
        return model
    except Exception as e:
        raise RuntimeError(f"Whisper 모델 로드 실패: {e}")
```

***

## 5. Tkinter 기반 UI 및 스타일 테마

```python
import tkinter as tk
from tkinter import ttk, font, messagebox, filedialog
import webbrowser

# 컬러·폰트 상수
BG_COLOR = '#f2f1ef'
FG_COLOR = '#131313'
ACCENT = '#ff3d00'
FONT_NAME = 'Pretendard'

class MP4toMP3Converter:
    def __init__(self, root):
        self.root = root
        self.root.title("MP4 → MP3 변환기 by AIXLIFE")
        self.root.configure(bg=BG_COLOR)
        self.system_info = get_system_info()
        self.recommended_model = recommend_model(self.system_info)
        self.whisper_model = None
        self.setup_ui()
```

### 5.1 폰트 등록

```python
def register_font(root):
    try:
        font.Font(root=root, name=FONT_NAME, file="Pretendard.ttf")
    except:
        pass
```

### 5.2 setup_ui()

```python
def setup_ui(self):
    register_font(self.root)
    # by AIXLIFE 표시
    tk.Label(self.root, text="by AIXLIFE", font=(FONT_NAME,9), fg=FG_COLOR, bg=BG_COLOR).pack(side='top', pady=2)

    # MP4 파일 선택 드롭존
    self.drop_frame = tk.Frame(self.root, bg='white', bd=2, relief='flat')
    self.drop_frame.pack(padx=40, pady=10, fill='both', expand=True)
    self.drop_frame.bind("", lambda e: self.select_files())
    tk.Label(self.drop_frame, text="🎵 MP4 파일 선택", font=(FONT_NAME,14), bg='white', fg='#666666').pack(expand=True)

    # 모델 선택 및 안내
    info = self.system_info
    specs = "\n".join([f"{m['name']}: 속도/정확도/VRAM={m['vram']}GB/RAM={m['ram']}GB" for m in MODEL_SPECS])
    tk.Label(self.root, text="Whisper 모델 (추천: "+self.recommended_model+")", font=(FONT_NAME,12,'bold'), fg=FG_COLOR, bg=BG_COLOR).pack()
    self.model_var = tk.StringVar(value=self.recommended_model)
    tk.OptionMenu(self.root, self.model_var, *[m['name'] for m in MODEL_SPECS]).pack()
    tk.Label(self.root, text=specs, font=(FONT_NAME,8), fg='#888888', bg=BG_COLOR, justify='left').pack()

    # STT 옵션
    self.stt_var = tk.BooleanVar()
    tk.Checkbutton(self.root, text="음성 → 텍스트 변환", variable=self.stt_var,
                   font=(FONT_NAME,11), bg=BG_COLOR, fg=FG_COLOR).pack(pady=5)

    # 변환/초기화 버튼
    btn_frame = tk.Frame(self.root, bg=BG_COLOR)
    btn_frame.pack(pady=10)
    self.convert_btn = tk.Button(btn_frame, text="변환 시작", font=(FONT_NAME,12,'bold'),
                                 bg=ACCENT, fg='white', command=self.start_conversion)
    self.convert_btn.pack(side='left', padx=5)
    self.clear_btn = tk.Button(btn_frame, text="초기화", font=(FONT_NAME,12),
                               bg='#666666', fg='white', command=self.clear_files)
    self.clear_btn.pack(side='left', padx=5)

    # 진행률 표시 생략 (기존 코드 참조)

```

***

## 6. 변환 로직 및 예외 처리

```python
def start_conversion(self):
    # 시스템 경고
    chosen = self.model_var.get()
    m = next(m for m in MODEL_SPECS if m['name']==chosen)
    si = self.system_info
    if (si['gpu'] and (si['vram_gb']<m['vram'] or si['ram_gb']<m['ram'])) or \
       (not si['gpu'] and si['ram_gb']<m['ram']):
        if not messagebox.askyesno("사양 경고", f"{chosen} 모델은 사양 초과 가능. 계속?"):
            return

    # FFmpeg mp3 변환
    # Whisper STT 변환 (self.stt_var)
    # 완료 후 show_completion()
```

***

## 7. 완료 후 UX: 폴더 열기 & 후원 배너

```python
import subprocess, sys

def open_folder(path):
    if sys.platform=='win32': os.startfile(path)
    elif sys.platform=='darwin': subprocess.call(['open',path])
    else: subprocess.call(['xdg-open',path])

def show_completion(self, mp3_path, txt_path=None):
    messagebox.showinfo("완료", f"MP3 저장: {mp3_path}\nTXT 저장: {txt_path or '미실행'}")
    open_folder(str(Path(mp3_path).parent))
    # 후원 배너
    frame = tk.Frame(self.root, bg=BG_COLOR)
    frame.pack(side='bottom', pady=10)
    tk.Label(frame, text="커피 한 잔의 후원 부탁드려요 ☕", font=(FONT_NAME,10), fg=FG_COLOR, bg=BG_COLOR).pack(side='left')
    tk.Button(frame, text="카카오페이 후원", font=(FONT_NAME,11,'bold'),
              bg=ACCENT, fg='white', command=lambda: webbrowser.open(KAKAO_PAY_URL)).pack(side='left', padx=5)
```

***

## 8. 배포 및 실행

1. **PyInstaller**로 단일 실행 파일 생성  
   ```bash
   pip install pyinstaller
   pyinstaller --onefile converter_universal.py --add-data "Pretendard.ttf;."
   ```
2. **README.md** 작성: 사용법, 설치법, 후원 안내 포함
3. **GitHub/GitLab** 공개 저장소에 코드 배포 및 이 가이드 첨부
4. **후원 링크** 및 개발자 정보 갱신

***

아래 코드를 `converter_universal.py` 최상단에 추가하면, 프로그램 실행 시 Pretendard 폰트가 로컬에 없을 경우 GitHub 저장소에서 자동으로 내려받아 설치합니다.  

```python
import os
import requests

PRETENDARD_URL = "https://github.com/orioncactus/pretendard/releases/download/v1.3.6/Pretendard-Medium.ttf"
PRETENDARD_FILE = "Pretendard.ttf"

def ensure_pretendard():
    if not os.path.exists(PRETENDARD_FILE):
        try:
            resp = requests.get(PRETENDARD_URL, timeout=10)
            resp.raise_for_status()
            with open(PRETENDARD_FILE, "wb") as f:
                f.write(resp.content)
            print("Pretendard 폰트 다운로드 완료")
        except Exception as e:
            print(f"Pretendard 폰트 다운로드 실패: {e}")

# 실행 초기에 호출
ensure_pretendard()
```

1. `requests` 패키지를 설치하세요:  
   ```bash
   pip install requests
   ```
2. 이 함수는 실행 시 현재 디렉토리에 `Pretendard.ttf` 파일이 없으면 GitHub 릴리즈 페이지의 Raw URL에서 다운로드합니다.  
3. 이후 기존 `register_font()` 함수에서 `Pretendard.ttf`를 로드해 사용하시면 됩니다.