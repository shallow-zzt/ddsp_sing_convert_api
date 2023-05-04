import requests
import re
import os, sys, configparser, json,shutil
import time
import random
#取中间
def make_dir(path):
    try:
        os.mkdir(path)
    except:
        pass
    return
        
def get_center_text(raw_text,left,right):
    try:
        strs = raw_text
        re2 = re.compile(r''+left+'(.*?)'+right)
        result = re2.findall(strs)
        return result

    except:
        return '-1'
    
#读配置    
def read_config(path,key1 = '#null#',key2 = '#null#',default = 0,enc=False):
    configs = configparser.ConfigParser()
    try:
        if enc:
            configs.read(path,encoding='utf-8')
        else:
            configs.read(path)
        if key1 == '#null#' and key2 == '#null#':
            result=configs.sections()
        elif key1 != '#null#' and key2 == '#null#':
            result=configs.options(key1)
        else:
            result=configs.get(key1,key2)
    except:
        result=default
    return result

#写配置
def write_config(path,key1,key2,value,enc=False):
    configs = configparser.ConfigParser()
    try:
        if enc:
            configs.read(path,encoding='utf-8')
        else:
            configs.read(path)        
    except:
        pass
    try:
        configs.add_section(key1)
    except:
        pass
    configs.set(key1, key2, value)
    if enc:
        f = open(path, 'w',encoding='utf-8')
    else:
        f = open(path, 'w')        
    configs.write(f)
    f.close()
    return
    
#访问网页
def url_content(url,headers=None):
    try:
        r=requests.get(url,headers=headers)
        return r.text
    except Exception as e:
        print(e)
        return '-1'