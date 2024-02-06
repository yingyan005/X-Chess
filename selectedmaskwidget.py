'''
Author: Paoger
Date: 2023-11-24 08:55:19
LastEditors: Paoger
LastEditTime: 2024-02-04 12:57:59
Description: 

Copyright (c) 2023 by Paoger, All Rights Reserved. 
'''
import os

from kivymd.app import MDApp
from kivy.utils import platform
from kivy.uix.scatter import Scatter
from kivy.graphics.svg import Svg

#棋子选中描边Widget
class SelectedMaskWidget(Scatter):
    svg_filename = ''
    
    def __init__(self,svg_fn='mask.svg', **kwargs):
        #if platform == "android":
        #    self.scale = 0.9
        #else:
        #    self.scale = 0.28
        self.do_rotation = False
        self.do_scale = False
        self.do_translation = False
        self.auto_bring_to_front = True

        super(SelectedMaskWidget, self).__init__(**kwargs)

        svg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'img')

        # 这种写法 linux中有问题
        # self.svg_filename = f'{svg_path}\{svg_fn}'
        self.svg_filename = os.path.join(svg_path,svg_fn)
        with self.canvas:
            filename = os.path.join( os.getcwd(),self.svg_filename)
            svg = Svg(filename)
            self.size = svg.width, svg.height

            app = MDApp.get_running_app()
            #使棋子宽度的1/2 等于 网格边长的 2/5
            self.scale = (app.root.ids['id_screenmain'].ids.id_chessboard.grid_side_len * 2 / 5) * ( 2 / svg.width)
