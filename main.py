'''
Author: Paoger
Date: 2023-10-30 10:18:15
LastEditors: Paoger
LastEditTime: 2023-12-19 09:22:32
Description: 

Copyright (c) 2023 by Paoger, All Rights Reserved. 
'''
import os
import sys

#打包时如果指定--noconsole模式时，它会自动将您的sys.stdout和sys.stderr设置为None。所以如果你的代码或库使用日志或写消息到这些流中的任何一个，
# 它将导致一个错误。通常类似于NoneType object has no attribute write。如果这是您收到的错误，
# 那么您需要做的就是将sys.stdout和sys.stderr重定向到一个新的流，如打开的文件或io缓冲区。
#import platform
#systemname = platform.system()
#if systemname == 'Windows':
#    import io
#    stream = io.StringIO()
#    sys.stdout = stream
#    sys.stderr = stream

print ("Python Version {}".format(str(sys.version).replace('\n', '')))

from kivy.utils import platform
from kivy.config import Config

""" [kivy]
log_level = info
log_enable = 1
log_dir = logs
log_name = kivy_%y-%m-%d_%_.txt
log_maxfiles = 100 """
#由于pyinstall打包成exe后，__file__非我所想要的，且是临时目录，退出exe后临时目录就被清空了
#Config.set('kivy', 'log_dir',os.path.join(os.path.dirname(os.path.abspath(__file__)),'logs'))
Config.set('kivy', 'log_dir',os.path.join(os.getcwd(),'logs'))
print(f"log_dir={Config.get('kivy', 'log_dir')}")
Config.set('kivy', 'log_name','X-Chess_%y-%m-%d_%_.txt')
print(f"log_name={Config.get('kivy', 'log_name')}")

from kivy.logger import Logger, LOG_LEVELS

Logger.setLevel(LOG_LEVELS["debug"])
#Logger.setLevel(LOG_LEVELS["info"])

Logger.info('X-Chess main: This is a info message:X_ChessApp will run.')
Logger.debug('X-Chess mian: This is a debug message:X_ChessApp will run.')

""" import platform
from kivy.config import Config

systemname = platform.system()
print(f"{systemname=}")
if systemname == 'Windows':
    #在导入 MD 模块和导入 kivy.core.window.Window 模块之前设置窗口大小
    print("***限定Windows操作系统中，该应用的窗口大小，且不可改变***")
    Config.set('graphics','resizable', False) # 窗体可变设置为False
    Config.set('graphics', 'width', '500')
    Config.set('graphics', 'height', '600') """



#systemname = platform.system()
#print(f"{systemname=}")
#if systemname == 'Windows':
print(f"{platform=}")
#fw = fh = w = h = None
if platform == "win":
    #在导入 MD 模块和导入 kivy.core.window.Window 模块之前设置窗口大小
    Config.set('graphics', 'fullscreen', 0)
    Config.set('graphics', 'width', '350')
    Config.set('graphics', 'height', '700')
    #将窗口设置为全屏，便于获取屏幕分辨率
    #Config.set('graphics', 'fullscreen', 1)
    #Config.set('graphics', 'position', 'custom')
    #在这里设置位置有效，不知为何
    #Config.set('graphics', 'top', '50')
    #Config.set('graphics', 'left', '800')
    #print("***限定Windows操作系统中，该应用的窗口大小，且不可改变***")
    #Config.set('graphics','resizable', False) # 窗体可变设置为False

    ##一定要在Config.set之后
    #from kivy.core.window import Window
    #print(f"global==>{Window.size=}")
    #Logger.debug(f"global==>{Window.size=}")
    #fw = Window.size[0]
    #fh = Window.size[1]
    ##打包成exe后，不知为何 Window.size=800*600,so
    #if fw < 1366:
    #    fw = 1366
    #if fh < 768:
    #    fh = 768
    #h = fh * 8.7 / 10#8.7 / 10
    #w = h * 5.2 / 10
    #print(f"global 8.7 5.2==>{w=},{h=}")
    #Logger.debug(f"global 8.7 5.2==>{w=},{h=}")
    #Window.fullscreen = False
    #Window.size = (w, h)
    ##Window.top = fh - h
    ##Window.left = fw - w

from kivy.resources import resource_add_path

from x_chessapp import X_ChessApp
    
if __name__ == '__main__':
    #运行实例
    #try-catch 语句帮助我们识别程序中的错误，并在我们想要它之前阻止控制台关闭
    #try:
    if platform == "win":
        if hasattr(sys, '_MEIPASS'):
            #用 pyinstaller 打包生成的 exe 文件，在运行时动态生成依赖文件，sys._MEIPASS 就是这些依赖文件所在文件夹的路径
            #通常  C:\Windows\Temp\_MEIxxxx 或 C:\Users\用户名\AppData\Local\Temp\_MEIxxxx
            print(f"{sys._MEIPASS}")
            resource_add_path(os.path.join(sys._MEIPASS))
    
    if platform == "android":
        #import android
        #module 'android' has no attribute 'os',可能与app编译有关，参见https://blog.csdn.net/tkwxty/article/details/104842417
        #sdk_version = android.os.Build.VERSION.SDK_INT
        sdk_version = 29
        Logger.info(f'X-Chess main: {sdk_version=}')
        if sdk_version >= 29:
            Logger.info(f'X-Chess main: ***申请安卓权限：READ_EXTERNAL_STORAGE WRITE_EXTERNAL_STORAGE INTERNET***')
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.WRITE_EXTERNAL_STORAGE,Permission.READ_EXTERNAL_STORAGE,Permission.INTERNET])
            #request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE, Permission.INTERNET,Permission.PERMISSIONS_STORAGE,Permission.REQUEST_EXTERNAL_STORAGE])
            #app_folder = os.path.dirname(os.path.abspath(__file__))
            #from android.storage import primary_external_storage_path
            #appwd=primary_external_storage_path()+'/Download/yourapp'
            #SD_CARD = primary_external_storage_path()
        else:
            Logger.info(f'X-Chess main: ***不需要申请安卓权限：READ_EXTERNAL_STORAGE WRITE_EXTERNAL_STORAGE INTERNET***')

    app = X_ChessApp()
    app.run()
    #except Exception as e:
    #    print(e)
    #    input("Press enter.")