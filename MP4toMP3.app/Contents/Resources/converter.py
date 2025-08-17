#!/usr/bin/env python3
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import threading
import os
from pathlib import Path
import sys
import time
import platform
import urllib.request
import webbrowser

_WHISPER_MODEL_CACHE = {}

def ensure_pretendard(app_dir: str) -> str:
    """Ensure Pretendard.ttf exists; try download if missing. Returns local path or ''."""
    try:
        candidates = [
            os.path.join(app_dir, 'Pretendard.ttf'),
            os.path.join(app_dir, 'PretendardVariable.ttf'),
        ]
        meipass_dir = getattr(sys, '_MEIPASS', None)
        if meipass_dir:
            candidates += [
                os.path.join(meipass_dir, 'Pretendard.ttf'),
                os.path.join(meipass_dir, 'PretendardVariable.ttf'),
            ]
        for p in candidates:
            if os.path.isfile(p):
                return p
        # download variable font as Pretendard.ttf
        url = 'https://github.com/orioncactus/pretendard/releases/latest/download/PretendardVariable.ttf'
        target = os.path.join(app_dir, 'Pretendard.ttf')
        try:
            urllib.request.urlretrieve(url, target)
            if os.path.isfile(target) and os.path.getsize(target) > 0:
                return target
        except Exception:
            pass
        return ''
    except Exception:
        return ''

def get_system_info():
    """Return basic system info dict: {'has_cuda': False, 'vram_gb': None, 'ram_gb': float|None}."""
    info = {'has_cuda': False, 'vram_gb': None, 'ram_gb': None}
    # RAM
    try:
        import psutil  # type: ignore
        info['ram_gb'] = round(psutil.virtual_memory().total / (1024 ** 3), 1)
    except Exception:
        try:
            if sys.platform == 'darwin':
                # macOS: sysctl hw.memsize
                result = subprocess.run(['sysctl', '-n', 'hw.memsize'], capture_output=True, text=True)
                if result.returncode == 0:
                    info['ram_gb'] = round(int(result.stdout.strip()) / (1024 ** 3), 1)
        except Exception:
            info['ram_gb'] = None
    # CUDA not relevant on mac by default
    return info

def recommend_model(system_info):
    ram = system_info.get('ram_gb') or 0
    # mac default without GPU: use RAM thresholds
    if ram >= 16:
        return 'large-v3'
    if ram >= 12:
        return 'medium'
    if ram >= 8:
        return 'small'
    if ram >= 4:
        return 'base'
    return 'tiny'

def load_whisper_model(model_name: str):
    """Load whisper model on CPU (mac default)."""
    global _WHISPER_MODEL_CACHE
    device = 'cpu'
    try:
        import whisper  # type: ignore
    except Exception as e:
        raise RuntimeError('Whisper 라이브러리가 설치되어 있지 않습니다.') from e
    key = f'{model_name}:{device}'
    if key in _WHISPER_MODEL_CACHE:
        return _WHISPER_MODEL_CACHE[key]
    model = whisper.load_model(model_name, device=device)
    _WHISPER_MODEL_CACHE[key] = (model, device)
    return _WHISPER_MODEL_CACHE[key]
import re

class MP4toMP3Converter:
    def __init__(self, root):
        self.root = root
        self.root.title("MP4 to MP3 Converter")
        self.root.geometry("720x620")
        self.root.configure(bg='#f2f1ef')
        
        # Make window stay on top initially
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after(100, lambda: self.root.attributes('-topmost', False))
        
        self.files_to_convert = []
        self.current_file_index = 0
        self.start_time = None
        self.is_converting = False
        
        self.setup_ui()
        # Prefetch whisper model right after UI is ready (first app launch)
        try:
            self.root.after(100, self._start_model_prefetch)
        except Exception:
            pass
        
    def setup_ui(self):
        # Title / Theme / Font setup
        title_frame = tk.Frame(self.root, bg='#f2f1ef')
        title_frame.pack(pady=16)
        
        # Use different font based on OS
        if getattr(sys, 'frozen', False):
            app_dir = os.path.dirname(sys.executable)
        else:
            app_dir = os.path.dirname(os.path.abspath(__file__))
        ensure_pretendard(app_dir)
        if platform.system() == 'Darwin':
            font_family = 'Pretendard'
        elif platform.system() == 'Windows':
            font_family = 'Pretendard'
        else:
            font_family = 'Pretendard'
            
        title_label = tk.Label(
            title_frame,
            text="MP4 → MP3 변환기",
            font=(font_family, 24, 'bold'),
            bg='#f2f1ef',
            fg='#131313'
        )
        title_label.pack()
        sub_label = tk.Label(title_frame, text="by AIXLIFE", font=(font_family, 10), bg='#f2f1ef', fg='#131313')
        sub_label.pack(pady=(2, 0))
        
        # Drop zone
        self.drop_frame = tk.Frame(
            self.root,
            bg='white',
            relief=tk.FLAT,
            bd=2,
            highlightbackground='#e0e0e0',
            highlightthickness=2
        )
        self.drop_frame.pack(padx=24, pady=12, fill=tk.BOTH, expand=True)
        
        self.drop_label = tk.Label(
            self.drop_frame,
            text="🎵\n\nMP4 파일을 선택하세요\n클릭하여 파일 선택",
            font=(font_family, 14),
            bg='white',
            fg='#131313'
        )
        self.drop_label.pack(expand=True)
        
        # Make drop zone clickable
        self.drop_frame.bind("<Button-1>", lambda e: self.select_files())
        self.drop_label.bind("<Button-1>", lambda e: self.select_files())
        
        # Model / STT options
        options_frame = tk.Frame(self.root, bg='#f2f1ef')
        options_frame.pack(padx=24, pady=(0, 8), fill=tk.X)
        tk.Label(options_frame, text='Whisper 모델', font=(font_family, 12, 'bold'), bg='#f2f1ef', fg='#131313').pack(side=tk.LEFT)
        self.model_var = tk.StringVar()
        self.model_combo = ttk.Combobox(options_frame, textvariable=self.model_var, state='readonly', values=['tiny','base','small','medium','large-v3'], width=12)
        self.model_combo.pack(side=tk.LEFT, padx=(10, 12))
        sys_info = get_system_info()
        self.model_recommended = recommend_model(sys_info)
        self.model_var.set(self.model_recommended)
        # Prefetch when model selection changes, too
        try:
            self.model_combo.bind('<<ComboboxSelected>>', lambda e: self._start_model_prefetch())
        except Exception:
            pass
        self.enable_stt = tk.BooleanVar(value=False)
        tk.Label(options_frame, text=f"추천: {self.model_recommended} (RAM: {sys_info.get('ram_gb','?')}GB)", font=(font_family, 10), bg='#f2f1ef', fg='#131313').pack(side=tk.LEFT)
        self.stt_check = tk.Checkbutton(options_frame, text='STT (텍스트 생성)', variable=self.enable_stt, bg='#f2f1ef', fg='#131313', selectcolor='#f2f1ef', activebackground='#f2f1ef')
        self.stt_check.pack(side=tk.RIGHT)
        info_frame = tk.Frame(self.root, bg='#f2f1ef')
        info_frame.pack(padx=24, pady=(0,8), fill=tk.X)
        info_text = (
            "모델 안내 — 대략적 경향\n"
            "tiny: 가장 빠름 / 낮은 정확도 / ~1GB RAM\n"
            "base: 빠름 / 보통 정확도 / ~2-3GB RAM\n"
            "small: 보통 / 높은 정확도 / ~4-6GB RAM\n"
            "medium: 다소 느림 / 더 높은 정확도 / ~8-12GB RAM\n"
            "large-v3: 가장 느림 / 최고 정확도 / >=16GB RAM"
        )
        tk.Label(info_frame, text=info_text, font=(font_family, 9), justify=tk.LEFT, bg='#f2f1ef', fg='#131313').pack(anchor='w')
        
        # Progress frame (hidden initially)
        self.progress_frame = tk.Frame(self.root, bg='#f2f1ef')
        
        # Overall progress
        self.overall_label = tk.Label(
            self.progress_frame,
            text="전체 진행률",
            font=(font_family, 14, 'bold'),
            bg='#f2f1ef',
            fg='#131313'
        )
        self.overall_label.pack(pady=(10, 5))
        
        self.overall_progress = ttk.Progressbar(
            self.progress_frame,
            length=500,
            mode='determinate',
            style='green.Horizontal.TProgressbar'
        )
        self.overall_progress.pack(pady=5)
        
        self.overall_percent = tk.Label(
            self.progress_frame,
            text="0%",
            font=(font_family, 20, 'bold'),
            bg='#f2f1ef',
            fg='#ff3d00'
        )
        self.overall_percent.pack(pady=5)
        
        # Current file progress
        self.current_label = tk.Label(
            self.progress_frame,
            text="현재 파일",
            font=(font_family, 12),
            bg='#f2f1ef',
            fg='#131313'
        )
        self.current_label.pack(pady=(20, 5))
        
        self.current_progress = ttk.Progressbar(
            self.progress_frame,
            length=500,
            mode='determinate',
            style='green.Horizontal.TProgressbar'
        )
        self.current_progress.pack(pady=5)
        
        self.file_label = tk.Label(
            self.progress_frame,
            text="",
            font=(font_family, 10),
            bg='#f2f1ef',
            fg='#131313'
        )
        self.file_label.pack(pady=5)
        
        # Time estimation
        self.time_frame = tk.Frame(self.progress_frame, bg='#f2f1ef')
        self.time_frame.pack(pady=10)
        
        self.elapsed_label = tk.Label(
            self.time_frame,
            text="경과 시간: 00:00",
            font=(font_family, 10),
            bg='#f2f1ef',
            fg='#131313'
        )
        self.elapsed_label.pack(side=tk.LEFT, padx=10)
        
        self.remaining_label = tk.Label(
            self.time_frame,
            text="예상 남은 시간: 계산 중...",
            font=(font_family, 10),
            bg='#f2f1ef',
            fg='#131313'
        )
        self.remaining_label.pack(side=tk.LEFT, padx=10)
        
        # Status text
        self.status_label = tk.Label(
            self.progress_frame,
            text="",
            font=(font_family, 11),
            bg='#f2f1ef',
            fg='#131313'
        )
        self.status_label.pack(pady=10)
        
        # Donation banner (bottom)
        banner_frame = tk.Frame(self.root, bg='#f2f1ef')
        banner_frame.pack(padx=24, pady=(0, 8), fill=tk.X)
        tk.Label(
            banner_frame,
            text='도움이 되셨나요? 카카오페이로 후원해 주세요!',
            font=(font_family, 10),
            bg='#f2f1ef',
            fg='#131313'
        ).pack(side=tk.LEFT)
        tk.Button(
            banner_frame,
            text='카카오페이 후원하기',
            font=(font_family, 10, 'bold'),
            bg='#ff3d00',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=lambda: webbrowser.open('https://qr.kakaopay.com')
        ).pack(side=tk.LEFT, padx=8)

        # Button frame
        button_frame = tk.Frame(self.root, bg='#f2f1ef')
        button_frame.pack(pady=20)
        
        self.convert_button = tk.Button(
            button_frame,
            text="변환 시작",
            font=(font_family, 14, 'bold'),
            bg='#ff3d00',
            fg='white',
            padx=30,
            pady=10,
            relief=tk.FLAT,
            cursor='hand2',
            command=self.start_conversion,
            state=tk.DISABLED
        )
        self.convert_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = tk.Button(
            button_frame,
            text="초기화",
            font=(font_family, 14),
            bg='#666666',
            fg='white',
            padx=20,
            pady=10,
            relief=tk.FLAT,
            cursor='hand2',
            command=self.clear_files,
            state=tk.DISABLED
        )
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # Configure progress bar styles
        style = ttk.Style()
        style.theme_use('default')
        style.configure('green.Horizontal.TProgressbar', 
                       troughcolor='#e0e0e0',
                       background='#ff3d00',
                       borderwidth=0,
                       lightcolor='#ff3d00',
                       darkcolor='#ff3d00')
        
    def select_files(self):
        files = filedialog.askopenfilenames(
            title="MP4 파일 선택",
            filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")]
        )
        if files:
            self.add_files(files)
    
    def add_files(self, files):
        self.files_to_convert = list(files)
        count = len(self.files_to_convert)
        
        if count > 0:
            self.drop_label.config(
                text=f"✅\n\n{count}개 파일 선택됨\n\n변환 시작 버튼을 누르세요",
                fg='#34C759'
            )
            self.convert_button.config(state=tk.NORMAL)
            self.clear_button.config(state=tk.NORMAL)
            self.drop_frame.configure(highlightbackground='#34C759')
    
    def clear_files(self):
        self.is_converting = False
        self.files_to_convert = []
        self.drop_label.config(
            text="🎵\n\nMP4 파일을 선택하세요\n클릭하여 파일 선택",
            fg='#666666'
        )
        self.convert_button.config(state=tk.DISABLED)
        self.clear_button.config(state=tk.DISABLED)
        self.drop_frame.configure(highlightbackground='#e0e0e0')
        self.progress_frame.pack_forget()
        self.drop_frame.pack(padx=40, pady=20, fill=tk.BOTH, expand=True)
    
    def start_conversion(self):
        if not self.files_to_convert:
            return
        
        # Check if ffmpeg exists
        self.ffmpeg_path = self.check_ffmpeg()
        if not self.ffmpeg_path:
            messagebox.showerror(
                "오류",
                "MP3 변환에 필요한 구성 요소를 찾을 수 없습니다.\n\n앱을 다시 다운로드하거나 개발자에게 문의하세요."
            )
            return

        # Model and STT feasibility (if enabled)
        self.selected_model = getattr(self, 'model_var', tk.StringVar(value='small')).get()
        if getattr(self, 'enable_stt', tk.BooleanVar(value=False)).get():
            sys_info = get_system_info()
            # mac: check only RAM heuristics
            reqs = {
                'tiny': 1, 'base': 2, 'small': 4, 'medium': 8, 'large-v3': 16
            }
            need = reqs.get(self.selected_model, 4)
            ram = sys_info.get('ram_gb') or 0
            if ram < need:
                proceed = messagebox.askyesno(
                    "사양 경고",
                    f"선택한 모델({self.selected_model})은 현재 사양에서 메모리 부족이 예상됩니다.\n그래도 진행하시겠습니까?"
                )
                if not proceed:
                    return
        
        # Hide drop zone and show progress
        self.drop_frame.pack_forget()
        self.progress_frame.pack(padx=40, pady=20, fill=tk.BOTH, expand=True)
        
        # Disable buttons
        self.convert_button.config(state=tk.DISABLED)
        self.clear_button.config(state=tk.DISABLED)
        
        # Initialize progress
        self.current_file_index = 0
        self.overall_progress['maximum'] = 100
        self.overall_progress['value'] = 0
        self.start_time = time.time()
        self.is_converting = True
        self.eta_seconds = None

        # Pre-scan durations for accurate overall progress and ETA
        try:
            self.file_durations = self.pre_scan_durations(self.files_to_convert)
        except Exception:
            # Fallback to None durations
            self.file_durations = [None for _ in self.files_to_convert]
        self.total_duration_seconds = (
            sum(d for d in self.file_durations if d is not None)
            if any(d is not None for d in self.file_durations) else None
        )
        self.completed_seconds_accum = 0.0
        
        # Reset current progress bar
        self.current_progress['maximum'] = 100
        self.current_progress['value'] = 0
        
        # Start conversion in thread
        thread = threading.Thread(target=self.convert_files)
        thread.daemon = True
        thread.start()
        
        # Start time update
        self.update_time()

        # Prefetch whisper model in background to trigger first-time download
        try:
            self.root.after(100, self._start_model_prefetch)
        except Exception:
            pass
    
    def check_ffmpeg(self):
        # Check for embedded ffmpeg first
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            app_dir = os.path.dirname(sys.executable)
        else:
            # Running as script
            app_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Check different locations based on OS
        if platform.system() == 'Windows':
            ffmpeg_name = 'ffmpeg.exe'
            possible_paths = [
                os.path.join(app_dir, ffmpeg_name),
                os.path.join(app_dir, 'bin', ffmpeg_name),
            ]
        else:
            ffmpeg_name = 'ffmpeg'
            possible_paths = [
                os.path.join(app_dir, ffmpeg_name),
                os.path.join(os.path.dirname(app_dir), 'MacOS', ffmpeg_name),
            ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Fall back to system ffmpeg
        try:
            if platform.system() == 'Windows':
                result = subprocess.run(['where', 'ffmpeg'], capture_output=True, text=True, shell=True)
            else:
                result = subprocess.run(['which', 'ffmpeg'], capture_output=True, text=True)
            
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
        except:
            pass
        
        return None
    
    def update_time(self):
        if not self.is_converting:
            return
            
        elapsed = time.time() - self.start_time
        elapsed_str = self.format_time(elapsed)
        self.elapsed_label.config(text=f"경과 시간: {elapsed_str}")
        
        # Calculate remaining time
        if self.eta_seconds is not None and self.eta_seconds >= 0:
            remaining_str = self.format_time(self.eta_seconds)
            self.remaining_label.config(text=f"예상 남은 시간: {remaining_str}")
        else:
            # Fallback simple estimate by average per completed files
            if self.current_file_index > 0:
                avg_time_per_file = elapsed / self.current_file_index
                remaining_files = len(self.files_to_convert) - self.current_file_index
                remaining_time = avg_time_per_file * remaining_files
                remaining_str = self.format_time(remaining_time)
                self.remaining_label.config(text=f"예상 남은 시간: {remaining_str}")
        
        # Schedule next update
        self.root.after(1000, self.update_time)
    
    def format_time(self, seconds):
        if seconds < 60:
            return f"{int(seconds)}초"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{minutes:02d}:{secs:02d}"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            secs = int(seconds % 60)
            return f"{hours}:{minutes:02d}:{secs:02d}"
    
    def convert_files(self):
        success_count = 0
        failed_files = []
        total_files = len(self.files_to_convert)
        
        for i, file_path in enumerate(self.files_to_convert):
            if not self.is_converting:
                break
                
            self.current_file_index = i
            input_path = Path(file_path)
            output_path = input_path.with_suffix('.mp3')
            
            # Update UI BEFORE conversion starts - show current file being processed
            self.root.after(0, self.update_progress_start, i, input_path.name, 0)
            self.root.update_idletasks()
            time.sleep(0.05)
            
            try:
                # Determine duration for this file
                duration_seconds = None
                if hasattr(self, 'file_durations') and i < len(self.file_durations):
                    duration_seconds = self.file_durations[i]
                if duration_seconds is None:
                    try:
                        duration_seconds = self.get_media_duration(str(input_path))
                        if hasattr(self, 'file_durations') and i < len(self.file_durations):
                            self.file_durations[i] = duration_seconds
                    except Exception:
                        duration_seconds = None

                # Run ffmpeg as a streaming process to parse progress
                cmd = [
                    self.ffmpeg_path,
                    '-y',
                    '-i', str(input_path),
                    '-vn',
                    '-acodec', 'libmp3lame',
                    '-ab', '192k',
                    str(output_path)
                ]

                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    bufsize=1
                )

                processed_seconds = 0.0

                # If duration is not known yet, try to capture from ffmpeg header lines
                duration_pattern = re.compile(r"Duration: (\d{2}):(\d{2}):(\d{2})\.(\d+)")
                time_pattern = re.compile(r"time=(\d{2}):(\d{2}):(\d{2})\.?([0-9]{0,2})")

                while True:
                    line = process.stderr.readline()
                    if not line:
                        if process.poll() is not None:
                            break
                        else:
                            continue

                    # Parse duration from header if unknown
                    if duration_seconds is None:
                        m = duration_pattern.search(line)
                        if m:
                            duration_seconds = (
                                int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3))
                            ) + float('0.' + (m.group(4) or '0'))
                            if hasattr(self, 'file_durations') and i < len(self.file_durations):
                                self.file_durations[i] = duration_seconds
                            if getattr(self, 'total_duration_seconds', None) is None:
                                self.total_duration_seconds = 0
                            self.total_duration_seconds += duration_seconds

                    # Parse current processed time
                    tm = time_pattern.search(line)
                    if tm:
                        processed_seconds = (
                            int(tm.group(1)) * 3600 + int(tm.group(2)) * 60 + int(tm.group(3))
                        ) + (int(tm.group(4)) / (10 ** len(tm.group(4))) if tm.group(4) else 0)

                        # Compute percents
                        if duration_seconds and duration_seconds > 0:
                            current_percent = max(0, min(99, int((processed_seconds / duration_seconds) * 100)))
                        else:
                            current_percent = 0

                        # Overall percent based on durations
                        if getattr(self, 'total_duration_seconds', None):
                            total_done = self.completed_seconds_accum + processed_seconds
                            overall_percent = max(0, min(99, int((total_done / self.total_duration_seconds) * 100)))
                            remaining_seconds = max(0, self.total_duration_seconds - total_done)
                            self.eta_seconds = remaining_seconds
                        else:
                            # Fallback by files count if total duration unknown
                            overall_percent = int((((i + (current_percent / 100.0)) / total_files) * 100)) if total_files > 0 else int(current_percent)
                            if duration_seconds:
                                self.eta_seconds = max(0, duration_seconds - processed_seconds)
                            else:
                                self.eta_seconds = None

                        # Schedule UI update
                        self.root.after(0, self.update_progress_dynamic, i, input_path.name, current_percent, overall_percent)

                process.wait()

                if process.returncode == 0:
                    success_count += 1
                    # Update accumulators
                    if duration_seconds:
                        self.completed_seconds_accum += duration_seconds
                    self.current_file_index = i + 1
                    # Finalize progress to 100 for current step
                    if getattr(self, 'total_duration_seconds', None):
                        total_done = self.completed_seconds_accum
                        overall_percent = int(min(100, (total_done / self.total_duration_seconds) * 100))
                    else:
                        overall_percent = int(((i + 1) / total_files) * 100) if total_files > 0 else 100
                    self.root.after(0, self.update_progress_dynamic, i, input_path.name, 100, overall_percent)
                    self.root.after(0, self.update_progress_complete, i + 1, overall_percent)
                    self.root.update_idletasks()
                    time.sleep(0.05)

                    # STT: Whisper 전사 (옵션)
                    if getattr(self, 'enable_stt', tk.BooleanVar(value=False)).get():
                        try:
                            self.status_label.config(text=f"STT 전사 중: {input_path.name}")
                            self.root.update_idletasks()
                            model, device = load_whisper_model(self.selected_model or 'small')
                            result_txt = model.transcribe(str(output_path))
                            text = result_txt.get('text', '').strip()
                            if text:
                                with open(str(input_path.with_suffix('.txt')), 'w', encoding='utf-8') as f:
                                    f.write(text)
                        except Exception as stt_err:
                            self.status_label.config(text=f"STT 실패: {stt_err}")
                            self.root.update_idletasks()
                else:
                    failed_files.append(input_path.name)
                    
            except Exception as e:
                failed_files.append(input_path.name)
        
        # Final update
        self.root.after(0, self.update_progress_complete, total_files, 100)
        
        # Show completion message
        self.root.after(0, self.show_completion, success_count, failed_files)
    
    def update_progress_start(self, index, filename, percent):
        """파일 변환 시작 시 진행률 업데이트"""
        # Only set labels here; percentages are handled dynamically
        # Keep overall percent text as-is until we have progress
        self.overall_percent.config(text=f"{self.overall_progress['value']}%")
        self.file_label.config(text=f"변환 중: {filename}")
        self.current_label.config(text=f"현재 파일 ({index + 1}/{len(self.files_to_convert)})")
        self.status_label.config(text=f"📁 {index}개 완료, {len(self.files_to_convert) - index}개 남음")
        self.root.update_idletasks()
    
    def update_progress_dynamic(self, index, filename, current_percent, overall_percent):
        """실시간 변환 진행률 갱신"""
        # Current file progress
        self.current_progress['value'] = current_percent
        # Overall progress
        self.overall_progress['value'] = overall_percent
        self.overall_percent.config(text=f"{int(overall_percent)}%")
        # Labels
        self.file_label.config(text=f"변환 중: {filename}")
        self.current_label.config(text=f"현재 파일 ({index + 1}/{len(self.files_to_convert)})")
        self.root.update_idletasks()

    def update_progress_complete(self, completed_count, percent):
        """파일 변환 완료 시 진행률 업데이트"""
        self.overall_progress['value'] = percent
        self.overall_percent.config(text=f"{percent}%")
        
        if completed_count < len(self.files_to_convert):
            self.current_label.config(text=f"진행 상황 ({completed_count}/{len(self.files_to_convert)})")
            self.status_label.config(text=f"📁 {completed_count}개 완료, {len(self.files_to_convert) - completed_count}개 남음")
        else:
            self.file_label.config(text="모든 변환 완료!")
            self.status_label.config(text="✅ 변환 작업이 완료되었습니다")
        self.root.update_idletasks()

    def parse_time_to_seconds(self, time_str):
        """HH:MM:SS(.ms) -> seconds(float)"""
        try:
            parts = time_str.split(":")
            h = int(parts[0])
            m = int(parts[1])
            s = float(parts[2])
            return h * 3600 + m * 60 + s
        except Exception:
            return None

    def get_media_duration(self, input_path):
        """Try to get media duration in seconds using ffprobe or ffmpeg -i metadata."""
        # Try ffprobe if available in same directory as ffmpeg
        ffprobe_path = None
        if self.ffmpeg_path:
            base_dir = os.path.dirname(self.ffmpeg_path)
            candidate = os.path.join(base_dir, 'ffprobe' + ('.exe' if platform.system() == 'Windows' else ''))
            if os.path.exists(candidate):
                ffprobe_path = candidate
        try:
            if ffprobe_path:
                result = subprocess.run(
                    [ffprobe_path, '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', input_path],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0 and result.stdout.strip():
                    return float(result.stdout.strip())
        except Exception:
            pass

        # Fallback to ffmpeg -i to parse Duration line
        try:
            result = subprocess.run(
                [self.ffmpeg_path, '-i', input_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            m = re.search(r"Duration: (\d{2}):(\d{2}):(\d{2})\.(\d+)", result.stderr)
            if m:
                return (
                    int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3))
                ) + float('0.' + (m.group(4) or '0'))
        except Exception:
            pass
        return None

    def pre_scan_durations(self, files):
        durations = []
        for p in files:
            try:
                d = self.get_media_duration(p)
            except Exception:
                d = None
            durations.append(d)
        # If at least one duration known, compute total
        if any(d is not None for d in durations):
            self.total_duration_seconds = sum(d for d in durations if d is not None)
        else:
            self.total_duration_seconds = None
        return durations
    
    def show_completion(self, success_count, failed_files):
        self.is_converting = False
        total = len(self.files_to_convert)
        
        if success_count == total:
            # 작은 팝업과 '폴더 열기' 버튼 제공
            popup = tk.Toplevel(self.root)
            popup.title('완료')
            popup.configure(bg='#f2f1ef')
            msg = tk.Label(popup, text=f"✅ {success_count}개 파일 변환 완료!\n\nMP3 파일이 원본 파일과 같은 위치에 저장되었습니다.", bg='#f2f1ef', fg='#131313')
            msg.pack(padx=20, pady=12)
            folder = None
            if self.files_to_convert:
                folder = str(Path(self.files_to_convert[-1]).parent)
            def _open_and_close():
                if folder and os.path.isdir(folder):
                    try:
                        subprocess.run(['open', folder])
                    except Exception:
                        pass
                popup.destroy()
            tk.Button(popup, text='폴더 열기', bg='#ff3d00', fg='white', relief=tk.FLAT, command=_open_and_close).pack(pady=(0, 12))
        else:
            message = f"변환 완료: {success_count}/{total}\n"
            if failed_files:
                message += f"\n실패한 파일:\n" + "\n".join(failed_files[:5])
                if len(failed_files) > 5:
                    message += f"\n... 외 {len(failed_files) - 5}개"
            messagebox.showwarning("부분 완료", message)
        
        self.clear_files()

    def _start_model_prefetch(self):
        """Background prefetch to download whisper model on first run."""
        try:
            target = self.model_var.get() or getattr(self, 'model_recommended', 'small')
        except Exception:
            target = 'small'
        def _worker():
            try:
                load_whisper_model(target)
            except Exception:
                pass
        t = threading.Thread(target=_worker, daemon=True)
        t.start()

def main():
    root = tk.Tk()
    
    # Set window icon if available
    try:
        if platform.system() == 'Windows':
            root.iconbitmap('icon.ico')
    except:
        pass
    
    app = MP4toMP3Converter(root)
    
    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main()