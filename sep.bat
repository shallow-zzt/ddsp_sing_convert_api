@echo off
call G:\voice_seperate\venv\Scripts\activate.bat
cd G:\voice_seperate\spleeter
spleeter separate -p spleeter:2stems -o output test2.wav