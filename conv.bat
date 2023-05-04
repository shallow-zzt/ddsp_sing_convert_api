@echo off
call G:\DDSP-SVC-master\venv\Scripts\activate.bat
cd G:\DDSP-SVC-master\
python main.py -i test2.wav -m model2\model_320000.pt -o output.wav -k 1 -id 1 -e true -eak 1