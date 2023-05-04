#coding=utf-8
import os
import shutil
import requests
import json
import re
import datetime
import random
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
from flask import Flask, send_file, request
from gevent import pywsgi

app = Flask(__name__)



def url_content(url,headers=None):
    try:
        r=requests.get(url,headers=headers)
        return r.text
    except Exception as e:
        print(e)
        return '-1'

def make_path(filename):
    try:
        os.mkdir(filename)
    except:
        pass


def dl(url,path,mode="wb"):
    if mode=="wb":
        r = requests.get(url)
        with open(path, mode) as f:
            f.write(r.content)
    elif mode=="w":
        with open(path, mode,encoding='utf-8') as f:
            f.write(url)        
    return

def mixer(filename):
    bgm = AudioSegment.from_file(f"storage/{filename}/bgm.wav")
    voice = AudioSegment.from_file(f"storage/{filename}/soft_voice.wav")
    voice = voice + 12
    voice.export(f"storage/{filename}/soft_voice.wav", format="wav")
    output = voice.overlay(bgm)
    output.export(f"storage/{filename}/mixed.wav", format="wav")

    return 


def convert(filename):
    pure_filename=filename.split('.')[0]
    convert_path='G:/DDSP-SVC-master/'
    shutil.copy(f'storage/{pure_filename}/vocals.wav',f'{convert_path}test2.wav')
    os.system(f'conv.bat')
    shutil.copy(f'{convert_path}output.wav',f'storage/{pure_filename}/soft_voice.wav')
    mixer(pure_filename)
    
    return

def seperate(filename):
    pure_filename=filename.split('.')[0]
    spleeter_path='G:/voice_seperate/spleeter/'
    shutil.copy(f'storage/{pure_filename}/{filename}',f'{spleeter_path}test2.wav')
    os.system(f'sep.bat')
    shutil.copy(f'{spleeter_path}output/test2/vocals.wav',f'storage/{pure_filename}/vocals.wav')
    shutil.copy(f'{spleeter_path}output/test2/accompaniment.wav',f'storage/{pure_filename}/bgm.wav')

    convert(filename)
    return

def read_lyric(filename,song_length,select=6):
    lyric_content=open(f'storage/{filename}/{filename}.txt','r',encoding='utf-8').read().split('\n')
    if len(lyric_content)<=select+3:
        return (-1,-1,None)
    
    times=[]
    re2 = re.compile(r'\[(.*)\]')

    for i in range(0,len(lyric_content)-1):
        lyric_time=re2.findall(lyric_content[i])[0]

        #print(lyric_time)
        dt = datetime.datetime.strptime(lyric_time, '%M:%S.%f')
        time = (dt - datetime.datetime(1900, 1, 1)).total_seconds()

        times.append(time)
    
    times.append(song_length/1000)

    start_sen=random.randint(3,len(lyric_content)-select-1)
    end_sen=start_sen+select-1

    start_time=times[start_sen]
    end_time= times[start_sen+select-1]

    apart_node=start_time
    apart_node_pos=start_sen

    max_combo=0
    combo=0

    for i in range(start_sen,start_sen+select):
        if times[i+1]-times[i]>len(lyric_content[i].encode())*0.25-2.5:
            if combo>max_combo:
                start_time = apart_node
                start_sen = apart_node_pos
                end_time = times[i+1]
                end_sen = i+1
                max_combo=combo
            combo=0
            apart_node = times[i+1]
            apart_node_pos = i+1
        else:
            combo+=1

    # if end_time != None and end_sen != None:
    #     end_time = times[start_sen+select-1]
    #     end_sen = start_sen+select-1    

    lyric_return=lyric_content[start_sen:end_sen]

    return(start_time,end_time,lyric_return)


def song_cut(full_file,filename,start,end):
    origin_file=AudioSegment.from_file(full_file)
    cutted=origin_file[start*1000:end*1000]
    # nonsilent_ranges = detect_nonsilent(cutted,silence_thresh=-50.0,min_silence_len=500)
    # if len(nonsilent_ranges) > 0:
    #     last_nonsilent_end = nonsilent_ranges[-1][1]
    #     audio_trimmed = cutted[:last_nonsilent_end]
    #     audio_trimmed.export(f"storage/{filename}/output.wav", format="wav")
    # else:
    cutted.export(f"storage/{filename}/output.wav", format="wav")         

def get_song_list():
    song_saved_list=open('song_list.txt','r',encoding='utf-8')
    song_saved_list=song_saved_list.read().split('\n')
    return song_saved_list

def get_music(name,mode='dl'):
    search_url=url_content(f'http://124.223.43.30:4000/search?keywords={name}')
    search_url=json.loads(search_url)

    status=search_url['code']
    if status==200:
        song_list=search_url['result']['songs']
        song_id=song_list[0]['id']
        song_name=song_list[0]['name']
        song_author=song_list[0]['artists'][0]['name']

        if mode != 'dl':
            return f'{song_name}-{song_author}'.replace('.','-')

        song_url=url_content(f'http://124.223.43.30:4000/song/url?id={song_id}')
        song_lyric=url_content(f'http://124.223.43.30:4000/lyric?id={song_id}')
        song_url=json.loads(song_url)
        song_lyric=json.loads(song_lyric)

        song_dl_url=song_url['data'][0]['url']
        song_lyric_dl=song_lyric['lrc']['lyric']
        filename=f'{song_name}-{song_author}'.replace('.','-')
        
        song_saved_list=get_song_list()
        #print(song_saved_list)
        if filename not in song_saved_list:
            open('song_list.txt','a',encoding='utf-8').write(f'\n{filename}')

            make_path(f'storage/{filename}')
            dl(song_dl_url,f'storage/{filename}/{filename}.wav')
            dl(song_lyric_dl,f'storage/{filename}/{filename}.txt','w')   
            seperate(f'{filename}.wav')
        return filename

    else:
        return '-1'

@app.route('/list')
def able_song_show():
    name = request.args.get('name','-1')
    origin_name='-1'
    if name != '-1':
        origin_name=get_music(name,mode='search')

    song_list_show=get_song_list()
    response={"code":200,"origin_name":origin_name,"song_list":song_list_show}
    return str(response) 

@app.route('/download/<path:filename>')
def download(filename):
    file_path = filename
    return send_file(file_path, as_attachment=True)

@app.route('/singing')
def download_file():
    name = request.args.get('name')
    mode = request.args.get('mode')
    iscut = int(request.args.get('iscut',0))
    select = int(request.args.get('select',6))
    start = float(request.args.get('start',-1))
    duration = float(request.args.get('duration',10))
    filename = get_music(name)
    use_cut=False

    if filename == '-1':
        response={"code":404}
        return str(response)        

    if iscut != 0:
        origin_file=AudioSegment.from_file(f"storage/{filename}/{filename}.wav")
        song_length=len(origin_file)
        song_start,song_end,song_lyric=read_lyric(filename,song_length,select)
        use_cut=True
    elif iscut == 0 and start != -1:
        song_start=start*1000
        song_end=(start+duration)*1000
        song_lyric=None
        use_cut=True

    # print(song_start,song_end)

    dl_path={'o':f'storage/{filename}/{filename}.wav',
             'v':f'storage/{filename}/vocals.wav',
             'b':f'storage/{filename}/bgm.wav',
             'sv':f'storage/{filename}/soft_voice.wav',
             'm':f'storage/{filename}/mixed.wav',}
    
    if use_cut:
        song_cut(dl_path[mode],filename,song_start,song_end)
    else:
        song_lyric=open(f'storage/{filename}/{filename}.txt','r',encoding='utf=8').read().split('\n')
        shutil.copy(dl_path[mode],f"storage/{filename}/output.wav")        

    response={"code":200,"url":f"http://singer.botsh.io:7003/download/storage/{filename}/output.wav","lyric":song_lyric}
    return str(response)

if __name__ == '__main__':
    make_path('storage')
    server = pywsgi.WSGIServer(('0.0.0.0', 12345), app)
    server.serve_forever()   


