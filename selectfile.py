'''
Author: Paoger
Date: 2024-01-19 15:58:11
LastEditors: Paoger
LastEditTime: 2024-01-20 18:29:30
Description: 

Copyright (c) 2024 by Paoger, All Rights Reserved. 
'''
import os
import glob
import binascii
from treelib import Tree
import uuid
import datetime

from kivy.logger import Logger
from kivymd.app import MDApp

from onelinelistfiles import OneLineListFiles
from onelinelistpathwithfile import OneLineListPathWithFile

#切换到上一级目录
def toUperLevelDirWithFile(curDir):
    Logger.debug(f"X-Chess selectfile:toUperLevelDir {curDir=}")

    app = MDApp.get_running_app()

    app.root.ids['id_screenselectfile'].ids['id_btn_back'].disabled = True    

    upDir = os.path.dirname(curDir)
    Logger.debug(f"X-Chess selectfile:toUperLevelDir {upDir=}")

    app.root.ids['id_screenselectfile'].ids['id_cur_path'].text = upDir

    seachdir = app.root.ids['id_screenselectfile'].ids['id_cur_path'].text
    Logger.debug(f"X-Chess X-ChessApp:open_XQFFile {seachdir=}")
    seachdir = os.path.join(seachdir,'*')
    Logger.debug(f"X-Chess X-ChessApp:open_XQFFile {seachdir=}")
    subdirs = [name for name in glob.glob(seachdir) if os.path.isdir(name)]
    app.root.ids['id_screenselectfile'].ids.id_dir_list.clear_widgets()
    for sd in subdirs:
        last_level_dir = os.path.basename(sd)
        app.root.ids['id_screenselectfile'].ids.id_dir_list.add_widget(OneLineListPathWithFile(text=f"{last_level_dir}",font_style="Overline"))
                
    seachdir = app.root.ids['id_screenselectfile'].ids['id_cur_path'].text
    filetype = app.root.ids['id_screenselectfile'].ids['id_filetype'].text
    filetype = filetype.split('.')
    seachdir = os.path.join(seachdir,f'*.{filetype[1]}')
    Logger.debug(f"X-Chess X-ChessApp:open_XQFFile {seachdir=}")
    files = [name for name in glob.glob(seachdir) if os.path.isfile(name)]
    app.root.ids['id_screenselectfile'].ids.id_file_list.clear_widgets()
    for file in files:
        filename = os.path.basename(file)
        app.root.ids['id_screenselectfile'].ids.id_file_list.add_widget(OneLineListFiles(text=f"{filename}",font_style="Overline"))
    
    app.root.ids['id_screenselectfile'].ids['id_btn_back'].disabled = False
