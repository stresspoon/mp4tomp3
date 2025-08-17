#!/usr/bin/env python3
"""
Whisper 모델 관리자 - 선택적 다운로드 방식
"""

import os
import sys
import json
import hashlib
import urllib.request
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
        
        self.config_file = self.app_dir / 'config.json'
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
    
    def is_whisper_installed(self):
        """Whisper 라이브러리 설치 확인"""
        try:
            import whisper
            return True
        except ImportError:
            return False
    
    def install_whisper_minimal(self, progress_callback=None):
        """최소 Whisper 설치 (torch 제외 옵션)"""
        try:
            if progress_callback:
                progress_callback(10, "Whisper 코어 설치 중...")
            
            # CPU 전용 가벼운 설치
            cmd = [
                sys.executable, "-m", "pip", "install",
                "--no-deps",  # 의존성 최소화
                "openai-whisper"
            ]
            subprocess.check_call(cmd, timeout=300)
            
            if progress_callback:
                progress_callback(50, "필수 패키지 설치 중...")
            
            # 필수 의존성만 설치
            essential = ["numpy", "tqdm", "more-itertools", "tiktoken"]
            for pkg in essential:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", pkg],
                    timeout=60
                )
            
            if progress_callback:
                progress_callback(90, "PyTorch CPU 버전 설치 중...")
            
            # CPU 전용 PyTorch (더 작은 크기)
            subprocess.check_call([
                sys.executable, "-m", "pip", "install",
                "torch", "torchaudio",
                "--index-url", "https://download.pytorch.org/whl/cpu"
            ], timeout=300)
            
            self.config['whisper_installed'] = True
            self.save_config()
            
            if progress_callback:
                progress_callback(100, "설치 완료!")
            
            return True
            
        except Exception as e:
            print(f"설치 실패: {e}")
            return False
    
    def download_model(self, model_name='tiny', progress_callback=None):
        """개별 모델 다운로드"""
        model_info = self.MODEL_SIZES.get(model_name)
        if not model_info:
            return False
        
        model_file = self.models_dir / f"{model_name}.pt"
        
        # 이미 다운로드됨
        if model_file.exists():
            return True
        
        try:
            if progress_callback:
                progress_callback(0, f"{model_name} 모델 다운로드 중... ({model_info['size']}MB)")
            
            # Whisper 모델 URL
            url = f"https://openaipublic.azureedge.net/main/whisper/models/{model_name}.pt"
            
            # 다운로드 with progress
            def download_hook(block_num, block_size, total_size):
                downloaded = block_num * block_size
                percent = min(int(downloaded * 100 / total_size), 100)
                if progress_callback:
                    progress_callback(percent, f"다운로드 중... {percent}%")
            
            urllib.request.urlretrieve(url, model_file, reporthook=download_hook)
            
            # 설정 업데이트
            if model_name not in self.config['installed_models']:
                self.config['installed_models'].append(model_name)
            
            if not self.config['default_model']:
                self.config['default_model'] = model_name
            
            self.save_config()
            
            if progress_callback:
                progress_callback(100, "다운로드 완료!")
            
            return True
            
        except Exception as e:
            print(f"모델 다운로드 실패: {e}")
            if model_file.exists():
                model_file.unlink()
            return False
    
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