'''
Author: Paoger
Date: 2023-11-06 16:33:03
LastEditors: Paoger
LastEditTime: 2024-02-06 14:00:07
Description: 

Copyright (c) 2023 by Paoger, All Rights Reserved. 
'''

class Piece:
    #棋子Widget
    pieceWidget = None

    #阵营，红：w，黑：b
    camp = None
    #棋子标识符，车：r，马：n，象：b，士：a，帅(将)：k，炮：c，兵（卒）：p
    #决定走子规则
    identifier = None

    #camp + identifier 决定棋子图片

    #坐标原点左下角，横坐标,整数 0~8
    x = None
    #纵坐标,整数 0~9
    y = None

    def __init__(self,camp,identifier,x,y,pieceWidget=None):
        self.pieceWidget = pieceWidget
        self.camp = camp
        self.identifier = identifier
        self.x = x
        self.y = y
    
    def __str__(self):#重写__str__(),显示更多有用信息
        return f"{self.camp}:{self.identifier}({self.x},{self.y})"
    
    def getMoveName(self,end_x,end_y,situation):
        #print("getMoveName begin")
        #print(f"棋子：{self.camp=},{self.identifier=},{self.x=},{self.y=}")
        #rint(f"棋子：{self}")
        #rint(f"{self.x=},{self.y=},{end_x=},{end_y=}")
        #rint_situation("...situation...",situation)

        moveName = ""

        if self.camp == 'w':#红方
            moveName = f"红"
            #判断该子前后是否有相同的棋子
            for yy in range(0,9,1):#y坐标
                #print(f"{yy=}")
                if yy == self.y:
                    continue
                if (f"{self.x},{yy}" in situation) and isinstance(situation[f'{self.x},{yy}'],Piece):
                    p = situation[f'{self.x},{yy}']
                    #print(f"{p}")
                    if (p.camp == self.camp) and (p.identifier == self.identifier):
                        if p.y > self.y:
                            moveName = f"{moveName}后"
                        elif p.y < self.y:
                            moveName = f"{moveName}前"
                else:
                    continue

            if self.identifier == 'r':
                moveName = f"{moveName}车{9 - self.x}"
                if end_y > self.y:
                    moveName = f"{moveName}进{end_y - self.y}"
                elif end_y == self.y:
                    moveName = f"{moveName}平{9 - end_x}"
                else:
                    moveName = f"{moveName}退{self.y - end_y}"
            elif self.identifier == 'n':
                moveName = f"{moveName}马{9 - self.x}"
                if end_y > self.y:
                    moveName = f"{moveName}进{9 - end_x}"
                else:
                    moveName = f"{moveName}退{9 - end_x}"
            elif self.identifier == 'b':
                moveName = f"{moveName}相{9 - self.x}"
                if end_y > self.y:
                    moveName = f"{moveName}进{9 - end_x}"
                else:
                    moveName = f"{moveName}退{9 - end_x}"
            elif self.identifier == 'a':
                moveName = f"{moveName}仕{9 - self.x}"
                if end_y > self.y:
                    moveName = f"{moveName}进{9 - end_x}"
                else:
                    moveName = f"{moveName}退{9 - end_x}"
            elif self.identifier == 'k':
                moveName = f"{moveName}帅{9 - self.x}"
                if end_y > self.y:
                    moveName = f"{moveName}进{end_y - self.y}"
                elif end_y == self.y:
                    moveName = f"{moveName}平{9 - end_x}"
                else:
                    moveName = f"{moveName}退{self.y - end_y}"
            elif self.identifier == 'c':
                moveName = f"{moveName}炮{9 - self.x}"
                if end_y > self.y:
                    moveName = f"{moveName}进{end_y - self.y}"
                elif end_y == self.y:
                    moveName = f"{moveName}平{9 - end_x}"
                else:
                    moveName = f"{moveName}退{self.y - end_y}"
            elif self.identifier == 'p':
                moveName = f"{moveName}兵{9 - self.x}"
                if end_y > self.y:
                    moveName = f"{moveName}进{end_y - self.y}"
                elif end_y == self.y:
                    moveName = f"{moveName}平{9 - end_x}"
                else:
                    moveName = f"{moveName}退{self.y - end_y}"
        elif self.camp == 'b':#黑方
            moveName = f"黑"
            #判断该子前后是否有相同的棋子
            for yy in range(0,9,1):#y坐标
                if yy == self.y:
                    continue
                if (f"{self.x},{yy}" in situation) and isinstance(situation[f'{self.x},{yy}'],Piece):
                    p = situation[f'{self.x},{yy}']
                    if (p.camp == self.camp) and (p.identifier == self.identifier):
                        if p.y > self.y:
                            moveName = f"{moveName}前"
                        elif p.y < self.y:
                            moveName = f"{moveName}后"
                else:
                    continue
            

            if self.identifier == 'r':
                moveName = f"{moveName}车{1 + self.x}"
                if end_y > self.y:
                    moveName = f"{moveName}退{end_y - self.y}"
                elif end_y == self.y:
                    moveName = f"{moveName}平{1 + end_x}"
                else:
                    moveName = f"{moveName}进{self.y - end_y}"
            elif self.identifier == 'n':
                moveName = f"{moveName}马{1 + self.x}"
                if end_y > self.y:
                    moveName = f"{moveName}退{1 + end_x}"
                else:
                    moveName = f"{moveName}进{1 + end_x}"
            elif self.identifier == 'b':
                moveName = f"{moveName}象{1 + self.x}"
                if end_y > self.y:
                    moveName = f"{moveName}退{1 + end_x}"
                else:
                    moveName = f"{moveName}进{1 + end_x}"
            elif self.identifier == 'a':
                moveName = f"{moveName}士{1 + self.x}"
                if end_y > self.y:
                    moveName = f"{moveName}退{1 + end_x}"
                else:
                    moveName = f"{moveName}进{1 + end_x}"
            elif self.identifier == 'k':
                moveName = f"{moveName}将{1 + self.x}"
                if end_y > self.y:
                    moveName = f"{moveName}退{end_y - self.y}"
                elif end_y == self.y:
                    moveName = f"{moveName}平{1 + end_x}"
                else:
                    moveName = f"{moveName}进{self.y - end_y}"
            elif self.identifier == 'c':
                moveName = f"{moveName}炮{1 + self.x}"
                if end_y > self.y:
                    moveName = f"{moveName}退{end_y - self.y}"
                elif end_y == self.y:
                    moveName = f"{moveName}平{1 + end_x}"
                else:
                    moveName = f"{moveName}进{self.y - end_y}" 
            elif self.identifier == 'p':
                moveName = f"{moveName}卒{1 + self.x}"
                if end_y > self.y:
                    moveName = f"{moveName}退{end_y - self.y}"
                elif end_y == self.y:
                    moveName = f"{moveName}平{1 + end_x}"
                else:
                    moveName = f"{moveName}进{self.y - end_y}"
        else:#啥也不是
            moveName = f"X"
        
        #print(f"{moveName}")
        #print("getMoveName end")

        return moveName


