'''
Author: Paoger
Date: 2024-01-01 13:15:58
LastEditors: Paoger
LastEditTime: 2024-01-22 17:21:18
Description: 

Copyright (c) 2024 by Paoger, All Rights Reserved. 
'''
from XQlightPy.position import Position
from XQlightPy.search import Search
from XQlightPy.cchess import move2Iccs,Iccs2move
import numpy as np
import datetime

from kivy.logger import Logger
from kivymd.app import MDApp
from kivymd.toast import toast

from situation import print_situation,sit2Fen

uni_pieces = {4+8:'车', 3+8:'马', 2+8:'相', 1+8:'仕', 0+8:'帅', 6+8:'兵', 5+8:'炮',
                  4+16:'俥', 3+16:'傌', 2+16:'象', 1+16:'士', 0+16:'将', 6+16:'卒', 5+16:'砲', 0:'．'}

def print_board(pos):
    print()
    Logger.debug(f'')
    for i, row in enumerate(np.asarray(pos.squares).reshape(16,16)[3:3+10,3:3+9]):
        print(' ', 9 - i, ''.join(uni_pieces.get(p, p) for p in row))
    print('    ａｂｃｄｅｆｇｈｉ\n\n')

def XQlight_moves(node,nextCamp):
    Logger.debug(f'X-Chess XQlight_moves: begin')

    aimove = []

    app = MDApp.get_running_app()
    app.root.ids['id_screenmain'].ids['id_movesnote_input'].text = ""

    """ pos = Position()
    #初始局面 rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1CC6/9/RNBAKABNR b
    #该红方走棋 rnbakab1r/9/1c4nc1/p1p1p1p1p/9/9/P1P1P1P1P/1CC6/9/RNBAKABNR w
    initFen = 'rnbakab1r/9/1c4nc1/p1p1p1p1p/9/9/P1P1P1P1P/1CC6/9/RNBAKABNR w'
    print(f'初始局面00==》{initFen}')
    pos.fromFen(initFen)
    print_board(pos)

    print("AI思考5秒中……")
    # 电脑下棋
    search_time_ms = 10000
    search = Search(pos, 16)
    mov = search.searchMain(64, search_time_ms) # 搜索3秒钟
    print(f"{mov},{mov=}")
    print(f'{move2Iccs(mov).replace("-","").lower()}')
    pos.makeMove(mov)
    print(f'电脑走棋后==》{pos.toFen()}')
    print_board(pos) """

    xqfPos = node.data['situation']
    #print_situation("XQF situation",xqfPos)

    curFen = sit2Fen(xqfPos)    
    curFen = f'{curFen} {nextCamp}' #注意用空格隔开，“b”表示黑方，除此以外都表示红方
    print(f'局面00==》{curFen}')

    pos = Position()
    pos.fromFen(curFen)
    print_board(pos)

    winner = pos.winner()
    if winner is not None:
        if winner == 0:
            Logger.debug(f'X-Chess XQlight_moves:红方胜利！行棋结束')
            app.root.ids['id_screenmain'].ids['id_movesnote_input'].text = f'胜负已定'
            app.gameover = True
            return aimove
        elif winner == 1:
            Logger.debug(f'X-Chess XQlight_moves:黑方方胜利！行棋结束')
            app.root.ids['id_screenmain'].ids['id_movesnote_input'].text = f'胜负已定'
            app.gameover = True
            return aimove
        elif winner == 2:
            Logger.debug(f'X-Chess XQlight_moves:和棋')
            app.root.ids['id_screenmain'].ids['id_movesnote_input'].text = f'大概率和棋'

    search_time_ms = 5000
    search = Search(pos, 16)

    Logger.debug(f'X-Chess XQlight_moves:{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} 开始思考{search_time_ms/1000}秒')
    #print("AI思考5秒中……")
    # 电脑下棋
    
    mov = search.searchMain(64, search_time_ms) # 搜索3秒钟

    Logger.debug(f'X-Chess XQlight_moves:{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} 结束思考')

    #print(f"{mov},{mov=}")
    #print(f'{move2Iccs(mov).replace("-","").lower()}')

    #起止点XY坐标
    sexy = move2Iccs(mov).replace("-","").lower()
    #print(f'111 {sexy=}')
    sexy = sexy.replace('a','0')
    sexy = sexy.replace('b','1')
    sexy = sexy.replace('c','2')
    sexy = sexy.replace('d','3')
    sexy = sexy.replace('e','4')
    sexy = sexy.replace('f','5')
    sexy = sexy.replace('g','6')
    sexy = sexy.replace('h','7')
    sexy = sexy.replace('i','8')
    #print(f'222 {sexy=}')

    pos.makeMove(mov)
    print(f'电脑走棋后==》{pos.toFen()}')
    print_board(pos) 

    se = list(sexy)
    for item in se:
        aimove.append(int(item))
    
    Logger.debug(f'X-Chess XQlight_moves: end')

    return aimove