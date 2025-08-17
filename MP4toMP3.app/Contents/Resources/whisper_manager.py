#!/usr/bin/env python3
"""
Whisper 모델 관리자 - 선택적 다운로드 방식
"""

import os
import sys
import json
import hashlib
import urllib.request
import time
from pathlib import Path
import subprocess

class WhisperManager:
    """경량 Whisper 관리 시스템"""
    
    # 모델 크기 정보 (실제 다운로드 크기)
    MODEL_SIZES = {
        'tiny': {'size': 39, 'accuracy': '기본', 'speed': '최고속'},
        'base': {'size': 74, 'accuracy': '양호', 'speed': '빠름'},
        'small': {'size': 244, 'accuracy': '좋음', 'speed': '보통'},
        'medium': {'size': 769, 'accuracy': '우수', 'speed': '느림'},
        'large': {'size': 1550, 'accuracy': '최고', 'speed': '매우 느림'}
    }
    
    def __init__(self):
        # 앱 데이터 폴더에 모델 저장
        self.app_dir = Path.home() / '.mp4tomp3'
        self.models_dir = self.app_dir / 'models'
        self.models_dir.mkdir(parents=True, exist_ok=True)
        # 전용 가상환경(venv)
        self.venv_dir = self.app_dir / 'venv'
        self.venv_python = self._resolve_venv_python()
        
        self.config_file = self.app_dir / 'config.json'
        self.last_error = ""
        self.load_config()
    
    def load_config(self):
        """설정 파일 로드"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                'installed_models': [],
                'default_model': None,
                'whisper_installed': False
            }
    
    def save_config(self):
        """설정 저장"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def _resolve_venv_python(self) -> Path:
        """가상환경 파이썬 경로 계산"""
        if sys.platform.startswith('win'):
            return self.venv_dir / 'Scripts' / 'python.exe'
        else:
            # python3 또는 python
            p3 = self.venv_dir / 'bin' / 'python3'
            p = self.venv_dir / 'bin' / 'python'
            return p3 if p3.exists() else p

    def ensure_venv(self, progress_callback=None) -> bool:
        """전용 venv 생성 및 기본 업그레이드"""
        try:
            if not self.venv_dir.exists() or not self.venv_python.exists():
                if progress_callback:
                    progress_callback(3, '전용 환경 생성 중...')
                result = subprocess.run([sys.executable, '-m', 'venv', str(self.venv_dir)], capture_output=True, text=True)
                if result.returncode != 0:
                    self.last_error = result.stderr or result.stdout or ''
                    if progress_callback:
                        progress_callback(0, f'venv 생성 실패: {self.last_error[:200]}')
                    return False
            # pip 업그레이드
            if progress_callback:
                progress_callback(6, 'pip 업그레이드 중...')
            up = subprocess.run([str(self.venv_python), '-m', 'pip', 'install', '-U', 'pip', 'setuptools', 'wheel'], capture_output=True, text=True)
            if up.returncode != 0:
                # 치명적이지 않음 - 계속 진행
                self.last_error = up.stderr or up.stdout or ''
            return True
        except Exception as e:
            self.last_error = str(e)
            return False
    
    def is_whisper_installed(self):
        """Whisper 라이브러리 설치 확인 (전용 venv 기준)"""
        if not self.venv_python.exists():
            return False
        result = subprocess.run([str(self.venv_python), '-c', 'import whisper,sys;print("ok")'], capture_output=True, text=True)
        return result.returncode == 0 and 'ok' in (result.stdout or '')
    
    def install_whisper_minimal(self, progress_callback=None):
        """Whisper + Torch(CPU) 사용자 영역에 설치. 권한 문제 최소화/안정성 향상."""
        try:
            # 전용 venv 보장
            if not self.ensure_venv(progress_callback):
                return False
            env = os.environ.copy()
            env.setdefault('PIP_DISABLE_PIP_VERSION_CHECK', '1')
            # 1) Whisper 설치 (전용 venv)
            if progress_callback:
                progress_callback(5, "Whisper 설치 준비...")
            cmd_whisper = [str(self.venv_python), '-m', 'pip', 'install', '-U', 'openai-whisper']
            result = subprocess.run(cmd_whisper, capture_output=True, text=True, timeout=900, env=env)
            if result.returncode != 0:
                # Fallback: GitHub 소스에서 설치
                if progress_callback:
                    progress_callback(10, "Whisper 소스 설치 시도...")
                fallback = [str(self.venv_python), '-m', 'pip', 'install', 'git+https://github.com/openai/whisper.git']
                result_fb = subprocess.run(fallback, capture_output=True, text=True, timeout=900, env=env)
                if result_fb.returncode != 0:
                    err = (result_fb.stderr or result_fb.stdout or result.stderr or '')
                    self.last_error = err
                    if progress_callback:
                        progress_callback(0, f"Whisper 설치 실패: {err[:200]}")
                    return False
            if progress_callback:
                progress_callback(40, "PyTorch(CPU) 설치 중...")
            # 2) Torch CPU 설치 (torchaudio는 플랫폼에 따라 선택)
            cmd_torch = [str(self.venv_python), '-m', 'pip', 'install', 'torch', '--index-url', 'https://download.pytorch.org/whl/cpu']
            result_t = subprocess.run(cmd_torch, capture_output=True, text=True, timeout=900, env=env)
            if result_t.returncode != 0:
                err = (result_t.stderr or result_t.stdout or '')
                self.last_error = err
                if progress_callback:
                    progress_callback(0, f"Torch 설치 실패: {err[:200]}")
                return False
            # torchaudio는 선택 설치 (실패해도 계속)
            if progress_callback:
                progress_callback(70, "선택 패키지 설치...")
            ta = subprocess.run([str(self.venv_python), '-m', 'pip', 'install', 'torchaudio', '--index-url', 'https://download.pytorch.org/whl/cpu'], capture_output=True, text=True, timeout=600, env=env)
            if ta.returncode != 0:
                # 비치명적 오류 기록만
                self.last_error = (ta.stderr or ta.stdout or '')
            if progress_callback:
                progress_callback(90, "마무리 중...")
            self.config['whisper_installed'] = True
            self.save_config()
            self.last_error = ""
            if progress_callback:
                progress_callback(100, "설치 완료!")
            return True
        except Exception as e:
            self.last_error = str(e)
            if progress_callback:
                progress_callback(0, f"설치 실패: {e}")
            return False
    
    def download_model(self, model_name='tiny', progress_callback=None):
        """개별 모델 다운로드"""
        model_info = self.MODEL_SIZES.get(model_name)
        if not model_info:
            return False
        
        model_file = self.models_dir / f"{model_name}.pt"
        
        # 이미 다운로드됨
        if model_file.exists():
            if progress_callback:
                progress_callback(100, f"{model_name.upper()} 모델이 이미 설치되어 있습니다")
            return True
        
        try:
            if progress_callback:
                progress_callback(0, f"{model_name.upper()} 모델 다운로드 중... ({model_info['size']}MB)")

            # 1차: Azure CDN, 2차: Hugging Face
            model_hash = self._get_model_hash(model_name)
            primary = f"https://openaipublic.azureedge.net/main/whisper/models/{model_hash}/{model_name}.pt" if model_hash else None
            mirror = f"https://huggingface.co/openai/whisper-{model_name}/resolve/main/{model_name}.pt"
            urls = [u for u in [primary, mirror] if u]

            def _download_with_retries(url_list, dest):
                last_err = None
                for url in url_list:
                    for attempt in range(4):
                        try:
                            req = urllib.request.Request(url)
                            opener = urllib.request.build_opener()  # proxies from env respected
                            with opener.open(req, timeout=30) as resp:
                                total = int(resp.getheader('Content-Length') or 0)
                                downloaded = 0
                                with open(dest, 'wb') as f:
                                    while True:
                                        chunk = resp.read(8192)
                                        if not chunk:
                                            break
                                        f.write(chunk)
                                        downloaded += len(chunk)
                                        if progress_callback and total:
                                            percent = min(int(downloaded * 100 / total), 100)
                                            progress_callback(percent, f"다운로드 중... {downloaded/(1024*1024):.1f}/{total/(1024*1024):.1f} MB ({percent}%)")
                            return True
                        except Exception as e:
                            last_err = str(e)
                            time.sleep(min(2 ** attempt, 10))
                    # 다음 URL 시도
                if last_err:
                    self.last_error = last_err
                return False

            ok = _download_with_retries(urls, model_file)
            if not ok:
                if progress_callback:
                    progress_callback(0, f"모델 다운로드 실패: {self.last_error[:200]}")
                return False

            # 설정 업데이트
            if model_name not in self.config['installed_models']:
                self.config['installed_models'].append(model_name)
            
            if not self.config['default_model']:
                self.config['default_model'] = model_name
            
            self.save_config()
            
            if progress_callback:
                progress_callback(100, "다운로드 완료!")
            self.last_error = ""
            
            return True
            
        except Exception as e:
            print(f"모델 다운로드 실패: {e}")
            self.last_error = str(e)
            if model_file.exists():
                model_file.unlink()
            return False
    
    def _get_model_hash(self, model_name):
        """모델별 해시 값 반환"""
        hashes = {
            'tiny': '65147644a518d12f04e32d6f3b26facc3f8dd46e5390956a9424a650c0ce22b9',
            'base': 'ed3a0b6b1c0edf879ad9b11b1af5a0e6ab5db9205f891f668f8b0e6c6326e34e',
            'small': '9ecf779972d90ba49c06d968637d720dd632c55bbf19d441fb42bf17a411e794',
            'medium': '345ae4da62f9b3d59415adc60127b97c714f32e89e936602e85993674d08dcb1',
            'large': 'e5b1a55542b56bf9f0060627744b95e15d47bdc604f2dc34a4afcae68649bb48'
        }
        return hashes.get(model_name, '')
    
    def get_available_models(self):
        """설치된 모델 목록"""
        return self.config['installed_models']
    
    def load_model(self, model_name='tiny'):
        """모델 로드"""
        import whisper
        
        model_file = self.models_dir / f"{model_name}.pt"
        if model_file.exists():
            # 로컬 모델 사용
            return whisper.load_model(str(model_file))
        else:
            # 자동 다운로드 (Whisper 기본)
            return whisper.load_model(model_name)

    def transcribe_cli(self, audio_path: str, model_name: str = 'small', language: str = 'ko', output_dir: str = None) -> str:
        """전용 venv의 whisper CLI로 전사 수행. txt 내용을 반환."""
        try:
            if not self.ensure_venv():
                return ''
            if not self.is_whisper_installed():
                ok = self.install_whisper_minimal()
                if not ok:
                    return ''
            if output_dir is None:
                output_dir = str(Path(audio_path).parent)
            cmd = [
                str(self.venv_python), '-m', 'whisper', audio_path,
                '--model', model_name,
                '--language', language,
                '--device', 'cpu',
                '--fp16', 'False',
                '--task', 'transcribe',
                '--output_format', 'txt',
                '--output_dir', output_dir
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            # Find txt file
            base = Path(audio_path).with_suffix('').name
            txt_path = Path(output_dir) / f"{base}.txt"
            if txt_path.exists():
                return txt_path.read_text(encoding='utf-8').strip()
            # If not found, parse stdout
            return (result.stdout or '').strip()
        except Exception as e:
            self.last_error = str(e)
            return ''

    def get_last_error(self) -> str:
        return self.last_error or ""
    
    def estimate_space_needed(self, model_name='tiny'):
        """필요한 디스크 공간 계산"""
        model_info = self.MODEL_SIZES.get(model_name, {})
        size_mb = model_info.get('size', 0)
        
        # Whisper 라이브러리 + PyTorch CPU + 모델
        if not self.config['whisper_installed']:
            size_mb += 500  # PyTorch CPU 버전
        
        return size_mb
    
    def clean_unused_models(self):
        """사용하지 않는 모델 삭제"""
        for model_file in self.models_dir.glob("*.pt"):
            model_name = model_file.stem
            if model_name not in self.config['installed_models']:
                model_file.unlink()
                print(f"삭제됨: {model_name}")


# 사용 예제
if __name__ == "__main__":
    manager = WhisperManager()
    
    # 1. 최소 설치 (약 500MB)
    if not manager.is_whisper_installed():
        print("Whisper 설치 중...")
        manager.install_whisper_minimal()
    
    # 2. Tiny 모델만 다운로드 (39MB)
    print("Tiny 모델 다운로드 중...")
    manager.download_model('tiny')
    
    # 3. 사용
    model = manager.load_model('tiny')
    print("모델 로드 완료!")