'''
Author: Paoger
Date: 2023-11-06 16:13:14
LastEditors: Paoger
LastEditTime: 2024-02-06 13:45:40
Description: 

Copyright (c) 2023 by Paoger, All Rights Reserved. 
'''

#从棋盘网点的角度来设计，关注每个网点上的棋子：棋盘是固定的，棋子是动的，以静制动，神御万法
#XQF 1.0 初始局面，棋子顺序
"""
在XQF文件中，使用连续的32个字节表示棋盘的初始局面。这32个字节的位置顺序是固定的，含义如下: 
01 - 16:依次为红方的车马相士帅士相马车炮炮兵兵兵兵兵
依次记录红9路车、8路马、7路象、6路士、5路帅、4路士、3路象、2路马、1路车、8路炮、2路炮、9路兵、7路兵、5路兵、3路兵、1路兵的初始坐标位置。
17 - 32:依次为黑方的车马象士将士像马车炮炮卒卒卒卒卒
依次记录黑1路车、2路马、3路象、4路士、5路帅、6路士、7路象、8路马、9路车、2路炮、8路炮、1路卒、3路卒、5路卒、7路卒、9路卒的初始坐标位置。
"""
"""修改FEN格式，此处统一为小写
红方 黑方	字母
帅	 将	    k
仕	 士	    a
相	 象	    b
马	 马	    n
车	 车	    r
炮	 炮	    c
兵	 卒	    p
"""
#g_const_S_P_ORDEER = ['ju','ma','xiang','shi','shuai','shi','xiang','ma','ju','pao','pao','bing','bing','bing','bing','bing','ju','ma','xiang','shi','shuai','shi','xiang','ma','ju','pao','pao','bing','bing','bing','bing','bing']
g_const_S_P_ORDEER = ['r','n','b','a','k','a','b','n','r','c','c','p','p','p','p','p','r','n','b','a','k','a','b','n','r','c','c','p','p','p','p','p']

#key:f'{x},{y}' value:{Piece}
#全局变量 棋盘的初始局面,此值不可改变
g_const_INIT_SITUATION = {}
