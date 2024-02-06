'''
Author: Paoger
Date: 2023-12-16 18:43:36
LastEditors: Paoger
LastEditTime: 2023-12-18 17:08:38
Description: 

Copyright (c) 2023 by Paoger, All Rights Reserved. 
'''
from kivymd.app import MDApp

from piecewidget2 import PieceWidget2
from global_var import g_const_S_P_ORDEER

def edit_situation_clear():
    #print("******edit_situation_clear begin******")
    app = MDApp.get_running_app()
    #候选棋子集归位
    for child in app.root.ids['id_screditsituiation'].ids.id_chessboard2.children[:]:
        if isinstance(child,PieceWidget2) and child.bx != child.old_x and child.by != child.old_y:
            child.movexy(0,0,'B')
    #print("******edit_situation_clear end******")

def edit_situation_full():
    print("******edit_situation_full begin******")
    app = MDApp.get_running_app()
    #先归位
    edit_situation_clear()

    childs = []
    for child in app.root.ids['id_screditsituiation'].ids.id_chessboard2.children[:]:
        if isinstance(child,PieceWidget2) :
            childs.append(child)

    full_situation='000a141e28323c46500c4803172b3f5309131d27313b454f59114d061a2e4256'
    for i in range(0,32,1):
        #print(f'{i=}')
        if i < 16:#红                
            for item in childs:
                #print(f"{item}")
                if item.camp == 'w' and item.identifier == g_const_S_P_ORDEER[i]:
                    #棋子到达位置
                    endxy = full_situation[i*2:i*2+2]
                    #print(f"{endxy=}")
                    exy = int(endxy,16)
                    ex = exy // 10
                    ey = exy % 10
                    #print(f"{ex=},{ey=}")

                    item.movexy(ex,ey,'F')

                    childs.remove(item)#从列表中删除
                    break
        else :#黑
            for item in childs:
                #print(f"{item}")
                if item.camp == 'b' and item.identifier == g_const_S_P_ORDEER[i]:
                    #棋子到达位置
                    endxy = full_situation[i*2:i*2+2]
                    #print(f"{endxy=}")
                    exy = int(endxy,16)
                    ex = exy // 10
                    ey = exy % 10
                    #print(f"{ex=},{ey=}")

                    item.movexy(ex,ey,'F')

                    childs.remove(item)#从列表中删除
                    break


    print("******edit_situation_full end******")

def edit_situation_cancle():
    #print("******edit_situation_cancle begin******")
    app = MDApp.get_running_app()
    app.root.current_heroes = ""
    app.root.current = "screenMain"
    #print("******edit_situation_cancle end******")
