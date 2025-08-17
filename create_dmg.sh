#!/bin/bash

echo "Creating DMG installer for MP4toMP3..."

# Create a temporary directory for DMG contents
mkdir -p dmg_temp
cp -R MP4toMP3.app dmg_temp/

# Create a symbolic link to Applications folder
ln -s /Applications dmg_temp/Applications

# Create README file
cat > dmg_temp/README.txt << 'EOF'
MP4 to MP3 Converter
====================

설치 방법:
1. MP4toMP3 앱을 Applications 폴더로 드래그하세요
2. Applications 폴더에서 MP4toMP3를 실행하세요

사용 방법:
1. 앱을 실행합니다
2. MP4 파일을 선택합니다
3. 변환 시작 버튼을 클릭합니다
4. MP3 파일이 원본과 같은 위치에 저장됩니다

참고: ffmpeg는 앱에 포함되어 있어 추가 설치가 필요 없습니다.
EOF

# Create DMG
hdiutil create -volname "MP4toMP3" -srcfolder dmg_temp -ov -format ULFO MP4toMP3_Installer.dmg

# Clean up
rm -rf dmg_temp

echo "✅ DMG created: MP4toMP3_Installer.dmg"