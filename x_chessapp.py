'''
Author: Paoger
Date: 2023-11-23 16:21:31
LastEditors: Paoger
LastEditTime: 2024-01-05 10:05:06
Description: 

Copyright (c) 2024 by Paoger, All Rights Reserved. 
'''
'''
Author: Paoger
Date: 2023-10-30 10:18:15
LastEditors: Paoger
LastEditTime: 2024-01-01 13:15:24
Description: 

Copyright (c) 2023 by Paoger, All Rights Reserved. 
'''
#from kivy.utils import platform
#from kivy.config import Config
#if platform == "win":
#    Config.set('graphics','resizable', False) # 窗体可变设置为False

import os
import time
import binascii
from treelib import Tree

from kivy.logger import Logger
from kivy.utils import platform
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.core.window import Window

from kivymd.app import MDApp
from kivymd.uix.bottomsheet import MDListBottomSheet
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivymd.uix.filemanager import MDFileManager
from kivymd.toast import toast
from kivymd.utils import asynckivy
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivy.properties import StringProperty


#全局变量 棋盘的初始局面,此值不应改变
from global_var import g_const_INIT_SITUATION,g_const_S_P_ORDEER
from x_chess_cfg import get_theLast_Path,save_theLast_Path
from situation import init_g_init_situation,xqfinit2xchessinit,print_situation,check_situation

from myScreen import ScreenMain,ScreenMoves,ScreenEditSituation,ScreenInputFileName,ScreenMergeXQF,ScreenInfo
from selectedmaskwidget import SelectedMaskWidget
from piecewidget import PieceWidget
from piece import Piece
from onelinelistwithid import OneLineListWithId
from chessboard import Chessboard
from chessboard2 import Chessboard2
from piecewidget2 import PieceWidget2
from movesnote import Movesnote
from mymdtextfield import MyMDTextField
from tree2txt import tree2txt
from tree2xqf import saveMovestreeToXQF

from edit_situation import edit_situation_clear,edit_situation_full,edit_situation_cancle
from tree2xqf import saveFileXQF
from mergexqf import mergexqf2tree



from xqlight_ai import XQlight_moves

Logger.info('X-Chess X_ChessApp: This is a info message:X_ChessApp will run.')
Logger.debug('X-Chess X_ChessApp: This is a debug message:X_ChessApp will run.')

class X_ChessApp(MDApp):
    #Toolbar menu打开的子菜单
    menu = None

    #最近一次选择的路径
    last_sel_path = get_theLast_Path()

    #当前打开的棋谱文件名
    chessmovesfilename = ""

    #保存打开的xqf文件头【0:2048]，便于保存或另存
    xqfFile2048 = ""

    gameover = False
    #招法树
    moves_tree = Tree()
    #该谁走
    next_camp = 'r'#默认该红走

    #当前所选棋子
    selected_piece = None

    #棋子移动前位置上的标识
    selectedmask1 = None
    #棋子移动后位置上的标识
    selectedmask2 = None

    dialog = None

    file_manager = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        Window.bind(on_keyboard=self.events)

        self.theme_cls.theme_style = "Light"
    
    def build(self):
        #Material design 3 style
        #self.theme_cls.material_style = "M3"
        self.title = "X-Chess"   
        self.icon = 'x-chess.png'

        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": "新建局面",
                "height": dp(48),
                "on_release": lambda x="新建": self.new_situation(),
             },
             {
                "viewclass": "OneLineListItem",
                "text": "编辑局面",
                "height": dp(48),
                "on_release": lambda x="编辑": self.edit_situation(),
             },
            {
                "viewclass": "OneLineListItem",
                "text": "打开棋谱",
                "height": dp(48),
                "on_release": lambda x="Open": self.open_XQFFile(x),
             },
             {
                "viewclass": "OneLineListItem",
                "text": "保存棋谱",
                "height": dp(48),
                "on_release": lambda x="": self.saveXQF(),
             },
             {
                "viewclass": "OneLineListItem",
                "text": "另存棋谱",
                "height": dp(48),
                "on_release": lambda x="": self.saveAs(),
             },
             {
                "viewclass": "OneLineListItem",
                "text": "合并XQF",
                "height": dp(48),
                "on_release": lambda x="编辑": self.mergeXQF(),
             },
             {
                "viewclass": "OneLineListItem",
                "text": "xqf==>txt",
                "height": dp(48),
                "on_release": lambda x="xqf2txt": self.xqf2txt(x),
             },
             {
                "viewclass": "OneLineListItem",
                "text": "退到初始",
                "height": dp(48),
                "on_release": lambda x="初始局面": self.back_init(),
             },
             {
                "viewclass": "OneLineListItem",
                "text": "自动路演",
                "height": dp(48),
                "on_release": lambda x="自动路演": self.auto_roadshow(),
             },
             {
                "viewclass": "OneLineListItem",
                "text": "Test",
                "height": dp(48),
                "on_release": lambda x="Test": self.test_callback(x),
             }, 
             {
                "viewclass": "OneLineListItem",
                "text": "退出",
                "height": dp(48),
                "on_release": lambda x="Quit": self.stop(),
             },            
        ]
        self.menu = MDDropdownMenu(
            items=menu_items,
            width_mult=4,
        )
        
        parent = Builder.load_file("./main.kv")

        return parent
    
    def on_start(self):
        super().on_start()
        #此时棋盘还没在窗口上画出来，导致预期没达到
        """******draw_init_situation begin******
******draw_init_situation end******
******new_situation end******
[INFO   ] [Base        ] Start application main loop
[INFO   ] [Loader      ] using a thread pool of 2 workers
self.width=1366,self.height=399.36000000000007
取self.height=399.36000000000007的11等分作为格子的边长
self.grid_side_len=36.30545454545455,self.x_offset=501.4727272727272,self.y_offset=0
[INFO   ] [GL          ] NPOT texture support is available"""
        #self.new_situation()
    
    def new_situation(self):
        Logger.debug("X-Chess X-ChessApp:******new_situation begin******")
        self.menu.dismiss()

        self.chessmovesfilename = "新建局面"
        self.title = f"X-Chess 新建局面"

        self.next_camp = 'r'
        self.gameover = False

        self.xqfFile2048 = '58510a00000000000000000000000000000a141e28323c46500c4803172b3f5309131d27313b454f59114d061a2e425600000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
        
        init_situation='000a141e28323c46500c4803172b3f5309131d27313b454f59114d061a2e4256'
        #将初始局面字符串初始化到全局变量g_const_INIT_SITUATION
        init_g_init_situation(init_situation)

        #identifier让其默认生成，If identifier is absent, a UUID will be generated automatically.
        self.moves_tree.remove_subtree(nid=None)#清空以前的树
        self.moves_tree = Tree()
        nroot = self.moves_tree.create_node(tag=os.path.basename(self.chessmovesfilename), 
                data={'sp':'18','ep':'20','flag':'f0','rsv':'ff',
                      'notelen':'00000000','note':"",
                      'situation':g_const_INIT_SITUATION,'pieceWidget':None})  # 根节点
        
        #print("1111111111")
        #for i in self.root.ids:
        #    print(f"id:{i}")
        #print("22222222")


        #self.root.ids.id_moveslist.clear_widgets()
        #由于使用多个kv文件，导致self.root.ids不能访问到子kv模块中的ID，所以
        self.root.ids['id_screenmoves'].ids.id_moveslist.clear_widgets()
        self.root.ids['id_screenmoves'].ids.id_movesbranch.clear_widgets()
        #把根节点加入到招法列表中的第一项
        self.root.ids['id_screenmoves'].ids.id_moveslist.add_widget(OneLineListWithId(id=nroot.identifier,text=nroot.tag,font_style="H6"))#bg_color = [0,1,1,1])

        #将初始局面绘制到棋盘上
        self.draw_init_situation()

        Logger.debug("X-Chess X-ChessApp:******new_situation end******")
    
    #The MDDropdownMenu works well with the standard MDTopAppBar. 
    # Since the buttons on the Toolbar are created by the MDTopAppBar component, 
    # it is necessary to pass the button as an argument to the callback using lambda x: app.callback(x).
    def menucallback(self, button):
        self.menu.caller = button
        self.menu.open()
    
    def file_manager_open(self):
        #self.file_manager.show(os.path.expanduser("~"))
        # show the available disks first, then the files contained in them. Works correctly on: Windows, Linux, OSX, Android. Not tested on iOS.
        #self.file_manager.show_disks()
        
        """ if self.last_sel_path == "":
            if platform == "android":
                from android.storage import primary_external_storage_path
                SD_CARD = primary_external_storage_path()
                self.last_sel_path = os.path.join(SD_CARD)
            elif platform == "win":
                self.last_sel_path = os.path.expanduser("~")
            else:
                self.last_sel_path = os.path.expanduser("~")
        #当前目录
        #app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'xqf')
        toast(self.last_sel_path)
        self.file_manager.show(self.last_sel_path) """

        if self.last_sel_path == "":
            if platform == "android":
                #exs = os.getenv('EXTERNAL_STORAGE')
                #Logger.debug(f'X-Chess X_ChessApp: {exs=}')
                ##toast(exs)
                #appdata = os.getenv('APPDATA')
                ##toast(appdata)
                #Logger.debug(f'X-Chess X_ChessApp: {appdata=}')
                ##创建一个目录，试试
                #from android.storage import primary_external_storage_path
                #Logger.debug(f'X-Chess X_ChessApp: {primary_external_storage_path()=}')
                
                #x_chess_xqf = os.path.join(primary_external_storage_path(),'x_chess_xqf')
                #if not os.path.exists(x_chess_xqf):
                #    os.makedirs(x_chess_xqf)
                #self.last_sel_path  = x_chess_xqf
                self.last_sel_path = os.path.join(os.getcwd(),'xqf')
                self.file_manager.show(self.last_sel_path) 
            else:
                self.file_manager.show_disks()            
        else:
            #toast(self.last_sel_path)
            self.file_manager.show(self.last_sel_path)

        # output manager to the screen
        self.manager_open = True
    
    def events(self, instance, keyboard, keycode, text, modifiers):
        '''Called when buttons are pressed on the mobile device.'''

        if keyboard in (1001, 27):
            if self.manager_open:
                self.file_manager.back()
        return True
    
    def exit_manager(self, *args):
        '''Called when the user reaches the root of the directory tree.'''

        self.manager_open = False
        self.file_manager.close()
    
    def open_XQFFile(self, text_item):
        self.menu.dismiss()

        #print(f"{text_item=}")
        #Window.bind(on_keyboard=self.events)
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,#用户到达目录树根目录时调用的函数
            select_path=self.select_xqf_path,   #选择文件/目录时调用的函数
            icon_selection_button="pencil",
            selector='file',#只选择文件
            ext=['.xqf']
        )        
        
        self.file_manager_open()
        
    
    def select_xqf_path(self, path: str):
        '''
        It will be called when you click on the file name
        or the catalog selection button.

        :param path: path to the selected directory or file;
        '''

        self.last_sel_path = os.path.dirname(path)
        save_theLast_Path(self.last_sel_path)
        
        self.chessmovesfilename = path
        file_name = os.path.basename(self.chessmovesfilename)
        self.title = f"X-Chess {file_name[:-4]}"
        self.gameover  = False

        self.exit_manager()
        
        #print(f"{path=}")
        #将选择结果显示回显到屏幕上
        #toast(path)

        self.root.ids['id_screenmoves'].ids.id_moveslist.clear_widgets()
        self.root.ids['id_screenmoves'].ids.id_movesbranch.clear_widgets()

        self.readXQFFile(path)
    
    #创建招法树
    #此函数要在draw_init_situation之后执行，否则node中记录的widget为空
    def generate_moves_tree(self,chess_moves):
        Logger.debug("X-Chess X-ChessApp:******generate_moves_tree begin******")
        
        sx = sy = ex = ey = None

        moveslen = len(chess_moves) #用来判断是否跳出循环
        #print(f"棋谱长度：{moveslen=},记录：{chess_moves=}")

        #空着批注的长度
        note = ""
        #第5-8字节:为一个32位整数(x86格式,高字节在后)，表明本步批注的大小
        s = f'{chess_moves[14:16]}{chess_moves[12:14]}{chess_moves[10:12]}{chess_moves[8:10]}'
        notelen = int(s,16)
        #print(f"{notelen=},{chess_moves[8:16]},{chess_moves[16:16+notelen*2]=}")
        if notelen > 0:
            byte_str = binascii.unhexlify(chess_moves[16:16+notelen*2])
            note = byte_str.decode("gbk")
            #print(f"note:{note}")
        
        #identifier让其默认生成，If identifier is absent, a UUID will be generated automatically.
        self.moves_tree = self.moves_tree.remove_subtree(nid=None)#清空以前的树
        self.moves_tree = Tree()

        #flag = int(chess_moves[4:6],16)
        flag = chess_moves[4:6]#使用16进制字符串
        nroot = self.moves_tree.create_node(tag=os.path.basename(self.chessmovesfilename), 
                data={'sp':'18','ep':'20','flag':flag,'rsv':'ff',
                      'notelen':chess_moves[8:16],'note':note,
                      'situation':g_const_INIT_SITUATION,'pieceWidget':None})  # 根节点
        
        
        #把根节点加入到招法列表中的第一项
        self.root.ids['id_screenmoves'].ids.id_moveslist.add_widget(OneLineListWithId(id=nroot.identifier,text=nroot.tag,font_style="H6"))#bg_color = [0,1,1,1])
        
        #tv = ChessTreeView(root_options=dict(text=self.chessmovesfilename,font_size=10,color=[0,0,0,1]),
        #              hide_root=True,
        #              indent_level=8)
        #tv.size_hint = 1, None
        #tv.bind(minimum_height = tv.setter('height'))
        #tv.bind(minimum_width = tv.setter('width'))

        #print(f"nroot id==>{nroot.identifier}")

        i = 1#循环次数，便于调试        
        istart = 16 + notelen * 2
        #print(f"{istart=}")
        branchStack = [] #当前招法链枝点链表，后进先出
        branchStack.append(nroot)
        #tvbranchStack = [] #当前招法链枝点链表，后进先出
        #tvbranchStack.append(None)
        #f0branchStack = []#中间压入的f0节点，需要在出现 f0-->00时，全部从branchStack中删除
        n0 = nroot
        #tvn0 = None
        while istart < moveslen:
            #print(f"*** {i=} ***")

            #保存当前招法走后的局面
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
            if i == 1:#获取该谁走棋
                p = n0.data['situation'][f'{sx},{sy}']
                self.next_camp = p.camp
                print(f"该{self.next_camp=}走棋")

            # 走子前局面保存在其父节点中的data['situation']
            # print_situation("******走子前局面******",n0.data['situation'])

            if (f"{sx},{sy}" in n0.data['situation']) and isinstance(n0.data['situation'][f'{sx},{sy}'],Piece):
                #当前招法走子前的棋子实例，其x,y与sx，sy相同
                p = n0.data['situation'][f'{sx},{sy}']
                #print(f"网点：({sx},{sy}),棋子：{p.camp=},{p.identifier=},{p.x=},{p.y=},{p.pieceWidget=}")
                #print(f"网点：({sx},{sy}),棋子：{p}")

                #获取招法名称
                mn =p.getMoveName(ex,ey,n0.data['situation'])
                #print(f"{mn=}")

                #使用 copy 模块中的 deepcopy() 方法来创建原始 dictionary 的一个新的深度拷贝。深度拷贝为 dictionary 中的所有易变对象创建一个新的拷贝，
                #而不仅仅是创建对它们的引用。这意味着对新的 dictionary 中的易变对象所做的改变将不会影响到原来的 dictionary
                #深拷贝导致widget会被再次创建，
                #realtime_situation = copy.deepcopy(n0.data['situation'])

                #实现自我的深层拷贝：内部的对象的重新创建
                for m in range(0,9,1):#x坐标
                    for n in range(0,10,1):#y坐标
                        if (f"{m},{n}" in n0.data['situation']) and isinstance(n0.data['situation'][f'{m},{n}'],Piece):
                            p0 = n0.data['situation'][f'{m},{n}']
                            #创建新的对象
                            p1 = Piece(p0.camp,p0.identifier,p0.x,p0.y,p0.pieceWidget)
                            #此时p0 与 p1相同，指向相同的棋子Widget
                            realtime_situation[f'{m},{n}'] = p1                

                #print_situation("******deepcopy 后 realtime_situation******",realtime_situation)

                # #更新 实时局面 realtime_situation
                #起点置空
                realtime_situation[f'{sx},{sy}'] = None
                #终点指向新的Piece实例，其x,y为ex ey
                realtime_situation[f'{ex},{ey}'] = Piece(p.camp,p.identifier,ex,ey,p.pieceWidget)

                #print_situation("******更新后 realtime_situation******",realtime_situation)
            else:#todo 一般不会，除非异常，待完善代码结构
                print(f"异常了，当前局面{n0.data['situation']}中({sx},{sy})处没有棋子")
                print_situation("******异常局面******",n0.data['situation'])

                toast(f"异常了，当前局面{n0.data['situation']}中({sx},{sy})处没有棋子")
                break

            #print_situation("******走子后局面 realtime_situation******",realtime_situation)

            #movesname = f"{i: <3}{mn}-{chess_moves[istart:istart+2]}{chess_moves[istart+2:istart+4]}-{chess_moves[istart+4:istart+6]}"
            movesname = mn
            #print(f"{movesname=}")

            #获取当前招法的分支标记
            #flag = int(chess_moves[istart+4:istart+6],16)
            #print(f"{flag=},{chess_moves[istart+4:istart+6]}")
            flag = chess_moves[istart+4:istart+6]
            #print(f"{flag=}")

            note = ""
            #批注的长度
            s = f'{chess_moves[istart+14:istart+16]}{chess_moves[istart+12:istart+14]}{chess_moves[istart+10:istart+12]}{chess_moves[istart+8:istart+10]}'
            notelen = int(s,16)
            if notelen > 0:
                byte_str = binascii.unhexlify(chess_moves[istart+16:istart+16+notelen*2])
                note = byte_str.decode("gbk")
                #print(f"note:{note}")

            n = self.moves_tree.create_node(tag=movesname,parent = n0.identifier,
                                            data={'sp':chess_moves[istart:istart+2],'ep':chess_moves[istart+2:istart+4],'flag':flag,'rsv':'00',
                                                  'notelen':chess_moves[istart+8:istart+16],'note':note,
                                                  'situation':realtime_situation,'pieceWidget':p.pieceWidget,'sx':sx,'sy':sy,'ex':ex,'ey':ey
                                                  })

            #Logger.debug(f"X-Chess X-ChessApp:{movesname}=={n.identifier}")
            #tvn = tv.add_node(TreeViewLabelWithId(id=n.identifier,text=f"{i: <3}{mn}",font_size=10,color=[0,0,0,1],is_open=False),tvn0)
            
            #print(f"current n0:{n0.tag},flag:{n0.data['flag']}")
            #print(f"n:{n.tag},flag:{n.data['flag']}")#,note:{n.data['note']}

            #print_situation("******走子后局面******",n.data['situation'])

            #str = ""
            #for item in branchStack:
            #    str = f"{str}{item.tag}==>"
            #print(f"之前叉点链表：{str}")

            #str = ""
            #for item in tvbranchStack:
            #    if item != None:
            #        str = f"{str}{item.text}==>"
            #    else:
            #        str = f"{str}None==>"
            #print(f"之前叉点链表：{str}")

            #print(f"{n.data['flag']=},{n0.data['flag']=}")

            #判断该节点是否有分支            
            if flag == 'f0':#240:#0xf0 中间节点,或者说其同级的最后一个
                n0 = n
                #tvn0 = tvn
            elif flag == 'ff':#255 : #0xff 分支节点
                #如果其父级是f0(f0同级的最后一个)，需要将其父级也压入堆栈
                if n0.data['flag'] == 'f0':#240:
                    #f0branchStack.append(n0)
                    branchStack.append(n0)
                    #tvbranchStack.append(tvn0)
                branchStack.append(n)#将该节点压入枝点链表，后进先出
                #tvbranchStack.append(tvn)
                n0 = n
                #tvn0 = tvn
            elif flag == '00':#00:
                ##如果其父级是f0(f0同级的最后一个)，将之前压入的f0节点从branchStack中删除
                #if (n0.data['flag'] == 240): #and (n0 == branchStack[len(branchStack)-1]):
                #    #branchStack.pop()
                #    for item in f0branchStack:
                #        branchStack.remove(item)
                #    f0branchStack.clear()

                #print("000000")
                #print(f"{n0.tag=},{branchStack[len(branchStack)-1].tag}")

                #从branchStack倒数，把之前压入的f0都弹出，直到遇到ff为止，并且把ff的也弹出
                if (n0.data['flag'] == 'f0') : #240
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
                    #tvbranchStack.pop()
                    
                if len(branchStack) > 0:
                    n0 = branchStack[len(branchStack)-1]
                else:#到根节点
                    n0 = nroot
                
                #print(f"{len(tvbranchStack)=}")                
                #if len(tvbranchStack) > 0:
                #    tvn0 = tvbranchStack[len(tvbranchStack)-1]
                #else:#到根节点
                #    tvn0 = None
            elif flag == '0f': #15:#15=0x0f,0f经验证是兄弟中所有单身汉中非最小的那些单身汉
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
                print(f"{flag=},pass")                
            else:
                print(f"xxx {i=}:{flag=},{chess_moves[istart+4:istart+6]}")
            
            #str = ""
            #for item in branchStack:
            #    str = f"{str}{item.tag}==>"
            #print(f"之后叉点链表：{str}")

            #str = ""
            #for item in tvbranchStack:
            #    if item != None:
            #        str = f"{str}{item.text}==>"
            #    else:
            #        str = f"{str}None==>"
            #print(f"之后叉点链表：{str}")
            
            #print(f"next n0:{n0.tag}")
            #if len(branchStack) > 0:
            #    print(f"lastest branchStack :{branchStack[len(branchStack)-1].tag}")
            #else:
            #    print(f"lastest branchStack :None")

            i = i+1
            #if i > 2:#循环次数，便于调试
            #    break            

            istart = istart + 16 + notelen * 2
            #print(f"next {istart=}")
            if istart >= moveslen:#没招了
                break

        #while循环结束

        #toast("解析完成")

        #self.moves_tree.save2file(filename="moves_tree.txt",sorting=False)

        
        print(f"节点数:{len(self.moves_tree)}")  # 节点数
        print(f"树的深度:{self.moves_tree.depth()}")  # 树的深度
        #self.moves_tree.show(sorting=False)  # 可能和创建顺序不同
        #print(self.moves_tree)
        #print(f"Dict:{self.moves_tree.to_dict(sort=False)}")
        
        #app.root.chessmanualtree.add_widget(tv)

        Logger.debug("X-Chess X-ChessApp:******generate_moves_tree end******")
    
    def draw_init_situation(self):
        Logger.debug("X-Chess X-ChessApp:******draw_init_situation begin******")

        #print_situation("******初始局面******",g_const_INIT_SITUATION)

        #清空棋盘,包括棋子和跟随框
        for child in self.root.ids['id_screenmain'].ids.id_chessboard.children[:]:
            self.root.ids['id_screenmain'].ids.id_chessboard.remove_widget(child)

        self.selectedmask1 = SelectedMaskWidget(size_hint=(None,None),center=[self.root.ids['id_screenmain'].ids.id_chessboard.width/2,self.root.ids['id_screenmain'].ids.id_chessboard.height/2])
        #sm = SelectedMaskWidget(size_hint=(None,None),center=[50,50])
        self.root.ids['id_screenmain'].ids.id_chessboard.add_widget(self.selectedmask1)

        self.selectedmask2 = SelectedMaskWidget(size_hint=(None,None),center=[self.root.ids['id_screenmain'].ids.id_chessboard.width/2,self.root.ids['id_screenmain'].ids.id_chessboard.height/2])
        self.root.ids['id_screenmain'].ids.id_chessboard.add_widget(self.selectedmask2)

        #print(f"{self.root.ids['id_screenmain'].ids.id_chessboard.width=}")
        #print(f"{self.root.ids['id_screenmain'].ids.id_chessboard.height=}")

        #X轴10等分比例：X方向，各网点位置相对于父组件的距离依次为0.1,0.2，……，0.9
        #self.x_bisection = 0.10
        #由于棋子是采用Scater缩放，导致中心点有变化，所以加上修正值，此值为不对手调值，不知道规律
        #self.x_corrected = self.root.ids['id_screenmain'].ids.id_chessboard.width * (-0.00)

        #y轴11等分比例：Y方向，各网点位置相对于父组件的距离依次为
        #self.y_bisection = 0.11
        #由于棋子是采用Scater缩放，导致中心点有变化，所以加上修正值，且y方向上下有空白，此值为不对手调值，不知道规律
        #self.y_corrected = self.root.ids['id_screenmain'].ids.id_chessboard.height * (-0.000)

        svg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'img')

        async def onebyone(self):
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
                        #print(f"网点：({x},{y}),棋子：{p.camp=},{p.identifier=},{p.x=},{p.y=}")

                        #xs = self.x_bisection * (x+1)
                        #ys = self.y_bisection * (y+1)
                        #cx = self.root.ids['id_screenmain'].ids.id_chessboard.width * (x+1) / 10.0 + self.x_corrected
                        #cy = self.root.ids['id_screenmain'].ids.id_chessboard.height * (y+1) / 11.0 + self.y_corrected
                        cx = self.root.ids['id_screenmain'].ids.id_chessboard.x_offset + self.root.ids['id_screenmain'].ids.id_chessboard.grid_side_len * (x+1)
                        cy = self.root.ids['id_screenmain'].ids.id_chessboard.y_offset + self.root.ids['id_screenmain'].ids.id_chessboard.grid_side_len * (y+1)

                        #piece = PieceWidget(svg_fn=f'img/{p.camp}{p.identifier}.svg',size_hint=(None,None),
                        #                    pos_hint={'center_x':self.x_bisection * (x+1) + self.x_corrected,'center_y':self.y_bisection * (y+1) + self.y_corrected})
                        #pw = PieceWidget(svg_fn=f'{svg_path}/{p.camp}{p.identifier}.svg',camp=p.camp,identifier=p.identifier,bx=p.x,by=p.y,size_hint=(None,None),center=[cx,cy])
                        
                        pw = PieceWidget(svg_fn=os.path.join(f'{svg_path}',f'{p.camp}{p.identifier}.svg'),
                                         camp=p.camp,identifier=p.identifier,bx=p.x,by=p.y,size_hint=(None,None),center=[cx,cy])
                        
                        p.pieceWidget = pw
                        
                        self.root.ids['id_screenmain'].ids.id_chessboard.add_widget(pw)

                        g_const_INIT_SITUATION[f'{x},{y}'] = p

                    #else:
                    #    print(f"网点：({x},{y}),棋子：None")
                    
                    #break
                #break
                #await asynckivy.sleep(1)
            #for 循环结束            
            
        asynckivy.start(onebyone(self))

        Logger.debug("X-Chess X-ChessApp:******draw_init_situation end******")
    
    def readXQFFile(self,filename):
        print("******readXQFFile begin******")

        print(f"{filename=}")

        # 打开文件
        with open(filename, 'rb') as file:
            # 读取文件内容
           content = file.read()
         
        # 将二进制data转换为16进制表示
        #hex_content = binascii.hexlify(content).decode('utf-8')
        #b2a_hex等同于hexlify，但函数名见名知意
        hex_content = binascii.b2a_hex(content).decode('utf-8')  
         
        # 输出16进制内容
        #print(f"{hex_content=}")

        #版本标记
        """
        XQF 1.0
        0000 - 0001：XQF文件标记，'XQ' (0000 = 'X', 0001 = 'Q') 
        0002       ：XQF文件版本号，0x0a 
        """
        version_tag = hex_content[0:6]
        print(f"版本标记：{version_tag=}")
        if version_tag != '58510a':
            toast(f"{filename} 不是XQF1.0格式，58510a !!!!!!!!!!!")
            return
        
        toast(f"{filename} 是XQF1.0格式，58510a，静待花开",duration=1.5)

        #保存打开的xqf文件头【0:2048]，便于保存或另存
        self.xqfFile2048 = hex_content[0:2048]
        #print(f"{self.xqfFile2048=}")

        #初始局面
        """
        0010 - 001f：依次记录红9路车、8路马、7路象、6路士、5路帅、4路士、3路象、2路马、1路车、8路炮、2路炮、9路兵、7路兵、5路兵、3路兵、1路兵的初始坐标位置
        0020 - 002f：依次记录黑1路车、2路马、3路象、4路士、5路帅、6路士、7路象、8路马、9路车、2路炮、8路炮、1路卒、3路卒、5路卒、7路卒、9路卒的初始坐标位置
        """
        init_situation = hex_content[32:96]
        print(f"初始局面{len(init_situation)}：{init_situation=}")
        #init_situation='000a141e28323c46500c4803172b3f5309131d27313b454f59114d061a2e4256'

        #将初始局面字符串初始化到全局变量g_const_INIT_SITUATION
        init_g_init_situation(init_situation)

        rst = check_situation(g_const_INIT_SITUATION)

        if  rst['result_code'] == False:#局面有误
            toast(rst['result_desc'],duration=5)
            return

        #将初始局面绘制到棋盘上
        self.draw_init_situation()

        self.generate_moves_tree(hex_content[2048:])

        #显示空着(初始局面)注解
        self.root.ids['id_screenmain'].ids.id_movesnote.text = self.moves_tree.get_node(self.moves_tree.root).data['note']

        print("******readXQFFile end******")
    
    def todo_list(self):
        print("todo_list begin")
        self.menu.dismiss()
        if not self.todo_dialog:
            self.todo_dialog = MDDialog(
                type="simple",
                #title="to do list",
                text="""
doing list:
1.测试

to do list:
1.开局库
2.皮卡鱼引擎
3.送将、困毙判断
4.走子后判断胜负
5.清理日志、备份文件
6.设置界面

done:
23-11-27 检查初始局面是否合法
23-12-01 走子&走子规则
23-12-05 编辑局面
23-12-08 保存xqf
"""
            )
        self.todo_dialog.open()
        print("todo_list end")
    
    def test_callback(self,menuname):
        print("test_callback begin")
        print(f"{menuname=}")
        self.menu.dismiss()
        toast("测试专用")
        print("test_callback end")
    
    def auto_roadshow(self):
        print("auto_roadshow begin")
        self.menu.dismiss()

        #招法树必须先有
        if self.moves_tree.root == None:
            return

        if len(self.moves_tree) == 0:
            return

        curNodeId = self.root.ids['id_screenmoves'].ids.id_moveslist.children[0].id

        #回到初始
        self.back_init()

        roadshowid=[]
        for nodeid in self.moves_tree.rsearch(curNodeId):
            #print(f"{self.moves_tree[nodeid].tag=}")
            roadshowid.append(nodeid)
        #把根节点弹出来
        roadshowid.pop()
        
        async def onebyone():
            #self.root.ids['id_screenmain'].ids.id_bottombar.disabled = True
            self.root.ids['id_screenmain'].disabled = True
            print("onebyone begin")
            #使用[::-1]来设置切片的步长为-1，从而实现了倒序遍历
            for id in roadshowid[::-1]:
                node = self.moves_tree.get_node(id)
                #print(f"{node.tag=}")
                plus = ""
                if len(self.moves_tree.children(node.identifier)) > 1:#其下有多个招法，添加一个+号
                    plus = "+"
                num = len(self.root.ids['id_screenmoves'].ids.id_moveslist.children)
                self.root.ids['id_screenmoves'].ids.id_moveslist.add_widget(OneLineListWithId(id=node.identifier,
                                                                            text=f"{plus}{num:<3}{node.tag}",font_style="H6"))#,bg_color = [0,1,1,1]))
                
                p = node.data['pieceWidget']
                if p and isinstance(p,PieceWidget):
                    parent = self.moves_tree.parent(node.identifier)
                    node.data['pieceWidget'].movexy(node.data['sx'],node.data['sy'],node.data['ex'],node.data['ey'],'F',parent.data['situation'])
                    
                #显示招法注解
                self.root.ids['id_screenmain'].ids.id_movesnote.text = node.data['note']

                #time.sleep(1)
                await asynckivy.sleep(3)

            #self.root.ids['id_screenmain'].ids.id_bottombar.disabled = False
            self.root.ids['id_screenmain'].disabled = False

            toast("回放结束")
            print("onebyone end")        
        
        toast("自动回放中，静待花开……",duration=len(roadshowid)*3 + 1)        
        asynckivy.start(onebyone())
        
        print("auto_roadshow end")
    
    def back_init(self):
        print("back_init begin")
        self.menu.dismiss()

        #招法树必须先有
        if self.moves_tree.root == None:
            return

        if len(self.moves_tree) > 0:
            id = self.root.ids['id_screenmoves'].ids.id_moveslist.children[0].id
            curid = None
            if id != None:
                curid = id
                while True:#循环到下一个分支点，或者结尾
                    parent = self.moves_tree.parent(curid)
                    if parent == None:
                        break
                    
                    node = self.moves_tree.get_node(curid)
                    if node != None:
                        p = node.data['pieceWidget']
                        if p and isinstance(p,PieceWidget):
                            p.movexy(node.data['ex'],node.data['ey'],node.data['sx'],node.data['sy'],'B',parent.data['situation'])
                            self.root.ids['id_screenmoves'].ids.id_moveslist.remove_widget(self.root.ids['id_screenmoves'].ids.id_moveslist.children[0])
                            curid = self.root.ids['id_screenmoves'].ids.id_moveslist.children[0].id
                            #显示招法注解
                            self.root.ids['id_screenmain'].ids.id_movesnote.text = parent.data['note']
                        else:
                            break
                    else:
                        break
                #end while
            #end if id != None:

        #清除走法示意线
        self.root.ids['id_screenmain'].ids.id_chessboard.remove_Allarrows()
                
        self.selectedmask1.center=[self.root.ids['id_screenmain'].ids.id_chessboard.width/2,self.root.ids['id_screenmain'].ids.id_chessboard.height/2]
        self.selectedmask2.center=[self.root.ids['id_screenmain'].ids.id_chessboard.width/2,self.root.ids['id_screenmain'].ids.id_chessboard.height/2]

        print("back_init end")
    
    def previous_branch(self):
        print("previous_branch begin")
        if self.chessmovesfilename == "":
            toast('请先打开棋谱或新建局面')
            return
        
        #招法树必须先有
        if self.moves_tree.root == None:
            return
        if self.gameover == True:
            self.gameover = False

        id = self.root.ids['id_screenmoves'].ids.id_moveslist.children[0].id
        curid = None
        moves_num = None
        if id != None:
            curid = id
            while True:#循环到下一个分支点，或者结尾
                parent = self.moves_tree.parent(curid)
                if parent == None:
                    break
                
                node = self.moves_tree.get_node(curid)
                if node != None:
                    p = node.data['pieceWidget']
                    if p and isinstance(p,PieceWidget):
                        p.movexy(node.data['ex'],node.data['ey'],node.data['sx'],node.data['sy'],'B',parent.data['situation'])
                        self.root.ids['id_screenmoves'].ids.id_moveslist.remove_widget(self.root.ids['id_screenmoves'].ids.id_moveslist.children[0])
                        curid = self.root.ids['id_screenmoves'].ids.id_moveslist.children[0].id
                        #显示招法注解
                        self.root.ids['id_screenmain'].ids.id_movesnote.text = parent.data['note']

                        childs = self.moves_tree.children(parent.identifier)
                        moves_num = len(childs)
                        if moves_num > 1:
                            #画出对方应对此招的走法示意线
                            self.root.ids['id_screenmain'].ids.id_chessboard.remove_Allarrows()
                            for item in self.moves_tree.children(parent.identifier):
                                self.root.ids['id_screenmain'].ids.id_chessboard.add_arrow(item.data['sx'],item.data['sy'],item.data['ex'],item.data['ey'])

                            break
                        elif moves_num == 0:
                            break
                        else:# == 1
                            continue
                    else:
                        break
                else:
                    break
            #end while
        #end if id != None:

        print("previous_branch end")

    def next_branch(self):
        print("next_branch begin")
        if self.chessmovesfilename == "":
            toast('请先打开棋谱或新建局面')
            return
        
        #招法树必须先有
        if self.moves_tree.root == None:
            return
        if self.gameover == True:
            toast("此局已结束")
            return

        id = self.root.ids['id_screenmoves'].ids.id_moveslist.children[0].id
        childid = None
        moves_num = None
        if id != None:
            childid = id
            while True:#循环到下一个分支点，或者结尾
                childs = self.moves_tree.children(childid)
                moves_num = len(childs)
                if moves_num > 1:
                    child = childs[0]
                    break
                elif moves_num == 0:
                    child = self.moves_tree.get_node(childid)
                    break
                else:# == 1
                    childid = childs[0].identifier

                    node = childs[0]
                    plus = ""
                    if len(self.moves_tree.children(node.identifier)) > 1:#其下有多个招法，添加一个+号
                        plus = "+"
                    num = len(self.root.ids['id_screenmoves'].ids.id_moveslist.children)
                    wg = OneLineListWithId(id=node.identifier,text=f"{plus}{num:<3}{node.tag}",font_style="H6")
                    aa = self.root.ids['id_screenmoves'].ids.id_moveslist.add_widget(wg)#,bg_color = [0,1,1,1]))
                    p = node.data['pieceWidget']
                    if p and isinstance(p,PieceWidget):
                        parent = self.moves_tree.parent(node.identifier)
                        node.data['pieceWidget'].movexy(node.data['sx'],node.data['sy'],node.data['ex'],node.data['ey'],'F',parent.data['situation'])
                
                    #显示招法注解
                    self.root.ids['id_screenmain'].ids.id_movesnote.text = node.data['note']

                    #画出对方应对此招的走法示意线
                    self.root.ids['id_screenmain'].ids.id_chessboard.remove_Allarrows()
                    for item in self.moves_tree.children(node.identifier):
                        self.root.ids['id_screenmain'].ids.id_chessboard.add_arrow(item.data['sx'],item.data['sy'],item.data['ex'],item.data['ey'])

                    #aa.ask_update()
                    #self.root.do_layout()

                    #time.sleep(5)

                    continue
            #end while
        #end if id != None:
        
        if  moves_num > 1:#多个招法，需选择
            bottom_sheet_menu = MDListBottomSheet()
            for item in self.moves_tree.children(childid):
                print(f"{item.tag=},{item.identifier=}")
                bottom_sheet_menu.add_item(
                    f"{item.tag}"
                    ,lambda x,y=item.tag,z=item.identifier: self.showallnextmoves(f"{y}",f"{z}")
                )        
            bottom_sheet_menu.open()
        elif moves_num == 0:
            toast(f"{self.moves_tree.get_node(self.root.ids['id_screenmoves'].ids.id_moveslist.children[0].id).tag} 之后无谱了！")            
        
        print("next_branch end")

    
    def previous_moves(self):
        print("previous_moves begin")
        if self.chessmovesfilename == "":
            toast('请先打开棋谱或新建局面')
            return
        
        #招法树必须先有
        if self.moves_tree.root == None:
            return
        
        if self.gameover == True:
            self.gameover = False

        node = self.moves_tree.get_node(self.root.ids['id_screenmoves'].ids.id_moveslist.children[0].id)
        if node != None:
            #print(f"{node.tag},{node.data['pieceWidget']}")
            parent = self.moves_tree.parent(node.identifier)
            if parent != None:
                p = node.data['pieceWidget']
                if p and  isinstance(p,PieceWidget):
                    parent = self.moves_tree.parent(node.identifier)
                    node.data['pieceWidget'].movexy(node.data['ex'],node.data['ey'],node.data['sx'],node.data['sy'],'B',parent.data['situation'])

                    self.root.ids['id_screenmoves'].ids.id_moveslist.remove_widget(self.root.ids['id_screenmoves'].ids.id_moveslist.children[0])
                    #for child in self.root.ids['id_screenmoves'].ids.id_moveslist.children[:]:
                    #    print(f"{child.id=},{child.text=}")
                
                #显示招法注解
                self.root.ids['id_screenmain'].ids.id_movesnote.text = parent.data['note']

                #画出对方应对此招的走法示意线
                self.root.ids['id_screenmain'].ids.id_chessboard.remove_Allarrows()
                for item in self.moves_tree.children(parent.identifier):
                    self.root.ids['id_screenmain'].ids.id_chessboard.add_arrow(item.data['sx'],item.data['sy'],item.data['ex'],item.data['ey'])
        
        print("previous_moves end")
    
    def next_moves(self):
        print("next_moves begin")

        if self.chessmovesfilename == "":
            toast('请先打开棋谱或新建局面')
            return

        #招法树必须先有
        if self.moves_tree.root == None:
            return
        
        if self.gameover == True:
            toast("此局已结束！")
            return

        #MDList的最后一个item
        id = self.root.ids['id_screenmoves'].ids.id_moveslist.children[0].id
        if id != None:        
            childs = self.moves_tree.children(id)
            moves_num = len(childs)
            print(f"{moves_num=}")

            if  moves_num > 1:#多个招法，需选择
                bottom_sheet_menu = MDListBottomSheet()
                for item in self.moves_tree.children(id):
                    #print(f"{item.tag=},{item.identifier=}")
                    bottom_sheet_menu.add_item(
                        f"{item.tag}"
                        ,lambda x,y=item.tag,z=item.identifier: self.showallnextmoves(f"{y}",f"{z}")
                    )        
                bottom_sheet_menu.open()
            elif moves_num == 1:
                node = childs[0]
                #print(f"{node.tag=},{node.identifier=}")

                plus = ""
                if len(self.moves_tree.children(node.identifier)) > 1:#其下有多个招法，添加一个+号
                    plus = "+"
                num = len(self.root.ids['id_screenmoves'].ids.id_moveslist.children)
                self.root.ids['id_screenmoves'].ids.id_moveslist.add_widget(OneLineListWithId(id=node.identifier,
                                                                        text=f"{plus}{num:<3}{node.tag}",font_style="H6"))#,bg_color = [0,1,1,1]))
                p = node.data['pieceWidget']
                if p and  isinstance(p,PieceWidget):
                    parent = self.moves_tree.parent(node.identifier)
                    #print(f"{parent.identifier=},{parent.tag=}")
                    #print_situation("******parent局面******",parent.data['situation'])

                    #print(f"{node.identifier=},{node.tag=},{node.data['sx']=},{node.data['sy']=},{node.data['ex']=},{node.data['ey']=}")
                    #print_situation("******node局面******",node.data['situation'])

                    node.data['pieceWidget'].movexy(node.data['sx'],node.data['sy'],node.data['ex'],node.data['ey'],'F',parent.data['situation'])
                
                #显示招法注解
                self.root.ids['id_screenmain'].ids.id_movesnote.text = node.data['note']

                #画出对方应对此招的走法示意线
                self.root.ids['id_screenmain'].ids.id_chessboard.remove_Allarrows()
                for item in self.moves_tree.children(node.identifier):
                    self.root.ids['id_screenmain'].ids.id_chessboard.add_arrow(item.data['sx'],item.data['sy'],item.data['ex'],item.data['ey'])


            else:
                toast(f"{self.moves_tree.get_node(self.root.ids['id_screenmoves'].ids.id_moveslist.children[0].id).tag} 之后无谱了！")
        
        #toast(f'{self.next_camp}')
        
        print("next_moves end")
    
    def showallnextmoves(self, *args):
        #toast(f"{args[0]},{args[1]}")
        nodeid = args[1]
        node = self.moves_tree.get_node(nodeid)
        if node != None:
            #print(f"{node.tag},{node.data['pieceWidget']}")
            plus = ""
            if len(self.moves_tree.children(node.identifier)) > 1:#其下有多个招法，添加一个+号
                plus = "+"
            num = len(self.root.ids['id_screenmoves'].ids.id_moveslist.children)
            self.root.ids['id_screenmoves'].ids.id_moveslist.add_widget(OneLineListWithId(id=node.identifier,text=f"{plus}{num:<3}{node.tag}",font_style="H6"))#,bg_color = [0,1,1,1]))
            p = node.data['pieceWidget']
            if p and isinstance(p,PieceWidget):
                parent = self.moves_tree.parent(node.identifier)
                node.data['pieceWidget'].movexy(node.data['sx'],node.data['sy'],node.data['ex'],node.data['ey'],'F',parent.data['situation'])
            
            #显示招法注解
            self.root.ids['id_screenmain'].ids.id_movesnote.text = node.data['note']

            #画出对方应对此招的走法示意线
            self.root.ids['id_screenmain'].ids.id_chessboard.remove_Allarrows()
            for item in self.moves_tree.children(node.identifier):
                self.root.ids['id_screenmain'].ids.id_chessboard.add_arrow(item.data['sx'],item.data['sy'],item.data['ex'],item.data['ey'])
    

    
        
    def xqf2txt(self, text_item):
        #print(f"{text_item=}")
        self.menu.dismiss()

        #Window.bind(on_keyboard=self.events)
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,#用户到达目录树根目录时调用的函数
            select_path=tree2txt,   #选择文件/目录时调用的函数
            icon_selection_button="pencil",
            selector='file',#只选择文件
            ext=['.xqf']
        )
        
        self.file_manager_open()
    
    def edit_situation(self):
        #print("******edit_situation begin******")
        self.menu.dismiss()

        app = MDApp.get_running_app()

        app.root.current_heroes = ""
        app.root.current = "screenEditSituation"

        #print("******edit_situation end******")
    
    def edit_situation_done(self):
        print("******edit_situation_done begin******")

        print(f'{self.next_camp=}')

        #print("full_situation='000a141e28323c46500c4803172b3f5309131d27313b454f59114d061a2e4256'")

        #找到哪些棋子落在棋盘上
        childs = []
        for child in self.root.ids['id_screditsituiation'].ids.id_chessboard2.children[:]:
            if isinstance(child,PieceWidget2) and child.bx != child.old_x and child.by != child.old_y:
                childs.append(child)

        #初始局面
        xqf_init=""
        for i in range(0,32,1):
            xqf_location = 'ff'
            if i < 16:#红                
                for item in childs:
                    if item.camp == 'r' and item.identifier == g_const_S_P_ORDEER[i]:
                        childs.remove(item)#从列表中删除
                        #当前棋子的棋盘坐标
                        xqf_location = f'{item.bx * 10 + item.by:x}'
                        xqf_location = f'{xqf_location:0>2}'#前补0
                        break
            else :#黑
                for item in childs:
                    if item.camp == 'b' and item.identifier == g_const_S_P_ORDEER[i]:
                        childs.remove(item)#从列表中删除
                        xqf_location = f'{item.bx * 10 + item.by:x}'
                        xqf_location = f'{xqf_location:0>2}'#前补0
                        break

            xqf_init = f'{xqf_init}{xqf_location}'

        #print(f"end：{xqf_init=}")

        xchess_init = {}
        xqfinit2xchessinit(xqf_init,xchess_init)
        rst = check_situation(xchess_init)
        if  rst['result_code'] == False:#局面有误
            Logger.debug(f"X-Chess edit_situation_done: {rst['result_desc']}")
            toast(rst['result_desc'],duration=5)
            return

        app = MDApp.get_running_app()
        app.root.current_heroes = ""
        app.root.current = "screenMain"

        self.chessmovesfilename = "新建局面"
        self.title = f"X-Chess 新建局面"
        self.gameover = False

        self.xqfFile2048 = f'58510a00000000000000000000000000{xqf_init}00000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'

        #将初始局面字符串初始化到全局变量g_const_INIT_SITUATION
        init_g_init_situation(xqf_init)

        print(f"{self.next_camp=}")

        #identifier让其默认生成，If identifier is absent, a UUID will be generated automatically.
        self.moves_tree.remove_subtree(nid=None)#清空以前的树
        self.moves_tree = Tree()
        nroot = self.moves_tree.create_node(tag=os.path.basename(self.chessmovesfilename), 
                data={'sp':'18','ep':'20','flag':'f0','rsv':'ff',
                      'notelen':'00000000','note':"",
                      'situation':g_const_INIT_SITUATION,'pieceWidget':None})  # 根节点
        
        
        self.root.ids['id_screenmoves'].ids.id_moveslist.clear_widgets()
        self.root.ids['id_screenmoves'].ids.id_movesbranch.clear_widgets()
        #把根节点加入到招法列表中的第一项
        self.root.ids['id_screenmoves'].ids.id_moveslist.add_widget(OneLineListWithId(id=nroot.identifier,text=nroot.tag,font_style="H6"))#bg_color = [0,1,1,1])

        #将初始局面绘制到棋盘上
        self.draw_init_situation()

        print("******edit_situation_done end******")

    def info(self):
        self.root.ids['id_screeninfo'].ids.id_info.text="""
X-Chess：中国象棋打谱助手
作者：3037609807@qq.com
QQ群：780150228
开源地址：https://github.com/yingyan005/X-Chess
缘由：不胜其烦的广告，恰好接触到Kivy(Python cross-platform GUI)，那就练练手
目标：学习象棋的打谱小工具
特点：
        开源、免费、无广告、不收集信息
        借助Kivy特点，可运行在Android, iOS, Linux, macOS and Windows

待实现：
        接入免费开源引擎皮卡鱼
        支持开局库

版本0.02:
        修复已知bug
        内置开源引擎XQPy
            (象棋巫师非官方python实现,https://github.com/bupticybee/XQPy)
        增加合并XQF棋谱功能，示例如下：
*棋谱1开局
└── 1  红兵7进1
    └── 2  黑马8进7
        └── 3  红马8进7
            └── 4  黑炮2平3
*棋谱2开局
└── 1  红马8进7
    └── 2  黑马8进7
        └── 3  红兵7进1
            └── 4  黑卒7进1

**X-Chess合并后
开局
├── 1  红兵7进1
│   └── 2  黑马8进7
│       └── 3  红马8进7
│           ├── 4  黑炮2平3
│           └── 5  黑卒7进1
└── 6  红马8进7
    └── 7  黑马8进7
        └── 8  红兵7进1
            ├── 9  黑卒7进1
            └── 10 黑炮2平3


版本0.01:
        实现xqf打谱功能


鸣谢：
        XQF作者：公开了1.0规范
        网络资料提供者：技术文档、象棋素材
        热心的棋友，不一一列举了

"""

        app = MDApp.get_running_app()
        app.root.current_heroes = ""
        app.root.current = "ScreenInfo"
        
    def bakupXQF(self,filename):
        Logger.debug(f'X-Chess bakupXQF: begin')
        #备份小心驶得万年船
        #由于pyinstall打包成exe后，__file__非我所想要的，且是临时目录，退出exe后临时目录就被清空了
        #bak_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'xbak')
        bak_path = os.path.join(os.getcwd(),'xbak')
        if not os.path.exists(bak_path):
            os.makedirs(bak_path)
            
        cur_time = f'{time.strftime("%Y-%m-%d %H-%M-%S", time.localtime())}'
        bak_filename = os.path.join(f'{bak_path}',f'{os.path.basename(filename)}.{cur_time}')
        Logger.debug(f'X-Chess bakupXQF: {bak_filename=}')

        with open(self.chessmovesfilename, 'rb') as fsrc, open(bak_filename, 'wb') as fdst:
            # 逐块1MB读取和写入数据
            while True:
                buf = fsrc.read(1024 * 1024)
                if buf:
                    fdst.write(buf)
                else:
                    break
        Logger.debug(f'X-Chess bakupXQF: end')
    
    def letsfight(self):
        Logger.debug(f'X-Chess letsfight: begin')

        if self.chessmovesfilename == "":
            toast('彩旗飘飘')
            self.new_situation()            
            return
        
        if len(self.moves_tree) <2 :#至少要走一步
            toast("至少要走1步")
            return
        
        if self.chessmovesfilename == "新建局面":#输入文件名
            self.root.current_heroes = ""
            self.root.current = "ScreenInputFileName"
            """ if self.last_sel_path == "":
                if platform == "android":
                    self.last_sel_path = os.path.join(os.getenv('EXTERNAL_STORAGE'))
                elif platform == "win":
                    self.last_sel_path = os.path.expanduser("~")
                else:
                    self.last_sel_path = os.path.expanduser("~") """
            self.root.ids['id_scrinputfilename'].ids['id_filepath'].text = self.last_sel_path
            self.root.ids['id_scrinputfilename'].ids['id_savebtn'].text = '保存'
        else:
            Logger.debug(f'X-Chess saveFileXQF: 开始备份')
            self.bakupXQF(self.chessmovesfilename)
            saveMovestreeToXQF(self.moves_tree,self.xqfFile2048,self.chessmovesfilename) 
        
        Logger.debug(f'X-Chess letsfight: end')       
        
    
    def saveXQF(self):
        print("******saveXQF begin******")

        self.menu.dismiss()

        if len(self.moves_tree) <2 :#至少要走一步
            toast("至少要走1步")
            return

        #print(f"{self.chessmovesfilename=}")
        
        if self.chessmovesfilename == "":
            toast('请先打开棋谱或新建局面，才需要保存')
            return
        if self.chessmovesfilename == "新建局面":#输入文件名
            self.root.current_heroes = ""
            self.root.current = "ScreenInputFileName"
            #self.root.ids['id_scrinputfilename'].ids['id_filepath'].text = os.path.join(os.path.dirname(os.path.abspath(__file__)),'xqf')
            """ if self.last_sel_path == "":
                if platform == "android":
                    self.last_sel_path = os.path.join(os.getenv('EXTERNAL_STORAGE'))
                elif platform == "win":
                    self.last_sel_path = os.path.expanduser("~")
                else:
                    self.last_sel_path = os.path.expanduser("~") """
            self.root.ids['id_scrinputfilename'].ids['id_filepath'].text = self.last_sel_path
            self.root.ids['id_scrinputfilename'].ids['id_savebtn'].text = '保存'
        else:
            self.bakupXQF(self.chessmovesfilename)
            saveMovestreeToXQF(self.moves_tree,self.xqfFile2048,self.chessmovesfilename)        

        print("******saveXQF end******")
    
    def set_select_path(self, path: str,screenid=None,filenameid=None):
        self.last_sel_path = path
        save_theLast_Path(self.last_sel_path)

        app = MDApp.get_running_app()
        if screenid and filenameid:
            self.root.ids[f'{screenid}'].ids[f'{filenameid}'].text=path
        self.exit_manager()
        toast(path)
    
    def select_savepath(self,screenid,filenameid):
        #Window.bind(on_keyboard=self.events)
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,#用户到达目录树根目录时调用的函数
            select_path=lambda path:self.set_select_path(path,screenid=screenid,filenameid=filenameid),   #选择文件/目录时调用的函数
            icon_selection_button="hand-pointing-left",
            search='dirs',
            selector='folder'#只选择目录            
        )

        """ if self.last_sel_path == "":
            if platform == "android":
                self.last_sel_path = os.path.join(os.getenv('EXTERNAL_STORAGE'))
            elif platform == "win":
                self.last_sel_path = os.path.expanduser("~")
            else:
                self.last_sel_path = os.path.expanduser("~")
        
        #self.file_manager.show(os.path.join(os.path.dirname(os.path.abspath(__file__)),'xqf'))  # output manager to the screen
        self.file_manager.show(self.last_sel_path) """

        if self.last_sel_path == "":
            self.file_manager.show_disks()
        else:
            toast(self.last_sel_path)
            self.file_manager.show(self.last_sel_path)
            
        self.manager_open = True
    
    def saveAs(self):
        print("******saveAs begin******")
        self.menu.dismiss()

        if self.chessmovesfilename == "":
            toast('请先打开棋谱,才需要另存吧')
            return
        
        if len(self.moves_tree) <2 :#至少要走一步
            toast("至少要走1步")
            return

        self.root.current_heroes = ""
        self.root.current = "ScreenInputFileName"
        #self.root.ids['id_scrinputfilename'].ids['id_filepath'].text = os.path.join(os.path.dirname(os.path.abspath(__file__)),'xqf')
        """ if self.last_sel_path == "":
            if platform == "android":
                self.last_sel_path = os.path.join(os.getenv('EXTERNAL_STORAGE'))
            elif platform == "win":
                self.last_sel_path = os.path.expanduser("~")
            else:
                self.last_sel_path = os.path.expanduser("~") """
        self.root.ids['id_scrinputfilename'].ids['id_filepath'].text = self.last_sel_path
        self.root.ids['id_scrinputfilename'].ids['id_savebtn'].text = '另存'
        
        print("******saveAs end******")
    
    def in_the_future(self):
        toast("快了，快了，静待花开！！！")
    
    def delete_movesdlg(self):
        Logger.debug(f'X-Chess delete_movesdlg: begin')        

        #招法树必须先有
        if self.moves_tree.root == None:
            return
        
        num = len(self.root.ids['id_screenmoves'].ids.id_moveslist.children)        
        if num < 2:
            toast("还没出招呢，无招可删")
            return
        
        Logger.debug(f"X-Chess delete_movesdlg: 当前招法：id={self.root.ids['id_screenmoves'].ids.id_moveslist.children[0].id},{self.root.ids['id_screenmoves'].ids.id_moveslist.children[0].text}")
        #nodeid = self.root.ids['id_screenmoves'].ids.id_moveslist.children[0].id

        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None

        if not self.dialog:        
            self.dialog = MDDialog(
                text= f"真的要删除当前招法：\n{self.root.ids['id_screenmoves'].ids.id_moveslist.children[0].text}？删除后将无法恢复！",
                buttons=[
                    MDFlatButton(
                        text="取消", text_color=self.theme_cls.primary_color, on_release = self.closeDialog
                    ),
                    MDFlatButton(
                        text="删除", text_color=self.theme_cls.primary_color, on_release = self.delete_moves
                    ),
                ],
            )
        self.dialog.open()

        Logger.debug(f'X-Chess delete_movesdlg: end')
    
    def closeDialog(self,inst):
        self.dialog.dismiss()
    
    def delete_moves(self,inst):
        Logger.debug(f'X-Chess delete_moves: begin')
        nodeid = self.root.ids['id_screenmoves'].ids.id_moveslist.children[0].id
        #Logger.debug(f'X-Chess delete_moves: {nodeid=}')

        self.dialog.dismiss()
        
        if self.moves_tree:
            node = self.moves_tree.get_node(nodeid)
            if node != None :
                Logger.debug(f"X-Chess delete_moves : {node.tag=},{node.data['flag']=}")
                self.previous_moves()
                flag = node.data['flag']                

                n0 = self.moves_tree.parent(nodeid)
                if n0.identifier != self.moves_tree.root:#根节点不用修改
                    childnums = len(self.moves_tree.children(n0.identifier)) - 1 #减去自身
                    Logger.debug(f"X-Chess delete_moves : {n0.tag=},{n0.data['flag']=},{childnums=}")
                    if childnums == 0:                        
                        n0.data['flag'] = '00'
                    elif childnums == 1:                        
                        n0.data['flag'] = 'f0'
                    
                    if childnums >= 1:
                        #修改兄弟中最后1个是ff的将其flag==>f0
                        lastSibff = None
                        lastSib0f = None
                        for item in self.moves_tree.siblings(nodeid):#疑问：是否是按照创建顺序排序未知，先假定如此吧
                            Logger.debug(f"X-Chess delete_moves : {item.tag=},{item.data['flag']=}")
                            if item.data['flag'] == 'ff':
                                lastSibff = item
                            if flag == '00' and item.data['flag'] == '0f':
                                lastSib0f = item
                        if lastSibff:
                            Logger.debug(f"X-Chess delete_moves : {lastSibff.tag=},{lastSibff.data['flag']=}")
                            lastSibff.data['flag'] = 'f0'
                        if lastSib0f:
                            Logger.debug(f"X-Chess delete_moves : {lastSib0f.tag=},{lastSib0f.data['flag']=}")
                            lastSib0f.data['flag'] = '00' 
                
                num = self.moves_tree.remove_node(nodeid)
                Logger.debug(f"X-Chess delete_moves: 删除{node.tag=},{node.data['flag']=},共个 {num} 节点")
                
            else:
                Logger.debug(f'X-Chess delete_moves: 树中无此节点:{nodeid=}')
        else:
            Logger.debug(f'招法树为空')

        Logger.debug(f'X-Chess delete_moves: end')
    
    #pyinstaller打包成exe后，会出现： Unable to import package ，so改到py中
    def edit_situation_full(self):
        edit_situation_full()
    
    def edit_situation_clear(self):
        edit_situation_clear()
    
    def edit_situation_cancle(self):
        edit_situation_cancle()
    
    def back_mainScreen(self):
        self.root.current_heroes = ""
        self.root.current = "screenMain"
    
    def saveFileXQF(self):
        saveFileXQF()
    
    def mergeXQF(self):
        self.menu.dismiss()
        app = MDApp.get_running_app()
        app.root.current_heroes = ""
        app.root.current = "ScreenMergeXQF"
    
    def set_xqffile(self, path: str,screenid=None,filenameid=None):
        self.exit_manager()
        #print(f"***set_xqffile {path=},{screenid=},{filenameid=}***")
        if screenid and filenameid:
            self.root.ids[f'{screenid}'].ids[f'{filenameid}'].text=path
    
    def select_xqffile(self,screenid,filenameid):
        Logger.debug(f'X-Chess select_xqffile: begin')

        #Window.bind(on_keyboard=self.events)
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,#用户到达目录树根目录时调用的函数
            select_path=lambda path:self.set_xqffile(path,screenid=screenid,filenameid=filenameid),   #选择文件/目录时调用的函数
            icon_selection_button="pencil",
            selector='file',#只选择文件
            ext=['.xqf']            
        )

        self.file_manager_open()

        Logger.debug(f'X-Chess select_xqffile: end')
    
    def generate_merge_tree(self):
        Logger.debug(f'X-Chess generate_merge_tree: begin')

        filenames = []
        mergeTree = Tree()

        filename01 = self.root.ids['id_screenmergexqf'].ids['id_filename01'].text
        if filename01 == "":
            toast("请选择第1个文件")
            return
        if not os.path.exists(filename01):
            toast(f"{filename01}，不存在！")
            return
        
        #注意顺序，第一个文件将作为主文件
        filenames.append(filename01)
        
        filename02 = self.root.ids['id_screenmergexqf'].ids['id_filename02'].text
        #filename03 = self.root.ids['id_screenmergexqf'].ids['id_filename03'].text
        #Logger.debug(f'X-Chess generate_merge_tree: {filename02=}，{filename03=}')

        #if filename02 == "" and filename03 == "":
        #    toast("第2个文件和第3个文件至少应有1个")
        #    return
        if filename02 == "":
            toast("第2个文件必须指定")
            return
        
        if filename01.casefold() == filename02.casefold() :
            toast("应指定两个不同的文件")
            return        
        
        if  os.path.exists(filename02):
            filenames.append(filename02)

        #if  os.path.exists(filename03):
        #    filename.append(filename03)
        
        mergefn = os.path.join(f"{self.root.ids['id_screenmergexqf'].ids['id_filepath'].text}",f"{self.root.ids['id_screenmergexqf'].ids['id_filename'].text}")
        #如果没有.xqf后缀，则自动补上
        if len(mergefn) > 4 and mergefn[-4:].lower() != '.xqf':
            mergefn = f"{mergefn}.xqf"
        elif len(mergefn) > 4 and mergefn[-4:].lower() == '.xqf':
            mergefn = f"{mergefn[:-4]}.xqf"
        else:
            mergefn = f"{mergefn}.xqf"
        print(f'{mergefn=}')

        if  os.path.exists(mergefn):
            toast(f"{mergefn} 已存在，请指定1个不存在的文件")
            return
        
        self.root.ids['id_screenmergexqf'].ids['id_progress'].start()#并没有滚动，？？
        toast("合并中……",duration=0.5)

        self.root.ids['id_screenmergexqf'].disabled = True

        async def tt():
            await asynckivy.sleep(0.5)
        
            mergeTree = mergexqf2tree(filenames)
            if mergeTree and len(mergeTree) > 0:
                Logger.debug(f'X-Chess generate_merge_tree: 写入文件 开始')
                with open(filenames[0], 'rb') as file:
                    # 读取文件内容
                    content = file.read()
                hex_content = binascii.b2a_hex(content).decode('utf-8')
                saveMovestreeToXQF(mergeTree,hex_content[0:2048],mergefn)
                Logger.debug(f'X-Chess generate_merge_tree: 写入文件 结束')
                toast("合并成功")
            else:
                toast(f'{filenames[0]} 和 {filenames[1]} 没有交集')
        
            self.root.ids['id_screenmergexqf'].disabled = False        
            self.root.ids['id_screenmergexqf'].ids['id_progress'].stop() 

        asynckivy.start(tt())

        Logger.debug(f'X-Chess generate_merge_tree: end')
    
    def ai(self):
        #toast("AI在路上，快了，快了，静待花开！！！")
        Logger.debug(f'X-Chess ai: begin')
        
        #这个toast无法实时显示
        toast("AI思考中",duration=0.5)

        async def tt():
            await asynckivy.sleep(0.5)
            nodeid = self.root.ids['id_screenmoves'].ids.id_moveslist.children[0].id
            if nodeid:
                node = self.moves_tree.get_node(nodeid)
                aimove = XQlight_moves(node,self.next_camp)
                if aimove:
                    #print(f"{aimove=}")
                    self.root.ids['id_screenmain'].ids.id_chessboard.add_aiarrow(aimove[0],aimove[1],aimove[2],aimove[3])
            else:
                toast("还没摆棋呢，请新建局面或者打开棋谱")
        
        asynckivy.start(tt())
        
        Logger.debug(f'X-Chess ai: end')
