'''
Author: Paoger
Date: 2023-11-06 16:13:14
LastEditors: Paoger
LastEditTime: 2024-02-06 08:47:03
Description: 

Copyright (c) 2023 by Paoger, All Rights Reserved. 
'''

import os
import configparser

from kivy.utils import platform
from kivy.logger import Logger
from kivymd.app import MDApp
from kivymd.toast import toast

#获取上一次选择的路径
def get_theLast_Path():
    Logger.debug('X-Chess X_ChessApp get_theLast_Path: begin')
    app = MDApp.get_running_app()

    theLast_Path = ''
    # 读取 INI 文件，给g_theLast_Path赋值
    conf_info = configparser.ConfigParser()

    #if len(conf_info.read(os.path.join(os.getcwd(),'cfg/cfg.ini'),encoding='gbk')) != 0:
    if len(conf_info.read(app.cfgFileName,encoding='gbk')) != 0:
        theLast_Path = conf_info.get("XQF","theLast_Path")
        Logger.debug(f'X-Chess X_ChessApp get_theLast_Path: {theLast_Path=}')
        if theLast_Path == '':
            if platform == "android":
                Logger.debug(f'X-Chess X_ChessApp get_theLast_Path: android=={platform=}')

                from android.storage import primary_external_storage_path
                from android.permissions import  check_permission

                p_w = ("android.permission.WRITE_EXTERNAL_STORAGE")
                if check_permission(p_w) == True:                    
                    SD_CARD = primary_external_storage_path()
                    mypath = os.path.join(SD_CARD,'X-Chess/xqf')
                    if not os.path.exists(mypath):
                        try:
                            os.makedirs(mypath)
                        except Exception as e:
                            Logger.debug(f"X-Chess UCIEngine:get_theLast_Path Exception: {str(e)}")
                        finally:
                            pass
                    theLast_Path = os.path.join(SD_CARD,'X-Chess/xqf')
                    Logger.debug(f'X-Chess X_ChessApp get_theLast_Path:有 android.permission.WRITE_EXTERNAL_STORAGE,so {theLast_Path=}')
                else:
                    theLast_Path = ''
                    Logger.debug(f'X-Chess X_ChessApp get_theLast_Path: 没有权限,so {theLast_Path=}')
                    toast("请允许权限后，先退出app，再运行！！！")
            else:
                theLast_Path = os.path.join(os.getcwd(),'xqf')
        #print(f'{theLast_Path=},{type(theLast_Path)=}')
    else:
        #写个空的
        conf_info.add_section('XQF')
        conf_info.set("XQF","theLast_Path",'')
        cfg_path = os.path.join(os.getcwd(),'cfg')
        if not os.path.exists(cfg_path):
            os.makedirs(cfg_path)
        #conf_info.write(open(os.path.join(os.getcwd(),'cfg/cfg.ini'),'w',encoding='gbk'))
        conf_info.write(open(app.cfgFileName,'w',encoding='gbk'))
        theLast_Path = ''

    Logger.debug(f'X-Chess X_ChessApp get_theLast_Path: {theLast_Path=}')
    Logger.debug('X-Chess X_ChessApp get_theLast_Path: end')
    return theLast_Path

#保存上一次选择的路径
def save_theLast_Path(theLast_Path):
    Logger.debug('X-Chess save_theLast_Path: begin')

    app = MDApp.get_running_app()

    Logger.debug(f'X-Chess X_ChessApp save_theLast_Path: {theLast_Path=}')

    conf_info = configparser.ConfigParser()
    #cfgfilename = os.path.join(os.getcwd(),'cfg/cfg.ini')
    #cfgfilename = os.path.join(app.cfgFileName)

    Logger.debug(f'X-Chess save_theLast_Path: {app.cfgFileName=}')
    conf_info.read(app.cfgFileName,encoding='gbk')

    conf_info.set("XQF","theLast_Path",theLast_Path)
    #conf_info.write(open(os.path.join(os.getcwd(),'cfg/cfg.ini'),'w',encoding='gbk'))
    conf_info.write(open(app.cfgFileName,'w',encoding='gbk'))

    Logger.debug('X-Chess X_ChessApp save_theLast_Path: end')

def save_engine_settings(uci_options=None,**kargs):
    app = MDApp.get_running_app()

    conf_info = configparser.ConfigParser()
    #conf_info.read(os.path.join(os.getcwd(),'cfg/cfg.ini'),encoding='gbk')
    conf_info.read(app.cfgFileName,encoding='gbk')

    for k,v in kargs.items():
        print(f"{k=},{v=}")
        conf_info.set("ENGINE",k,f"{v}")
    
    print(f"***{uci_options=}")
    option_list = uci_options.split("\n")#os.linesep
    i = 1
    for op in option_list:
        print(f"option{i},{op=}")
        if op == "":#忽略
            continue
        conf_info.set("ENGINE",f"option{i}",f"{op}")
        i = i + 1
    
    #conf_info.write(open(os.path.join(os.getcwd(),'cfg/cfg.ini'),'w',encoding='gbk'))
    conf_info.write(open(app.cfgFileName,'w',encoding='gbk'))

    return

#获取引擎配置信息
def get_engine_settings():
    app = MDApp.get_running_app()
    
    engine_settings = {}

    # 读取 INI 文件
    conf_info = configparser.ConfigParser()
    #if len(conf_info.read(os.path.join(os.getcwd(),'cfg/cfg.ini'),encoding='gbk')) != 0:
    if len(conf_info.read(app.cfgFileName,encoding='gbk')) != 0:    
        settings = conf_info['ENGINE']
        for k,v in settings.items():
           #print(f"{k=},{v=}")
           engine_settings[k] = v
           
        #print(f"{engine_settings}")
    else:
        #写个空的
        conf_info.add_section('ENGINE')
        conf_info.set("ENGINE","engine_name",'')
        conf_info.set("ENGINE","ai_think_time",'')
        conf_info.set("ENGINE","engine_filename",'')
        conf_info.set("ENGINE","engine_location",'inner')
        cfg_path = os.path.join(os.getcwd(),'cfg')
        if not os.path.exists(cfg_path):
            os.makedirs(cfg_path)
        #conf_info.write(open(os.path.join(os.getcwd(),'cfg/cfg.ini'),'w',encoding='gbk'))
        conf_info.write(open(app.cfgFileName,'w',encoding='gbk'))

    return engine_settings


    


