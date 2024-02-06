'''
Author: Paoger
Date: 2024-01-19 15:58:11
LastEditors: Paoger
LastEditTime: 2024-01-20 18:30:01
Description: 

Copyright (c) 2024 by Paoger, All Rights Reserved. 
'''
import os
import glob

from kivy.logger import Logger
from kivymd.app import MDApp

from onelinelistpath import OneLineListPath

#切换到上一级目录
def toUperLevelDir(curDir):
    Logger.debug(f"X-Chess selectpath:toUperLevelDir {curDir=}")

    app = MDApp.get_running_app()

    app.root.ids['id_screenselectpath'].ids['id_btn_back'].disabled = True    

    upDir = os.path.dirname(curDir)
    Logger.debug(f"X-Chess id_screenselectpath:toUperLevelDir {upDir=}")
    app.sel_path = upDir

    app.root.ids['id_screenselectpath'].ids['id_cur_path'].text = upDir

    seachdir = app.root.ids['id_screenselectpath'].ids['id_cur_path'].text
    seachdir = os.path.join(seachdir,'*')
    subdirs = [name for name in glob.glob(seachdir) if os.path.isdir(name)]
    app.root.ids['id_screenselectpath'].ids.id_dir_list.clear_widgets()
    for sd in subdirs:
        last_level_dir = os.path.basename(sd)
        app.root.ids['id_screenselectpath'].ids.id_dir_list.add_widget(OneLineListPath(text=f"{last_level_dir}",font_style="Overline"))
                
    app.root.ids['id_screenselectpath'].ids['id_btn_back'].disabled = False
