#!/usr/bin/env python3
"""
MP4 to MP3 Converter with Bundled Whisper
배포용 독립 실행 버전
"""

import sys
import os
from pathlib import Path

# 번들 경로 설정 (PyInstaller용)
if getattr(sys, 'frozen', False):
    # PyInstaller 번들
    application_path = Path(sys._MEIPASS)
else:
    # 일반 Python 스크립트
    application_path = Path(__file__).parent

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import threading
import platform
import re
import time

# Whisper lazy import
WHISPER_AVAILABLE = False
whisper = None

def init_whisper():
    """Whisper 초기화 (필요시에만)"""
    global WHISPER_AVAILABLE, whisper
    try:
        import whisper as _whisper
        whisper = _whisper
        WHISPER_AVAILABLE = True
        return True
    except ImportError:
        print("Whisper 설치 중...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "openai-whisper"], 
                         capture_output=True, check=True)
            import whisper as _whisper
            whisper = _whisper
            WHISPER_AVAILABLE = True
            return True
        except:
            return False

class MP4ConverterBundled:
    def __init__(self, root):
        self.root = root
        self.root.title("MP4 to MP3 Converter Pro")
        self.root.geometry("800x650")
        
        # 색상 테마
        self.colors = {
            'bg': '#f2f1ef',
            'card': '#ffffff',
            'accent': '#ff3d00',
            'accent_hover': '#e63600',
            'text': '#131313',
            'text_secondary': '#666666',
            'success': '#10b981',
            'error': '#ef4444',
            'border': '#e0e0e0'
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        # 번들된 모델 경로
        self.bundled_model_path = application_path / "models" / "small.pt"
        if not self.bundled_model_path.exists():
            # 대체 경로
            self.bundled_model_path = application_path / "small.pt"
        
        self.whisper_model = None
        self.files_to_convert = []
        self.enable_stt = tk.BooleanVar(value=False)
        self.is_converting = False
        
        self.setup_ui()
        
    def setup_ui(self):
        """UI 구성"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 메인 컨테이너
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # 타이틀
        self.create_title_section(main_container)
        
        # 드롭 존
        self.create_drop_zone(main_container)
        
        # STT 옵션
        self.create_stt_option(main_container)
        
        # 진행률
        self.create_progress_section(main_container)
        
        # 버튼
        self.create_buttons(main_container)
    
    def create_title_section(self, parent):
        """타이틀 섹션"""
        title_frame = tk.Frame(parent, bg=self.colors['bg'])
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            title_frame,
            text="MP4 to MP3 Converter",
            font=('Arial', 24, 'bold'),
            bg=self.colors['bg'],
            fg=self.colors['text']
        ).pack()
        
        tk.Label(
            title_frame,
            text="AI 음성인식 기능 내장",
            font=('Arial', 12),
            bg=self.colors['bg'],
            fg=self.colors['accent']
        ).pack()
    
    def create_drop_zone(self, parent):
        """파일 선택 영역"""
        card = tk.Frame(
            parent,
            bg=self.colors['card'],
            highlightbackground=self.colors['border'],
            highlightthickness=1
        )
        card.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        self.drop_frame = tk.Frame(card, bg=self.colors['card'])
        self.drop_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        drop_content = tk.Frame(self.drop_frame, bg=self.colors['card'])
        drop_content.pack(expand=True)
        
        tk.Label(
            drop_content,
            text="📁",
            font=('Arial', 48),
            bg=self.colors['card'],
            fg=self.colors['accent']
        ).pack(pady=(40, 10))
        
        self.drop_label = tk.Label(
            drop_content,
            text="클릭하여 MP4 파일 선택",
            font=('Arial', 14),
            bg=self.colors['card'],
            fg=self.colors['text']
        )
        self.drop_label.pack(pady=(0, 40))
        
        # 클릭 이벤트
        for widget in [self.drop_frame, drop_content] + list(drop_content.winfo_children()):
            widget.bind("<Button-1>", lambda e: self.select_files())
    
    def create_stt_option(self, parent):
        """STT 옵션"""
        option_frame = tk.Frame(parent, bg=self.colors['bg'])
        option_frame.pack(fill=tk.X, pady=(0, 20))
        
        stt_container = tk.Frame(
            option_frame,
            bg=self.colors['card'],
            highlightbackground=self.colors['border'],
            highlightthickness=1
        )
        stt_container.pack(fill=tk.X)
        
        stt_inner = tk.Frame(stt_container, bg=self.colors['card'])
        stt_inner.pack(fill=tk.X, padx=15, pady=12)
        
        self.stt_check = tk.Checkbutton(
            stt_inner,
            text="음성을 텍스트로 변환 (STT)",
            variable=self.enable_stt,
            font=('Arial', 12, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text'],
            selectcolor=self.colors['card'],
            activebackground=self.colors['card'],
            command=self.on_stt_toggle
        )
        self.stt_check.pack(side=tk.LEFT)
        
        self.stt_status = tk.Label(
            stt_inner,
            text="",
            font=('Arial', 11),
            bg=self.colors['card'],
            fg=self.colors['text_secondary']
        )
        self.stt_status.pack(side=tk.LEFT, padx=(20, 0))
        
        # 초기 상태 확인
        self.check_whisper_status()
    
    def check_whisper_status(self):
        """Whisper 상태 확인"""
        if self.bundled_model_path.exists():
            self.stt_status.config(
                text="✓ AI 모델 내장 (즉시 사용 가능)",
                fg=self.colors['success']
            )
        else:
            self.stt_status.config(
                text="⚠️ AI 모델을 찾을 수 없습니다",
                fg=self.colors['error']
            )
            self.stt_check.config(state=tk.DISABLED)
    
    def on_stt_toggle(self):
        """STT 토글시 Whisper 초기화"""
        if self.enable_stt.get() and not WHISPER_AVAILABLE:
            self.stt_status.config(text="AI 엔진 초기화 중...")
            self.root.update()
            
            if init_whisper():
                self.stt_status.config(
                    text="✓ AI 모델 준비 완료",
                    fg=self.colors['success']
                )
            else:
                self.stt_status.config(
                    text="⚠️ AI 초기화 실패",
                    fg=self.colors['error']
                )
                self.enable_stt.set(False)
    
    def create_progress_section(self, parent):
        """진행률 섹션"""
        self.progress_frame = tk.Frame(parent, bg=self.colors['bg'])
        
        progress_card = tk.Frame(
            self.progress_frame,
            bg=self.colors['card'],
            highlightbackground=self.colors['border'],
            highlightthickness=1
        )
        progress_card.pack(fill=tk.BOTH, expand=True)
        
        progress_inner = tk.Frame(progress_card, bg=self.colors['card'])
        progress_inner.pack(fill=tk.BOTH, padx=20, pady=20)
        
        self.current_file_label = tk.Label(
            progress_inner,
            text="변환 중...",
            font=('Arial', 14, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text']
        )
        self.current_file_label.pack(anchor='w', pady=(0, 10))
        
        self.progress_bar = ttk.Progressbar(
            progress_inner,
            length=740,
            mode='determinate'
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        
        self.progress_text = tk.Label(
            progress_inner,
            text="0%",
            font=('Arial', 24, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['accent']
        )
        self.progress_text.pack(pady=(10, 5))
        
        self.status_label = tk.Label(
            progress_inner,
            text="",
            font=('Arial', 11),
            bg=self.colors['card'],
            fg=self.colors['text_secondary']
        )
        self.status_label.pack()
    
    def create_buttons(self, parent):
        """버튼 섹션"""
        button_frame = tk.Frame(parent, bg=self.colors['bg'])
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.convert_button = tk.Button(
            button_frame,
            text="변환 시작",
            font=('Arial', 14, 'bold'),
            bg=self.colors['accent'],
            fg='white',
            padx=40,
            pady=12,
            relief=tk.FLAT,
            cursor='hand2',
            command=self.start_conversion,
            state=tk.DISABLED
        )
        self.convert_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_button = tk.Button(
            button_frame,
            text="초기화",
            font=('Arial', 14),
            bg=self.colors['text_secondary'],
            fg='white',
            padx=30,
            pady=12,
            relief=tk.FLAT,
            cursor='hand2',
            command=self.clear_files,
            state=tk.DISABLED
        )
        self.clear_button.pack(side=tk.LEFT)
        
        # 호버 효과
        def on_enter(e, btn, color):
            if btn['state'] == tk.NORMAL:
                btn.config(bg=color)
        
        def on_leave(e, btn, color):
            if btn['state'] == tk.NORMAL:
                btn.config(bg=color)
        
        self.convert_button.bind('<Enter>', lambda e: on_enter(e, self.convert_button, self.colors['accent_hover']))
        self.convert_button.bind('<Leave>', lambda e: on_leave(e, self.convert_button, self.colors['accent']))
        self.clear_button.bind('<Enter>', lambda e: on_enter(e, self.clear_button, '#555555'))
        self.clear_button.bind('<Leave>', lambda e: on_leave(e, self.clear_button, self.colors['text_secondary']))
    
    def select_files(self):
        """파일 선택"""
        files = filedialog.askopenfilenames(
            title="MP4 파일 선택",
            filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")]
        )
        if files:
            self.files_to_convert = list(files)
            count = len(self.files_to_convert)
            self.drop_label.config(
                text=f"{count}개 파일 선택됨",
                fg=self.colors['success']
            )
            self.convert_button.config(state=tk.NORMAL)
            self.clear_button.config(state=tk.NORMAL)
    
    def clear_files(self):
        """선택 초기화"""
        self.files_to_convert = []
        self.drop_label.config(
            text="클릭하여 MP4 파일 선택",
            fg=self.colors['text']
        )
        self.convert_button.config(state=tk.DISABLED)
        self.clear_button.config(state=tk.DISABLED)
        self.progress_frame.pack_forget()
        self.drop_frame.master.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
    
    def start_conversion(self):
        """변환 시작"""
        if not self.files_to_convert:
            return
        
        # ffmpeg 확인
        self.ffmpeg_path = self.check_ffmpeg()
        if not self.ffmpeg_path:
            messagebox.showerror("오류", "ffmpeg를 찾을 수 없습니다.\n프로그램을 다시 설치해주세요.")
            return
        
        # Whisper 모델 로드
        if self.enable_stt.get():
            if not WHISPER_AVAILABLE:
                self.on_stt_toggle()
            
            if WHISPER_AVAILABLE and self.bundled_model_path.exists():
                try:
                    self.status_label.config(text="AI 모델 로딩 중...")
                    self.root.update()
                    
                    # 번들된 모델 로드
                    self.whisper_model = whisper.load_model(str(self.bundled_model_path))
                    print("✓ Whisper 모델 로드 완료")
                except Exception as e:
                    print(f"모델 로드 실패: {e}")
                    messagebox.showwarning("경고", "AI 모델을 로드할 수 없습니다.\n일반 변환만 진행합니다.")
                    self.enable_stt.set(False)
        
        # UI 업데이트
        self.drop_frame.master.pack_forget()
        self.progress_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        self.convert_button.config(state=tk.DISABLED)
        self.clear_button.config(state=tk.DISABLED)
        
        # 변환 시작
        self.is_converting = True
        thread = threading.Thread(target=self.convert_files, daemon=True)
        thread.start()
    
    def check_ffmpeg(self):
        """ffmpeg 경로 확인"""
        # 번들된 ffmpeg 확인
        bundled_ffmpeg = application_path / ("ffmpeg.exe" if platform.system() == "Windows" else "ffmpeg")
        if bundled_ffmpeg.exists():
            return str(bundled_ffmpeg)
        
        # 시스템 ffmpeg
        if platform.system() == "Darwin":
            paths = ['/opt/homebrew/bin/ffmpeg', '/usr/local/bin/ffmpeg']
            for path in paths:
                if Path(path).exists():
                    return path
        
        # which/where 명령
        try:
            cmd = "where" if platform.system() == "Windows" else "which"
            result = subprocess.run([cmd, "ffmpeg"], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
        except:
            pass
        
        return None
    
    def get_file_duration(self, file_path):
        """파일 길이 확인"""
        try:
            cmd = [
                self.ffmpeg_path,
                '-i', file_path,
                '-f', 'null',
                '-'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            duration_match = re.search(r'Duration: (\d{2}):(\d{2}):(\d{2})\.\d+', result.stderr)
            if duration_match:
                hours = int(duration_match.group(1))
                minutes = int(duration_match.group(2))
                seconds = int(duration_match.group(3))
                return hours * 3600 + minutes * 60 + seconds
        except:
            pass
        return 0
    
    def convert_files(self):
        """파일 변환 실행"""
        total = len(self.files_to_convert)
        
        for i, file_path in enumerate(self.files_to_convert):
            if not self.is_converting:
                break
            
            input_path = Path(file_path)
            output_path = input_path.with_suffix('.mp3')
            
            # 파일 길이 확인
            duration = self.get_file_duration(str(input_path))
            
            try:
                # MP3 변환
                cmd = [
                    self.ffmpeg_path,
                    '-i', str(input_path),
                    '-vn',
                    '-acodec', 'libmp3lame',
                    '-ab', '192k',
                    '-y',
                    '-progress', 'pipe:1',
                    str(output_path)
                ]
                
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                
                # 진행률 업데이트
                while True:
                    line = process.stdout.readline()
                    if not line:
                        break
                    
                    if 'out_time_ms=' in line:
                        try:
                            time_ms = int(line.split('=')[1])
                            current_seconds = time_ms / 1000000
                            if duration > 0:
                                file_percent = min(int((current_seconds / duration) * 100), 100)
                                overall_percent = int(((i + file_percent/100) / total) * 100)
                                self.root.after(0, self.update_progress, input_path.name, overall_percent)
                        except:
                            pass
                
                process.wait()
                
                # STT 실행
                if self.enable_stt.get() and self.whisper_model:
                    self.root.after(0, lambda name=input_path.name: self.status_label.config(
                        text=f"음성 인식 중: {name}"
                    ))
                    
                    try:
                        result = self.whisper_model.transcribe(
                            str(output_path),
                            language='ko',
                            fp16=False
                        )
                        
                        text = result.get('text', '').strip()
                        if text:
                            txt_path = input_path.with_suffix('.txt')
                            with open(txt_path, 'w', encoding='utf-8') as f:
                                f.write(text)
                            
                            self.root.after(0, lambda name=txt_path.name: self.status_label.config(
                                text=f"텍스트 파일 생성: {name}"
                            ))
                    except Exception as e:
                        print(f"STT 오류: {e}")
                
            except Exception as e:
                print(f"변환 오류: {e}")
        
        # 완료
        self.root.after(0, self.conversion_complete)
    
    def update_progress(self, filename, percent):
        """진행률 업데이트"""
        self.current_file_label.config(text=f"변환 중: {filename}")
        self.progress_bar['value'] = percent
        self.progress_text.config(text=f"{percent}%")
    
    def conversion_complete(self):
        """변환 완료"""
        self.is_converting = False
        self.whisper_model = None
        messagebox.showinfo("완료", "모든 파일 변환이 완료되었습니다!")
        self.clear_files()

def main():
    root = tk.Tk()
    app = MP4ConverterBundled(root)
    
    # 앱 아이콘 설정 (있는 경우)
    icon_path = application_path / "icon.ico"
    if icon_path.exists():
        try:
            root.iconbitmap(str(icon_path))
        except:
            pass
    
    root.mainloop()

if __name__ == "__main__":
    main()
