'''
Author: Paoger
Date: 2023-12-04 13:56:00
LastEditors: Paoger
LastEditTime: 2023-12-18 13:03:07
Description: 

Copyright (c) 2023 by Paoger, All Rights Reserved. 
'''
import os

from kivy.utils import platform
from kivy.uix.scatter import Scatter
from kivy.graphics.svg import Svg
from kivy.properties import StringProperty

from kivymd.app import MDApp
from kivymd.uix.label import MDLabel

#棋子Widget
class PieceWidget2(Scatter):
    #svg_filename = StringProperty('svg_filename')
    svg_filename = None

    #阵营，红：r，黑：b
    camp = None
    #棋子标识符，车：ju，马：ma，象：xiang，士：shi，帅(将)：shuai，炮：pao，兵（卒）：bing
    identifier = None
    old_x = old_y = None #便于将棋子移回原位，布局坐标
    #坐标原点左下角，棋盘横坐标,整数 0~8,变量不能是内部变量x，否则有冲突
    #初始值为布局坐标，移动后转为棋盘坐标
    bx = None
    #纵坐标,整数 0~9
    by = None

    def __init__(self,svg_fn=None,camp=None,identifier=None,bx=None,by=None,**kwargs):
        #if platform == "android":
        #    self.scale = 0.8
        #else:
        #    self.scale = 0.3
        
        self.do_rotation = False
        self.do_scale = False
        self.do_translation = False
        self.auto_bring_to_front = False

        super(PieceWidget2, self).__init__(**kwargs)
        
        self.svg_filename = svg_fn
        self.camp = camp
        self.identifier = identifier
        self.bx = bx
        self.by = by
        self.old_x = bx
        self.old_y = by

        with self.canvas:
           filename = os.path.join( os.getcwd(),self.svg_filename)
           svg = Svg(filename)
           self.size = svg.width, svg.height

           app = MDApp.get_running_app()
           #使棋子宽度的1/2 等于 网格边长的 2/5
           self.scale = (app.root.ids['id_screditsituiation'].ids.id_chessboard2.grid_side_len * 2 / 5) * ( 2 / svg.width)


           #不显示角标
           #MDLabel(text="9",font_style="H1",center=self.center,theme_text_color="Custom",text_color=(.1,.5,1,1))

    def __str__(self):#重写__str__(),显示更多有用信息
        return f"{self.camp}:{self.identifier}({self.bx},{self.by})"
    
    #def on_svg_filename(self, instance, filename):
    #    with self.canvas:
    #        self.svg_filename = os.path.join( os.getcwd(),filename)
    #        svg = Svg(self.svg_filename)
    #        self.size = svg.width, svg.height

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            self.pressed = touch.pos
            app = MDApp.get_running_app()
            app.root.ids['id_screditsituiation'].ids.id_chessboard2.selected_piece = self
            app.root.ids['id_screditsituiation'].ids.id_chessboard2.selectedmask.center=[self.center[0],self.center[1]]
            return True
        
        return super(PieceWidget2, self).on_touch_up(touch)
    
    def movexy(self,ex,ey,direction):
        #print("PieceWidget2.movexy begin")
        #print(f"{sx=},{sy=},{ex=},{ey=}")
        app = MDApp.get_running_app()

        if direction == 'F':
            self.center = [app.root.ids['id_screditsituiation'].ids.id_chessboard2.x_offset + app.root.ids['id_screditsituiation'].ids.id_chessboard2.grid_side_len * (ex+1),app.root.ids['id_screditsituiation'].ids.id_chessboard2.y_offset + app.root.ids['id_screditsituiation'].ids.id_chessboard2.grid_side_len * (ey+1) ]

            #将坐标更新为棋盘坐标
            self.bx = ex
            self.by = ey
        elif direction == 'B':
            #将移回原位
            self.bx = self.old_x
            self.by = self.old_y
            self.center = [self.old_x,self.old_y]
        else:
            print("啥也不是")
        
        #选择框跟随
        app.root.ids['id_screditsituiation'].ids.id_chessboard2.selectedmask.center=[self.center[0],self.center[1]]
        
        #print("PieceWidget2.movexy end")