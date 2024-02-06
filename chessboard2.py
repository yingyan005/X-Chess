import os
from kivy.graphics import *

from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.label import MDLabel
from kivymd.utils import asynckivy

from global_var import g_const_S_P_ORDEER

from piecewidget2 import PieceWidget2
from piece import Piece
from selectedmaskwidget2 import SelectedMaskWidget2

class Chessboard2(MDRelativeLayout):
    grid_side_len = 0
    x_offset = 0
    y_offset = 0
    
    selectedmask =  None
    selected_piece = None

    def __init__(self, **kwargs):
        super(Chessboard2, self).__init__(**kwargs)

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
        #with self.canvas:
        with self.canvas:
            self.canvas.clear()
            Color(0.5,0.5,0.5,0.5)
            #Color(.1,.5,1,0.5)#蓝色
            #Color(.9,.9,1,0.5)
            #Rectangle(pos=(0,0),size=self.size)
            print(f"Chessboard2 {self.width=},{self.height=}")
            if self.width == 100:#100这个是初始尺寸，别画了，浪费
                return
            
            #将最短边11等分，作为网格的边长
            #self.width x轴，self.height y轴
            if self.height > self.width:
                #print(f"Chessboard2 取棋盘{self.width=}的11等分作为格子的边长")
                self.grid_side_len = self.width / 11
                self.x_offset = self.grid_side_len /2
                #使棋盘保持在y轴中间,宽高差的一半 - 格子的1半 （X轴比Y轴少一个格子）
                self.y_offset = (self.height - self.width) /2
            else:
                #print(f"Chessboard2 取棋盘{self.height=}的11等分作为格子的边长")
                self.grid_side_len = self.height / 11
                self.y_offset = 0
                #使棋盘保持在y轴中间,宽高差的一半 + 格子的1半 （X轴比Y轴少一个格子）
                self.x_offset = (self.width - self.height) /2 + self.grid_side_len /2

            
            #print(f"Chessboard2 {self.grid_side_len=},{self.x_offset=},{self.y_offset=}")

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
            
            for i in range(1,10,1):
                #红方
                MDLabel(text=str(10-i),font_style="Overline",center=(self.x_offset+self.grid_side_len*i+48,self.y_offset+10),theme_text_color="Custom",text_color=(0.5,0.5,0.5,0.5))
                #黑方
                MDLabel(text=str(i),font_style="Overline",center=(self.x_offset+self.grid_side_len*i+48,self.y_offset+self.grid_side_len*10+22),theme_text_color="Custom",text_color=(0.5,0.5,0.5,0.5))
            
            self.selectedmask = SelectedMaskWidget2(size_hint=(None,None),center=[self.width/2,self.height/2])
            
            async def onebyone(self):
                svg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'img')
                for i in range(0,32,1):
                    if i < 16:#红方棋子
                        if i < 8:#第一排
                            x = self.x_offset + self.grid_side_len * (i+1) + self.grid_side_len/2
                            y = self.y_offset - self.grid_side_len / 2
                        else:
                            x = self.x_offset + self.grid_side_len * (i+1-8) + self.grid_side_len/2
                            y = self.y_offset - self.grid_side_len*3/2
                        p = Piece('w',g_const_S_P_ORDEER[i],x,y)
                    else: #黑方棋子
                        if i < 24:#第一排
                            x = self.x_offset + self.grid_side_len * (i+1-16) + self.grid_side_len/2
                            y = self.y_offset - self.grid_side_len / 2 + self.grid_side_len * 13
                        else:
                            x = self.x_offset + self.grid_side_len * (i+1-8-16) + self.grid_side_len/2
                            y = self.y_offset - self.grid_side_len*3/2 + self.grid_side_len * 13
                        p = Piece('b',g_const_S_P_ORDEER[i],x,y)
                    
                    pw = PieceWidget2(svg_fn=os.path.join(f'{svg_path}',f'{p.camp}{p.identifier}.svg'),camp=p.camp,identifier=p.identifier,bx=p.x,by=p.y,
                                            size_hint=(None,None),center=[p.x,p.y])

                    self.add_widget(pw)

                    #await asynckivy.sleep(1)
            
            asynckivy.start(onebyone(self))
    
    def on_touch_up(self, touch):
        #print("Chessboard2.on_touch_up begin")
        ret = super(MDRelativeLayout, self).on_touch_up(touch)

        if self.collide_point(*touch.pos):
            if self.selected_piece != None:
                #print(f"{self.selected_piece.camp=},{self.selected_piece.identifier=},{self.selected_piece.bx=},{self.selected_piece.by=}")
                
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
                bFnd = False
                for x in range(0,9,1):
                    for y in range(0,10,1):
                        #print(f"网点：({x},{y})")
                        leftx = self.x_offset + self.grid_side_len * (x+1) - self.grid_side_len / 3
                        rightx = self.x_offset + self.grid_side_len * (x+1) + self.grid_side_len / 3
                        boty = self.y_offset + self.grid_side_len * (y+1) - self.grid_side_len / 3
                        topy = self.y_offset + self.grid_side_len * (y+1) + self.grid_side_len / 3

                        if (tx > leftx) and (tx < rightx) and (ty > boty) and (ty < topy):
                            bFnd = True
                            #print(f"中标：{x},{y}")
                            #print(f"{leftx=},{rightx=},{boty=},{topy=}")
                            #print(f"{touch.pos[0]=},{touch.pos[1]=}")
                            self.selected_piece.movexy(x,y,'F')
                
                if bFnd == False:
                    #将棋子移回初始位置
                    self.selected_piece.movexy(0,0,'B')
        
        #print("Chessboard2.on_touch_up end")
        
        # 最后就是返回结果了
        return ret
                
