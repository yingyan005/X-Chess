'''
Author: Paoger
Date: 2023-11-24 09:46:39
LastEditors: Paoger
LastEditTime: 2024-01-20 18:34:37
Description: 

Copyright (c) 2023 by Paoger, All Rights Reserved. 
'''
import os
import glob

from kivy.logger import Logger
from kivymd.app import MDApp
from kivymd.uix.list import OneLineListItem


class OneLineListPath(OneLineListItem):
    def __init__(self,id=None, **kwargs):
        super(OneLineListPath, self).__init__(**kwargs)
    
    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            # we consumed the touch. return False here to propagate
            # the touch further to the children.
            if touch.is_double_tap:
                #print("....OneLineListPath.on_touch_up on me...")
                #print(f"{self.text=}") 
                
                app = MDApp.get_running_app()

                seachdir = os.path.join(app.root.ids['id_screenselectpath'].ids['id_cur_path'].text,f'{self.text}')                 
                app.sel_path = seachdir

                #Logger.debug(f"X-Chess X-OneLineListPath:on_touch_up {seachdir=}")

                app.root.ids['id_screenselectpath'].ids['id_cur_path'].text = seachdir

                seachdir = app.root.ids['id_screenselectpath'].ids['id_cur_path'].text
                #Logger.debug(f"X-Chess X-ChessApp:OneLineListPath {seachdir=}")
                seachdir = os.path.join(seachdir,'*')
                #Logger.debug(f"X-Chess X-ChessApp:OneLineListPath {seachdir=}")
                subdirs = [name for name in glob.glob(seachdir) if os.path.isdir(name)]
                app.root.ids['id_screenselectpath'].ids.id_dir_list.clear_widgets()
                for sd in subdirs:
                    last_level_dir = os.path.basename(sd)
                    app.root.ids['id_screenselectpath'].ids.id_dir_list.add_widget(OneLineListPath(text=f"{last_level_dir}",font_style="Overline"))
                
            return False
        
        return super().on_touch_up(touch)