'''
Author: Paoger
Date: 2023-11-30 09:57:29
LastEditors: Paoger
LastEditTime: 2024-01-01 15:04:20
Description: 

Copyright (c) 2023 by Paoger, All Rights Reserved. 
'''
from kivy.logger import Logger
from kivymd.toast import toast

from global_var import g_const_S_P_ORDEER,g_const_INIT_SITUATION

from piece import Piece

#初始化全局变量g_init_situation
def init_g_init_situation(init_s):
    global g_const_INIT_SITUATION
    #清空，不要用={}
    g_const_INIT_SITUATION.clear()

    print("init_g_init_situation begin")

    for i in range(0,32,1):
        #print(f"{i=}")
        xy = int(init_s[i*2:(i+1)*2],16)
        #print(f"{xy=}")
        #p = Piece(None,None,None,None)
        p = None
        if xy != 255:#255 0xff 无子
            x = xy // 10
            y = xy % 10
            #print(f"{x=},{y=}")
            if i < 16:#红方棋子
                p = Piece('r',g_const_S_P_ORDEER[i],x,y)
            else: #黑方棋子
                p = Piece('b',g_const_S_P_ORDEER[i],x,y)
            g_const_INIT_SITUATION[f'{x},{y}'] = p
    
    print_situation("******初始局面******",g_const_INIT_SITUATION)

    print("init_g_init_situation end")

#将初始化字符串转换为局面变量
def xqfinit2xchessinit(init_s,xchess_init):
    #清空，不要用={}
    xchess_init.clear()

    #print("xqfinit2xchessinit begin")

    for i in range(0,32,1):
        #print(f"{i=}")
        xy = int(init_s[i*2:(i+1)*2],16)
        #print(f"{xy=}")
        #p = Piece(None,None,None,None)
        p = None
        if xy != 255:#255 0xff 无子
            x = xy // 10
            y = xy % 10
            #print(f"{x=},{y=}")
            if i < 16:#红方棋子
                p = Piece('r',g_const_S_P_ORDEER[i],x,y)
            else: #黑方棋子
                p = Piece('b',g_const_S_P_ORDEER[i],x,y)
            xchess_init[f'{x},{y}'] = p
    
    #print_situation("******xchess局面******",xchess_init)

    #print("xqfinit2xchessinit end")


#打印局面
def print_situation(des,sit):
    Logger.info(des)
    for y in range(9,-1,-1):
        str = ""
        for x in range(0,9,1):
            if f"{x},{y}" in sit:
                p = sit[f'{x},{y}']
                #if isinstance(p,Piece):
                if p:
                    #print(f"网点：({x},{y}),棋子：{p.camp=},{p.identifier=},{p.x=},{p.y=},{p.pieceWidget=}")
                    if x == 0:
                        str = f"{p.camp}{p.identifier:-<8}"
                    else:
                        str = f"{str}{p.camp}{p.identifier:-<8}"
                else:
                    if x == 0:
                        str = f"{'x':-<9}"
                    else:
                        str = f"{str}{'x':-<9}"
            else:
                if x == 0:
                    str = f"{'x':-<9}"
                else:
                    str = f"{str}{'x':-<9}"
        Logger.info(str)

#检查棋盘局面
def check_situation(init_s):
    rst = {'result_code':True,'result_desc':'疑罪从无或者检查无误'}

    
    #检查同一位置是否有多个棋子
    #key:f'{x},{y}' value:{Piece}，不需要，一个key只有1个值

    #检查各棋子是否在合理的位置上
    for y in range(0,10,1):
        for x in range(0,9,1):
            #if (f"{x},{y}" in init_s) and (isinstance(init_s[f'{x},{y}'],Piece)):
            if (f"{x},{y}" in init_s) and (init_s[f'{x},{y}']):
                p = init_s[f'{x},{y}']
                #红下黑上，暂无实现翻转
                if p.camp == 'r':#红方
                    if p.identifier == 'shuai':
                        if p.x < 3 or p.x > 5 or p.y < 0 or p.y > 2:
                            rst['result_code'] = False
                            rst['result_desc'] = f'帅{p.camp=},{p.identifier=}不在其位((3,0) to (5,2)):{p.x=},{p.y}'
                            return rst
                    elif p.identifier == 'shi':
                        if not ((p.x == 3 and p.y == 0) or (p.x == 5 and p.y == 0) or (p.x == 4 and p.y == 1) or (p.x == 3 and p.y == 2) or (p.x == 5 and p.y == 2)):
                            rst['result_code'] = False
                            rst['result_desc'] = f'仕{p.camp=},{p.identifier=}不在其位:{p.x=},{p.y}'
                            return rst
                    elif p.identifier == 'xiang':
                        if not ((p.x == 2 and p.y == 0) or (p.x == 6 and p.y == 0) or (p.x == 4 and p.y == 2) or (p.x == 2 and p.y == 4) or (p.x == 6 and p.y == 4)):
                            rst['result_code'] = False
                            rst['result_desc'] = f'相{p.camp=},{p.identifier=}不在其位:{p.x=},{p.y}'
                            return rst
                    elif p.identifier == 'bing':#兵不能在后方，或兵在己方横走
                        if p.y < 3 or (p.y == 3 and (p.x == 1 or p.x == 3 or p.x == 5 or p.x == 7)) or (p.y == 4 and (p.x == 1 or p.x == 3 or p.x == 5 or p.x == 7)):
                            rst['result_code'] = False
                            rst['result_desc'] = f'兵{p.camp=},{p.identifier=}不在其位:{p.x=},{p.y}'
                            return rst
                elif p.camp == 'b':#黑方
                    if p.identifier == 'shuai':
                        if p.x < 3 or p.x > 5 or p.y < 7 or p.y > 9:
                            rst['result_code'] = False
                            rst['result_desc'] = f'将{p.camp=},{p.identifier=}不在其位((3,7) to (5,9)):{p.x=},{p.y}'
                            return rst
                    elif p.identifier == 'shi':
                        if not ((p.x == 3 and p.y == 9) or (p.x == 5 and p.y == 9) or (p.x == 4 and p.y == 8) or (p.x == 3 and p.y == 7) or (p.x == 5 and p.y == 7)):
                            rst['result_code'] = False
                            rst['result_desc'] = f'士{p.camp=},{p.identifier=}不在其位:{p.x=},{p.y}'
                            return rst
                    elif p.identifier == 'xiang':
                        if not ((p.x == 2 and p.y == 9) or (p.x == 6 and p.y == 9) or (p.x == 4 and p.y == 7) or (p.x == 2 and p.y == 5) or (p.x == 6 and p.y == 5)):
                            rst['result_code'] = False
                            rst['result_desc'] = f'象{p.camp=},{p.identifier=}不在其位:{p.x=},{p.y}'
                            return rst
                    elif p.identifier == 'bing':#兵不能在后方，或兵在己方横走
                        if p.y > 6 or (p.y == 6 and (p.x == 1 or p.x == 3 or p.x == 5 or p.x == 7)) or (p.y == 5 and (p.x == 1 or p.x == 3 or p.x == 5 or p.x == 7)):
                            rst['result_code'] = False
                            rst['result_desc'] = f'卒{p.camp=},{p.identifier=}不在其位:{p.x=},{p.y}'
                            return rst
                else:
                    rst['result_code'] = False
                    rst['result_desc'] = f'旗帜要鲜明(r or b):{p.camp=}'
                    return rst

    return rst

#转换为Fen记谱法
"rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w - - 0 1"
"""
中国象棋没有“王车易位”和“吃过路兵”的着法，所以FEN格式串的这两项空缺以最初局面为例说明:
             rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w - - 0 1
r:黑车 n:黑马 b:黑象 a:黑士 k:黑将 c:黑炮 p:卒
R:红车 N:红马 B:红象 A:红士 K:红将 C:红炮 P:兵
上述局面如下
  9 俥傌象士将士象傌俥      ==》从左至右 ：rnbakabnr
  8 ．．．．．．．．．      ==》9个空子  ：9
  7 ．砲．．．．．砲．      ==>         ：1c5c1
  6 卒．卒．卒．卒．卒
  5 ．．．．．．．．．
  4 ．．．．．．．．．
  3 兵．兵．兵．兵．兵
  2 ．炮．．．．．炮．
  1 ．．．．．．．．．
  0 车马相仕帅仕相马车
    ａｂｃｄｅｆｇｈｉ

(1)表示棋盘布局，小写表示黑方，大写表示红方，其他规则同国际象棋的 FEN 规范。
这里要注意两点，一是中国象棋棋盘有 10行，所以要用9个“/”把每一行隔开;二是棋子名称用英文字母表示，国际象棋中没有的棋子是仕(士)和炮，这里分别用字母 A(a)和
C(c)表示。
(2)表示轮到哪一方走子，“w”表示红方，“b”表示黑方。(有人认为红方应该用“r”表示，很多象棋软件确实是这样表示的。ElephantBoard 尽管用“w
表示，但识别时采取灵活的办法，即“b”表示黑方，除此以外都表示红方。)
(3)空缺，始终用“-”表示
(4)空缺，始终用“-”表示。
(5)表示双方没有吃子的走棋步数(半回合数)，通常该值达到 120就要判和(六十回合自然限着)，一旦形成局面的上一步是吃子，这里就标记“0”。(这个参数对
于普通局面的意义不大，ElephantBoard的规则处理器并不是根据这一项来判断和棋的所以总是计为“0”。)
(6)表示当前的回合数，在研究中局或排局时，作为研究对象的局面，这-项可以写1，随着局势的发展逐渐增加。
"""
def sit2Fen(init_s):
    str = ""
    rst = check_situation(init_s)

    if  rst['result_code'] == False:#局面有误
        toast(rst['result_desc'],duration=5)
        return str
    
    #rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR
    for y in range(9,-1,-1):
        for x in range(0,9,1):
            #print(f"{y=},{x=}")
            if (f"{x},{y}" in init_s) and (init_s[f'{x},{y}']):
                p = init_s[f'{x},{y}']

                fenPiece = ''
                if p.identifier == 'ju':
                    fenPiece = 'r'
                elif p.identifier == 'ma':
                    fenPiece = 'n'
                elif p.identifier == 'xiang':
                    fenPiece = 'b'
                elif p.identifier == 'shi':
                    fenPiece = 'a'
                elif p.identifier == 'shuai':
                    fenPiece = 'k'
                elif p.identifier == 'pao':
                    fenPiece = 'c'
                elif p.identifier == 'bing':
                    fenPiece = 'p'
                else:
                    fenPiece = '1'
                
                if p.camp == 'r':#红方
                    fenPiece = fenPiece.upper()
                #print(f'{fenPiece}')
                str = f'{str}{fenPiece}'
                #print(f'{str=}')
            else:
                str = f'{str}1'
            
        if y > 0:
            str = f'{str}/'
            #print(f'{str=}')
    
    return str
            
