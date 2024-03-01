'''
Author: Paoger
Date: 2023-11-27 10:12:51
LastEditors: Paoger
LastEditTime: 2024-02-06 16:39:48
Description: 

Copyright (c) 2023 by Paoger, All Rights Reserved. 
'''
import os

from kivy.graphics import *
from kivy.utils import platform
from kivy.logger import Logger
from kivy.clock import Clock
from functools import partial

from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.label import MDLabel
from kivymd.utils import asynckivy



from arrowline import Arrowline,AIArrowline

from global_var import g_const_INIT_SITUATION,g_const_S_P_ORDEER
from situation import init_g_init_situation,xqfinit2xchessinit,print_situation,check_situation

from selectedmaskwidget import SelectedMaskWidget
from piece import Piece
from piecewidget import PieceWidget

class Chessboard(MDRelativeLayout):
    #红下黑上：棋盘显示坐标与棋盘系统坐标一致，不存在转换
    #红上黑下：棋盘翻转后，棋盘显示坐标原点依然是左下角，但棋盘系统坐标的原点变成右上角，因此存在棋盘显示坐标与棋盘系统坐标的转换
    red_bottom = True

    grid_side_len = 0
    x_offset = 0
    y_offset = 0

    arrows = []
    aiarrows = []

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
        #with self.canvas.before:
        with self.canvas:
        #with self.canvas.after:
            self.canvas.clear()
            #self.opacity = 0
            Color(0,0,0,1)#黑色
            #Color(0.5,0.5,0.5,1)#灰色
            #Color(.1,.5,1,1)#蓝色
            #Color(.9,.9,1,0.5)#浅灰
            #Rectangle(pos=(0,0),size=self.size)
            print(f"Chessboard {self.width=},{self.height=}")
            #将最短边11等分，作为网格的边长
            #self.width x轴，self.height y轴
            if self.height > self.width:
                print(f"Chessboard 取棋盘{self.width=}的11等分作为格子的边长")
                Logger.info(f"Chessboard 取棋盘{self.width=}的11等分作为格子的边长")
                self.grid_side_len = self.width / 10
                self.x_offset = 0#self.grid_side_len * 1 / 2
                #self.x_offset = 0
                #使棋盘保持在y轴中间,宽高差的一半 - 格子的1半 （X轴比Y轴少一个格子）
                #1/2的话，分屏和大屏时最上面的棋子显示有遮挡，所以，改成1/4
                self.y_offset = (self.height - self.width) / 2
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
                         self.grid_side_len*9+self.x_offset,self.grid_side_len*(y+1)+self.y_offset],width=1.05)

            #x0
            Line(points=[self.grid_side_len*1+self.x_offset,self.grid_side_len*1+self.y_offset,
                         self.grid_side_len*1+self.x_offset,self.grid_side_len*10+self.y_offset],width=1.05)
            for x in range(1,8,1):#x坐标
                #x-1
                Line(points=[self.grid_side_len*(x+1)+self.x_offset,self.grid_side_len*1+self.y_offset,
                            self.grid_side_len*(x+1)+self.x_offset,self.grid_side_len*5+self.y_offset],width=1.05)
                #x-2
                Line(points=[self.grid_side_len*(x+1)+self.x_offset,self.grid_side_len*6+self.y_offset,
                            self.grid_side_len*(x+1)+self.x_offset,self.grid_side_len*10+self.y_offset],width=1.05)
            
            #x8
            Line(points=[self.grid_side_len*9+self.x_offset,self.grid_side_len*1+self.y_offset,
                        self.grid_side_len*9+self.x_offset,self.grid_side_len*10+self.y_offset],width=1.05)
            
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
            
            #MDLabel(text="9",font_style="Overline",center=(self.x_offset+self.grid_side_len*1+48,self.y_offset+self.grid_side_len*0.2),theme_text_color="Custom",text_color=(0,0,0,0.8))
            #MDLabel(text="8",font_style="Overline",center=(self.x_offset+self.grid_side_len*2+48,self.y_offset+self.grid_side_len*0.2),theme_text_color="Custom",text_color=(0,0,0,0.8))
            #MDLabel(text="7",font_style="Overline",center=(self.x_offset+self.grid_side_len*3+48,self.y_offset+self.grid_side_len*0.2),theme_text_color="Custom",text_color=(0,0,0,0.8))
            #MDLabel(text="6",font_style="Overline",center=(self.x_offset+self.grid_side_len*4+48,self.y_offset+self.grid_side_len*0.2),theme_text_color="Custom",text_color=(0,0,0,0.8))
            #MDLabel(text="5",font_style="Overline",center=(self.x_offset+self.grid_side_len*5+48,self.y_offset+self.grid_side_len*0.2),theme_text_color="Custom",text_color=(0,0,0,0.8))
            #MDLabel(text="4",font_style="Overline",center=(self.x_offset+self.grid_side_len*6+48,self.y_offset+self.grid_side_len*0.2),theme_text_color="Custom",text_color=(0,0,0,0.8))
            #MDLabel(text="3",font_style="Overline",center=(self.x_offset+self.grid_side_len*7+48,self.y_offset+self.grid_side_len*0.2),theme_text_color="Custom",text_color=(0,0,0,0.8))
            #MDLabel(text="2",font_style="Overline",center=(self.x_offset+self.grid_side_len*8+48,self.y_offset+self.grid_side_len*0.2),theme_text_color="Custom",text_color=(0,0,0,0.8))
            #MDLabel(text="1",font_style="Overline",center=(self.x_offset+self.grid_side_len*9+48,self.y_offset+self.grid_side_len*0.2),theme_text_color="Custom",text_color=(0,0,0,0.8))

            #MDLabel(text="1",font_style="Overline",center=(self.x_offset+self.grid_side_len*1+48,self.y_offset+self.grid_side_len*10.8),theme_text_color="Custom",text_color=(0,0,0,0.8))
            #MDLabel(text="2",font_style="Overline",center=(self.x_offset+self.grid_side_len*2+48,self.y_offset+self.grid_side_len*10.8),theme_text_color="Custom",text_color=(0,0,0,0.8))
            #MDLabel(text="3",font_style="Overline",center=(self.x_offset+self.grid_side_len*3+48,self.y_offset+self.grid_side_len*10.8),theme_text_color="Custom",text_color=(0,0,0,0.8))
            #MDLabel(text="4",font_style="Overline",center=(self.x_offset+self.grid_side_len*4+48,self.y_offset+self.grid_side_len*10.8),theme_text_color="Custom",text_color=(0,0,0,0.8))
            #MDLabel(text="5",font_style="Overline",center=(self.x_offset+self.grid_side_len*5+48,self.y_offset+self.grid_side_len*10.8),theme_text_color="Custom",text_color=(0,0,0,0.8))
            #MDLabel(text="6",font_style="Overline",center=(self.x_offset+self.grid_side_len*6+48,self.y_offset+self.grid_side_len*10.8),theme_text_color="Custom",text_color=(0,0,0,0.8))
            #MDLabel(text="7",font_style="Overline",center=(self.x_offset+self.grid_side_len*7+48,self.y_offset+self.grid_side_len*10.8),theme_text_color="Custom",text_color=(0,0,0,0.8))
            #MDLabel(text="8",font_style="Overline",center=(self.x_offset+self.grid_side_len*8+48,self.y_offset+self.grid_side_len*10.8),theme_text_color="Custom",text_color=(0,0,0,0.8))
            #MDLabel(text="9",font_style="Overline",center=(self.x_offset+self.grid_side_len*9+48,self.y_offset+self.grid_side_len*10.8),theme_text_color="Custom",text_color=(0,0,0,0.8))
            
        #延迟一会，让界面有所反应后，再绘制棋子，避免黑屏
        Clock.schedule_once(self.draw_full_piece,0.2)

        #app = MDApp.get_running_app()
        #if app.selectedmask1 is not None:
        #    Logger.debug("X-Chess X-Chessboard update_canvas: app.selectedmask1 is not None,先破再立")
        #    #cen = app.selectedmask1.center
        #    #self.remove_widget(app.selectedmask1)
        #    #pw = SelectedMaskWidget(size_hint=(None,None),center=cen)
        #    #self.add_widget(pw)
        #    #app.selectedmask1 = pw
        #    pw = app.selectedmask1
        #    pw.center = [self.width/2,self.height/2]
        #    pw.auto_bring_to_front = True
        #    pw.scale = 0.5
        #    #pw._bring_to_front()
        #else:
        #    pw = SelectedMaskWidget(size_hint=(None,None),center=[self.width/2,self.height/2])
        #    self.add_widget(pw)
        #iCnt = 0
        #for child in self.children[:]:
        #    if isinstance(child,SelectedMaskWidget):
        #        iCnt = iCnt + 1
        #Logger.debug(f"X-Chess X-Chessboard update_canvas:{iCnt=}")
            
    #摆满棋子
    def draw_full_piece(self,dt=None):
        Logger.debug("X-Chess X-Chessboard draw_full_piece:******draw_full_piece begin******")

        app = MDApp.get_running_app()

        bHadPiece = False
        for child in self.children[:]:
            if isinstance(child,PieceWidget):#只要找到1个就认为有了
                bHadPiece = True
                break
        
        if bHadPiece == False:
            Logger.debug("X-Chess X-Chessboard draw_full_piece:绘制棋子")

            #清空棋盘,包括棋子和跟随框
            for child in self.children[:]:
                self.remove_widget(child)

            #app.selectedmask1 = SelectedMaskWidget(size_hint=(None,None),center=[self.width/2,self.height/2])
            app.selectedmask1 = SelectedMaskWidget(size_hint=(None,None),center=[-1000,-1000])
            self.add_widget(app.selectedmask1)

            #app.selectedmask2 = SelectedMaskWidget(size_hint=(None,None),center=[self.width/2,self.height/2])
            app.selectedmask2 = SelectedMaskWidget(size_hint=(None,None),center=[-1000,-1000])
            self.add_widget(app.selectedmask2)

            #svg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'img')
            pieceimg = app.cfg_info['UI']['pieceimg']
            Logger.debug(f'X-Chess X_ChessApp build: {pieceimg=}')
            if pieceimg == 'DIY':
                if platform != 'android':
                    svg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'img')
                else:
                    from android.storage import primary_external_storage_path
                    SD_CARD = primary_external_storage_path()
                    svg_path = os.path.join(SD_CARD,'X-Chess/img')                
            else:
                svg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'img')
            
            Logger.debug(f'X-Chess X_ChessApp build: {svg_path=}')

            async def onebyone(self):
                app.root.ids['id_screenmain'].disabled = True

                #休息下让界面有所反应
                await asynckivy.sleep(0.2)

                #遍历下棋盘
                for y in range(0,10,1):
                    for x in range(0,9,1):
                        if (f"{x},{y}" in g_const_INIT_SITUATION):
                            p = g_const_INIT_SITUATION[f'{x},{y}']
                            if p == None:
                                continue
                            if not isinstance(p,Piece):
                                continue
                            """ if p.camp == None:
                                continue """

                            cx = self.x_offset + self.grid_side_len * (x+1)
                            cy = self.y_offset + self.grid_side_len * (y+1)
                                                    
                            pw = PieceWidget(svg_fn=os.path.join(f'{svg_path}',f'{p.camp}{p.identifier}.svg'),
                                            camp=p.camp,identifier=p.identifier,bx=p.x,by=p.y,size_hint=(None,None),center=[cx,cy])
                            
                            #Logger.debug(f"X-Chess X-Chessboard draw_full_piece:{pw.camp=},{pw.identifier=},{pw.bx=},{pw.by=},{pw.board_x=},{pw.board_y=}")
                            
                            p.pieceWidget = pw
                            
                            self.add_widget(pw)

                            g_const_INIT_SITUATION[f'{x},{y}'] = p
                        #else:
                        #    print(f"网点：({x},{y}),棋子：None")
                        
                        #break
                    #break
                    await asynckivy.sleep(0.1)
                #for 循环结束
                app.root.ids['id_screenmain'].disabled = False
            #end onebyone        
                
            asynckivy.start(onebyone(self))
        else:#棋子已经有了,先破后立，否则棋子不显示
            Logger.debug("X-Chess X-Chessboard draw_full_piece:移动棋子")
            childs = []
            for child in self.children[:]:
                childs.append(child)
            
            for child in childs:
                if isinstance(child,SelectedMaskWidget):
                    self.remove_widget(app.selectedmask1)
                    app.selectedmask1.scale = (self.grid_side_len * 2 / 5) * ( 2 / child.size[0])
                    app.selectedmask1.center=[-1000,-1000]
                    #pw = SelectedMaskWidget(size_hint=(None,None),center=[self.width/2,self.height/2])
                    self.add_widget(app.selectedmask1)
                    #app.selectedmask1 = pw
                    #self.remove_widget(app.selectedmask2)
                    self.remove_widget(app.selectedmask2)
                    app.selectedmask2.scale = (self.grid_side_len * 2 / 5) * ( 2 / child.size[0])
                    app.selectedmask2.center=[-1000,-1000]
                    self.add_widget(app.selectedmask2)
                elif isinstance(child,PieceWidget):
                    self.remove_widget(child)
                    #使棋子宽度的1/2 等于 网格边长的 2.35/5
                    child.scale = (self.grid_side_len * 2.35 / 5) * ( 2 / child.size[0])
                    cx = self.x_offset + self.grid_side_len * (child.board_x+1)
                    cy = self.y_offset + self.grid_side_len * (child.board_y+1)
                    child.center=[cx,cy]                    
                    self.add_widget(child)

        Logger.debug("X-Chess X-Chessboard:******draw_full_piece end******")
    
    #根据初始局面，按谱就位
    def piece_by_chessmanual(self):
        Logger.debug("X-Chess X-Chessboard:******piece_by_chessmanual begin******")

        self.remove_Allarrows()

        i = 0
        for child in self.children[:]:
            #跟随框就位
            if isinstance(child,SelectedMaskWidget):
                #child.center_x = self.width/2
                #child.center_y = self.height/2
                child.center_x = -1000
                child.center_y = -1000
            elif isinstance(child,PieceWidget):
                child.center_x = -1000
                child.center_y = -1000
                child.bx = -1000
                child.by = -1000
                child.board_x = -1000
                child.board_y = -1000
                i = i + 1
        
        Logger.debug(f"X-Chess X-Chessboard:共{i}个棋子已清空，开始摆子")
        
        i=0
        for y in range(0,10,1):
            for x in range(0,9,1):
                if (f"{x},{y}" in g_const_INIT_SITUATION):
                    p = g_const_INIT_SITUATION[f'{x},{y}']
                    if p == None:
                        continue
                    if not isinstance(p,Piece):
                        continue

                    #Logger.debug(f"X-Chess X-Chessboard:{y=},{x=},p:{p}")

                    cx = self.x_offset + self.grid_side_len * (x+1)
                    cy = self.y_offset + self.grid_side_len * (y+1)
                                                
                    #pw = PieceWidget(svg_fn=os.path.join(f'{svg_path}',f'{p.camp}{p.identifier}.svg'),
                    #                     camp=p.camp,identifier=p.identifier,bx=p.x,by=p.y,size_hint=(None,None),center=[cx,cy])

                    pw=None
                    for child in self.children[:]:
                        if isinstance(child,PieceWidget):
                            if child.bx != -1000:#已经摆上棋盘了
                                continue
                            if child.camp == p.camp and child.identifier == p.identifier:
                                child.center=[cx,cy]
                                child.bx = p.x
                                child.by = p.y
                                child.board_x = p.x
                                child.board_y = p.y
                                pw = child
                                
                                Logger.debug(f"X-Chess X-Chessboard draw_full_piece:{pw.camp=},{pw.identifier=},{pw.bx=},{pw.by=},{pw.board_x=},{pw.board_y=}")
                                
                                i = i + 1
                                break
                    if pw == None:
                        Logger.debug(f"X-Chess X-Chessboard:{y=},{x=},p:{p},没有找到对应的棋子")

                    p.pieceWidget = pw
                    g_const_INIT_SITUATION[f'{x},{y}'] = p

                #else:
                #    print(f"网点：({x},{y}),棋子：None")                    
                #break
            #break
        #for 循环结束
        Logger.debug(f"X-Chess X-Chessboard:棋盘已摆好{i}个棋子，请享用！")

        Logger.debug("X-Chess X-Chessboard:******piece_by_chessmanual end******")
    
    def remove_Allarrows(self):
        for i in self.arrows:
            self.remove_widget(i)
        self.arrows.clear()
    
    def remove_AllAIarrows(self):
        for i in self.aiarrows:
            self.remove_widget(i)
        self.aiarrows.clear()
    
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
        self.aiarrows.append(ar)
    
    def on_touch_up(self, touch):
        #Logger.debug(f"X-Chess Chessboard on_touch_up:begin")

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

                Logger.debug(f"X-Chess Chessboard on_touch_up:{tx=},{ty=}")

                #距离网格点2.2/5处均视为该网点有效范围内
                #遍历下棋盘
                bFndBoardXY = False
                for x in range(0,9,1):
                    for y in range(0,10,1):
                        #print(f"网点：({x},{y})")
                        leftx = self.x_offset + self.grid_side_len * (x+1) - self.grid_side_len * (2.2 / 5)
                        rightx = self.x_offset + self.grid_side_len * (x+1) + self.grid_side_len * (2.2 / 5)
                        boty = self.y_offset + self.grid_side_len * (y+1) - self.grid_side_len * (2.2 / 5)
                        topy = self.y_offset + self.grid_side_len * (y+1) + self.grid_side_len * (2.2 / 5)
                        if (tx > leftx) and (tx < rightx) and (ty > boty) and (ty < topy):
                            Logger.debug(f"X-Chess Chessboard on_touch_up:中标 {x=},{y=}")
                            Logger.debug(f"X-Chess Chessboard on_touch_up:{leftx=},{rightx=},{boty=},{boty=}")

                            bFndBoardXY = True
                            board_x = x
                            board_y = y
                            Logger.debug(f"X-Chess Chessboard on_touch_up:{board_x=},{board_y=}")                            
                            break
                    #end for y
                    if bFndBoardXY == True:
                        break
                #end for x
                if bFndBoardXY == True:
                    #letsgo棋盘显示坐标
                    app.selected_piece.letsgo(board_x,board_y)
        
        #Logger.debug(f"X-Chess Chessboard on_touch_up:end")
        
        # 最后就是返回结果了
        return ret
    
    def bottom2top(self,curSit):
        Logger.debug("X-Chess Chessboard bottom2top:begin")

        for y in range(0,10,1):
            for x in range(0,9,1):
                if (f"{x},{y}" in curSit) and (isinstance(curSit[f'{x},{y}'],Piece)):
                    pw = curSit[f'{x},{y}'].pieceWidget
                    if pw :
                        pw.board_x = abs(pw.board_x-8)
                        pw.board_y = abs(pw.board_y-9)
                        cx = self.x_offset + self.grid_side_len * (pw.board_x+1)
                        cy = self.y_offset + self.grid_side_len * (pw.board_y+1)
                        pw.center = [cx,cy]
        
        #移动跟随框
        app = MDApp.get_running_app()
        app.selectedmask1.center = [-1000,-1000]
        app.selectedmask2.center = [-1000,-1000]

        #示意线
        self.remove_Allarrows()
        self.remove_AllAIarrows()

        Logger.debug("X-Chess Chessboard bottom2top:end")
        


