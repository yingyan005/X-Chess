'''
Author: Paoger
Date: 2023-11-06 16:13:14
LastEditors: Paoger
LastEditTime: 2023-12-19 14:36:00
Description: 

Copyright (c) 2023 by Paoger, All Rights Reserved. 
'''

import os
import configparser


#获取上一次选择的路径
def get_theLast_Path():
    theLast_Path = ''
    # 读取 INI 文件，给g_theLast_Path赋值
    conf_info = configparser.ConfigParser()
    if len(conf_info.read(os.path.join(os.getcwd(),'cfg/cfg.ini'),encoding='gbk')) != 0:
        theLast_Path = conf_info.get("XQF","theLast_Path")
        #print(f'{theLast_Path=},{type(theLast_Path)=}')
        if theLast_Path == '':
            theLast_Path = os.path.join(os.getcwd(),'xqf')
        #print(f'{theLast_Path=},{type(theLast_Path)=}')
    else:
        #写个空的
        conf_info.add_section('XQF')
        conf_info.set("XQF","theLast_Path",'')
        cfg_path = os.path.join(os.getcwd(),'cfg')
        if not os.path.exists(cfg_path):
            os.makedirs(cfg_path)
        conf_info.write(open(os.path.join(os.getcwd(),'cfg/cfg.ini'),'w',encoding='gbk'))

    return theLast_Path

#保存上一次选择的路径
def save_theLast_Path(theLast_Path):
    conf_info = configparser.ConfigParser()
    conf_info.read(os.path.join(os.getcwd(),'cfg/cfg.ini'),encoding='gbk')
    conf_info.set("XQF","theLast_Path",theLast_Path)
    conf_info.write(open(os.path.join(os.getcwd(),'cfg/cfg.ini'),'w',encoding='gbk'))




    


