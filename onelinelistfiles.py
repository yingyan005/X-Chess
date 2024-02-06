'''
Author: Paoger
Date: 2023-11-24 09:46:39
LastEditors: Paoger
LastEditTime: 2024-01-20 18:24:55
Description: 

Copyright (c) 2023 by Paoger, All Rights Reserved. 
'''
import os

from kivymd.app import MDApp
from kivymd.uix.list import OneLineListItem

class OneLineListFiles(OneLineListItem):
    def __init__(self,id=None, **kwargs):
        super(OneLineListFiles, self).__init__(**kwargs)
    
    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            # we consumed the touch. return False here to propagate
            # the touch further to the children.
            #print("....OneLineListFiles.on_touch_up on me...")            
            #print(f"{self.text=}")            

            app = MDApp.get_running_app()
            app.sel_filename = os.path.join(app.root.ids['id_screenselectfile'].ids['id_cur_path'].text,f'{self.text}')

            #print(f"{app.sel_filename=}")

            #改变选中项的背景色  
            for child in app.root.ids['id_screenselectfile'].ids.id_file_list.children[:]:
                #print(f"{child.text}")
                if child.bg_color == [0,1,1,1]:
                    child.bg_color = app.theme_cls.bg_normal
            #self.bg_color = [0,1,1,1]
            self.bg_color = [0,1,1,1]

            return False
        
        return super().on_touch_up(touch)