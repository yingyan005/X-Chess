'''
Author: Paoger
Date: 2023-11-27 15:32:43
LastEditors: Paoger
LastEditTime: 2024-01-12 14:11:13
Description: 

Copyright (c) 2023 by Paoger, All Rights Reserved. 
'''
from kivy.graphics import *
from kivy.uix.widget import Widget

from kivymd.app import MDApp

class Arrowline(Widget):
    sx = sy = ex = ey = w = r = None

    def __init__(self,sx,sy,ex,ey,w=1,r=1,**kwargs):
        super(Arrowline, self).__init__(**kwargs)
        self.sx = sx
        self.sy = sy
        self.ex = ex
        self.ey = ey
        self.w = w
        self.r = r

        self.bind(pos=self.update_canvas)
        self.bind(size=self.update_canvas)
        self.update_canvas
    
    def update_canvas(self,*args):
        with self.canvas:
            self.canvas.clear()
            #Color(128,128,0,0.6)#浅黄
            Color(0.129,0.588,0.953,0.6)#浅蓝 33 150 243 

            Line(points=[self.sx,self.sy,self.ex,self.ey],width=self.w)
            Line(circle=(self.ex,self.ey,self.r),width=self.r)

class AIArrowline(Widget):
    sx = sy = ex = ey = w = r = None

    def __init__(self,sx,sy,ex,ey,w=1,r=1,**kwargs):
        super(AIArrowline, self).__init__(**kwargs)
        self.sx = sx
        self.sy = sy
        self.ex = ex
        self.ey = ey
        self.w = w
        self.r = r

        self.bind(pos=self.update_canvas)
        self.bind(size=self.update_canvas)
        self.update_canvas
    
    def update_canvas(self,*args):
        with self.canvas:
            self.canvas.clear()
            Color(128,128,0,0.6)#浅黄
            #Color(0.129,0.588,0.953,0.3)#浅蓝 33 150 243 

            Line(points=[self.sx,self.sy,self.ex,self.ey],width=self.w)
            Line(circle=(self.ex,self.ey,self.r),width=self.r)