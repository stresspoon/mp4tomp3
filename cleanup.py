#!/usr/bin/env python3
"""
프로젝트 정리 스크립트
불필요한 파일 제거 및 구조 최적화
"""

import os
import shutil
from pathlib import Path

def cleanup_project():
    """프로젝트 정리"""
    project_dir = Path(__file__).parent
    
    # 삭제할 파일들
    files_to_delete = [
        # 테스트 및 임시 파일
        "test_converter.py",
        "bundle_builder.py",
        "create_bundle_with_whisper.py",
        "test_rounded_button.py",
        "check_deps.py",
        
        # 이전 버전 파일들
        "converter_original.py",
        "converter_original_backup.py",
        "converter_stable.py",
        "converter_before_cleanup.py",
        
        # 불필요한 번들 파일
        "MP4toMP3.app/Contents/Resources/converter_bundled.py",
        "MP4toMP3.app/Contents/Resources/whisper_bundle",
        "MP4toMP3.app/Contents/MacOS/mp4tomp3_bundled",
        
        # 빌드 잔여물
        "macos.spec",
        "windows.spec",
        "mp4tomp3.spec",
    ]
    
    # 삭제할 디렉토리들
    dirs_to_delete = [
        "build",
        "dist",
        "__pycache__",
        ".pytest_cache",
        "MP4toMP3.app/Contents/Resources/whisper_bundle",
    ]
    
    print("🧹 프로젝트 정리 시작...")
    
    # 파일 삭제
    for file_path in files_to_delete:
        full_path = project_dir / file_path
        if full_path.exists():
            full_path.unlink()
            print(f"  ✓ 삭제: {file_path}")
    
    # 디렉토리 삭제
    for dir_path in dirs_to_delete:
        full_path = project_dir / dir_path
        if full_path.exists():
            shutil.rmtree(full_path)
            print(f"  ✓ 삭제: {dir_path}/")
    
    # __pycache__ 재귀적 삭제
    for pycache in project_dir.rglob("__pycache__"):
        shutil.rmtree(pycache)
        print(f"  ✓ 삭제: {pycache}")
    
    # .pyc 파일 삭제
    for pyc in project_dir.rglob("*.pyc"):
        pyc.unlink()
    
    print("\n✅ 정리 완료!")

if __name__ == "__main__":
    cleanup_project()