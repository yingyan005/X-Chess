'''
Author: Paoger
Date: 2023-11-27 10:12:51
LastEditors: Paoger
LastEditTime: 2024-01-01 16:15:21
Description: 

Copyright (c) 2023 by Paoger, All Rights Reserved. 
'''
from kivy.graphics import *

from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.label import MDLabel

from kivy.logger import Logger

from arrowline import Arrowline,AIArrowline

class Chessboard(MDRelativeLayout):
    grid_side_len = 0
    x_offset = 0
    y_offset = 0

    arrows = []

    def __init__(self, **kwargs):
        super(Chessboard, self).__init__(**kwargs)

        #self.bind(pos=self.update_canvas)
        self.bind(size=self.update_canvas)
        self.update_canvas
    
    def update_canvas(self,*args):
        #need to reset everything

        #self.canvas.clear()        
        #with self.canvas.before:
        #    #context instruction
        #    Color(.1,.5,1,0.5)#蓝色
        #    Rectangle(pos=(0,0),size=self.size)
        #    print(f"canvas.before,{self.size=}")
        with self.canvas:
            self.canvas.clear()
            Color(0.5,0.5,0.5,0.5)
            #Color(.1,.5,1,0.5)#蓝色
            #Color(.9,.9,1,0.5)
            #Rectangle(pos=(0,0),size=self.size)
            print(f"Chessboard {self.width=},{self.height=}")
            #将最短边11等分，作为网格的边长
            #self.width x轴，self.height y轴
            if self.height > self.width:
                print(f"Chessboard 取棋盘{self.width=}的11等分作为格子的边长")
                Logger.info(f"Chessboard 取棋盘{self.width=}的11等分作为格子的边长")
                self.grid_side_len = self.width / 11
                self.x_offset = self.grid_side_len /2
                #使棋盘保持在y轴中间,宽高差的一半 - 格子的1半 （X轴比Y轴少一个格子）
                self.y_offset = (self.height - self.width) /2
            else:
                print(f"Chessboard 取棋盘{self.height=}的11等分作为格子的边长")
                Logger.info(f"Chessboard 取棋盘{self.height=}的11等分作为格子的边长")
                self.grid_side_len = self.height / 11
                self.y_offset = 0
                #使棋盘保持在y轴中间,宽高差的一半 + 格子的1半 （X轴比Y轴少一个格子）
                self.x_offset = (self.width - self.height) /2 + self.grid_side_len /2

            
            print(f"{self.grid_side_len=},{self.x_offset=},{self.y_offset=}")

            for y in range(0,10,1):#y坐标
                Line(points=[self.grid_side_len+self.x_offset,self.grid_side_len*(y+1)+self.y_offset,
                         self.grid_side_len*9+self.x_offset,self.grid_side_len*(y+1)+self.y_offset],width=1)

            #x0
            Line(points=[self.grid_side_len*1+self.x_offset,self.grid_side_len*1+self.y_offset,
                         self.grid_side_len*1+self.x_offset,self.grid_side_len*10+self.y_offset],width=1)
            for x in range(1,8,1):#x坐标
                #x-1
                Line(points=[self.grid_side_len*(x+1)+self.x_offset,self.grid_side_len*1+self.y_offset,
                            self.grid_side_len*(x+1)+self.x_offset,self.grid_side_len*5+self.y_offset],width=1)
                #x-2
                Line(points=[self.grid_side_len*(x+1)+self.x_offset,self.grid_side_len*6+self.y_offset,
                            self.grid_side_len*(x+1)+self.x_offset,self.grid_side_len*10+self.y_offset],width=1)
            
            #x8
            Line(points=[self.grid_side_len*9+self.x_offset,self.grid_side_len*1+self.y_offset,
                        self.grid_side_len*9+self.x_offset,self.grid_side_len*10+self.y_offset],width=1)
            
            #X
            Line(points=[self.grid_side_len*4+self.x_offset,self.grid_side_len*1+self.y_offset,
                            self.grid_side_len*6+self.x_offset,self.grid_side_len*3+self.y_offset],width=1)
            Line(points=[self.grid_side_len*4+self.x_offset,self.grid_side_len*3+self.y_offset,
                            self.grid_side_len*6+self.x_offset,self.grid_side_len*1+self.y_offset],width=1)
            
            #X
            Line(points=[self.grid_side_len*4+self.x_offset,self.grid_side_len*8+self.y_offset,
                            self.grid_side_len*6+self.x_offset,self.grid_side_len*10+self.y_offset],width=1)
            Line(points=[self.grid_side_len*4+self.x_offset,self.grid_side_len*10+self.y_offset,
                            self.grid_side_len*6+self.x_offset,self.grid_side_len*8+self.y_offset],width=1)
            
            MDLabel(text="9",font_style="Overline",center=(self.x_offset+self.grid_side_len*1+48,self.y_offset+10),theme_text_color="Custom",text_color=(0.5,0.5,0.5,0.5))
            MDLabel(text="8",font_style="Overline",center=(self.x_offset+self.grid_side_len*2+48,self.y_offset+10),theme_text_color="Custom",text_color=(0.5,0.5,0.5,0.5))
            MDLabel(text="7",font_style="Overline",center=(self.x_offset+self.grid_side_len*3+48,self.y_offset+10),theme_text_color="Custom",text_color=(0.5,0.5,0.5,0.5))
            MDLabel(text="6",font_style="Overline",center=(self.x_offset+self.grid_side_len*4+48,self.y_offset+10),theme_text_color="Custom",text_color=(0.5,0.5,0.5,0.5))
            MDLabel(text="5",font_style="Overline",center=(self.x_offset+self.grid_side_len*5+48,self.y_offset+10),theme_text_color="Custom",text_color=(0.5,0.5,0.5,0.5))
            MDLabel(text="4",font_style="Overline",center=(self.x_offset+self.grid_side_len*6+48,self.y_offset+10),theme_text_color="Custom",text_color=(0.5,0.5,0.5,0.5))
            MDLabel(text="3",font_style="Overline",center=(self.x_offset+self.grid_side_len*7+48,self.y_offset+10),theme_text_color="Custom",text_color=(0.5,0.5,0.5,0.5))
            MDLabel(text="2",font_style="Overline",center=(self.x_offset+self.grid_side_len*8+48,self.y_offset+10),theme_text_color="Custom",text_color=(0.5,0.5,0.5,0.5))
            MDLabel(text="1",font_style="Overline",center=(self.x_offset+self.grid_side_len*9+48,self.y_offset+10),theme_text_color="Custom",text_color=(0.5,0.5,0.5,0.5))

            MDLabel(text="1",font_style="Overline",center=(self.x_offset+self.grid_side_len*1+48,self.y_offset+self.grid_side_len*10+22),theme_text_color="Custom",text_color=(0.5,0.5,0.5,0.5))
            MDLabel(text="2",font_style="Overline",center=(self.x_offset+self.grid_side_len*2+48,self.y_offset+self.grid_side_len*10+22),theme_text_color="Custom",text_color=(0.5,0.5,0.5,0.5))
            MDLabel(text="3",font_style="Overline",center=(self.x_offset+self.grid_side_len*3+48,self.y_offset+self.grid_side_len*10+22),theme_text_color="Custom",text_color=(0.5,0.5,0.5,0.5))
            MDLabel(text="4",font_style="Overline",center=(self.x_offset+self.grid_side_len*4+48,self.y_offset+self.grid_side_len*10+22),theme_text_color="Custom",text_color=(0.5,0.5,0.5,0.5))
            MDLabel(text="5",font_style="Overline",center=(self.x_offset+self.grid_side_len*5+48,self.y_offset+self.grid_side_len*10+22),theme_text_color="Custom",text_color=(0.5,0.5,0.5,0.5))
            MDLabel(text="6",font_style="Overline",center=(self.x_offset+self.grid_side_len*6+48,self.y_offset+self.grid_side_len*10+22),theme_text_color="Custom",text_color=(0.5,0.5,0.5,0.5))
            MDLabel(text="7",font_style="Overline",center=(self.x_offset+self.grid_side_len*7+48,self.y_offset+self.grid_side_len*10+22),theme_text_color="Custom",text_color=(0.5,0.5,0.5,0.5))
            MDLabel(text="8",font_style="Overline",center=(self.x_offset+self.grid_side_len*8+48,self.y_offset+self.grid_side_len*10+22),theme_text_color="Custom",text_color=(0.5,0.5,0.5,0.5))
            MDLabel(text="9",font_style="Overline",center=(self.x_offset+self.grid_side_len*9+48,self.y_offset+self.grid_side_len*10+22),theme_text_color="Custom",text_color=(0.5,0.5,0.5,0.5))
    
    def remove_Allarrows(self):
        for i in self.arrows:
            self.remove_widget(i)
        self.arrows.clear()
    
    def get_width(self,sx,sy,ex,ey):
        u = 3
        w = u
        """ if sx == ex:
            w = (9 - abs(ey -sy)) * 2 * u / 9 
        elif sy == ey:
            w = (8 - abs(ex -sx)) * 2 * u / 8
        else:#shi ma xiang 它们的路线没有重叠的地方，统一返回1个单位的宽度
            w = 1 * u """
        
        return w
    
    def add_arrow(self,sx,sy,ex,ey):
        scx = self.x_offset + self.grid_side_len * (sx+1)
        scy = self.y_offset + self.grid_side_len * (sy+1)
        ecx = self.x_offset + self.grid_side_len * (ex+1)
        ecy = self.y_offset + self.grid_side_len * (ey+1)
        w = self.get_width(sx,sy,ex,ey)

        ar = Arrowline(scx,scy,ecx,ecy,w,self.grid_side_len/8)
        self.add_widget(ar)
        self.arrows.append(ar)
    
    def add_aiarrow(self,sx,sy,ex,ey):
        scx = self.x_offset + self.grid_side_len * (sx+1)
        scy = self.y_offset + self.grid_side_len * (sy+1)
        ecx = self.x_offset + self.grid_side_len * (ex+1)
        ecy = self.y_offset + self.grid_side_len * (ey+1)
        w = self.get_width(sx,sy,ex,ey)

        ar = AIArrowline(scx,scy,ecx,ecy,w,self.grid_side_len/8)
        self.add_widget(ar)
        self.arrows.append(ar)
    
    def on_touch_up(self, touch):
        #print("Chessboard.on_touch_up begin")
        ret = super(MDRelativeLayout, self).on_touch_up(touch)

        if self.collide_point(*touch.pos):
            app = MDApp.get_running_app()
            if app.selected_piece != None:
                #print(f"{app.selected_piece.camp=},{app.selected_piece.identifier=},{app.selected_piece.bx=},{app.selected_piece.by=}")
                if app.gameover == True:
                    toast("此局已结束！")
                    return ret
                
                # 这里用push先把当前的坐标位置存留起来，以后就还可以恢复到这个坐标
                touch.push()
                # 接下来就是把Touch的坐标转换成本地空间的坐标
                touch.apply_transform_2d(self.to_local)
                # Touch事件的坐标位置现在就是本地空间的了
                tx = touch.pos[0]
                ty = touch.pos[1]
                #无论结果如何，一定记得把这个转换用pop弹出
                # 之后，坐标就又恢复成上层空间的了
                touch.pop()

                #距离网格点1/3处均视为该网点有效范围内
                #遍历下棋盘
                for x in range(0,9,1):
                    for y in range(0,10,1):
                        #print(f"网点：({x},{y})")
                        leftx = app.root.ids['id_screenmain'].ids.id_chessboard.x_offset + app.root.ids['id_screenmain'].ids.id_chessboard.grid_side_len * (x+1) - app.root.ids['id_screenmain'].ids.id_chessboard.grid_side_len / 3
                        rightx = app.root.ids['id_screenmain'].ids.id_chessboard.x_offset + app.root.ids['id_screenmain'].ids.id_chessboard.grid_side_len * (x+1) + app.root.ids['id_screenmain'].ids.id_chessboard.grid_side_len / 3
                        boty = app.root.ids['id_screenmain'].ids.id_chessboard.y_offset + app.root.ids['id_screenmain'].ids.id_chessboard.grid_side_len * (y+1) - app.root.ids['id_screenmain'].ids.id_chessboard.grid_side_len / 3
                        topy = app.root.ids['id_screenmain'].ids.id_chessboard.y_offset + app.root.ids['id_screenmain'].ids.id_chessboard.grid_side_len * (y+1) + app.root.ids['id_screenmain'].ids.id_chessboard.grid_side_len / 3

                        if (tx > leftx) and (tx < rightx) and (ty > boty) and (ty < topy):
                            #print(f"中标：{x},{y}")

                            #print(f"{leftx=},{rightx=},{boty=},{topy=}")
                            #print(f"{touch.pos[0]=},{touch.pos[1]=}")
                            app.selected_piece.letsgo(x,y)                
        
        #print("Chessboard.on_touch_up end")
        
        # 最后就是返回结果了
        return ret


