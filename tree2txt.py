import os
import binascii
from treelib import Tree

from kivymd.app import MDApp
from kivymd.toast import toast
from kivy.logger import Logger

from global_var import g_const_S_P_ORDEER
from piece import Piece
from situation import print_situation

#android :path 从 app.sel_filename取
#other:从 MDFilemanager传参获取
def tree2txt(instance=None,path=None):
    Logger.debug("X-Chess X-ChessApp:******tree2txt begin******")

    app = MDApp.get_running_app()
    
    if path == None:        
        app.back_mainScreen()
        path = app.sel_filename
    else:#path从 MDFilemanager传参获取
        '''
        It will be called when you click on the file name
        or the catalog selection button.
        :param path: path to the selected directory or file;
        '''
        app.exit_manager()

    # 打开文件
    with open(path, 'rb') as file:
        # 读取文件内容
       content = file.read()
         
    # 将二进制内容转换为16进制表示
    hex_content = binascii.hexlify(content).decode('utf-8')
    version_tag = hex_content[0:6]
    Logger.debug("X-Chess X-ChessApp:版本标记：{version_tag=}")
    if version_tag != '58510a':
        toast(f"{path} 不是XQF1.0格式，58510a")
        return
    
    toast(f"{path} 是XQF1.0格式，58510a，静待花开",duration=1.5)
    init_situation = {}
    init_s = hex_content[32:96]

    for i in range(0,32,1):
        xy = int(init_s[i*2:(i+1)*2],16)
        p = Piece(None,None,None,None)
        if xy != 255:#255 0xff 无子
            x = xy // 10
            y = xy % 10
            if i < 16:#红方棋子
                p = Piece('w',g_const_S_P_ORDEER[i],x,y)
            else: #黑方棋子
                p = Piece('b',g_const_S_P_ORDEER[i],x,y)
            init_situation[f'{x},{y}'] = p
    
    #print_situation("初始局面",init_situation)

    chess_moves = hex_content[2048:]
    moveslen = len(chess_moves) #用来判断是否跳出循环
    #print(f"棋谱长度：{moveslen=},记录：{chess_moves=}")

    #空着批注的长度
    s = f'{chess_moves[14:16]}{chess_moves[12:14]}{chess_moves[10:12]}{chess_moves[8:10]}'        
    notelen = int(s,16)
    #print(f'{notelen=},{chess_moves[8:16]=}')

    m_tree = Tree()
    flag = chess_moves[4:6]#使用16进制字符串
    nroot = m_tree.create_node(tag=os.path.basename(path),
                data={'flag':flag,'situation':init_situation})  # 根节点

    i = 1#循环次数，便于调试        
    istart = 16 + notelen * 2
    branchStack = [] #当前招法链枝点链表，后进先出
    branchStack.append(nroot)
    n0 = nroot
    while istart < moveslen:
        #print(f"*** {i=} ***")            
        realtime_situation = {}           
        #print(f"cur {istart=}")
        p = Piece(None,None,None,None)
        mn = ""

        #棋子开始位置
        startxy = chess_moves[istart:istart+2]
        #print(f"{startxy=}")
        sxy = int(startxy,16) - 24
        sx = sxy // 10
        sy = sxy % 10
        #print(f"{sx=},{sy=}")            
        #棋子到达位置
        endxy = chess_moves[istart+2:istart+4]
        #print(f"{endxy=}")
        exy = int(endxy,16) - 32
        ex = exy // 10
        ey = exy % 10
        #print(f"{ex=},{ey=}")

        #print(f"{chess_moves[istart:istart+2]}{chess_moves[istart+2:istart+4]}==({sx},{sy})-->({ex},{ey})")

        #print_situation("******走子前局面******",n0.data['situation'])

        if (f"{sx},{sy}" in n0.data['situation']) and isinstance(n0.data['situation'][f'{sx},{sy}'],Piece):
            p = n0.data['situation'][f'{sx},{sy}']
            #print(f"网点：({sx},{sy}),棋子：{p.camp=},{p.identifier=},{p.x=},{p.y=},{p.pieceWidget=}")
            #print(f"网点：({sx},{sy}),棋子：{p}")

            mn =p.getMoveName(ex,ey,n0.data['situation'])
            #print(f"{mn=}")

            #实现自我的深层拷贝：内部的对象的重新创建
            for m in range(0,9,1):#x坐标
                for n in range(0,10,1):#y坐标
                    if (f"{m},{n}" in n0.data['situation']) and isinstance(n0.data['situation'][f'{m},{n}'],Piece):
                        p0 = n0.data['situation'][f'{m},{n}']
                        #创建新的对象
                        p1 = Piece(p0.camp,p0.identifier,p0.x,p0.y)
                        realtime_situation[f'{m},{n}'] = p1                

            #print_situation("******deepcopy 后 realtime_situation******",realtime_situation)

            # #更新 实时局面 realtime_situation
            realtime_situation[f'{sx},{sy}'] = None
            realtime_situation[f'{ex},{ey}'] = Piece(p.camp,p.identifier,ex,ey,p.pieceWidget)

            #print_situation("******更新后 realtime_situation******",realtime_situation)
        else:#todo 一般不会，除非异常，待完善代码结构
            Logger.debug(f"X-Chess X-ChessApp:{i=} 异常了，当前局面中({sx},{sy})处没有棋子")
            print_situation("******异常局面******",n0.data['situation'])
            toast(f"异常了，当前局面{n0.data['situation']}中({sx},{sy})处没有棋子")
            break

        #print_situation("******走子后局面******",realtime_situation)            
            
        movesname = f"{i: <3}{mn}-{chess_moves[istart:istart+2]}{chess_moves[istart+2:istart+4]}-{chess_moves[istart+4:istart+6]}"

        #获取当前招法的分支标记
        #flag = int(chess_moves[istart+4:istart+6],16)
        flag = chess_moves[istart+4:istart+6]
        #print(f"{flag=},{chess_moves[istart+4:istart+6]}")

        #批注的长度
        s = f'{chess_moves[istart+14:istart+16]}{chess_moves[istart+12:istart+14]}{chess_moves[istart+10:istart+12]}{chess_moves[istart+8:istart+10]}'
        notelen = int(s,16)

        n = m_tree.create_node(tag=movesname,parent = n0.identifier,
                                            data={'sp':chess_moves[istart:istart+2],'ep':chess_moves[istart+2:istart+4],'flag':flag,'rsv':'00',
                                                  'situation':realtime_situation,'sx':sx,'sy':sy,'ex':ex,'ey':ey})
            
        #判断该节点是否有分支            
        if flag == 'f0':#0xf0 中间节点,或者说其同级的最后一个
            n0 = n
            #tvn0 = tvn
        elif flag == 'ff' : #0xff 分支节点
            #如果其父级是f0(f0同级的最后一个)，需要将其父级也压入堆栈
            if n0.data['flag'] == 'f0':
                branchStack.append(n0)
            branchStack.append(n)#将该节点压入枝点链表，后进先出
            n0 = n
        elif flag == '00': 
            #从branchStack倒数，把之前压入的f0都弹出，直到遇到ff为止，并且把ff的也弹出
            if (n0.data['flag'] == 'f0') :                    
                while True:
                    #print(f"{len(branchStack)=}")
                    if len(branchStack) == 0:
                        break
                    
                    if len(branchStack) > 0 and branchStack[len(branchStack)-1].data['flag'] == 'ff': #255 0xff 分支节点
                        #print("22222")
                        branchStack.pop()#弹出最后一个
                        #tvbranchStack.pop()
                        break
                    if len(branchStack) > 0:
                        branchStack.pop()#弹出最后一个
                        #tvbranchStack.pop()
            else:
                branchStack.pop()#弹出最后一个
                
            if len(branchStack) > 0:
                n0 = branchStack[len(branchStack)-1]
            else:#到根节点
                n0 = nroot
        elif flag == '0f':#15=0x0f,0f经验证是兄弟中所有单身汉中非最小的那些单身汉
            """
            ── 49 红炮8平9-2422-f0
                ├── 50 黑车1平4-2147-ff
                │   └── 51 红炮9进4-1a26-0f
                └── 52 红兵9进1-1c25-00
            
            └── 285红炮4进4-4b57-f0                    
                └── 286黑车9平7-695d-f0                
                    ├── 287红相3退5-584a-0f            
                    ├── 288红相3进5-544a-ff            
                    │   └── 289黑车7平6-5553-00        
                    └── 290红相3进1-5472-f0            
                        └── 291黑车7平6-5553-f0        
                            └── 292红仕5进4-4154-f0    
                                └── 293黑车6退1-4b54-00
            """
            Logger.debug("X-Chess X-ChessApp:{flag=},pass")                
        else:
            Logger.debug("X-Chess X-ChessApp:xxx {i=}:{flag=},{chess_moves[istart+4:istart+6]}")
            
        i = i+1
        #if i > 5:#循环次数，便于调试
        #    break            
        istart = istart + 16 + notelen * 2
        #print(f"next {istart=}")
        if istart >= moveslen:#没招了
            break

    #while循环结束

    #toast("解析完成")
    Logger.debug(f"X-Chess X-ChessApp:节点数:{len(m_tree)}")  # 节点数
    Logger.debug(f"X-Chess X-ChessApp:树的深度:{m_tree.depth()}")  # 树的深度

    m_tree.save2file(filename=f"{path}.txt",sorting=False)

    toast(f"已保存至{path}.txt")
    Logger.debug("X-Chess X-ChessApp:******tree2txt end******")