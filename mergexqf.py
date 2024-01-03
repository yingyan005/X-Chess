'''
Author: Paoger
Date: 2023-12-19 15:15:08
LastEditors: Paoger
LastEditTime: 2024-01-02 20:17:03
Description: 

Copyright (c) 2023 by Paoger, All Rights Reserved. 
'''
import os
import binascii
from treelib import Tree
import uuid
import datetime

from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.utils import asynckivy

from kivy.logger import Logger

from situation import xqfinit2xchessinit,check_situation,print_situation
from piece import Piece
from tree2xqf import saveMovestreeToXQF

#创建招法树
def xqfmoves2tree(xqffilename):
    Logger.debug("X-Chess xqfmoves2tree:******xqfmoves2tree begin******")

    with open(xqffilename, 'rb') as file:
        # 读取文件内容
        content = file.read()
    hex_content = binascii.b2a_hex(content).decode('utf-8')
    version_tag = hex_content[0:6]
    if version_tag != '58510a':
        Logger.debug(f'X-Chess mergexqf2tree:{xqffilename} 不是XQF1.0格式，58510a !!!!!!!!!!!')
        return
    
    xqf_init = hex_content[32:96]
    xchess_init = {}
    xqfinit2xchessinit(xqf_init,xchess_init)
    rst = check_situation(xchess_init)
    if  rst['result_code'] == False:#局面有误
        Logger.debug(f'X-Chess mergexqf2tree:{xqffilename} 初始局面有误')
        return    
    
    #招法树
    moves_tree = Tree()
    
    sx = sy = ex = ey = None
    chess_moves = hex_content[2048:]
    moveslen = len(chess_moves) #用来判断是否跳出循环

    #空着批注的长度
    note = ""
    #第5-8字节:为一个32位整数(x86格式,高字节在后)，表明本步批注的大小
    s = f'{chess_moves[14:16]}{chess_moves[12:14]}{chess_moves[10:12]}{chess_moves[8:10]}'
    notelen = int(s,16)
    if notelen > 0:
        byte_str = binascii.unhexlify(chess_moves[16:16+notelen*2])
        note = byte_str.decode("gbk")
    
    flag = chess_moves[4:6]#使用16进制字符串

    nroot = moves_tree.create_node(tag='xqf招法树', 
            data={'camp':'','sp':'18','ep':'20','flag':flag,'rsv':'ff',
                  'notelen':chess_moves[8:16],'note':note,
                  'situation':xchess_init,'pieceWidget':None})  # 根节点
    
    i = 1#循环次数，便于调试        
    istart = 16 + notelen * 2
    branchStack = [] #当前招法链枝点链表，后进先出
    branchStack.append(nroot)
    n0 = nroot
    while istart < moveslen:
        #print(f"*** {i=} ***")

        #保存当前招法走后的局面
        realtime_situation = {}
        p = Piece(None,None,None,None)
        mn = ""
        
        #棋子开始位置
        startxy = chess_moves[istart:istart+2]
        sxy = int(startxy,16) - 24
        sx = sxy // 10
        sy = sxy % 10
        #棋子到达位置
        endxy = chess_moves[istart+2:istart+4]
        exy = int(endxy,16) - 32
        ex = exy // 10
        ey = exy % 10

        #p = n0.data['situation'][f'{sx},{sy}']
        #n0.data['camp'] = p.camp
        if i == 1:#赋值初始局面该谁走棋
            p = n0.data['situation'][f'{sx},{sy}']
            n0.data['camp'] = p.camp

        # 走子前局面保存在其父节点中的data['situation']
        if (f"{sx},{sy}" in n0.data['situation']) and isinstance(n0.data['situation'][f'{sx},{sy}'],Piece):
            #当前招法走子前的棋子实例，其x,y与sx，sy相同
            p = n0.data['situation'][f'{sx},{sy}']
            #获取招法名称
            mn =p.getMoveName(ex,ey,n0.data['situation'])
            #实现自我的深层拷贝：内部的对象的重新创建
            for m in range(0,9,1):#x坐标
                for n in range(0,10,1):#y坐标
                    if (f"{m},{n}" in n0.data['situation']) and isinstance(n0.data['situation'][f'{m},{n}'],Piece):
                        p0 = n0.data['situation'][f'{m},{n}']
                        #创建新的对象
                        p1 = Piece(p0.camp,p0.identifier,p0.x,p0.y,p0.pieceWidget)
                        #此时p0 与 p1相同，指向相同的棋子Widget
                        realtime_situation[f'{m},{n}'] = p1                
            #起点置空
            realtime_situation[f'{sx},{sy}'] = None
            #终点指向新的Piece实例，其x,y为ex ey
            realtime_situation[f'{ex},{ey}'] = Piece(p.camp,p.identifier,ex,ey,p.pieceWidget)
        else:#todo 一般不会，除非异常，待完善代码结构
            print(f"异常了，当前局面{n0.data['situation']}中({sx},{sy})处没有棋子")
            print_situation("******异常局面******",n0.data['situation'])
            toast(f"异常了，当前局面{n0.data['situation']}中({sx},{sy})处没有棋子")
            break
        movesname = mn
        flag = chess_moves[istart+4:istart+6]
        note = ""
        #批注的长度
        s = f'{chess_moves[istart+14:istart+16]}{chess_moves[istart+12:istart+14]}{chess_moves[istart+10:istart+12]}{chess_moves[istart+8:istart+10]}'
        notelen = int(s,16)
        if notelen > 0:
            byte_str = binascii.unhexlify(chess_moves[istart+16:istart+16+notelen*2])
            note = byte_str.decode("gbk")
        
        p = realtime_situation[f'{ex},{ey}']
        n = moves_tree.create_node(tag=movesname,parent = n0.identifier,
                                        data={'camp':p.camp,'sp':chess_moves[istart:istart+2],'ep':chess_moves[istart+2:istart+4],'flag':flag,'rsv':'00',
                                              'notelen':chess_moves[istart+8:istart+16],'note':note,
                                              'situation':realtime_situation,'pieceWidget':p.pieceWidget,'sx':sx,'sy':sy,'ex':ex,'ey':ey
                                              })
        
        #判断该节点是否有分支            
        if flag == 'f0':#240:#0xf0 中间节点,或者说其同级的最后一个
            n0 = n
        elif flag == 'ff':#255 : #0xff 分支节点
            #如果其父级是f0(f0同级的最后一个)，需要将其父级也压入堆栈
            if n0.data['flag'] == 'f0':#240:
                branchStack.append(n0)
            branchStack.append(n)#将该节点压入枝点链表，后进先出
            n0 = n
        elif flag == '00':#00:
            if (n0.data['flag'] == 'f0') : #240
                while True:
                    if len(branchStack) == 0:
                        break
                    
                    if len(branchStack) > 0 and branchStack[len(branchStack)-1].data['flag'] == 'ff': #255 0xff 分支节点
                        branchStack.pop()#弹出最后一个
                        break
                    if len(branchStack) > 0:
                        branchStack.pop()#弹出最后一个
            else:
                branchStack.pop()#弹出最后一个
                
            if len(branchStack) > 0:
                n0 = branchStack[len(branchStack)-1]
            else:#到根节点
                n0 = nroot
        elif flag == '0f': #15:#15=0x0f,0f经验证是兄弟中所有单身汉中非最小的那些单身汉
            print(f"{flag=},pass")                
        else:
            print(f"xxx {i=}:{flag=},{chess_moves[istart+4:istart+6]}")
        
        i = i+1
        #if i > 2:#循环次数，便于调试
        #    break            
        istart = istart + 16 + notelen * 2
        if istart >= moveslen:#没招了
            break
    #while循环结束
    
    
    print(f"节点数:{len(moves_tree)}")  # 节点数
    print(f"树的深度:{moves_tree.depth()}")  # 树的深度
    #print(moves_tree)
#
    #for nodeid in moves_tree.expand_tree(mode=Tree.DEPTH, sorting=False):
    #    node = moves_tree.get_node(nodeid)
    #    print(f"{node.tag},camp==>{node.data['camp']}")
#
    Logger.debug("X-Chess X-ChessApp:******xqfmoves2tree end******")

    return moves_tree


def mergexqf2tree(filenames:list):
    Logger.debug(f'X-Chess mergexqf2tree: begin')

    #注意顺序，第一个文件将作为主文件，以第1个文件的开始局面为准进行合并，最多合并3个文件
    filenum = len(filenames)
    #Logger.debug(f'X-Chess mergexqf2tree: {filenum=}')
    if filenum < 2 or filenum > 2:#至少要有2个文件,最多合并3个文件
        return
    
    """
*棋谱1开局
└── 1  红兵7进1-2f38-f0
    └── 2  黑马8进7-6763-f0
        └── 3  红马8进7-2236-f0
            └── 4  黑炮2平3-293b-0
*棋谱2开局
└── 1  红马8进7-2236-f0
    └── 2  黑马8进7-6763-f0
        └── 3  红兵7进1-2f38-f0
            └── 4  黑卒7进1-5a61-00
鹏飞合并后是这样的
开局
├── 1  红兵7进1-2f38-ff
│   └── 2  黑马8进7-6763-f0
│       └── 3  红马8进7-2236-f0
│           └── 4  黑炮2平3-293b-00
└── 5  红马8进7-2236-f0
    └── 6  黑马8进7-6763-f0
        └── 7  红兵7进1-2f38-f0
            └── 8  黑卒7进1-5a61-00
**X-Chess合并后
开局
├── 1  红兵7进1-2f38-ff
│   └── 2  黑马8进7-6763-f0
│       └── 3  红马8进7-2236-f0
│           ├── 4  黑炮2平3-293b-0f
│           └── 5  黑卒7进1-5a61-00
└── 6  红马8进7-2236-f0
    └── 7  黑马8进7-6763-f0
        └── 8  红兵7进1-2f38-f0
            ├── 9  黑卒7进1-5a61-0f
            └── 10 黑炮2平3-293b-00
            
？？？瘦身后，是否需要瘦身？？？
开局
├── 1  红兵7进1-2f38-f0
│   └── 2  黑马8进7-6763-f0
│       └── 3  红马8进7-2236-ff
│           ├── 4  黑炮2平3-293b-00
│           └── 5  黑卒7进1-5a61-00
│
└── 6  红马8进7-2236-f0
    └── 7  黑马8进7-6763-f0
        └── 8  红兵7进1-2f38-00

    """
    
    #招法树
    Logger.debug(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} X-Chess mergexqf2tree: 解析 tree0 开始')
    tree0 = xqfmoves2tree(filenames[0])
    Logger.debug(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} X-Chess mergexqf2tree: 解析 tree0 完成')
    
    Logger.debug(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} X-Chess mergexqf2tree: 解析 tree1 开始')
    tree1 = xqfmoves2tree(filenames[1])
    Logger.debug(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} X-Chess mergexqf2tree: 解析 tree1 完成')

    #deepcopy
    moves_tree = Tree(tree0.subtree(tree0.root), deep=True,identifier=None)

    #tree0和tree1是否有交集
    bHasIntersection = False

    """ Logger.debug("X-Chess : 000000000000000")
    Logger.debug("X-Chess : ***tree0***")
    Logger.debug(f'{tree0}')
    Logger.debug("X-Chess : ***tree1***")
    Logger.debug(f'{tree1}') """

    Logger.debug(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} X-Chess mergexqf2tree: 循环 节点 判断 开始')

    sameSitCount = 0#共发现几处可以合并的
    for nodeid1 in tree1.expand_tree(mode=Tree.DEPTH, sorting=False):
        cur_node = tree1.get_node(nodeid1)
        #Logger.debug(f'X-Chess : now {cur_node.tag=}')
        if cur_node.is_root():#略过初始局面，根节点
            #Logger.debug(f'X-Chess : 略过初始局面，根节点')
            continue
        node1 = tree1.parent(nodeid1)
        #Logger.debug(f'X-Chess : parent {node1.tag=}')
        #Logger.debug(f'X-Chess : {node1.data["camp"]=}')

        #判断局面是否相同
        bSitIsSame = None
        nodeSame = None
        for nodeid0 in tree0.expand_tree(mode=Tree.DEPTH, sorting=False):
            bSitIsSame = True
            node0 = tree0.get_node(nodeid0)
            #Logger.debug(f'X-Chess : now {node0.tag=}')
            #Logger.debug(f'X-Chess : {node0.data["camp"]=}')

            if node0.data["camp"] == node1.data["camp"]: #走棋方相同
                #调试begin
                """ if node1.tag == '红兵7进1' and node0.tag == '红马8进7':
                    print_situation("******node1局面******",node1.data['situation'])
                    print_situation("******node0局面******",node0.data['situation']) """
                #调试end

                for y in range(0,10,1):
                    for x in range(0,9,1):
                        p0 = p1 = None
                        if (f"{x},{y}" in node0.data['situation']) and (node0.data['situation'][f'{x},{y}']):
                            p0 = node0.data['situation'][f'{x},{y}']
                        if (f"{x},{y}" in node1.data['situation']) and (node1.data['situation'][f'{x},{y}']):
                            p1 = node1.data['situation'][f'{x},{y}']
                        
                        if p0 == None and p1 == None:
                            continue#视为相同
                        elif (p0 != None and p1 == None) or (p0 == None and p1 != None):
                            bSitIsSame = False #视为不同
                            #调试begin
                            """ if node1.tag == '红兵7进1' and node0.tag == '红马8进7':
                                Logger.debug(f'X-Chess : xxyy 视为不同') """
                            #调试end
                        elif p0.camp == p1.camp and p0.identifier == p1.identifier:#视为不同，
                            continue#相同

                        if bSitIsSame == False:
                            #调试begin
                            """ if node1.tag == '红兵7进1' and node0.tag == '红马8进7':
                                Logger.debug(f'X-Chess :xx 局面不同') """
                            #调试end
                            break#有一个不同，则局面就不同
                    
                    if bSitIsSame == False:
                        #调试begin
                        """ if node1.tag == '红兵7进1' and node0.tag == '红马8进7':
                            Logger.debug(f'X-Chess :yy 局面不同') """
                        #调试end
                        break#有一个不同，则局面就不同
                
                #局面相同
                if bSitIsSame == True:
                    #Logger.debug(f'X-Chess : 局面相同，跳出tree0循环')
                    nodeSame = node0
                    break
        #end for tree0
                        
        #Logger.debug(f"{bSitIsSame=}")
        #Logger.debug(f'{node1.tag=}')
        #if nodeSame is not None:
        #    Logger.debug(f'{nodeSame.tag=}')
        
        if bSitIsSame == True and nodeSame :
            #Logger.debug(f'X-Chess : {node1.tag=}')
            #Logger.debug(f'X-Chess : {nodeSame.tag=}')
            #如果cur_node的tag与nodeSame的子节点的tag相同则忽略，继续循环
            bIsExist = False
            for item in moves_tree.children(nodeSame.identifier):
                if item.tag == cur_node.tag:
                    bIsExist = True
            #Logger.debug(f"{bIsExist=}")
            if bIsExist == True:
                #Logger.debug(f'X-Chess : ***找到相同局面，但已存在，忽略***')
                continue

            #Logger.debug(f'X-Chess : ***找到相同局面，开始合并***')            
            #print_situation("******node1局面******",node1.data['situation'])            
            #print_situation("******nodeSame局面******",nodeSame.data['situation'])

            #Logger.debug("00000000")
            #Logger.debug("***moves_tree***")
            #Logger.debug(moves_tree)

            sameSitCount = sameSitCount + 1
            if node1.is_root():                
                #将nodeSame为根节点的子树加入到moves_tree
                subTree = tree1.subtree(node1.identifier)
                #Logger.debug("***subTree***")
                #Logger.debug(subTree)
                bHasIntersection = True
                moves_tree.merge(nodeSame.identifier,subTree)
                #Logger.debug("1111111")
                #Logger.debug("***moves_tree***")
                #Logger.debug(moves_tree)
            else:#为了避免identifier重复，更新identifier后再加入到moves_tree
                subTree0 = tree1.subtree(node1.identifier)
                #deepcopy
                subTree1 = Tree(subTree0.subtree(subTree0.root), deep=True,identifier=None)
                #Logger.debug("***subTree1***")
                #Logger.debug(subTree1)

                ids = []
                for id in subTree1.expand_tree(mode=Tree.DEPTH, sorting=False):
                    ids.append(id)
                for id in ids:
                    newid = uuid.uuid1()
                    subTree1.update_node(id,identifier=newid)

                #Logger.debug("22222222")
                #Logger.debug("***moves_tree***")
                #Logger.debug(moves_tree)

                bHasIntersection = True
                moves_tree.merge(nodeSame.identifier,subTree1)#nodeSame == node0
                
                #Logger.debug("33333333")
                #Logger.debug("***moves_tree***")
                #Logger.debug(moves_tree)               

                if moves_tree.contains(node1.identifier) == True:#将tree0中的节点也加入到自己的节点中
                    subTree0 = tree0.subtree(nodeSame.identifier)
                    #deepcopy
                    subTree2 = Tree(subTree0.subtree(subTree0.root), deep=True,identifier=None)
                    #Logger.debug("***subTree1***")
                    #Logger.debug(subTree2)

                    ids = []
                    for id in subTree2.expand_tree(mode=Tree.DEPTH, sorting=False):
                        ids.append(id)
                    for id in ids:
                        newid = uuid.uuid1()
                        subTree2.update_node(id,identifier=newid)
                    bHasIntersection = True
                    moves_tree.merge(node1.identifier,subTree2)
                    #Logger.debug("33333333")
                    #Logger.debug("***moves_tree***")
                    #Logger.debug(moves_tree)
                

            #Logger.debug("中间")
            #Logger.debug("***moves_tree***")
            #Logger.debug(moves_tree)
        else:
            continue
    #end for tree1
    
    Logger.debug(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} X-Chess mergexqf2tree: 循环 节点 判断 结束,{sameSitCount=}')

    if bHasIntersection == False:
        moves_tree = None
        Logger.debug(f'{filenames[0]} 可能完全包含了 {filenames[1]} ，或者没有交集')
        toast(f'{filenames[0]} 可能完全包含了 {filenames[1]} ，或者没有交集')
        return
    
    #Logger.debug("最终111")
    #Logger.debug("***moves_tree***")
    #Logger.debug(f'{moves_tree}')

    Logger.debug(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} X-Chess mergexqf2tree: 处理 moves_tree flag 开始')

    #调试begin
    #before_tree = Tree(moves_tree.subtree(moves_tree.root), deep=True,identifier=None)
    #i = 0
    #for id in before_tree.expand_tree(mode=Tree.DEPTH, sorting=False):
    #    i = i + 1
    #    node = before_tree.get_node(id)
    #    node.tag = f'{i: <3}{node.tag}-{node.data["flag"]}'
    #Logger.debug("处理flag前")
    #Logger.debug(f'{before_tree}')
    #调试end
    
    for id in moves_tree.expand_tree(mode=Tree.DEPTH, sorting=False):
        node = moves_tree.get_node(id)
        l = len(moves_tree.children(id))
        #Logger.debug(f"X-Chess mergexqf2tree : before {l=},{node.tag=},{node.data['flag']=}")
        if l == 0:
            node.data['flag']= '00'
        elif l > 1:
            node.data['flag']= 'ff'
        #Logger.debug(f"X-Chess mergexqf2tree : after {node.tag=},{node.data['flag']=}")
        
        #将兄弟中是f0的改成ff
        for item in moves_tree.siblings(id):
            #Logger.debug(f"X-Chess mergexqf2tree : {item.tag=},{item.data['flag']=}")
            if item.data['flag'] == 'f0':
               item.data['flag'] = 'ff'
            elif item.data['flag'] == '00':
               item.data['flag'] = '0f'
        if item:#如果有兄弟
            if node.data['flag'] == 'ff':#如果自己是ff
                node.data['flag']= 'f0'#将自己改成f0
    
    #调试begin
    #after_tree = Tree(moves_tree.subtree(moves_tree.root), deep=True,identifier=None)
    #i = 0
    #for id in after_tree.expand_tree(mode=Tree.DEPTH, sorting=False):
    #    i = i + 1
    #    node = after_tree.get_node(id)
    #    node.tag = f'{i: <3}{node.tag}-{node.data["flag"]}'
    #Logger.debug("处理flag后")
    #Logger.debug(f'{after_tree}')
    #调试end
    
    Logger.debug(f"moves_tree 节点数:{len(moves_tree)}")  # 节点数
    Logger.debug(f"moves_tree 树的深度:{moves_tree.depth()}")  # 树的深度
    
    #kivy log格式中第1个“:”有特殊含义
    Logger.debug(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} X-Chess mergexqf2tree: 处理 moves_tree flag 结束')
    Logger.debug(f'X-Chess mergexqf2tree:{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} 处理 moves_tree flag 结束')
    print(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} X-Chess mergexqf2tree: 处理 moves_tree flag 结束')
    
    #Logger.debug("最终")
    #Logger.debug("***moves_tree***")
    #Logger.debug(f'{moves_tree}')
    

    Logger.debug(f'X-Chess mergexqf2tree: end')

    return moves_tree