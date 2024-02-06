'''
Author: Paoger
Date: 2023-12-17 18:22:09
LastEditors: Paoger
LastEditTime: 2024-01-25 12:48:40
Description: 

Copyright (c) 2023 by Paoger, All Rights Reserved. 
'''
import os
import binascii
from treelib import Tree

from kivymd.app import MDApp
from kivymd.toast import toast
from kivy.logger import Logger

from global_var import g_const_S_P_ORDEER
from piece import Piece
from situation import print_situation

def saveMovestreeToXQF(moves_tree,xqfFile2048,fullfilename):
    Logger.debug(f'X-Chess saveMovestreeToXQF: begin')

    if len(moves_tree) <2 :#至少要走一步
        toast("至少要走1步")
        return

    Logger.debug(f'X-Chess saveMovestreeToXQF: {fullfilename=}')    

    #app.moves_tree.save2file(filename=f"{fullfilename}.txt",sorting=False)
    with open(fullfilename, 'wb') as fdst:
        #写入文件头部
        #print(f"{app.xqfFile2048=}")
        fdst.write(binascii.unhexlify(xqfFile2048.encode('gbk')))
        for nodeid in moves_tree.expand_tree(mode=Tree.DEPTH, sorting=False):
            node = moves_tree.get_node(nodeid)
            #print(f"{node.data['sp']}{node.data['ep']}{node.data['flag']}{node.data['rsv']}{node.data['notelen']}{node.data['note']}")
            
            #print(f"{node.data['note']=},{node.data['note'].encode('gbk')=}")
            #hexnote = binascii.hexlify(node.data['note'].encode('gbk'))
            hexnote = binascii.b2a_hex(node.data['note'].encode('gbk'))
            #print(f"1 {hexnote=}")
            hexnote = hexnote.decode('gbk')
            #print(f"2 {hexnote=}")
            move = f"{node.data['sp']}{node.data['ep']}{node.data['flag']}{node.data['rsv']}{node.data['notelen']}{hexnote}"
            #Logger.debug(f'X-Chess saveMovestreeToXQF:{move=}')
            
            #unhexlify 将16进制data转换为2进制表示
            fdst.write(binascii.unhexlify(move.encode('gbk')))
                
    Logger.debug(f'X-Chess saveMovestreeToXQF: end')

#将当前招法树保存到文件中
def saveFileXQF():
    app = MDApp.get_running_app()

    filePath = app.root.ids['id_scrinputfilename'].ids['id_filepath'].text
    if  filePath == '':
        toast("请指定文件路径！")
        return
    if not os.path.isdir(filePath):
        toast("路径格式不对！")
        return
    filename = app.root.ids['id_scrinputfilename'].ids['id_filename'].text
    if filename == '':
        toast("请输入文件名！")
        return
        
    #如果没有.xqf后缀，则自动补上
    if len(filename) > 4 and filename[-4:].lower() != '.xqf':
        filename = f"{filename}.xqf"
    elif len(filename) > 4 and filename[-4:].lower() == '.xqf':
        filename = f"{filename[:-4]}.xqf"
    else:
        filename = f"{filename}.xqf"
    #print(f"{filename=}")
    filename = os.path.join(filePath,filename)
    #import re
    #pattern = re.compile(r'^[a-zA-Z]:\\\\([^\\/:*?"<>|\r\n]+\\\\)*([^\\/:*?"<>|\r\n]+\.txt)$')
    #print(f"{filename}")
    #if not re.match(pattern, filename):
    #    toast("文件名格式不对！")
    #    return

    file_name = os.path.basename(filename)
    app.title = f"X-Chess {file_name[:-4]}"
    app.root.ids['id_screenmain'].ids['id_movesnote'].hint_text= app.title

    Logger.debug(f'X-Chess saveFileXQF: {app.chessmovesfilename=}')

    saveMovestreeToXQF(app.moves_tree,app.xqfFile2048,filename)       
        
    app.root.current_heroes = ""
    app.root.current = "screenMain"
        
    app.chessmovesfilename = filename

    #修改招法树第一个节点的tag
    node = app.moves_tree.get_node(app.moves_tree.root)
    node.tag = os.path.basename(app.chessmovesfilename)
    #修改招法列表第一个列表的名称
    num = len(app.root.ids['id_screenmoves'].ids.id_moveslist.children)
    app.root.ids['id_screenmoves'].ids.id_moveslist.children[num-1].text = node.tag

    toast("保存成功")
        
    return
