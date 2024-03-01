'''
Author: Paoger
Date: 2023-11-23 16:21:31
LastEditors: Paoger
LastEditTime: 2024-02-10 20:30:16
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
import glob
import time
import binascii
from treelib import Tree
import configparser
import shutil

from kivy.logger import Logger
from kivy.utils import platform
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.uix.dropdown import DropDown
from kivy.uix.screenmanager import RiseInTransition
from kivy.clock import Clock

from functools import partial

from kivymd.app import MDApp
from kivymd.uix.bottomsheet import MDListBottomSheet
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.filemanager import MDFileManager
from kivymd.toast import toast
from kivymd.utils import asynckivy
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog

#全局变量 棋盘的初始局面,此值不应改变
from global_var import g_const_INIT_SITUATION,g_const_S_P_ORDEER
from x_chess_cfg import get_theLast_Path,save_theLast_Path,save_engine_settings,get_engine_settings
from situation import init_g_init_situation,xqfinit2xchessinit,print_situation,check_situation

#from myScreen import ScreenMain,ScreenMoves,ScreenEditSituation,ScreenInputFileName,ScreenMergeXQF,ScreenInfo,ScreenSetEngine,ScreenMenu,ScreenSelectFile
import myScreen
from selectedmaskwidget import SelectedMaskWidget
from piecewidget import PieceWidget
from piece import Piece
from onelinelistwithid import OneLineListWithId
from onelinelistfiles import OneLineListFiles
from onelinelistpathwithfile import OneLineListPathWithFile
from onelinelistpath import OneLineListPath
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
from selectfile import toUperLevelDirWithFile
from selectpath import toUperLevelDir
from situation import print_situation,sit2Fen

#from xqlight_ai import XQlight_moves
from uci_engine import UCIEngine

Logger.info('X-Chess X_ChessApp: This is a info message:X_ChessApp will run.')
Logger.debug('X-Chess X_ChessApp: This is a debug message:X_ChessApp will run.')

class X_ChessApp(MDApp):
    Logger.debug('X-Chess X_ChessApp: 001')

    #配置文件名
    cfgFileName = None

    #Toolbar menu打开的子菜单
    #menu = None

    #最近一次选择的路径
    last_sel_path = ""

    #当前打开的棋谱文件名
    chessmovesfilename = ""

    #保存打开的xqf文件头【0:2048]，便于保存或另存
    xqfFile2048 = ""

    gameover = False
    #招法树
    moves_tree = Tree()
    #初始局面该谁走，固定的
    init_camp = 'w'#默认该红走
    #当前局面该谁走，动态的
    next_camp = 'w'#默认该红走

    #当前所选棋子
    selected_piece = None

    #棋子移动前位置上的标识
    selectedmask1 = None
    #棋子移动后位置上的标识
    selectedmask2 = None

    #dialog = None

    #文件浏览器，目前winddows下使用，andriod由于11以上存在闪退，所以暂不用
    #在cfg.ini做配置，如果FM==KIVYMD则使用kivy md filemanager，否则用自己造的轮子
    #[UI]
    #FM=KIVYMD
    ui_fm = None
    file_manager = None

    cfg_info = configparser.ConfigParser()
    
    engine_name = 'xqpy'#xqpy：内置XQ引擎  uci：uci协议引擎
    uci_engine = None #引擎进程
    uci_engine_location = None#内置:inner 外置:outer

    #用来保存selectfile.id_btnok on_release绑定的函数
    selectfile_btnok_bind = []    
    sel_filename = None #用来保存选择file页面中选择的file

    #用来保存selectpath.id_btnok on_release绑定的函数
    selectpath_btnok_bind = []
    sel_path = None #用来保存选择path页面中选择的path

    #用来保存screeninputinfo.id_btnok on_release绑定的函数
    screeninputinfo_btnok_bind = []
    #用来保存screeninputinfo.id_btncancle on_release绑定的函数
    screeninputinfo_btncancle_bind = []

    #分析模式，当处于有限分析模式时，手工分析及AI执黑、执红都不可选
    ai_analyzing = False

    #分析当前局面，无限分析
    show_ai_move_infinite = False

    #二者都为真，电脑对弈
    ai_black = False#AI不执黑
    ai_red = False#AI不执红

    Logger.debug('X-Chess X_ChessApp: 004')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        Logger.debug('X-Chess X_ChessApp init: begin')

        if platform != 'android': # "win" linux ...:
            self.cfgFileName = os.path.join(os.getcwd(),'cfg/cfg.ini')
        else:#android
            from android.storage import primary_external_storage_path
            SD_CARD = primary_external_storage_path()
            xc_version = ""
            conf_info = configparser.ConfigParser()
            if len(conf_info.read(os.path.join(os.getcwd(),'cfg/cfg.ini'),encoding='gbk')) != 0:
                xc_version = conf_info.get("XC","version")
            fn = os.path.join(SD_CARD,f'X-Chess/cfg/cfg{xc_version}.ini')
            if  os.path.exists(fn):
                self.cfgFileName = fn
            else:
                self.cfgFileName = os.path.join(os.getcwd(),'cfg/cfg.ini')
        
        Logger.debug(f'X-Chess X_ChessApp init: {self.cfgFileName=}')


        self.icon = 'x-chess.png'

        #Material design 3 style
        self.theme_cls.material_style = "M3"
        self.theme_cls.theme_style = "Dark" #"Dark" Light
        #self.theme_cls.primary_palette = "Orange"

        self.chessmovesfilename = "新建局面"
        self.title = f"X-Chess 新建局面"
        
        self.next_camp = 'w'
        self.init_camp = 'w'
        self.gameover = False

        self.xqfFile2048 = '58510a00000000000000000000000000000a141e28323c46500c4803172b3f5309131d27313b454f59114d061a2e425600000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
        
        init_situation='000a141e28323c46500c4803172b3f5309131d27313b454f59114d061a2e4256'
        #将初始局面字符串初始化到全局变量g_const_INIT_SITUATION
        init_g_init_situation(init_situation)

        self.last_sel_path = get_theLast_Path()

        # 读取 INI 文件        
        #self.cfg_info.read(os.path.join(os.getcwd(),'cfg/cfg.ini'),encoding='gbk')
        self.cfg_info.read(self.cfgFileName,encoding='gbk')

        if (f"UI" in self.cfg_info) and (f"FM" in self.cfg_info['UI']):
            self.ui_fm = self.cfg_info['UI']['FM']
        
        Logger.debug(f'X-Chess X_ChessApp init: {self.ui_fm=}')

        #初始化engine_name = 'xqpy'#xqpy：内置XQ引擎  uci：uci协议引擎
        if (f"ENGINE" in self.cfg_info) and (f"engine_name" in self.cfg_info['ENGINE']):
            self.engine_name = self.cfg_info['ENGINE']['engine_name']
        
        Logger.debug(f'X-Chess X_ChessApp init: {self.engine_name=}')

        #初始化 uci_engine_location 内置:inner 外置:outer    
        if (f"ENGINE" in self.cfg_info) and (f"engine_location" in self.cfg_info['ENGINE']):
            self.uci_engine_location = self.cfg_info['ENGINE']['engine_location']
        
        Logger.debug(f'X-Chess X_ChessApp init: {self.uci_engine_location=}')
        
        if platform != 'android':#简记01
            Window.bind(on_keyboard=self.events)

        Logger.debug('X-Chess X_ChessApp init: end')

    def build(self):
        Logger.debug('X-Chess X_ChessApp build: begin')

        parent = Builder.load_file("./main.kv")

        parent.ids['id_screenmain'].ids['id_movesnote'].hint_text= self.title

         #identifier让其默认生成，If identifier is absent, a UUID will be generated automatically.
        self.moves_tree.remove_subtree(nid=None)#清空以前的树
        self.moves_tree = Tree()
        nroot = self.moves_tree.create_node(tag=os.path.basename(self.chessmovesfilename), 
                data={'sp':'18','ep':'20','flag':'f0','rsv':'ff',
                      'notelen':'00000000','note':"",
                      'situation':g_const_INIT_SITUATION,'pieceWidget':None})  # 根节点
        
        #self.root.ids.id_moveslist.clear_widgets()
        #由于使用多个kv文件，导致self.root.ids不能访问到子kv模块中的ID，所以
        parent.ids['id_screenmoves'].ids.id_moveslist.clear_widgets()
        parent.ids['id_screenmoves'].ids.id_movesbranch.clear_widgets()
        #把根节点加入到招法列表中的第一项
        parent.ids['id_screenmoves'].ids.id_moveslist.add_widget(OneLineListWithId(id=nroot.identifier,text=nroot.tag,font_style="H6"))#bg_color = [0,1,1,1])

        mainbgimg = self.cfg_info['UI']['mainbgimg']
        Logger.debug(f'X-Chess X_ChessApp build: {mainbgimg=}')
        if mainbgimg == 'DIY':
            mainbgimg_fn = None
            if platform != 'android':
                mainbgimg_fn = os.path.join(os.getcwd(),'img/background.png')
            else:
                from android.storage import primary_external_storage_path
                SD_CARD = primary_external_storage_path()
                mainbgimg_fn = os.path.join(SD_CARD,'X-Chess/img/background.png')
            Logger.debug(f'X-Chess X_ChessApp build: {mainbgimg_fn=}')
            if os.path.exists(mainbgimg_fn):
                parent.ids['id_screenmain'].ids.id_backgroundimg.source = mainbgimg_fn
        
        if platform == 'android':
            #安卓中由于输入法会遮挡注解信息,所以否则只读,通过专用的编辑界面进行编辑
            parent.ids['id_screenmain'].ids['id_movesnote'].readonly = True
        
#MDDropdownMenu在android >= 11 闪退,so暂且把菜单改成按钮放在首页上，以及菜单Screen吧

#       menu_items = [
#           {
#               "viewclass": "OneLineListItem",
#               "text": "新建局面",
#               "height": dp(48),
#               "on_release": lambda x="新建": self.new_situation(),
#            },
#            {
#               "viewclass": "OneLineListItem",
#               "text": "编辑局面",
#               "height": dp(48),
#               "on_release": lambda x="编辑": self.edit_situation(),
#            },
#           {
#               "viewclass": "OneLineListItem",
#               "text": "打开棋谱",
#               "height": dp(48),
#               "on_release": lambda x="Open": self.open_XQFFile(x),
#            },
#            {
#               "viewclass": "OneLineListItem",
#               "text": "保存棋谱",
#               "height": dp(48),
#               "on_release": lambda x="": self.saveXQF(),
#            },
#            {
#               "viewclass": "OneLineListItem",
#               "text": "另存棋谱",
#               "height": dp(48),
#               "on_release": lambda x="": self.saveAs(),
#            },
#            {
#               "viewclass": "OneLineListItem",
#               "text": "合并XQF",
#               "height": dp(48),
#               "on_release": lambda x="编辑": self.mergeXQF(),
#            },
#            {
#               "viewclass": "OneLineListItem",
#               "text": "xqf==>txt",
#               "height": dp(48),
#               "on_release": lambda x="xqf2txt": self.xqf2txt(x),
#            },
#            {
#               "viewclass": "OneLineListItem",
#               "text": "退到初始",
#               "height": dp(48),
#               "on_release": lambda x="初始局面": self.back_init(),
#            },
#            {
#               "viewclass": "OneLineListItem",
#               "text": "自动路演",
#               "height": dp(48),
#               "on_release": lambda x="自动路演": self.auto_roadshow(),
#            },
#            {
#               "viewclass": "OneLineListItem",
#               "text": "引擎设置",
#               "height": dp(48),
#               "on_release": lambda x="引擎设置": self.set_engine(),
#            },
#            {
#               "viewclass": "OneLineListItem",
#               "text": "Test",
#               "height": dp(48),
#               "on_release": lambda x="Test": self.test_callback(x),
#            }, 
#            {
#               "viewclass": "OneLineListItem",
#               "text": "退出",
#               "height": dp(48),
#               "on_release": lambda x="Quit": self.stop(),
#            },            
#       ]
#
#       self.menu = MDDropdownMenu(
#           caller = parent.ids['id_screenmain'].ids['id_btnmenu'],
#           items=menu_items,
#           width_mult=4,
#       )
#

#    暂且把菜单改成按钮放在首页上，以及菜单Screen

        Logger.debug('X-Chess X_ChessApp build: end')
        return parent
    
    def on_start(self):
        super().on_start()
        Logger.debug('X-Chess X_ChessApp on_start: begin')

        self.root.current_heroes = "" #"" ["hero"]
        self.root.current = "ScreenWelcome"

        Logger.debug('X-Chess X_ChessApp on_start: end')
    
    def inputinfo_backto(self,instance=None,screenname=None):
        Logger.debug(f'X-Chess X_ChessApp inputinfo_backto: {screenname=}')

        self.root.transition = RiseInTransition()
        self.root.current_heroes = ""
        self.root.current = screenname

    def set_inputinfo(self,instance=None,screenname=None,screenid=None,textid=None):
        Logger.debug(f'X-Chess X_ChessApp set_inputinfo: begin')
        Logger.debug(f'X-Chess X_ChessApp inputinfo_backto: {screenname=},{screenid=},{textid}')

        self.root.ids[screenid].ids[textid].text = self.root.ids['id_screeninputinfo'].ids['id_input_info'].text        
        
        self.root.transition = RiseInTransition()
        self.root.current_heroes = ""
        self.root.current = screenname

        if screenid == 'id_screenmain':
            #print('User defocused')
            #app = MDApp.get_running_app()
            #招法树必须先有
            if self.moves_tree.root != None:
                #更新当前节点的注释
                #MDList的最后一个item
                id = self.root.ids['id_screenmoves'].ids.id_moveslist.children[0].id
                if id != None:
                    node = self.moves_tree.get_node(id)
                    notelen = node.data['notelen']
                    #print(f"before note==>{node.data['note']}")
                    #print(f"before notelen==>{notelen}")
                    Logger.debug(f"X-Chess ChessApp set_inputinfo:before note==>{node.data['note']}")
                    node.data['note'] = self.root.ids['id_screeninputinfo'].ids['id_input_info'].text
                    #print(f"after note==>{self.text=},{node.data['note']}")
                    #一顿骚操作
                    s = f"{len(self.root.ids['id_screeninputinfo'].ids['id_input_info'].text.encode('gbk')):x}" # 10==>a
                    #print(f"{len(self.text.encode('gbk'))=},{s=}")
                    s = f"{s:0>8}"#a==>0000000a
                    notelen = f'{s[6:8]}{s[4:6]}{s[2:4]}{s[0:2]}' #0000000a==>0a000000
                    node.data['notelen'] = notelen
                    #print(f"after notelen==>{notelen}")
                    Logger.debug(f"X-Chess ChessApp set_inputinfo:after note==>{node.data['note']}")

        Logger.debug(f'X-Chess X_ChessApp set_inputinfo: end')

    def input_noteedit(self):
        Logger.debug("X-Chess X-ChessApp:input_noteedit begin")

        #if platform == 'android':
        self.root.transition = RiseInTransition()
        self.root.current_heroes = ""
        self.root.current = "ScreenInputInfo"

        self.root.ids['id_screeninputinfo'].ids['id_input_info'].hint_text= "请输入棋谱注解"
        self.root.ids['id_screeninputinfo'].ids['id_input_info'].text = self.root.ids['id_screenmain'].ids['id_movesnote'].text

        #先把id_btn_ok之前的绑定清空了,再重新绑定
        for cb in self.screeninputinfo_btnok_bind:
            self.root.ids['id_screeninputinfo'].ids.id_btn_ok.funbind('on_release', cb)
        self.screeninputinfo_btnok_bind = []
        new_cb = partial(self.set_inputinfo,screenname='screenMain',screenid='id_screenmain',textid='id_movesnote')
        self.screeninputinfo_btnok_bind.append(new_cb)
        self.root.ids['id_screeninputinfo'].ids.id_btn_ok.fbind('on_release', new_cb)

        #先把id_btn_cancle之前的绑定清空了,再重新绑定
        for cb in self.screeninputinfo_btncancle_bind:
            self.root.ids['id_screeninputinfo'].ids.id_btn_cancle.funbind('on_release', cb)
        self.screeninputinfo_btncancle_bind = []
        new_cb = partial(self.inputinfo_backto,screenname='screenMain')
        self.screeninputinfo_btncancle_bind.append(new_cb)
        self.root.ids['id_screeninputinfo'].ids.id_btn_cancle.fbind('on_release', new_cb)
        
        #else:
        #    pass

        Logger.debug("X-Chess X-ChessApp:input_noteedit end")
    
    def input_engineoption_edit(self):
        Logger.debug("X-Chess X-ChessApp:input_engineoption_edit begin")

        #if platform == 'android':
        self.root.transition = RiseInTransition()
        self.root.current_heroes = ""
        self.root.current = "ScreenInputInfo"

        self.root.ids['id_screeninputinfo'].ids['id_input_info'].hint_text= "请输入引擎参数"
        self.root.ids['id_screeninputinfo'].ids['id_input_info'].text = self.root.ids['id_screensetengine'].ids['id_uci_options'].text

        Logger.debug(f"X-Chess X-ChessApp input_engineoption_edit: {self.root.ids['id_screensetengine'].ids['id_uci_options'].text=}")

        #先把id_btn_ok之前的绑定清空了,再重新绑定
        for cb in self.screeninputinfo_btnok_bind:
            self.root.ids['id_screeninputinfo'].ids.id_btn_ok.funbind('on_release', cb)
        self.screeninputinfo_btnok_bind = []
        new_cb = partial(self.set_inputinfo,screenname='screenSetEngine',screenid='id_screensetengine',textid='id_uci_options')
        self.screeninputinfo_btnok_bind.append(new_cb)
        self.root.ids['id_screeninputinfo'].ids.id_btn_ok.fbind('on_release', new_cb)

        #先把id_btn_cancle之前的绑定清空了,再重新绑定
        for cb in self.screeninputinfo_btncancle_bind:
            self.root.ids['id_screeninputinfo'].ids.id_btn_cancle.funbind('on_release', cb)
        self.screeninputinfo_btncancle_bind = []
        new_cb = partial(self.inputinfo_backto,screenname='screenSetEngine')
        self.screeninputinfo_btncancle_bind.append(new_cb)
        self.root.ids['id_screeninputinfo'].ids.id_btn_cancle.fbind('on_release', new_cb)
        
        #else:
        #    pass

        Logger.debug("X-Chess X-ChessApp:input_engineoption_edit end")
    
    def new_situation(self):
        Logger.debug("X-Chess X-ChessApp:******new_situation begin******")        
        #self.menu.dismiss()

        self.chessmovesfilename = "新建局面"
        self.title = f"X-Chess 新建局面"
        self.root.ids['id_screenmain'].ids['id_movesnote'].hint_text= self.title
        self.root.ids['id_screenmain'].ids['id_movesnote'].text  = ""
        self.root.ids['id_screenmain'].ids['id_movesnote'].cancel_selection()
        self.root.ids['id_screenmain'].ids['id_movesnote_input'].text  = ""
        self.root.ids['id_screenmain'].ids['id_movesnote_input'].cancel_selection()

        self.next_camp = 'w'
        self.init_camp = 'w'
        self.gameover = False

        self.root.ids['id_screenmain'].ids.id_chessboard.red_bottom = True

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

        #按棋谱g_const_INIT_SITUATION摆棋子
        self.root.ids['id_screenmain'].ids.id_chessboard.piece_by_chessmanual()

        #toast("新建局面ok")
        Logger.debug("X-Chess X-ChessApp:******new_situation end******")
    
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
                #self.last_sel_path = os.path.join(os.getcwd(),'xqf')
                from android.storage import primary_external_storage_path
                SD_CARD = primary_external_storage_path()
                mypath = os.path.join(SD_CARD,'X-Chess/xqf')
                if not os.path.exists(mypath):
                    try:
                        os.makedirs(mypath)
                    except Exception as e:
                        Logger.debug(f"X-Chess UCIEngine:subprocess Exception: {str(e)}")
                    finally:
                        pass
                self.last_sel_path = os.path.join(SD_CARD,'X-Chess/xqf')

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
    
    def toUperLevelDirWithFile(self):
        toUperLevelDirWithFile(self.root.ids['id_screenselectfile'].ids['id_cur_path'].text)
    
    def cdSubDir(self):#进入子目录
        if self.root.ids['id_screenselectfile'].ids['id_subdir'].text == "":
            return
        
        async def onebyone(self,filename):
            self.root.ids['id_screenselectfile'].ids.id_file_list.add_widget(OneLineListFiles(text=f"{filename}",font_style="Overline"))
            #await asynckivy.sleep(0.1)
        #end onebyone

        self.sel_filename = None
        seachdir = os.path.join(self.root.ids['id_screenselectfile'].ids['id_cur_path'].text,
                                f"{self.root.ids['id_screenselectfile'].ids['id_subdir'].text}")
        Logger.debug(f"X-Chess OneLineListPath:on_touch_up {seachdir=}")

        self.root.ids['id_screenselectfile'].ids['id_cur_path'].text = seachdir

        seachdir = self.root.ids['id_screenselectfile'].ids['id_cur_path'].text
        #Logger.debug(f"X-Chess X-ChessApp:OneLineListPathWithFile {seachdir=}")
        seachdir = os.path.join(seachdir,'*')
        #Logger.debug(f"X-Chess X-ChessApp:OneLineListPathWithFile {seachdir=}")
        subdirs = [name for name in glob.glob(seachdir) if os.path.isdir(name)]
        self.root.ids['id_screenselectfile'].ids.id_dir_list.clear_widgets()
        for sd in subdirs:
            last_level_dir = os.path.basename(sd)
            self.root.ids['id_screenselectfile'].ids.id_dir_list.add_widget(OneLineListPathWithFile(text=f"{last_level_dir}",font_style="Overline"))
                
        seachdir = self.root.ids['id_screenselectfile'].ids['id_cur_path'].text
        filetype = self.root.ids['id_screenselectfile'].ids['id_filetype'].text
        filetype = filetype.split('.')
        seachdir = os.path.join(seachdir,f'*.{filetype[1]}')
        #Logger.debug(f"X-Chess X-ChessApp:OneLineListPathWithFile {seachdir=}")
        files = [name for name in glob.glob(seachdir) if os.path.isfile(name)]
        self.root.ids['id_screenselectfile'].ids.id_file_list.clear_widgets()
        for file in files:
            filename = os.path.basename(file)
            #self.root.ids['id_screenselectfile'].ids.id_file_list.add_widget(OneLineListFiles(text=f"{filename}",font_style="Overline")) 
            asynckivy.start(onebyone(self,filename=filename)) 
    
    def open_XQFFile(self):
        #由于MDFileManager在android11之上闪退，换了flyer.filechoose也是问题多多，so
        #if platform == 'android':
        if self.ui_fm != 'KIVYMD':
            self.root.current_heroes = ""
            self.root.current = "ScreenSelectFile"
            self.sel_filename = None
            self.root.ids['id_screenselectfile'].ids['id_cur_path'].text = self.last_sel_path
            self.root.ids['id_screenselectfile'].ids['id_subdir'].text = ""
            filetype = '.xqf'
            self.root.ids['id_screenselectfile'].ids['id_filetype'].text = f"文件类型{filetype}"
        
            seachdir = self.root.ids['id_screenselectfile'].ids['id_cur_path'].text
            Logger.debug(f"X-Chess X-ChessApp:open_XQFFile {seachdir=}")
            seachdir = os.path.join(seachdir,'*')
            Logger.debug(f"X-Chess X-ChessApp:open_XQFFile {seachdir=}")
            subdirs = [name for name in glob.glob(seachdir) if os.path.isdir(name)]
            self.root.ids['id_screenselectfile'].ids.id_dir_list.clear_widgets()
            for sd in subdirs:
                last_level_dir = os.path.basename(sd)
                self.root.ids['id_screenselectfile'].ids.id_dir_list.add_widget(OneLineListPathWithFile(text=f"{last_level_dir}",font_style="Overline"))
        
            seachdir = self.root.ids['id_screenselectfile'].ids['id_cur_path'].text
            seachdir = os.path.join(seachdir,f'*{filetype}')
            Logger.debug(f"X-Chess X-ChessApp:open_XQFFile {seachdir=}")
            files = [name for name in glob.glob(seachdir) if os.path.isfile(name)]
            self.root.ids['id_screenselectfile'].ids.id_file_list.clear_widgets()
            for file in files:
                filename = os.path.basename(file)
                self.root.ids['id_screenselectfile'].ids.id_file_list.add_widget(OneLineListFiles(text=f"{filename}",font_style="Overline"))
            
            #self.root.ids['id_screenselectfile'].ids.id_btn_ok.bind(
            #    on_release=lambda instance:self.open_SelectedXQFFile(instance))
            
            #先把之前的绑定清空了
            for cb in self.selectfile_btnok_bind:
                self.root.ids['id_screenselectfile'].ids.id_btn_ok.funbind('on_release', cb)
            self.selectfile_btnok_bind = []

            new_cb = partial(self.open_SelectedXQFFile)
            self.selectfile_btnok_bind.append(new_cb)
            self.root.ids['id_screenselectfile'].ids.id_btn_ok.fbind('on_release', new_cb)
        else:           
            self.manager_open = False
            self.file_manager = MDFileManager(
                exit_manager=self.exit_manager,#用户到达目录树根目录时调用的函数
                select_path=lambda path:self.select_xqf_path(path=path),   #选择文件/目录时调用的函数
                icon_selection_button="pencil",
                selector='file',#只选择文件
                ext=['.xqf']
            )            
            self.file_manager_open()
    
    def open_SelectedXQFFile(self,instance):
        if self.sel_filename != None:
            self.back_mainScreen()
            
            self.last_sel_path = os.path.dirname(self.sel_filename)
            save_theLast_Path(self.last_sel_path)
            
            self.chessmovesfilename = self.sel_filename
            file_name = os.path.basename(self.chessmovesfilename)
            self.title = f"X-Chess {file_name[:-4]}"
            self.root.ids['id_screenmain'].ids['id_movesnote'].hint_text= self.title
            self.root.ids['id_screenmain'].ids['id_movesnote'].text= ""
            self.root.ids['id_screenmain'].ids['id_movesnote'].cancel_selection()
            self.root.ids['id_screenmain'].ids['id_movesnote_input'].text= ""
            self.root.ids['id_screenmain'].ids['id_movesnote_input'].cancel_selection()
            self.gameover  = False
            self.root.ids['id_screenmain'].ids.id_chessboard.red_bottom = True

            self.root.ids['id_screenmoves'].ids.id_moveslist.clear_widgets()
            self.root.ids['id_screenmoves'].ids.id_movesbranch.clear_widgets()

            self.readXQFFile(self.sel_filename)

            self.back_mainScreen()
        
    
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
        self.root.ids['id_screenmain'].ids['id_movesnote'].hint_text= self.title
        self.gameover  = False
        self.root.ids['id_screenmain'].ids.id_chessboard.red_bottom = True

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
                self.init_camp = p.camp
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
    
    def welcome2main(self):
        self.back_mainScreen()
        
        #self.root.ids['id_screenmain'].ids.id_chessboard.draw_full_piece()

    #此函数已弃用，在棋盘初始化时绘制初始棋子，整个app生命期间只有1副棋子，不用每次都重新绘制
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
            self.root.ids['id_screenmain'].disabled = True
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
            self.root.ids['id_screenmain'].disabled = False
        #end onebyone        
            
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
        #self.draw_init_situation()
        #按棋谱g_const_INIT_SITUATION摆棋子
        self.root.ids['id_screenmain'].ids.id_chessboard.piece_by_chessmanual()

        self.generate_moves_tree(hex_content[2048:])

        #显示空着(初始局面)注解
        self.root.ids['id_screenmain'].ids.id_movesnote.text = self.moves_tree.get_node(self.moves_tree.root).data['note']
        self.root.ids['id_screenmain'].ids.id_movesnote.cancel_selection()

        print("******readXQFFile end******")
    
    def test_callback(self,menuname):
        print("test_callback begin")
        print(f"{menuname=}")
        #self.menu.dismiss()

        toast(f"android == {platform=}")

        print("test_callback end")
    
    def auto_roadshow(self):
        print("auto_roadshow begin")
        #self.menu.dismiss()

        #招法树必须先有
        if self.moves_tree.root == None:
            return

        if len(self.moves_tree) == 0:
            return
        
        if self.ai_black == True:
            self.ai_black = False
            self.root.ids['id_screenmain'].ids['id_btn_ai_black'].icon_size = '28sp'                
        if self.ai_red == True:
            self.ai_red = False
            self.root.ids['id_screenmain'].ids['id_btn_ai_red'].icon_size = '28sp'
        
        #清除AI信息
        self.root.ids['id_screenmain'].ids['id_movesnote_input'].text = ""
        self.root.ids['id_screenmain'].ids['id_movesnote_input'].cancel_selection()

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
                    #node.data['pieceWidget'].movexy(node.data['sx'],node.data['sy'],node.data['ex'],node.data['ey'],'F',parent.data['situation'])
                    s_board_x = s_board_y = e_board_x = e_board_y = None
                    if self.root.ids['id_screenmain'].ids.id_chessboard.red_bottom == True:#红下黑上
                        s_board_x = node.data['sx']
                        s_board_y = node.data['sy']
                        e_board_x = node.data['ex']
                        e_board_y = node.data['ey']
                    else:#红上黑下
                        s_board_x = abs(node.data['sx']-8)
                        s_board_y = abs(node.data['sy']-9)
                        e_board_x = abs(node.data['ex']-8)
                        e_board_y = abs(node.data['ey']-9)
                    node.data['pieceWidget'].movexy(s_board_x,s_board_y,e_board_x,e_board_y,'F',parent.data['situation'])
                    
                #显示招法注解
                self.root.ids['id_screenmain'].ids.id_movesnote.text = node.data['note']
                self.root.ids['id_screenmain'].ids.id_movesnote.cancel_selection()

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
        #self.menu.dismiss()

        #招法树必须先有
        if self.moves_tree.root == None:
            return
        
        if self.gameover == True:
            self.gameover = False
        
        if self.ai_black == True:
            self.ai_black = False
            self.root.ids['id_screenmain'].ids['id_btn_ai_black'].icon_size = '28sp'                
        if self.ai_red == True:
            self.ai_red = False
            self.root.ids['id_screenmain'].ids['id_btn_ai_red'].icon_size = '28sp'
        
        #清除AI信息
        self.root.ids['id_screenmain'].ids['id_movesnote_input'].text = ""
        self.root.ids['id_screenmain'].ids['id_movesnote_input'].cancel_selection()

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
                            #p.movexy(node.data['ex'],node.data['ey'],node.data['sx'],node.data['sy'],'B',parent.data['situation'])
                            s_board_x = s_board_y = e_board_x = e_board_y = None
                            if self.root.ids['id_screenmain'].ids.id_chessboard.red_bottom == True:#红下黑上
                                s_board_x = node.data['ex']
                                s_board_y = node.data['ey']
                                e_board_x = node.data['sx']
                                e_board_y = node.data['sy']
                            else:#红上黑下
                                s_board_x = abs(node.data['ex']-8)
                                s_board_y = abs(node.data['ey']-9)
                                e_board_x = abs(node.data['sx']-8)
                                e_board_y = abs(node.data['sy']-9)
                            p.movexy(s_board_x,s_board_y,e_board_x,e_board_y,'B',parent.data['situation'])

                            self.root.ids['id_screenmoves'].ids.id_moveslist.remove_widget(self.root.ids['id_screenmoves'].ids.id_moveslist.children[0])
                            curid = self.root.ids['id_screenmoves'].ids.id_moveslist.children[0].id
                            #显示招法注解
                            self.root.ids['id_screenmain'].ids.id_movesnote.text = parent.data['note']
                            self.root.ids['id_screenmain'].ids.id_movesnote.cancel_selection()
                        else:
                            break
                    else:
                        break
                #end while
            #end if id != None:

        #清除走法示意线
        self.root.ids['id_screenmain'].ids.id_chessboard.remove_Allarrows()
                
        #self.selectedmask1.center=[self.root.ids['id_screenmain'].ids.id_chessboard.width/2,self.root.ids['id_screenmain'].ids.id_chessboard.height/2]
        #self.selectedmask2.center=[self.root.ids['id_screenmain'].ids.id_chessboard.width/2,self.root.ids['id_screenmain'].ids.id_chessboard.height/2]
        self.selectedmask1.center=[-1000,-1000]
        self.selectedmask2.center=[-1000,-1000]

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

        if self.ai_black == True:
            self.ai_black = False
            self.root.ids['id_screenmain'].ids['id_btn_ai_black'].icon_size = '28sp'                
        if self.ai_red == True:
            self.ai_red = False
            self.root.ids['id_screenmain'].ids['id_btn_ai_red'].icon_size = '28sp' 
        
        #清除AI信息
        self.root.ids['id_screenmain'].ids['id_movesnote_input'].text = ""
        self.root.ids['id_screenmain'].ids['id_movesnote_input'].cancel_selection()

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
                        #p.movexy(node.data['ex'],node.data['ey'],node.data['sx'],node.data['sy'],'B',parent.data['situation'])
                        s_board_x = s_board_y = e_board_x = e_board_y = None
                        if self.root.ids['id_screenmain'].ids.id_chessboard.red_bottom == True:#红下黑上
                            s_board_x = node.data['ex']
                            s_board_y = node.data['ey']
                            e_board_x = node.data['sx']
                            e_board_y = node.data['sy']
                        else:#红上黑下
                            s_board_x = abs(node.data['ex']-8)
                            s_board_y = abs(node.data['ey']-9)
                            e_board_x = abs(node.data['sx']-8)
                            e_board_y = abs(node.data['sy']-9)
                        p.movexy(s_board_x,s_board_y,e_board_x,e_board_y,'B',parent.data['situation'])
                        
                        self.root.ids['id_screenmoves'].ids.id_moveslist.remove_widget(self.root.ids['id_screenmoves'].ids.id_moveslist.children[0])
                        curid = self.root.ids['id_screenmoves'].ids.id_moveslist.children[0].id
                        #显示招法注解
                        self.root.ids['id_screenmain'].ids.id_movesnote.text = parent.data['note']
                        self.root.ids['id_screenmain'].ids.id_movesnote.cancel_selection()

                        childs = self.moves_tree.children(parent.identifier)
                        moves_num = len(childs)
                        if moves_num > 1:
                            #画出对方应对此招的走法示意线
                            self.root.ids['id_screenmain'].ids.id_chessboard.remove_Allarrows()
                            for item in self.moves_tree.children(parent.identifier):
                                #self.root.ids['id_screenmain'].ids.id_chessboard.add_arrow(item.data['sx'],item.data['sy'],item.data['ex'],item.data['ey'])
                                s_board_x = s_board_y = e_board_x = e_board_y = None
                                if self.root.ids['id_screenmain'].ids.id_chessboard.red_bottom == True:#红下黑上
                                    s_board_x = item.data['sx']
                                    s_board_y = item.data['sy']
                                    e_board_x = item.data['ex']
                                    e_board_y = item.data['ey']
                                else:#红上黑下
                                    s_board_x = abs(item.data['sx']-8)
                                    s_board_y = abs(item.data['sy']-9)
                                    e_board_x = abs(item.data['ex']-8)
                                    e_board_y = abs(item.data['ey']-9)
                                self.root.ids['id_screenmain'].ids.id_chessboard.add_arrow(s_board_x,s_board_y,e_board_x,e_board_y)

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
        
        if self.ai_black == True:
            self.ai_black = False
            self.root.ids['id_screenmain'].ids['id_btn_ai_black'].icon_size = '28sp'                
        if self.ai_red == True:
            self.ai_red = False
            self.root.ids['id_screenmain'].ids['id_btn_ai_red'].icon_size = '28sp'
        
        #清除AI信息
        self.root.ids['id_screenmain'].ids['id_movesnote_input'].text = ""
        self.root.ids['id_screenmain'].ids['id_movesnote_input'].cancel_selection()

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
                        #node.data['pieceWidget'].movexy(node.data['sx'],node.data['sy'],node.data['ex'],node.data['ey'],'F',parent.data['situation'])
                        s_board_x = s_board_y = e_board_x = e_board_y = None
                        if self.root.ids['id_screenmain'].ids.id_chessboard.red_bottom == True:#红下黑上
                            s_board_x = node.data['sx']
                            s_board_y = node.data['sy']
                            e_board_x = node.data['ex']
                            e_board_y = node.data['ey']
                        else:#红上黑下
                            s_board_x = abs(node.data['sx']-8)
                            s_board_y = abs(node.data['sy']-9)
                            e_board_x = abs(node.data['ex']-8)
                            e_board_y = abs(node.data['ey']-9)
                        node.data['pieceWidget'].movexy(s_board_x,s_board_y,e_board_x,e_board_y,'F',parent.data['situation'])
                
                    #显示招法注解
                    self.root.ids['id_screenmain'].ids.id_movesnote.text = node.data['note']
                    self.root.ids['id_screenmain'].ids.id_movesnote.cancel_selection()

                    #画出对方应对此招的走法示意线
                    self.root.ids['id_screenmain'].ids.id_chessboard.remove_Allarrows()
                    for item in self.moves_tree.children(node.identifier):
                        #self.root.ids['id_screenmain'].ids.id_chessboard.add_arrow(item.data['sx'],item.data['sy'],item.data['ex'],item.data['ey'])
                        s_board_x = s_board_y = e_board_x = e_board_y = None
                        if self.root.ids['id_screenmain'].ids.id_chessboard.red_bottom == True:#红下黑上
                            s_board_x = item.data['sx']
                            s_board_y = item.data['sy']
                            e_board_x = item.data['ex']
                            e_board_y = item.data['ey']
                        else:#红上黑下
                            s_board_x = abs(item.data['sx']-8)
                            s_board_y = abs(item.data['sy']-9)
                            e_board_x = abs(item.data['ex']-8)
                            e_board_y = abs(item.data['ey']-9)
                        self.root.ids['id_screenmain'].ids.id_chessboard.add_arrow(s_board_x,s_board_y,e_board_x,e_board_y)

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
        
        if self.ai_black == True:
            self.ai_black = False
            self.root.ids['id_screenmain'].ids['id_btn_ai_black'].icon_size = '28sp'                
        if self.ai_red == True:
            self.ai_red = False
            self.root.ids['id_screenmain'].ids['id_btn_ai_red'].icon_size = '28sp'
        
        #清除AI信息
        self.root.ids['id_screenmain'].ids['id_movesnote_input'].text = ""
        self.root.ids['id_screenmain'].ids['id_movesnote_input'].cancel_selection()

        node = self.moves_tree.get_node(self.root.ids['id_screenmoves'].ids.id_moveslist.children[0].id)
        if node != None:
            #print(f"{node.tag},{node.data['pieceWidget']}")
            parent = self.moves_tree.parent(node.identifier)
            if parent != None:
                p = node.data['pieceWidget']
                if p and  isinstance(p,PieceWidget):
                    parent = self.moves_tree.parent(node.identifier)

                    s_board_x = s_board_y = e_board_x = e_board_y = None
                    if self.root.ids['id_screenmain'].ids.id_chessboard.red_bottom == True:#红下黑上
                        s_board_x = node.data['ex']
                        s_board_y = node.data['ey']
                        e_board_x = node.data['sx']
                        e_board_y = node.data['sy']
                    else:#红上黑下
                        s_board_x = abs(node.data['ex']-8)
                        s_board_y = abs(node.data['ey']-9)
                        e_board_x = abs(node.data['sx']-8)
                        e_board_y = abs(node.data['sy']-9)
                    
                    #Logger.debug(f'X-Chess x-chessapp previous_moves: {s_board_x=},{s_board_y=},{e_board_x=},{e_board_y=}')

                    #movexy接受的是棋盘显示坐标
                    node.data['pieceWidget'].movexy(s_board_x,s_board_y,e_board_x,e_board_y,'B',parent.data['situation'])
                    #node.data['pieceWidget'].movexy(node.data['ex'],node.data['ey'],node.data['sx'],node.data['sy'],'B',parent.data['situation'])

                    self.root.ids['id_screenmoves'].ids.id_moveslist.remove_widget(self.root.ids['id_screenmoves'].ids.id_moveslist.children[0])
                    #for child in self.root.ids['id_screenmoves'].ids.id_moveslist.children[:]:
                    #    print(f"{child.id=},{child.text=}")
                
                #显示招法注解
                self.root.ids['id_screenmain'].ids.id_movesnote.text = parent.data['note']
                self.root.ids['id_screenmain'].ids.id_movesnote.cancel_selection()

                #画出对方应对此招的走法示意线
                self.root.ids['id_screenmain'].ids.id_chessboard.remove_Allarrows()
                for item in self.moves_tree.children(parent.identifier):
                    #Logger.debug(f'X-Chess x-chessapp previous_moves: {item.tag=}')
                    #self.root.ids['id_screenmain'].ids.id_chessboard.add_arrow(item.data['sx'],item.data['sy'],item.data['ex'],item.data['ey'])
                    s_board_x = s_board_y = e_board_x = e_board_y = None
                    if self.root.ids['id_screenmain'].ids.id_chessboard.red_bottom == True:#红下黑上
                        s_board_x = item.data['sx']
                        s_board_y = item.data['sy']
                        e_board_x = item.data['ex']
                        e_board_y = item.data['ey']
                    else:#红上黑下
                        s_board_x = abs(item.data['sx']-8)
                        s_board_y = abs(item.data['sy']-9)
                        e_board_x = abs(item.data['ex']-8)
                        e_board_y = abs(item.data['ey']-9)
                    self.root.ids['id_screenmain'].ids.id_chessboard.add_arrow(s_board_x,s_board_y,e_board_x,e_board_y)
        
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
        
        if self.ai_black == True:
            self.ai_black = False
            self.root.ids['id_screenmain'].ids['id_btn_ai_black'].icon_size = '28sp'                
        if self.ai_red == True:
            self.ai_red = False
            self.root.ids['id_screenmain'].ids['id_btn_ai_red'].icon_size = '28sp'

        #清除AI信息
        self.root.ids['id_screenmain'].ids['id_movesnote_input'].text = ""
        self.root.ids['id_screenmain'].ids['id_movesnote_input'].cancel_selection()

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

                    #node.data['pieceWidget'].movexy(node.data['sx'],node.data['sy'],node.data['ex'],node.data['ey'],'F',parent.data['situation'])
                    s_board_x = s_board_y = e_board_x = e_board_y = None
                    if self.root.ids['id_screenmain'].ids.id_chessboard.red_bottom == True:#红下黑上
                        s_board_x = node.data['sx']
                        s_board_y = node.data['sy']
                        e_board_x = node.data['ex']
                        e_board_y = node.data['ey']
                    else:#红上黑下
                        s_board_x = abs(node.data['sx']-8)
                        s_board_y = abs(node.data['sy']-9)
                        e_board_x = abs(node.data['ex']-8)
                        e_board_y = abs(node.data['ey']-9)

                    Logger.debug(f"X-Chess x-chessapp next_moves: {node.data['pieceWidget'].bx=},{node.data['pieceWidget'].by=},{node.data['pieceWidget'].board_x=},{node.data['pieceWidget'].board_y=},{s_board_x=},{s_board_y=},{e_board_x=},{e_board_y=}")
                    node.data['pieceWidget'].movexy(s_board_x,s_board_y,e_board_x,e_board_y,'F',parent.data['situation'])
                
                #显示招法注解
                self.root.ids['id_screenmain'].ids.id_movesnote.text = node.data['note']
                self.root.ids['id_screenmain'].ids.id_movesnote.cancel_selection()
                
                #画出对方应对此招的走法示意线
                self.root.ids['id_screenmain'].ids.id_chessboard.remove_Allarrows()
                for item in self.moves_tree.children(node.identifier):
                    #self.root.ids['id_screenmain'].ids.id_chessboard.add_arrow(item.data['sx'],item.data['sy'],item.data['ex'],item.data['ey'])
                    s_board_x = s_board_y = e_board_x = e_board_y = None
                    if self.root.ids['id_screenmain'].ids.id_chessboard.red_bottom == True:#红下黑上
                        s_board_x = item.data['sx']
                        s_board_y = item.data['sy']
                        e_board_x = item.data['ex']
                        e_board_y = item.data['ey']
                    else:#红上黑下
                        s_board_x = abs(item.data['sx']-8)
                        s_board_y = abs(item.data['sy']-9)
                        e_board_x = abs(item.data['ex']-8)
                        e_board_y = abs(item.data['ey']-9)
                    self.root.ids['id_screenmain'].ids.id_chessboard.add_arrow(s_board_x,s_board_y,e_board_x,e_board_y)


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
                #node.data['pieceWidget'].movexy(node.data['sx'],node.data['sy'],node.data['ex'],node.data['ey'],'F',parent.data['situation'])
                s_board_x = s_board_y = e_board_x = e_board_y = None
                if self.root.ids['id_screenmain'].ids.id_chessboard.red_bottom == True:#红下黑上
                    s_board_x = node.data['sx']
                    s_board_y = node.data['sy']
                    e_board_x = node.data['ex']
                    e_board_y = node.data['ey']
                else:#红上黑下
                    s_board_x = abs(node.data['sx']-8)
                    s_board_y = abs(node.data['sy']-9)
                    e_board_x = abs(node.data['ex']-8)
                    e_board_y = abs(node.data['ey']-9)
                node.data['pieceWidget'].movexy(s_board_x,s_board_y,e_board_x,e_board_y,'F',parent.data['situation'])
            
            #显示招法注解
            self.root.ids['id_screenmain'].ids.id_movesnote.text = node.data['note']
            self.root.ids['id_screenmain'].ids.id_movesnote.cancel_selection()

            #画出对方应对此招的走法示意线
            self.root.ids['id_screenmain'].ids.id_chessboard.remove_Allarrows()
            for item in self.moves_tree.children(node.identifier):
                #self.root.ids['id_screenmain'].ids.id_chessboard.add_arrow(item.data['sx'],item.data['sy'],item.data['ex'],item.data['ey'])
                s_board_x = s_board_y = e_board_x = e_board_y = None
                if self.root.ids['id_screenmain'].ids.id_chessboard.red_bottom == True:#红下黑上
                    s_board_x = item.data['sx']
                    s_board_y = item.data['sy']
                    e_board_x = item.data['ex']
                    e_board_y = item.data['ey']
                else:#红上黑下
                    s_board_x = abs(item.data['sx']-8)
                    s_board_y = abs(item.data['sy']-9)
                    e_board_x = abs(item.data['ex']-8)
                    e_board_y = abs(item.data['ey']-9)
                self.root.ids['id_screenmain'].ids.id_chessboard.add_arrow(s_board_x,s_board_y,e_board_x,e_board_y)
    
    def xqf2txt(self):
        #print(f"{text_item=}")
        #self.menu.dismiss()

        #if platform == 'adroid':
        if self.ui_fm != 'KIVYMD':
            self.root.current_heroes = ""
            self.root.current = "ScreenSelectFile"
            self.sel_filename = None
            self.root.ids['id_screenselectfile'].ids['id_cur_path'].text = self.last_sel_path
            filetype = '.xqf'
            self.root.ids['id_screenselectfile'].ids['id_filetype'].text = f"文件类型{filetype}"
            
            seachdir = self.root.ids['id_screenselectfile'].ids['id_cur_path'].text
            Logger.debug(f"X-Chess X-ChessApp:open_XQFFile {seachdir=}")
            seachdir = os.path.join(seachdir,'*')
            Logger.debug(f"X-Chess X-ChessApp:open_XQFFile {seachdir=}")
            subdirs = [name for name in glob.glob(seachdir) if os.path.isdir(name)]
            self.root.ids['id_screenselectfile'].ids.id_dir_list.clear_widgets()
            for sd in subdirs:
                last_level_dir = os.path.basename(sd)
                self.root.ids['id_screenselectfile'].ids.id_dir_list.add_widget(OneLineListPathWithFile(text=f"{last_level_dir}",font_style="Overline"))
            
            seachdir = self.root.ids['id_screenselectfile'].ids['id_cur_path'].text
            seachdir = os.path.join(seachdir,f'*{filetype}')
            Logger.debug(f"X-Chess X-ChessApp:open_XQFFile {seachdir=}")
            files = [name for name in glob.glob(seachdir) if os.path.isfile(name)]
            self.root.ids['id_screenselectfile'].ids.id_file_list.clear_widgets()
            for file in files:
                filename = os.path.basename(file)
                self.root.ids['id_screenselectfile'].ids.id_file_list.add_widget(OneLineListFiles(text=f"{filename}",font_style="Overline"))
            
            #self.root.ids['id_screenselectfile'].ids.id_btn_ok.bind(
            #    on_release=lambda instance:tree2txt(instance,path=self.sel_filename))
            
            #先把之前的绑定清空了
            for cb in self.selectfile_btnok_bind:
                self.root.ids['id_screenselectfile'].ids.id_btn_ok.funbind('on_release', cb)
            self.selectfile_btnok_bind = []

            new_cb = partial(tree2txt)
            self.selectfile_btnok_bind.append(new_cb)
            self.root.ids['id_screenselectfile'].ids.id_btn_ok.fbind('on_release', new_cb)
        
        else:
            #Window.bind(on_keyboard=self.events)
            self.manager_open = False
            self.file_manager = MDFileManager(
                exit_manager=self.exit_manager,#用户到达目录树根目录时调用的函数
                select_path=lambda path:tree2txt(path=path),   #选择文件/目录时调用的函数
                icon_selection_button="pencil",
                selector='file',#只选择文件
                ext=['.xqf']
            )        
            self.file_manager_open()
    
    def edit_situation(self):
        Logger.debug(f"******edit_situation begin******")
        #self.menu.dismiss()

        #app = MDApp.get_running_app()

        self.root.current_heroes = ""
        self.root.current = "screenEditSituation"

        Logger.debug(f"{self.next_camp=}")
        if self.next_camp == 'w':
            self.root.ids['id_screditsituiation'].ids['id_checkbox_red'].active = True
            self.root.ids['id_screditsituiation'].ids['id_checkbox_black'].active = False
        else:
            self.root.ids['id_screditsituiation'].ids['id_checkbox_red'].active = False
            self.root.ids['id_screditsituiation'].ids['id_checkbox_black'].active = True

        Logger.debug(f"******edit_situation end******")
    
    def edit_situation_done(self):
        Logger.debug(f"******edit_situation_done begin******")

        self.init_camp = self.next_camp
        
        Logger.debug(f'{self.next_camp=}')

        #print("full_situation='000a141e28323c46500c4803172b3f5309131d27313b454f59114d061a2e4256'")

        #找到哪些棋子落在棋盘上
        childs = []
        redShuai = None
        for child in self.root.ids['id_screditsituiation'].ids.id_chessboard2.children[:]:
            if isinstance(child,PieceWidget2) and child.bx != child.old_x and child.by != child.old_y:
                #先只判断将帅位置（用来判断棋盘是否翻转），士象暂不判断
                if child.identifier == 'k':
                    infoStr = f"{child.camp=},{child.identifier=},{child.bx=},{child.by=}"
                    Logger.debug(f"{infoStr}")
                    if child.bx < 3 or child.bx > 5 or (child.by > 2 and child.by < 7):
                        Logger.debug(f"{infoStr},不在其位")
                        toast(f"{infoStr},不在其位",duration=5)
                        return
                    if child.camp == 'w':
                        redShuai = child
                childs.append(child)
        
        #判断红黑上下
        red_bottom = True#红下黑上
        if redShuai == None:
            toast(f"红帅不在其位",duration=5)
        else:
            if redShuai.by > 2:
                red_bottom = False#红上黑下        
        Logger.debug(f"将帅检测完毕")

        #初始局面
        xqf_init=""
        for i in range(0,32,1):
            xqf_location = 'ff'
            if i < 16:#红                
                for item in childs:
                    if item.camp == 'w' and item.identifier == g_const_S_P_ORDEER[i]:
                        bx = by = None
                        if red_bottom == True: #红下黑上
                            bx = item.bx
                            by = item.by
                        else:#红上黑下
                            bx = abs(item.bx-8)
                            by = abs(item.by-9)
                        childs.remove(item)#从列表中删除
                        #当前棋子的棋盘坐标
                        xqf_location = f'{bx * 10 + by:x}'
                        xqf_location = f'{xqf_location:0>2}'#前补0
                        break
            else :#黑
                for item in childs:
                    if item.camp == 'b' and item.identifier == g_const_S_P_ORDEER[i]:
                        bx = by = None
                        if red_bottom == True: #红下黑上
                            bx = item.bx
                            by = item.by
                        else:#红上黑下
                            bx = abs(item.bx-8)
                            by = abs(item.by-9)
                        childs.remove(item)#从列表中删除
                        xqf_location = f'{bx * 10 + by:x}'
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
        self.root.ids['id_screenmain'].ids['id_movesnote'].hint_text= self.title
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
        #self.draw_init_situation()
        #按棋谱g_const_INIT_SITUATION摆棋子
        self.root.ids['id_screenmain'].ids.id_chessboard.piece_by_chessmanual()

        Logger.debug(f"******edit_situation_done end******")

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
特别鸣谢：棋友甲、风满楼、陶然、忄思、沧海一粟、行者无疆、蒙面棋王 等等（排名不分先后）

待实现：
        XQF解密格式
        支持开局库
版本0.12 棋乐融融版
    支持自定义背景
    有限支持自定义棋子 
版本0.11 棋如人生版
    调整主界面
    完美支持分屏
版本0.10 棋如人生版
    增大棋子、棋盘
    增加AI无限分析功能
    主题改为有深意的dark模式，不刺眼 
版本0.07 ~ 0.09
    优化ai分析相关功能    
版本0.06
        增加欢迎页
        增加简单的分析模式
        优化手机输入法遮挡注解问题
版本0.05
        提升打开棋谱速度
        支持外置uci引擎
        AI自动走棋
版本0.04
        修复已知bug
        显示AI成杀步数
版本0.03
        支持皮卡鱼引擎
版本0.02:
        修复已知bug
        内置开源引擎XQPy（天天象棋AI中高之间）,(象棋巫师非官方python实现)
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

        #self.menu.dismiss()

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
    
    def toUperLevelDir(self):
        toUperLevelDir(self.root.ids['id_screenselectpath'].ids['id_cur_path'].text)
    
    def select_path(self,screenname=None, screenid=None,filenameid=None):
        #if platform == 'android':
        if self.ui_fm != 'KIVYMD':
            self.root.current_heroes = ""
            self.root.current = "ScreenSelectPath"
            self.sel_path = self.last_sel_path
            self.root.ids['id_screenselectpath'].ids['id_cur_path'].text = self.last_sel_path
                    
            seachdir = self.root.ids['id_screenselectpath'].ids['id_cur_path'].text
            Logger.debug(f"X-Chess X-ChessApp:select_path {seachdir=}")
            seachdir = os.path.join(seachdir,'*')
            Logger.debug(f"X-Chess X-ChessApp:select_path {seachdir=}")
            subdirs = [name for name in glob.glob(seachdir) if os.path.isdir(name)]
            self.root.ids['id_screenselectpath'].ids.id_dir_list.clear_widgets()
            for sd in subdirs:
                last_level_dir = os.path.basename(sd)
                self.root.ids['id_screenselectpath'].ids.id_dir_list.add_widget(OneLineListPath(text=f"{last_level_dir}",font_style="Overline"))
            
            #self.root.ids['id_screenselectpath'].ids.id_btn_ok.bind(
            #    on_release=lambda instance:self.set_select_path(instance,screenname=screenname,
            #                                                    path=self.root.ids['id_screenselectpath'].ids['id_cur_path'].text,
            #                                                    screenid=screenid,textid=filenameid))
            
            #先把之前的绑定清空了
            for cb in self.selectpath_btnok_bind:
                self.root.ids['id_screenselectpath'].ids.id_btn_ok.funbind('on_release', cb)
            self.selectpath_btnok_bind = []

            new_cb = partial(self.set_select_path,screenname=screenname,screenid=screenid,textid=filenameid)
            self.selectpath_btnok_bind.append(new_cb)
            self.root.ids['id_screenselectpath'].ids.id_btn_ok.fbind('on_release', new_cb)
        else:
            self.select_savepath(screenid,filenameid)

    
    def set_select_path(self,path,instance=None,screenname=None,screenid=None,textid=None):
        Logger.debug(f"X-Chess X-ChessApp:set_select_path begin")

        if screenname != None:
            self.root.current_heroes = ""
            self.root.current = screenname

        Logger.debug(f"X-Chess X-ChessApp:set_select_path {self.sel_path=}")

        #if platform == 'android':#安卓环境中不使用MDFileManager
        if self.ui_fm != 'KIVYMD':
            path = self.sel_path

        self.last_sel_path = path
        save_theLast_Path(self.last_sel_path)

        app = MDApp.get_running_app()
        if screenid and textid:
            self.root.ids[f'{screenid}'].ids[f'{textid}'].text=path
        
        #if platform != 'android':#安卓环境中不使用MDFileManager
        if self.ui_fm == 'KIVYMD':
            self.exit_manager()

        #toast(path)
        
        Logger.debug(f"X-Chess X-ChessApp:set_select_path begin")
    
    #MDFileManager，该函数暂且弃用
    def select_savepath(self,screenid,filenameid):
        #Window.bind(on_keyboard=self.events)
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,#用户到达目录树根目录时调用的函数
            select_path=lambda path:self.set_select_path(path=path,screenid=screenid,textid=filenameid),   #选择文件/目录时调用的函数
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
                #self.last_sel_path = os.path.join(os.getcwd(),'xqf')
                from android.storage import primary_external_storage_path
                SD_CARD = primary_external_storage_path()
                mypath = os.path.join(SD_CARD,'X-Chess/xqf')
                if not os.path.exists(mypath):
                    try:
                        os.makedirs(mypath)
                    except Exception as e:
                        Logger.debug(f"X-Chess UCIEngine:subprocess Exception: {str(e)}")
                    finally:
                        pass
                self.last_sel_path = os.path.join(SD_CARD,'X-Chess/xqf')

                self.file_manager.show(self.last_sel_path) 
            else:
                self.file_manager.show_disks()      
        else:
            toast(self.last_sel_path)
            self.file_manager.show(self.last_sel_path)
            
        self.manager_open = True
    
    def saveAs(self):
        print("******saveAs begin******")
        #self.menu.dismiss()

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
    
    def in_the_future(self,text):
        toast(f"{text},待实现，静待花开…")
    
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

        #非模态对话框在android11之上会闪退,so
        self.delete_moves()

        """ if self.dialog:
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
        self.dialog.open() """

        Logger.debug(f'X-Chess delete_movesdlg: end')
    
    """ def closeDialog(self,inst):
        self.dialog.dismiss() """
    
    def delete_moves(self,inst=None):
        Logger.debug(f'X-Chess delete_moves: begin')
        nodeid = self.root.ids['id_screenmoves'].ids.id_moveslist.children[0].id
        #Logger.debug(f'X-Chess delete_moves: {nodeid=}')

        #self.dialog.dismiss()
        
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
        #from kivy.uix.screenmanager import NoTransition,SlideTransition,CardTransition,SwapTransition,FadeTransition,WipeTransition,FallOutTransition,RiseInTransition
        self.root.transition = RiseInTransition()
        self.root.current_heroes = ""
        #self.root.transition.direction = 'right'
        self.root.current = "screenMain"
    
    def saveFileXQF(self):
        saveFileXQF()
    
    def mergeXQF(self):
        #self.menu.dismiss()
        app = MDApp.get_running_app()
        app.root.current_heroes = ""
        app.root.current = "ScreenMergeXQF"
    
    def set_xqffile(self, instance=None,path=None,screenname=None,screenid=None,filenameid=None):
        if platform != 'android':
            self.exit_manager()
            
        #print(f"***set_xqffile {path=},{screenid=},{filenameid=}***")
        if platform == 'android':
            path = self.sel_filename
        
        if screenid and filenameid:
            self.root.ids[f'{screenid}'].ids[f'{filenameid}'].text=path
        
        if screenname != None:
            self.root.current_heroes = ""
            self.root.current = screenname
    
    def select_xqffile(self,screenname,screenid,filenameid):
        Logger.debug(f'X-Chess select_xqffile: begin')
        
        #if platform == 'android':
        if self.ui_fm != 'KIVYMD':
            self.root.current_heroes = ""
            self.root.current = "ScreenSelectFile"
            self.sel_filename = None
            self.root.ids['id_screenselectfile'].ids['id_cur_path'].text = self.last_sel_path
            filetype = '.xqf'
            self.root.ids['id_screenselectfile'].ids['id_filetype'].text = f"文件类型{filetype}"
            
            seachdir = self.root.ids['id_screenselectfile'].ids['id_cur_path'].text
            Logger.debug(f"X-Chess X-ChessApp:open_XQFFile {seachdir=}")
            seachdir = os.path.join(seachdir,'*')
            Logger.debug(f"X-Chess X-ChessApp:open_XQFFile {seachdir=}")
            subdirs = [name for name in glob.glob(seachdir) if os.path.isdir(name)]
            self.root.ids['id_screenselectfile'].ids.id_dir_list.clear_widgets()
            for sd in subdirs:
                last_level_dir = os.path.basename(sd)
                self.root.ids['id_screenselectfile'].ids.id_dir_list.add_widget(OneLineListPathWithFile(text=f"{last_level_dir}",font_style="Overline"))
            
            seachdir = self.root.ids['id_screenselectfile'].ids['id_cur_path'].text
            seachdir = os.path.join(seachdir,f'*{filetype}')
            Logger.debug(f"X-Chess X-ChessApp:open_XQFFile {seachdir=}")
            files = [name for name in glob.glob(seachdir) if os.path.isfile(name)]
            self.root.ids['id_screenselectfile'].ids.id_file_list.clear_widgets()
            for file in files:
                filename = os.path.basename(file)
                self.root.ids['id_screenselectfile'].ids.id_file_list.add_widget(OneLineListFiles(text=f"{filename}",font_style="Overline"))
            
            #self.root.ids['id_screenselectfile'].ids.id_btn_ok.bind(
            #    on_release=lambda instance:tree2txt(instance,path=self.sel_filename))
            
            #先把之前的绑定清空了
            for cb in self.selectfile_btnok_bind:
                self.root.ids['id_screenselectfile'].ids.id_btn_ok.funbind('on_release', cb)
            self.selectfile_btnok_bind = []

            new_cb = partial(self.set_xqffile,screenname=screenname,screenid=screenid,filenameid=filenameid)
            self.selectfile_btnok_bind.append(new_cb)
            self.root.ids['id_screenselectfile'].ids.id_btn_ok.fbind('on_release', new_cb)
        else:
            self.manager_open = False
            self.file_manager = MDFileManager(
                exit_manager=self.exit_manager,#用户到达目录树根目录时调用的函数
                select_path=lambda path:self.set_xqffile(path=path,screenid=screenid,filenameid=filenameid),   #选择文件/目录时调用的函数
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
    
    #分析模式下，走棋后自动分析
    def continue_analyzing(self):
        Logger.debug(f'X-Chess continue_analyzing: begin')

        if self.ai_analyzing == True:
            Logger.debug(f'X-Chess continue_analyzing: 继续分析')
            if len(self.uci_engine.goCount) > 0:
                Logger.debug(f'X-Chess continue_analyzing: 上一次的go没有结束，不再提交分析')
                return
            else:
                nodeid = self.root.ids['id_screenmoves'].ids.id_moveslist.children[0].id
                if nodeid:
                    node = self.moves_tree.get_node(nodeid)
                    xqfPos = node.data['situation']
                    fenstr = sit2Fen(xqfPos)
                    nextCamp = self.next_camp

                    fenstr = f'position fen {fenstr} {nextCamp} - - 0 1' #注意用空格隔开，“b”表示黑方，除此以外都表示红方
                    Logger.debug(f'X-Chess :局面00==》{fenstr}')

                    Logger.debug(f'X-Chess ai: {self.engine_name=}')
                    if self.uci_engine == None:
                        Logger.debug(f'X-Chess ai: 初始化uci引擎')
                        if (f"ENGINE" in self.cfg_info) and (f"engine_filename" in self.cfg_info['ENGINE']):
                            engine_filename = self.cfg_info['ENGINE']['engine_filename']
                            Logger.debug(f'X-Chess ai: {engine_filename=}')
                            settings = self.cfg_info['ENGINE']
                            options = []
                            for k,v in settings.items():
                                if k.startswith('option'):
                                    options.append(v)
                            self.uci_engine = UCIEngine(engine_filename=engine_filename,options=options)                            
                        else:
                            toast("uci没有配置")
                            return
                    #请求最佳招法    
                    thinktime = 5000                        
                    if (f"ENGINE" in self.cfg_info) and (f"ai_think_time" in self.cfg_info['ENGINE']):
                        str1 = self.cfg_info['ENGINE']['ai_think_time']
                        if (str1.isdigit() == True) or (int(str1) >= 0):
                            thinktime = int(str1)
                    Logger.debug(f'X-Chess ai: {thinktime=}')

                    self.uci_engine.polling_aimove2(fenstr=fenstr,thinktime=thinktime)
                #end if nodeid:
        else:
            Logger.debug(f'X-Chess continue_analyzing: 没有处于分析模式')            
        
        Logger.debug(f'X-Chess continue_analyzing: end')
    
    def analyzing(self):
        Logger.debug(f'X-Chess analyzing: begin')

        if self.ai_analyzing == False:
            #不能开启AI执红和执黑
            if self.ai_red == True:
                toast("请关闭AI执红")
                return
            if self.ai_black == True:
                toast("请关闭AI执黑")
                return
            
            if self.uci_engine is not None:            
                goCnt = len(self.uci_engine.goCount)
                if  goCnt >= 1:
                    toast(f"当前还有 {goCnt} 个AI分析在执行，请稍后再试")
                    return
            
            self.root.ids['id_screenmain'].ids['id_btn_ai'].disabled = True
            self.root.ids['id_screenmain'].ids['id_btn_ai_red'].disabled = True
            self.root.ids['id_screenmain'].ids['id_btn_ai_black'].disabled = True

            self.ai_analyzing = True
            self.root.ids['id_screenmain'].ids['id_btn_analyzing'].icon_size = '48sp'

            nodeid = self.root.ids['id_screenmoves'].ids.id_moveslist.children[0].id
            if nodeid:
                node = self.moves_tree.get_node(nodeid)
                xqfPos = node.data['situation']
                fenstr = sit2Fen(xqfPos)
                nextCamp = self.next_camp
   
                fenstr = f'position fen {fenstr} {nextCamp} - - 0 1' #注意用空格隔开，“b”表示黑方，除此以外都表示红方
                Logger.debug(f'X-Chess :局面00==》{fenstr}')

                Logger.debug(f'X-Chess ai: {self.engine_name=}')
                if self.uci_engine == None:
                    Logger.debug(f'X-Chess ai: 初始化uci引擎')
                    if (f"ENGINE" in self.cfg_info) and (f"engine_filename" in self.cfg_info['ENGINE']):
                        engine_filename = self.cfg_info['ENGINE']['engine_filename']
                        Logger.debug(f'X-Chess ai: {engine_filename=}')
                        settings = self.cfg_info['ENGINE']
                        options = []
                        for k,v in settings.items():
                            if k.startswith('option'):
                                options.append(v)
                        self.uci_engine = UCIEngine(engine_filename=engine_filename,options=options)                            
                    else:
                        toast("uci没有配置")
                        return
                #请求最佳招法    
                thinktime = 5000                        
                if (f"ENGINE" in self.cfg_info) and (f"ai_think_time" in self.cfg_info['ENGINE']):
                    str1 = self.cfg_info['ENGINE']['ai_think_time']
                    if (str1.isdigit() == True) or (int(str1) >= 0):
                        thinktime = int(str1)
                Logger.debug(f'X-Chess ai: {thinktime=}')

                self.uci_engine.polling_aimove2(fenstr=fenstr,thinktime=thinktime)
        else:
            self.ai_analyzing = False
            self.root.ids['id_screenmain'].ids['id_btn_analyzing'].icon_size = '28sp'

            self.root.ids['id_screenmain'].ids['id_btn_ai'].disabled = False
            self.root.ids['id_screenmain'].ids['id_btn_ai_red'].disabled = False
            self.root.ids['id_screenmain'].ids['id_btn_ai_black'].disabled = False

            """ if self.uci_engine is not None:            
                goCnt = len(self.uci_engine.goCount)
                if  goCnt >= 1:
                    toast(f"当前还有 {goCnt} 个AI分析在执行") """
        
        Logger.debug(f'X-Chess analyzing: end')
    
    #无限分析直至杀招
    def show_ai_move(self):
        Logger.debug(f'X-Chess show_ai_move: begin')

        if self.show_ai_move_infinite == False:
            if self.ai_analyzing == True:
                toast("请先关闭分析模式")
                return
            #不能开启AI执红和执黑
            if self.ai_red == True:
                toast("请关闭AI执红")
                return
            if self.ai_black == True:
                toast("请关闭AI执黑")
                return
            if self.uci_engine is not None:            
                goCnt = len(self.uci_engine.goCount)
                if  goCnt >= 1:
                    toast(f"当前还有 {goCnt} 个AI分析在执行，请稍后再试")
                    return
            
            nodeid = self.root.ids['id_screenmoves'].ids.id_moveslist.children[0].id
            if nodeid:
                node = self.moves_tree.get_node(nodeid)
                xqfPos = node.data['situation']
                fenstr = sit2Fen(xqfPos)
                nextCamp = self.next_camp
          
                fenstr = f'position fen {fenstr} {nextCamp} - - 0 1' #注意用空格隔开，“b”表示黑方，除此以外都表示红方
                Logger.debug(f'X-Chess :局面00==》{fenstr}')

                Logger.debug(f'X-Chess ai: {self.engine_name=}')
                if self.uci_engine == None:
                    Logger.debug(f'X-Chess ai: 初始化uci引擎')
                    if (f"ENGINE" in self.cfg_info) and (f"engine_filename" in self.cfg_info['ENGINE']):
                        engine_filename = self.cfg_info['ENGINE']['engine_filename']
                        Logger.debug(f'X-Chess ai: {engine_filename=}')
                        settings = self.cfg_info['ENGINE']
                        options = []
                        for k,v in settings.items():
                            if k.startswith('option'):
                                options.append(v)
                        self.uci_engine = UCIEngine(engine_filename=engine_filename,options=options)                            
                    else:
                        toast("uci没有配置")
                        return
                #请求最佳招法    
                #thinktime = 5000                        
                #if (f"ENGINE" in self.cfg_info) and (f"ai_think_time" in self.cfg_info['ENGINE']):
                #    str1 = self.cfg_info['ENGINE']['ai_think_time']
                #    if (str1.isdigit() == True) or (int(str1) >= 0):
                #        thinktime = int(str1)
                #Logger.debug(f'X-Chess ai: {thinktime=}')
                #self.uci_engine.goCount.append('go')
                #self.uci_engine.request_bestmove(fenstr=fenstr,thinktime=thinktime)

                #self.root.ids['id_screenmain'].ids['id_movesnote_input'].text = ""
                #self.root.ids['id_screenmain'].ids['id_movesnote_input'].cancel_selection()
                #定义1个定时器，1秒5次主动轮询结果至到获取到最佳招法
                #Logger.debug(f'X-Chess ai: 定义定时器')
                #定义1个定时器，1秒5次主动轮询结果至到获取到最佳招法，放弃这种做法，一是readline会堵塞，二是通过定时获取一次readline，效率太低
                #Clock.schedule_interval(partial(self.uci_engine.polling_bestmove,fenstr), 0.5)
                #定义1个定时器，as soon as possible (usually next frame.)，为啥要定时执行？
                #Clock.schedule_once(partial(self.uci_engine.polling_aimove,fenstr,thinktime))
                
                self.show_ai_move_infinite = True
                self.root.ids['id_screenmain'].ids['id_btn_ai'].icon_size = '48sp'
                #self.uci_engine.polling_aimove(fenstr=fenstr,thinktime=thinktime)

                #self.root.ids['id_screenmain'].disabled = True
                #self.root.ids['id_screenmain'].ids['id_btn_ai'].disabled = False
                #无限分析
                self.uci_engine.polling_aimove(fenstr=fenstr)
            else:
                toast("还没摆棋呢，请新建局面或者打开棋谱")
        else:
            self.show_ai_move_infinite = False
            self.root.ids['id_screenmain'].ids['id_btn_ai'].icon_size = '28sp'
            self.uci_engine.put_command("stop\n")
            self.uci_engine.goStop = True

            #self.root.ids['id_screenmain'].disabled = False
        
        Logger.debug(f'X-Chess show_ai_move: end')
        
    def set_engine(self):
        Logger.debug(f"X-Chess x-chessapp set_engine: begin")
        #self.menu.dismiss()

        Logger.debug(f"X-Chess x-chessapp set_engine: 111")

        if platform == 'android':#将非android专用组件去掉
            try:
                wg = self.root.ids['id_screensetengine'].ids['id_sel_engine_file']
                if wg != None:
                    self.root.ids['id_screensetengine'].ids['id_sel_engine_file'].parent.remove_widget(wg)
            except Exception as e:
                Logger.debug(f"X-Chess x-chessapp set_engine: Exception= {str(e)}")
            finally:
                pass
        else:#将android专用组件去掉
            try:
                wg = self.root.ids['id_screensetengine'].ids['id_checkbox_inner']
                if wg != None:
                    self.root.ids['id_screensetengine'].ids['id_checkbox_inner'].parent.remove_widget(wg)
                wg = self.root.ids['id_screensetengine'].ids['id_checkbox_inner_lab']
                if wg != None:
                    self.root.ids['id_screensetengine'].ids['id_checkbox_inner_lab'].parent.remove_widget(wg)

                wg = self.root.ids['id_screensetengine'].ids['id_checkbox_outer']
                if wg != None:
                    self.root.ids['id_screensetengine'].ids['id_checkbox_outer'].parent.remove_widget(wg)
                wg = self.root.ids['id_screensetengine'].ids['id_checkbox_outer_lab']
                if wg != None:
                    self.root.ids['id_screensetengine'].ids['id_checkbox_outer_lab'].parent.remove_widget(wg)
            except Exception as e:
                Logger.debug(f"X-Chess x-chessapp set_engine: Exception= {str(e)}")
            finally:
                pass
        
        Logger.debug(f"X-Chess x-chessapp set_engine: 222")

        engine_settings = get_engine_settings()
        options = ""
        for k,v in engine_settings.items():
           print(f"{k=},{v=}")
           if k.startswith('option'):
               options = f"{options}{v}\n"#{os.linesep}
        
        self.root.ids['id_screensetengine'].ids.id_ai_think_time.text = engine_settings['ai_think_time']

        self.engine_name = engine_settings['engine_name']
        Logger.debug(f"X-Chess set_engine: {self.engine_name=}")

        #if self.engine_name == 'xqpy':
        #    self.root.ids['id_screensetengine'].ids['id_checkbox_xqpy'].active = True
        #    self.root.ids['id_screensetengine'].ids['id_checkbox_uci'].active = False
        #else:
        #    self.root.ids['id_screensetengine'].ids['id_checkbox_xqpy'].active = False
        #    self.root.ids['id_screensetengine'].ids['id_checkbox_uci'].active = True

        
        if platform == 'android':
            self.uci_engine_location = engine_settings['engine_location']
            Logger.debug(f"X-Chess set_engine: {self.uci_engine_location=}")
            if self.uci_engine_location == 'inner':
                self.root.ids['id_screensetengine'].ids['id_checkbox_outer'].active = False
                self.root.ids['id_screensetengine'].ids['id_checkbox_inner'].active = True
            else:
                self.root.ids['id_screensetengine'].ids['id_checkbox_outer'].active = True
                self.root.ids['id_screensetengine'].ids['id_checkbox_inner'].active = False


        self.root.ids['id_screensetengine'].ids.id_uci_engine_filename.text = engine_settings['engine_filename']
        self.root.ids['id_screensetengine'].ids.id_uci_options.text = options

        self.root.current_heroes = ""
        self.root.current = "screenSetEngine"

        Logger.debug(f"X-Chess x-chessapp set_engine: end")
    
    def save_engine_settings(self):
        Logger.debug(f'X-Chess save_engine_settings: begin')        

        ai_think_time = self.root.ids['id_screensetengine'].ids.id_ai_think_time.text
        if (ai_think_time.isdigit() == False) or (int(ai_think_time) <= 0):
            toast("思考时间必须为大于0的整数")
            return
        ai_think_time = int(ai_think_time)

        engine_name = self.engine_name

        engine_filename = self.root.ids['id_screensetengine'].ids.id_uci_engine_filename.text

        uci_options = self.root.ids['id_screensetengine'].ids.id_uci_options.text

        uci_engine_location = 'inner'
        if self.uci_engine_location == 'outer':
            uci_engine_location = 'outer'
        

        Logger.debug(f'X-Chess save_engine_settings: {ai_think_time=},{uci_engine_location=},{engine_name=},{engine_filename=},{uci_options=},{os.linesep=}') 

        save_engine_settings(uci_options=uci_options,engine_location=uci_engine_location,engine_name=engine_name,ai_think_time=ai_think_time,engine_filename=engine_filename)

        #更新相关引擎变量
        #self.cfg_info.read(os.path.join(os.getcwd(),'cfg/cfg.ini'),encoding='gbk')
        self.cfg_info.read(self.cfgFileName,encoding='gbk')
        if (f"ENGINE" in self.cfg_info) and (f"engine_name" in self.cfg_info['ENGINE']):
            self.engine_name = self.cfg_info['ENGINE']['engine_name']

        if (f"ENGINE" in self.cfg_info) and (f"engine_location" in self.cfg_info['ENGINE']):
            self.uci_engine_location = self.cfg_info['ENGINE']['engine_location']

        self.uci_engine = None

        Logger.debug(f'X-Chess save_engine_settings: end')
    
    def get_uci_info(self):
        Logger.debug(f'X-Chess get_uci_info: begin') 

        engine_filename = self.root.ids['id_screensetengine'].ids.id_uci_engine_filename.text
        uci_engine = UCIEngine(engine_filename=engine_filename)
        uci_engine.quit_engine()

        Logger.debug(f'X-Chess get_uci_info: {uci_engine.uci_info=}') 
        self.root.ids['id_screensetengine'].ids.id_uci_info.text = uci_engine.uci_info

        Logger.debug(f'X-Chess get_uci_info: end')
    
    def set_engine_file(self, path: str):
        self.exit_manager()
        self.root.ids[f'id_screensetengine'].ids[f'id_uci_engine_filename'].text=path
    
    def select_engine_file(self):
        Logger.debug(f'X-Chess select_engine_file: begin')

        #Window.bind(on_keyboard=self.events)
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,#用户到达目录树根目录时调用的函数
            select_path=lambda path:self.set_engine_file(path=path),   #选择文件/目录时调用的函数
            icon_selection_button="pencil",
            selector='file'#只选择文件
            #ext=['.xqf']            
        )

        uci_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'uci')
        if not os.path.exists(uci_path):
            os.makedirs(uci_path)
        self.file_manager.show(uci_path)
        self.manager_open = True

        Logger.debug(f'X-Chess select_engine_file: end')
    
    #仅限安卓使用
    def set_inner_engine(self):
        Logger.debug(f'X-Chess set_inner_engine: begin')

        if self.root.ids['id_screensetengine'].ids['id_checkbox_inner'].active == True:
            Logger.debug(f'X-Chess set_inner_engine active = True')
            self.root.ids['id_screensetengine'].ids.id_uci_engine_filename.text = os.path.join(os.getcwd(),"uci/pikafish")
        #else:
        #    #Logger.debug(f'X-Chess set_inner_engine active = False')
        #    self.root.ids['id_screensetengine'].ids['id_checkbox_outer'].active = True

        Logger.debug(f'X-Chess set_inner_engine: end')
    
    #仅限安卓使用
    def set_outer_engine(self):
        Logger.debug(f'X-Chess set_outer_engine: begin')
        if self.root.ids['id_screensetengine'].ids['id_checkbox_outer'].active == True:
            Logger.debug(f'X-Chess set_outer_engine active = True')

            #if platform.lower() == "android":

            from android.storage import primary_external_storage_path
            SD_CARD = primary_external_storage_path()
            uci_outer_from_path = os.path.join(SD_CARD,"x-chess/uci")

            #uci_outer_from_path = os.path.join("","E:\htp\象棋\pikafish安卓引擎\stockfish引擎")
            
            #判断是否有且仅有1个exe*
            seachdir = os.path.join(uci_outer_from_path,f'exe*')
            Logger.debug(f'X-Chess set_outer_engine: {seachdir=}')
            files = [name for name in glob.glob(seachdir) if os.path.isfile(name)]        
            Logger.debug(f'X-Chess set_outer_engine: {type(files)=}, {files=}')
            exe_file_count = len(files)
            if exe_file_count != 1:
                Logger.debug(f"在'{uci_outer_from_path}'目录下应该有且只有1个 exe* 文件,其中*是引擎的可执行文件名，且大小写敏感")
                toast(f"在'{uci_outer_from_path}'目录下应该有且只有1个 exe* 文件,其中*是引擎的可执行文件名，且大小写敏感",duration=3)
                return
            
            uci_outer_to_path = os.path.join(os.getcwd(),"uci/outer")

            #删除outer目录下所有文件
            #清空文件夹内文件
            for file in os.listdir(uci_outer_to_path):
                file_path = os.path.join(uci_outer_to_path, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)

            seachdir = os.path.join(uci_outer_from_path,"*")
            files = [name for name in glob.glob(seachdir) if os.path.isfile(name)]
            for file in files:
                filename = os.path.basename(file)
                Logger.debug(f'X-Chess set_outer_engine: copy {file}')
                try:
                    file2 = os.path.join(uci_outer_to_path,filename)
                    Logger.debug(f'X-Chess set_outer_engine: to {file2}')
                    shutil.copy(file,file2)
                except Exception as e:
                    Logger.debug(f'X-Chess set_outer_engine: 复制文件时发生错误: {str(e)}')
                finally:
                    pass
            
            #查找exe*文件
            seachdir = os.path.join(uci_outer_to_path,f'exe*')
            files = [name for name in glob.glob(seachdir) if os.path.isfile(name)]
            self.root.ids['id_screensetengine'].ids.id_uci_engine_filename.text = files[0].replace("exe","")
            
            #else:
            #    pass
        else:
            Logger.debug(f'X-Chess set_outer_engine active = False')
            #self.root.ids['id_screensetengine'].ids['id_checkbox_inner'].active = True

        Logger.debug(f'X-Chess set_outer_engine: end')
    
    def ai_go_black(self):
        Logger.debug(f'X-Chess x-chessapp ai_go_black: begin')
        if self.gameover == False:
            if self.ai_analyzing == True:
                toast("请先关闭分析模式")
                return
            if self.ai_black == False:
                Logger.debug(f'X-Chess x-chessapp ai_go_black: ai执黑')
                self.ai_black = True
                self.root.ids['id_screenmain'].ids['id_btn_ai_black'].icon_size = '48sp'
                if self.next_camp == 'b':
                    #如果AI执棋，让AI走棋                
                    self.ai_go()
            else:
                Logger.debug(f'X-Chess x-chessapp ai_go_black: ai不执黑')
                self.ai_black = False
                self.root.ids['id_screenmain'].ids['id_btn_ai_black'].icon_size = '28sp'
        else:
            toast("胜负已定")

        Logger.debug(f'X-Chess x-chessapp ai_go_black: end')
    
    def ai_go_red(self):
        Logger.debug(f'X-Chess x-chessapp ai_go_red: begin')

        if self.gameover == False:
            if self.ai_analyzing == True:
                toast("请先关闭分析模式")
                return
            if self.ai_red == False:
                Logger.debug(f'X-Chess x-chessapp ai_go_red: ai执红')
                self.ai_red = True
                self.root.ids['id_screenmain'].ids['id_btn_ai_red'].icon_size = '48sp'
                if self.next_camp == 'w':
                    #如果AI执棋，让AI走棋                
                    self.ai_go()
            else:
                Logger.debug(f'X-Chess x-chessapp ai_go_red: ai不执红')
                self.ai_red = False
                self.root.ids['id_screenmain'].ids['id_btn_ai_red'].icon_size = '28sp'
        else:
            toast("胜负已定")

        Logger.debug(f'X-Chess x-chessapp ai_go_red: end')
    
    
    def ai_go(self):
        Logger.debug(f'X-Chess x-chessapp ai_go: begin')

        if (self.ai_black == True and self.next_camp == 'b') or (self.ai_red == True and self.next_camp == 'w'):
            #toast("AI思考中…")
            if self.next_camp == 'b':
                Logger.debug(f'X-Chess x-chessapp ai_go: AI执黑该走棋了')
            elif self.next_camp == 'w':
                Logger.debug(f'X-Chess x-chessapp ai_go: AI执红该走棋了')
            
            nodeid = self.root.ids['id_screenmoves'].ids.id_moveslist.children[0].id
            if nodeid:
                node = self.moves_tree.get_node(nodeid)
                xqfPos = node.data['situation']
                fenstr = sit2Fen(xqfPos)
                nextCamp = self.next_camp

                fenstr = f'position fen {fenstr} {nextCamp} - - 0 1' #注意用空格隔开，“b”表示黑方，除此以外都表示红方
                Logger.debug(f'X-Chess :局面00==》{fenstr}')

                Logger.debug(f'X-Chess ai: {self.engine_name=}')
                if self.uci_engine == None:
                    Logger.debug(f'X-Chess ai: 初始化uci引擎')
                    if (f"ENGINE" in self.cfg_info) and (f"engine_filename" in self.cfg_info['ENGINE']):
                        engine_filename = self.cfg_info['ENGINE']['engine_filename']
                        Logger.debug(f'X-Chess ai: {engine_filename=}')
                        settings = self.cfg_info['ENGINE']
                        options = []
                        for k,v in settings.items():
                            if k.startswith('option'):
                                options.append(v)
                        self.uci_engine = UCIEngine(engine_filename=engine_filename,options=options)                            
                    else:
                        toast("uci没有配置")
                        return
                #请求最佳招法    
                thinktime = 5000                        
                if (f"ENGINE" in self.cfg_info) and (f"ai_think_time" in self.cfg_info['ENGINE']):
                    str1 = self.cfg_info['ENGINE']['ai_think_time']
                    if (str1.isdigit() == True) or (int(str1) >= 0):
                        thinktime = int(str1)
                Logger.debug(f'X-Chess ai: {thinktime=}')

                self.uci_engine.go_bestmove(fenstr=fenstr,thinktime=thinktime)
                
            else:
                toast("还没摆棋呢，请新建局面或者打开棋谱")
        else:
            Logger.debug(f'X-Chess x-chessapp ai_go: 坐山观虎斗')
            pass
        
        Logger.debug(f'X-Chess x-chessapp ai_go: end')
    
    def bottom_top(self):
        curSit = None
        nodeid = self.root.ids['id_screenmoves'].ids.id_moveslist.children[0].id
        if nodeid:
            node = self.moves_tree.get_node(nodeid)
            curSit = node.data['situation']
        else:
            toast("还没摆棋呢，请新建局面或者打开棋谱")
            return
        
        if self.ai_black == True or self.ai_red == True or  self.ai_analyzing == True or self.show_ai_move_infinite == True:
            toast("AI分析期间，不能翻转棋盘")
            return

        if self.root.ids['id_screenmain'].ids.id_chessboard.red_bottom == True:
            self.root.ids['id_screenmain'].ids.id_chessboard.red_bottom = False
        else:
            self.root.ids['id_screenmain'].ids.id_chessboard.red_bottom = True
        
        self.root.ids['id_screenmain'].ids.id_chessboard.bottom2top(curSit)
    
    def set_ui(self):
        Logger.debug(f"X-Chess x-chessapp set_ui: begin")

        Logger.debug(f"X-Chess X_ChessApp set_ui: {self.cfg_info['UI']['mainbgimg']=}")
        if self.cfg_info['UI']['mainbgimg'] == 'DIY':
            self.root.ids['id_screensetui'].ids['id_sw_bkimg'].active = True
        else:
            self.root.ids['id_screensetui'].ids['id_sw_bkimg'].active = False
        
        Logger.debug(f"X-Chess X_ChessApp set_ui: {self.cfg_info['UI']['pieceimg']=}")
        if self.cfg_info['UI']['pieceimg'] == 'DIY':
            self.root.ids['id_screensetui'].ids['id_sw_piece'].active = True
        else:
            self.root.ids['id_screensetui'].ids['id_sw_piece'].active = False

        self.root.current_heroes = ""
        self.root.current = "screenSetUI"

        Logger.debug(f"X-Chess x-chessapp set_ui: end")
    
    def save_ui_settings(self):
        Logger.debug(f'X-Chess save_ui_settings: begin')

        self.cfg_info.read(self.cfgFileName,encoding='gbk')

        if self.root.ids['id_screensetui'].ids['id_sw_bkimg'].active == True:
            Logger.debug(f"X-Chess save_ui_settings: 背景图片：使用自定义图片")
            self.cfg_info.set("UI",'mainbgimg',"DIY")
        else:
            Logger.debug(f"X-Chess save_ui_settings: 背景图片：使用系统图片")
            self.cfg_info.set("UI",'mainbgimg',"")
        
        if self.root.ids['id_screensetui'].ids['id_sw_piece'].active == True:
            Logger.debug(f"X-Chess save_ui_settings: 棋子图片：使用自定义图片")
            self.cfg_info.set("UI",'pieceimg',"DIY")
        else:
            Logger.debug(f"X-Chess save_ui_settings: 棋子图片：使用系统图片")
            self.cfg_info.set("UI",'pieceimg',"")
        
        self.cfg_info.write(open(self.cfgFileName,'w',encoding='gbk'))

        toast("重启后生效")        

        Logger.debug(f'X-Chess save_ui_settings: end')

    

