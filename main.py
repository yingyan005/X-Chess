'''
Author: Paoger
Date: 2023-10-30 10:18:15
LastEditors: Paoger
LastEditTime: 2024-02-05 17:52:01
Description: 

Copyright (c) 2023 by Paoger, All Rights Reserved. 
'''
import os
import sys

#打包时如果指定--noconsole模式时，它会自动将您的sys.stdout和sys.stderr设置为None。所以如果你的代码或库使用日志或写消息到这些流中的任何一个，
# 它将导致一个错误。通常类似于NoneType object has no attribute write。如果这是您收到的错误，
# 那么您需要做的就是将sys.stdout和sys.stderr重定向到一个新的流，如打开的文件或io缓冲区。

#弃用了
#import platform
#systemname = platform.system()#注意它会把android识别为linux，慎用
#print(f"x-chess:{systemname=}")
#if systemname == 'Windows':
#    import io
#    stream = io.StringIO()
#    sys.stdout = stream
#    sys.stderr = stream

#本项目全部from kivy.utils import platform，避免混乱
from kivy.utils import platform
print(f"x-chess:{platform=}")
#if platform == 'win':
#    import io
#    stream = io.StringIO()
#    sys.stdout = stream
#    sys.stderr = stream

print ("Python Version {}".format(str(sys.version).replace('\n', '')))

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

Logger.info('X-Chess main: This is a info message,main will run.')
Logger.debug('X-Chess main: This is a debug message,mian will run.')

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
#print(f"x-chess:{platform=}")
Logger.info(f'X-Chess before main: {platform=}')
#fw = fh = w = h = None
if platform == "win" or platform == "linux":
    #在导入 MD 模块和导入 kivy.core.window.Window 模块之前设置窗口大小
    Config.set('graphics', 'fullscreen', 0)

    # 720 * 324 主要用来调界面，这个比例与手机1600*720一致
    Config.set('graphics', 'width', '324')
    Config.set('graphics', 'height', '720')
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


from x_chessapp import X_ChessApp

if platform == "android":
    from jnius import cast
    from jnius import autoclass
    from android import mActivity, api_version

    def permissions_external_storage(): 
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        Environment = autoclass("android.os.Environment")
        Intent = autoclass("android.content.Intent")
        Settings = autoclass("android.provider.Settings")
        Uri = autoclass("android.net.Uri")
        if api_version > 29:
            # If you have access to the external storage, do whatever you need
            if Environment.isExternalStorageManager():

                # If you don't have access, launch a new activity to show the user the system's dialog
                # to allow access to the external storage
                pass
            else:
                try:
                    activity = mActivity.getApplicationContext()
                    uri = Uri.parse("package:" + activity.getPackageName())
                    intent = Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION, uri)
                    currentActivity = cast(
                    "android.app.Activity", PythonActivity.mActivity
                    )
                    currentActivity.startActivityForResult(intent, 101)
                except:
                    intent = Intent()
                    intent.setAction(Settings.ACTION_MANAGE_ALL_FILES_ACCESS_PERMISSION)
                    currentActivity = cast(
                    "android.app.Activity", PythonActivity.mActivity
                    )
                    currentActivity.startActivityForResult(intent, 101)

if __name__ == '__main__':
    #运行实例
    #try-catch 语句帮助我们识别程序中的错误，并在我们想要它之前阻止控制台关闭
    #try:
    if platform == "win":
        from kivy.resources import resource_add_path
        if hasattr(sys, '_MEIPASS'):
            #用 pyinstaller 打包生成的 exe 文件，在运行时动态生成依赖文件，sys._MEIPASS 就是这些依赖文件所在文件夹的路径
            #通常  C:\Windows\Temp\_MEIxxxx 或 C:\Users\用户名\AppData\Local\Temp\_MEIxxxx
            print(f"{sys._MEIPASS}")
            resource_add_path(os.path.join(sys._MEIPASS))
    
    if platform == "android":
        from android import api_version
        from android.permissions import request_permissions, check_permission

        Logger.info(f'X-Chess main:*** {api_version=}')
        #Logger.info(f'X-Chess main:*** {type(Permission)=}')
        myPermissions = None
        myPermissions = [("android.permission.RUN_SCRIPT"),("android.permission.MANAGE_EXTERNAL_STORAGE"),
                             ("android.permission.READ_EXTERNAL_STORAGE"),("android.permission.WRITE_EXTERNAL_STORAGE"),
                             ("android.permission.FOREGROUND_SERVICE"),("android.permission.SYSTEM_ALERT_WINDOW"),
                             ("android.permission.SYSTEM_OVERLAY_WINDOW"),("android.permission.VIBRATE"),
                             ("android.permission.EXECUTE_SHELL_COMMAND"),("android.permission.EXECUTE_COMMAND"),
                             ("android.permission.INTERNET"),
                             ("android.permission.MANAGE_ALL_FILES_ACCESS_PERMISSION"),("android.permission.MANAGE_EXTERNAL_STORAGE")
                            ]
        request_permissions(myPermissions)

        if api_version > 29:
            Environment = autoclass("android.os.Environment")
            if not Environment.isExternalStorageManager():
                permissions_external_storage()

        p_w = ("android.permission.WRITE_EXTERNAL_STORAGE")
        if check_permission(p_w) == True:
            Logger.debug('X-Chess main: 有 WRITE_EXTERNAL_STORAGE 权限')
            #在存储根目录下创建 X-Chess/xqf:保存棋谱文件，X-Chess/log：log文件,X-Chess/uci：存放引擎
            from android.storage import primary_external_storage_path
            SD_CARD = primary_external_storage_path()

            #初次运行时将配置文件转移到外部目录便于定制
            mypath = os.path.join(SD_CARD,'X-Chess/cfg')
            if not os.path.exists(mypath):
                try:
                    os.makedirs(mypath)
                except Exception as e:
                    Logger.debug(f"X-Chess main: Exception: {str(e)}")
                finally:
                    pass            
            if os.path.exists(mypath):
                #获取当前版本号
                import configparser
                import shutil
                # 读取 INI 文件，给g_theLast_Path赋值
                conf_info = configparser.ConfigParser()
                xc_version = ""
                if len(conf_info.read(os.path.join(os.getcwd(),'cfg/cfg.ini'),encoding='gbk')) != 0:
                    xc_version = conf_info.get("XC","version")
                cfgFileName = os.path.join(mypath,f"cfg{xc_version}.ini")
                if not os.path.exists(cfgFileName):
                    Logger.debug(f"X-Chess main: copy {os.path.join(os.getcwd(),'cfg/cfg.ini')} to {cfgFileName}")
                    shutil.copy(os.path.join(os.getcwd(),'cfg/cfg.ini'),cfgFileName)
                else:
                    Logger.debug(f"X-Chess main: {cfgFileName} 已存在")


            mypath = os.path.join(SD_CARD,'X-Chess/xqf')
            if not os.path.exists(mypath):
                try:
                    os.makedirs(mypath)
                except Exception as e:
                    Logger.debug(f"X-Chess main: Exception: {str(e)}")
                finally:
                    pass
            
            mypath = os.path.join(SD_CARD,'X-Chess/uci')
            if not os.path.exists(mypath):
                try:
                    os.makedirs(mypath)
                except Exception as e:
                    Logger.debug(f"X-Chess main: Exception: {str(e)}")
                finally:
                    pass
            
            mypath = os.path.join(SD_CARD,'X-Chess/log')
            if not os.path.exists(mypath):
                try:
                    os.makedirs(mypath)
                except Exception as e:
                    Logger.debug(f"X-Chess main: Exception: {str(e)}")
                finally:
                    pass

            if os.path.exists(mypath):
                #由于权限问题在用户没有允许时该代码已经执行到，so，闪退后再次运行即可
                try:
                    Config.set('kivy', 'log_dir',os.path.join(SD_CARD,'X-Chess/log'))
                    Logger.info(f"X-Chess main: log_dir={Config.get('kivy', 'log_dir')}")
                    Config.set('kivy', 'log_name','X-Chess_%y-%m-%d_%_.txt')
                    Logger.info(f"X-Chess main: log_name={Config.get('kivy', 'log_name')}")
                except Exception as e:
                    Logger.debug(f"X-Chess main:Exception: {str(e)}")
                finally:
                    pass
        else:
            Logger.debug('X-Chess main: 没有 WRITE_EXTERNAL_STORAGE 权限')
    
    app = X_ChessApp()
    app.run()
    #except Exception as e:
    #    print(e)
    #    input("Press enter.")