'''
Author: Paoger
Date: 2023-11-24 09:46:39
LastEditors: Paoger
LastEditTime: 2024-01-27 15:06:00
Description: 

Copyright (c) 2023 by Paoger, All Rights Reserved. 
'''
import os
import glob

from kivy.logger import Logger
from kivymd.app import MDApp
from kivymd.uix.list import OneLineListItem
from kivymd.utils import asynckivy

from onelinelistfiles import OneLineListFiles

class OneLineListPathWithFile(OneLineListItem):
    def __init__(self,id=None, **kwargs):
        super(OneLineListPathWithFile, self).__init__(**kwargs)
    
    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            # we consumed the touch. return False here to propagate
            # the touch further to the children.
            #if touch.is_double_tap:#双击
                #print("....OneLineListPath.on_touch_up on me...")
                #print(f"{self.text=}") 
            app = MDApp.get_running_app()
            app.root.ids['id_screenselectfile'].ids['id_subdir'].text = self.text

            return True
        
        return super().on_touch_up(touch)