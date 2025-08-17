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

class MP4toMP3Converter:
    def __init__(self, root):
        self.root = root
        self.root.title("MP4 to MP3 Converter")
        self.root.geometry("650x500")
        self.root.configure(bg='#f0f0f0')
        
        # Make window stay on top initially
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after(100, lambda: self.root.attributes('-topmost', False))
        
        self.files_to_convert = []
        self.current_file_index = 0
        self.start_time = None
        self.is_converting = False
        
        self.setup_ui()
        
    def setup_ui(self):
        # Title
        title_frame = tk.Frame(self.root, bg='#f0f0f0')
        title_frame.pack(pady=20)
        
        # Use different font based on OS
        if platform.system() == 'Darwin':
            font_family = 'SF Pro Display'
        elif platform.system() == 'Windows':
            font_family = 'Segoe UI'
        else:
            font_family = 'Arial'
            
        title_label = tk.Label(
            title_frame,
            text="MP4 → MP3 변환기",
            font=(font_family, 24, 'bold'),
            bg='#f0f0f0'
        )
        title_label.pack()
        
        # Drop zone
        self.drop_frame = tk.Frame(
            self.root,
            bg='white',
            relief=tk.FLAT,
            bd=2,
            highlightbackground='#e0e0e0',
            highlightthickness=2
        )
        self.drop_frame.pack(padx=40, pady=20, fill=tk.BOTH, expand=True)
        
        self.drop_label = tk.Label(
            self.drop_frame,
            text="🎵\n\nMP4 파일을 선택하세요\n클릭하여 파일 선택",
            font=(font_family, 14),
            bg='white',
            fg='#666666'
        )
        self.drop_label.pack(expand=True)
        
        # Make drop zone clickable
        self.drop_frame.bind("<Button-1>", lambda e: self.select_files())
        self.drop_label.bind("<Button-1>", lambda e: self.select_files())
        
        # Progress frame (hidden initially)
        self.progress_frame = tk.Frame(self.root, bg='#f0f0f0')
        
        # Overall progress
        self.overall_label = tk.Label(
            self.progress_frame,
            text="전체 진행률",
            font=(font_family, 14, 'bold'),
            bg='#f0f0f0'
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
            bg='#f0f0f0',
            fg='#007AFF'
        )
        self.overall_percent.pack(pady=5)
        
        # Current file progress
        self.current_label = tk.Label(
            self.progress_frame,
            text="현재 파일",
            font=(font_family, 12),
            bg='#f0f0f0'
        )
        self.current_label.pack(pady=(20, 5))
        
        self.current_progress = ttk.Progressbar(
            self.progress_frame,
            length=500,
            mode='indeterminate'
        )
        self.current_progress.pack(pady=5)
        
        self.file_label = tk.Label(
            self.progress_frame,
            text="",
            font=(font_family, 10),
            bg='#f0f0f0',
            fg='#666666'
        )
        self.file_label.pack(pady=5)
        
        # Time estimation
        self.time_frame = tk.Frame(self.progress_frame, bg='#f0f0f0')
        self.time_frame.pack(pady=10)
        
        self.elapsed_label = tk.Label(
            self.time_frame,
            text="경과 시간: 00:00",
            font=(font_family, 10),
            bg='#f0f0f0',
            fg='#666666'
        )
        self.elapsed_label.pack(side=tk.LEFT, padx=10)
        
        self.remaining_label = tk.Label(
            self.time_frame,
            text="예상 남은 시간: 계산 중...",
            font=(font_family, 10),
            bg='#f0f0f0',
            fg='#666666'
        )
        self.remaining_label.pack(side=tk.LEFT, padx=10)
        
        # Status text
        self.status_label = tk.Label(
            self.progress_frame,
            text="",
            font=(font_family, 11),
            bg='#f0f0f0',
            fg='#34C759'
        )
        self.status_label.pack(pady=10)
        
        # Button frame
        button_frame = tk.Frame(self.root, bg='#f0f0f0')
        button_frame.pack(pady=20)
        
        self.convert_button = tk.Button(
            button_frame,
            text="변환 시작",
            font=(font_family, 14, 'bold'),
            bg='#007AFF',
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
                       background='#34C759',
                       borderwidth=0,
                       lightcolor='#34C759',
                       darkcolor='#34C759')
        
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
        
        # Hide drop zone and show progress
        self.drop_frame.pack_forget()
        self.progress_frame.pack(padx=40, pady=20, fill=tk.BOTH, expand=True)
        
        # Disable buttons
        self.convert_button.config(state=tk.DISABLED)
        self.clear_button.config(state=tk.DISABLED)
        
        # Initialize progress
        self.current_file_index = 0
        self.overall_progress['maximum'] = len(self.files_to_convert)
        self.overall_progress['value'] = 0
        self.start_time = time.time()
        self.is_converting = True
        
        # Start progress animation
        self.current_progress.start(10)
        
        # Start conversion in thread
        thread = threading.Thread(target=self.convert_files)
        thread.daemon = True
        thread.start()
        
        # Start time update
        self.update_time()
    
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
            current_percent = int((i / total_files) * 100) if total_files > 0 else 0
            self.root.after(0, self.update_progress_start, i, input_path.name, current_percent)
            
            # Force UI update
            self.root.update_idletasks()
            time.sleep(0.1)
            
            try:
                # Run ffmpeg
                cmd = [
                    self.ffmpeg_path,
                    '-i', str(input_path),
                    '-vn',
                    '-acodec', 'libmp3lame',
                    '-ab', '192k',
                    '-y',
                    str(output_path)
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    success_count += 1
                    self.current_file_index = i + 1
                    # Update progress after successful conversion
                    completed_percent = int(((i + 1) / total_files) * 100) if total_files > 0 else 100
                    self.root.after(0, self.update_progress_complete, i + 1, completed_percent)
                    self.root.update_idletasks()
                    time.sleep(0.05)  # Small delay for UI update
                else:
                    failed_files.append(input_path.name)
                    
            except Exception as e:
                failed_files.append(input_path.name)
        
        # Final update
        self.root.after(0, self.update_progress_complete, total_files, 100)
        self.current_progress.stop()
        
        # Show completion message
        self.root.after(0, self.show_completion, success_count, failed_files)
    
    def update_progress_start(self, index, filename, percent):
        """파일 변환 시작 시 진행률 업데이트"""
        self.overall_progress['value'] = index
        self.overall_percent.config(text=f"{percent}%")
        self.file_label.config(text=f"변환 중: {filename}")
        self.current_label.config(text=f"현재 파일 ({index + 1}/{len(self.files_to_convert)})")
        self.status_label.config(text=f"📁 {index}개 완료, {len(self.files_to_convert) - index}개 남음")
        self.root.update_idletasks()
    
    def update_progress_complete(self, completed_count, percent):
        """파일 변환 완료 시 진행률 업데이트"""
        self.overall_progress['value'] = completed_count
        self.overall_percent.config(text=f"{percent}%")
        
        if completed_count < len(self.files_to_convert):
            self.current_label.config(text=f"진행 상황 ({completed_count}/{len(self.files_to_convert)})")
            self.status_label.config(text=f"📁 {completed_count}개 완료, {len(self.files_to_convert) - completed_count}개 남음")
        else:
            self.file_label.config(text="모든 변환 완료!")
            self.status_label.config(text="✅ 변환 작업이 완료되었습니다")
        self.root.update_idletasks()
    
    def show_completion(self, success_count, failed_files):
        self.is_converting = False
        total = len(self.files_to_convert)
        
        if success_count == total:
            messagebox.showinfo(
                "완료",
                f"✅ {success_count}개 파일 변환 완료!\n\nMP3 파일이 원본 파일과 같은 위치에 저장되었습니다."
            )
        else:
            message = f"변환 완료: {success_count}/{total}\n"
            if failed_files:
                message += f"\n실패한 파일:\n" + "\n".join(failed_files[:5])
                if len(failed_files) > 5:
                    message += f"\n... 외 {len(failed_files) - 5}개"
            messagebox.showwarning("부분 완료", message)
        
        self.clear_files()

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