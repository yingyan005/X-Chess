import os
import subprocess
import datetime
import time
import threading
#import platform
#systemname = platform.system()

from kivy.utils import platform
from kivy.logger import Logger
from kivy.clock import Clock
from functools import partial

from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.utils import asynckivy as ak
#import asynckivy as ak

from situation import print_situation,sit2Fen
from piece import Piece
from piecewidget import PieceWidget


"""
uci协议也可参考
https://www.xqbase.com/protocol/uci.htm

"""

class UCIEngine:
    eng_proc = None
    engine_filename = None
    uci_info = ""

    #go指令计数器，每发送一次go指令，增加1次，每获取到bestmove，减少1次
    goCount = []

    #是否发出了stop指令，如果发出了stop指令，则忽略readline读取的内容
    goStop = False

    #线程函数内循环间休眠时间，便于界面有所反应
    asysleeptime = 0.01

    def __init__(self,engine_filename,options=None):
        #0. 使用subprocess.Popen函数创建一个新的进程对象，该进程对象将执行UCl引擎。
        #engine_path = os.path.join("E:\htp\象棋\PengfeiChess\pikafish230218", "pikafish-bmi2.exe")
        self.engine_filename = engine_filename

        app = MDApp.get_running_app()
        app.root.ids['id_screenmain'].ids['id_movesnote_input'].hint_text= os.path.basename(self.engine_filename)

        Logger.debug(f"X-Chess UCIEngine:{platform=}")

        #if systemname == "Windows":
        if platform == "win":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags = subprocess.CREATE_NEW_CONSOLE | subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

            file_path = os.path.dirname(f'{self.engine_filename}')
            Logger.debug(f"X-Chess UCIEngine:subprocess.run {file_path=}")

            self.eng_proc = subprocess.Popen(self.engine_filename,cwd=file_path, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                    universal_newlines=True,startupinfo = startupinfo)
        elif platform == "linux":
            self.eng_proc = subprocess.Popen(self.engine_filename, stdin=subprocess.PIPE, stdout=subprocess.PIPE,universal_newlines=True)
        elif platform == "android":
            #cmd = ['ls', '-l']
            ##执行shell命令
            #result = subprocess.run(cmd, stdout=subprocess.PIPE)
            ##打印输出
            ##print(result.stdout.decode())
            #Logger.debug(f"X-Chess UCIEngine:subprocess.run {cmd},{result.stdout.decode()}")
#
            #result = subprocess.Popen("ls", stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            #                        universal_newlines=True)
            #Logger.debug(f"X-Chess UCIEngine:subprocess.Popen {cmd},{result.stdout.decode()}")

            #Logger.debug(f"X-Chess UCIEngine:0000000000000")
            #try:
            #    #能执行
            #    cmd = ["chmod",f" 777 {self.engine_filename}"]
            #    result = subprocess.run(cmd, stdout=subprocess.PIPE)
            #    Logger.debug(f"X-Chess UCIEngine:subprocess.run {cmd},{result.stdout.decode()}")
            #    #toast("000 正常")
            #except Exception as e:
            #    Logger.debug(f"X-Chess UCIEngine:subprocess Exception: {str(e)}")
            #finally:
            #    pass

            #Logger.debug(f"X-Chess UCIEngine:111111111111")
            #try:
            #    #内置引擎&外置引擎：这种方式能正常调用，但不是我要的
            #    cmd = ['/system/bin/sh', f'{self.engine_filename}']
            #    result = subprocess.run(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,universal_newlines=True)                
            #    Logger.debug(f"X-Chess UCIEngine:subprocess.run {cmd}")
            #    toast("111 正常")
            #except Exception as e:
            #    Logger.debug(f"X-Chess UCIEngine:subprocess Exception: {str(e)}")
            #finally:
            #    pass

            #Logger.debug(f"X-Chess UCIEngine:222222222222")
            #try:
            #    #内置引擎&外置引擎：[Errno 13] Permission denied
            #    cmd = [f'{self.engine_filename}']
            #    result = subprocess.run(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,universal_newlines=True)
            #    Logger.debug(f"X-Chess UCIEngine:subprocess.run {cmd}")
            #    toast("222 正常")
            #except Exception as e:
            #    Logger.debug(f"X-Chess UCIEngine:subprocess Exception: {str(e)}")
            #finally:
            #    pass

            #Logger.debug(f"X-Chess UCIEngine:333333333333333")
            #try:
            #    #内置引擎&外置引擎：[Errno 13] Permission denied
            #    cmd = [f'{self.engine_filename}']
            #    result = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,universal_newlines=True)
            #    Logger.debug(f"X-Chess UCIEngine:subprocess.Popen {cmd}")
            #    toast("333 正常")
            #except Exception as e:
            #    Logger.debug(f"X-Chess UCIEngine:subprocess Exception: {str(e)}")
            #finally:
            #    pass

            #Logger.debug(f"X-Chess UCIEngine:44444444444")
            #try:
            #    #故意试个不存在的,得到预期：subprocess Exception: [Errno 2] No such file or directory
            #    cmd = [f'{self.engine_filename}xxx']
            #    self.eng_proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,universal_newlines=True)
            #    Logger.debug(f"X-Chess UCIEngine:subprocess.Popen {cmd},")
            #    toast("444 正常")
            #except Exception as e:
            #    Logger.debug(f"X-Chess UCIEngine:subprocess Exception: {str(e)}")
            #finally:
            #    pass

            cmd = ['ls', '-la',f'{self.engine_filename}']
            #执行shell命令
            result = subprocess.run(cmd, stdout=subprocess.PIPE)
            #打印输出
            #print(result.stdout.decode())
            Logger.debug(f"X-Chess UCIEngine:subprocess.run {cmd},{result.stdout.decode()}")

            cmd = ['chmod', '777',f'{self.engine_filename}']
            #执行shell命令
            result = subprocess.run(cmd, stdout=subprocess.PIPE)
            #打印输出
            #print(result.stdout.decode())
            Logger.debug(f"X-Chess UCIEngine:subprocess.run {cmd},{result.stdout.decode()}")

            cmd = ['ls', '-la',f'{self.engine_filename}']
            #执行shell命令
            result = subprocess.run(cmd, stdout=subprocess.PIPE)
            #打印输出
            #print(result.stdout.decode())
            Logger.debug(f"X-Chess UCIEngine:subprocess.run {cmd},{result.stdout.decode()}")

            file_path = os.path.dirname(f'{self.engine_filename}')
            Logger.debug(f"X-Chess UCIEngine:subprocess.run {file_path=}")

            Logger.debug(f"X-Chess UCIEngine:subprocess.run {file_path=}")

            Logger.debug(f"X-Chess UCIEngine:555555555555")
            try:
                #内置引擎&外置引擎：subprocess Exception: [Errno 13] Permission denied
                cmd = [f'{self.engine_filename}']
                self.eng_proc = subprocess.Popen(cmd,cwd=file_path, stdin=subprocess.PIPE, stdout=subprocess.PIPE,universal_newlines=True)
                Logger.debug(f"X-Chess UCIEngine:subprocess.Popen {cmd},pid:{self.eng_proc.pid}")
                #toast("555 引擎启动正常")

                pro_name = os.path.basename(self.engine_filename)
                cmd = ['ps', '-ef','|','grep',f'{pro_name}']
                #执行shell命令
                result = subprocess.run(cmd, stdout=subprocess.PIPE)
                #打印输出
                #print(result.stdout.decode())
                Logger.debug(f"X-Chess UCIEngine:subprocess.run {cmd},{result.stdout.decode()}")
            except Exception as e:
                Logger.debug(f"X-Chess UCIEngine:subprocess Exception: {str(e)}")

                Logger.debug(f"X-Chess UCIEngine:66666666666666")
                try:
                    #su :可以正常调起来
                    cmd = ['su',f'{self.engine_filename}']
                    self.eng_proc = subprocess.Popen(cmd,cwd=file_path, stdin=subprocess.PIPE, stdout=subprocess.PIPE,universal_newlines=True)
                    Logger.debug(f"X-Chess UCIEngine:subprocess.Popen {cmd},pid:{self.eng_proc.pid}")
                    toast("666 su 引擎启动正常")

                    pro_name = os.path.basename(self.engine_filename)
                    cmd = ['ps', '-ef','|','grep',f'{pro_name}']
                    #执行shell命令
                    result = subprocess.run(cmd, stdout=subprocess.PIPE)
                    #打印输出
                    #print(result.stdout.decode())
                    Logger.debug(f"X-Chess UCIEngine:subprocess.run {cmd},{result.stdout.decode()}")

                except Exception as e:
                    Logger.debug(f"X-Chess UCIEngine:subprocess Exception: {str(e)}")
                finally:
                    pass

            finally:
                pass

        else:
            self.eng_proc = subprocess.Popen(self.engine_filename, stdin=subprocess.PIPE, stdout=subprocess.PIPE,universal_newlines=True)
        
              
        """
        1.uci 
告诉引擎使用UCI协议，这将作为引擎启动后的第一个命令发送，以告诉引擎切换到UCI模式。
在收到UCI命令后，引擎必须用 id命令来帮助GUI识别自己的身份。
并发送 option命令以告诉GUI该引擎支持哪些引擎设置（如果有的话）
之后，引擎应该发送 uciok 来确认UCI模式
如果在一定时间内没有发送uciok，引擎进程将被GUI杀死
        """
        Logger.debug(f"X-Chess UCIEngine:***uci==>")
        self.eng_proc.stdin.write("uci\n")
        self.eng_proc.stdin.flush()#刷新锾冲区，确保指令被发送给引擎
        #等待"uciok"响应
        while True:
            output = self.eng_proc.stdout.readline().strip()
            self.uci_info = f"{self.uci_info}{output}\n"
            Logger.debug(f"X-Chess UCIEngine:{output}")
            if output.startswith('id name'):
                idname = output.split(' ')
                uciname = idname[2:]
                Logger.debug(f"X-Chess UCIEngine:{idname=},{uciname=}")
                app.root.ids['id_screenmain'].ids['id_movesnote_input'].hint_text= ' '.join(uciname)

            #time.sleep(1) #暂停1秒
            if "uciok" == output :#uciok
                break
        Logger.debug(f"X-Chess UCIEngine:***<==uciok")
        """
        uci==>
Pikafish 2023-02-17 by the Pikafish developers (see AUTHORS file)
id name Pikafish 2023-02-17
id author the Pikafish developers (see AUTHORS file)
#option name <id> type <t> [default <x>] [min <x>] [max <x>] [var <x> [var <x> [...]]]
option name Debug Log File type string default
option name Threads type spin default 1 min 1 max 1024
option name Hash type spin default 16 min 1 max 33554432
option name Clear Hash type button
#Clear hash:清除哈希。清除引擎目前的哈希记忆
option name Ponder type check default false
option name MultiPV type spin default 1 min 1 max 500
#MultiPV:多主变思考。引擎分析时默认是1个主要变化，当改变此选项，引擎会增加思考的主变数量并同时显示，会分配相同的算力给各个主变思考
option name Skill Level type spin default 20 min 0 max 20
#Skill Level:引擎的棋力水平。设置范围0、20，默认为最强的20。可用作人与引擎对弈
option name Move Overhead type spin default 10 min 0 max 5000
#Move overhead:出招提前量。引擎提前出招的时间，例如默认为10，引擎假设会有10亳秒延迟，为防超时所以会提前出招。设置范围0、5000，单位是亳秒。
#（注意，只有引擎自己控制时间时该设置才会有效，请分辨是否是界面在控制时间）
option name Slow Mover type spin default 100 min 10 max 1000
#Slow mover：调整引擎的时间控制。设置范围10、1000，默认值为100正常值，越低引擎走得越快，越高引擎走得越慢。
#（只有引擎自己控制时间时该设置才会有效，且若为固定步时则该设置无效）
option name nodestime type spin default 0 min 0 max 10000
option name Sixty Move Rule type check default true
#Sixty move rule:60回合自然限招规则。开启时引擎将会考虑到60回合不吃子判和，将60回合不吃子视为0 分，可以提高棋力。
#如果分析局面不考虑60回合，或者不喜欢，或者平台不兼容皮卡鱼60规则，则可以关闭。皮卡鱼的60回合规则不会把一方多于10次的将军回合计入，
#兼容天天象棋与奕天（由于奕天不会自动判和，而兵河界面的60规则与皮卡鱼不兼容，所以在奕天不适合开启60规则）
option name Strict Three Fold type check default false
#Strict three fold：相同局面出现3次判决。主流引擎为了棋力都是相同局面出现2次判决。开启将会大幅度降低棋力，只适合极少因为相同局面2次判决而导致错误分析的局面，例如
#3aka3 /4n4/9 /9 /9/9/9 /2C6/2r6/3AK4 w, 这个局面实际上是和棋，因为实战并不是相同局面出现2次判决。
option name Mate Threat Depth type spin default 1 min 0 max 10
#Mate Threat Depth:该选项在Repetition Rule里设定为中国规则才会生效，设置范围0、10，设置0则引擎不会判断“杀"。
#设置1、10引擎会在搜索中判断循环招法是不是1、1 0步内的“杀"，而“杀"在中规里可能导致循环违规。设置得越高棋力下降越严重。适合纯人在中规环境下拆棋
option name Repetition Rule type combo default AsianRule var AsianRule var ChineseRule var TiantianRule
option name UCI_LimitStrength type check default false
option name UCI_Elo type spin default 1350 min 1350 max 2850
option name UCI_WDLCentipawn type check default true
#UCI_WDLCentipawn:胜率分数。根据胜率模型转换的分数，关闭会显示原始分数，如果不习惯胜率分就关闭
option name UCI_ShowWDL type check default false
#除显示分数外还显示胜率负率和棋率
option name EvalFile type string default pikafish.nnue
uciok
<==uciok
        """
        """ ucicmd = "setoption name Hash value 128"
        Logger.debug(f"X-Chess UCIEngine:***{ucicmd}==>")
        self.eng_proc.stdin.write(f"{ucicmd}\n")
        self.eng_proc.stdin.flush()#刷新锾冲区，确保指令被发送给引擎

        ucicmd = "setoption name MultiPV value 2"
        Logger.debug(f"X-Chess UCIEngine:***{ucicmd}==>")
        self.eng_proc.stdin.write(f"{ucicmd}\n")
        self.eng_proc.stdin.flush()

        ucicmd = "setoption name UCI_WDLCentipawn value false"
        Logger.debug(f"X-Chess UCIEngine:***{ucicmd}==>")
        self.eng_proc.stdin.write(f"{ucicmd}\n")
        self.eng_proc.stdin.flush()

        ucicmd = "setoption name UCI_ShowWDL value true"
        Logger.debug(f"X-Chess UCIEngine:***{ucicmd}==>")
        self.eng_proc.stdin.write(f"{ucicmd}\n")
        self.eng_proc.stdin.flush() """

        if options  and isinstance(options, list):
            for op in options:
                ucicmd = f"{op}"
                Logger.debug(f"X-Chess UCIEngine:***{ucicmd}==>")
                self.eng_proc.stdin.write(f"{ucicmd}\n")
                self.eng_proc.stdin.flush()
       

        """
        2 debug [ on | off ]
开启或关闭引擎的调试模式。
在调试模式下，引擎应该向GUI发送额外的信息来帮助调试，例如，用 info string命令
这个模式应该在默认情况下被关闭，这个命令可以在任何时候被发送，包括引擎思考时
        """

        """
        3 isready
这是用来使引擎与GUI同步。当GUI发送了一条或多条命令，可能需要一些时间来完成时、这个命令可以用来等待引擎再次准备好
或者用来确认引擎是否在正常运行。
例如，这条命令应该在设置tablebases的路径之后发送，因为这可能需要一些时间。
在引擎被要求做任何搜索之前，也需要这个命令，以等待引擎完成初始化。
这条命令必须总是以 readyok来回答，也可以在引擎正在计算的时候发送。
在这种情况下，引擎也应该立即回答 readyok而不停止搜索。
        """
        #发送"isneady”指令
        Logger.debug(f"X-Chess UCIEngine:***isready==>")
        self.eng_proc.stdin.write("isready\n")
        self.eng_proc.stdin.flush()
        #等待“readyok”响应
        while True:
            output = self.eng_proc.stdout.readline().strip()
            rst = output
            Logger.debug(f"X-Chess UCIEngine:{rst}")
            #time.sleep(1) #暂停1秒
            if "readyok" == rst :#readyok
                break
        Logger.debug(f"X-Chess UCIEngine:***<==readyok")
    
    def quit_engine(self):
        command = "quit"
        Logger.debug(f"X-Chess UCIEngine:***{command}==>")
        self.eng_proc.stdin.write(command + "\n")
        self.eng_proc.stdin.flush()#刷新锾冲区，确保指令被发送给引擎
    
    def put_command(self, command):
        command = command.replace("\n","")
        Logger.debug(f"X-Chess UCIEngine:***{command}==>")
        self.eng_proc.stdin.write(command + "\n")
        self.eng_proc.stdin.flush()#刷新锾冲区，确保指令被发送给引擎
    
    def get_response(self):        
        for line in self.eng_proc.stdout:
            print(line.strip())
    
    """
    info
    可以包含的信息有：
depth x
引擎的搜索深度
seldepth x
选择性的搜索深度、
如果引擎发送seldepth，在同一个字符串中还必须有一个 “深度”。
time x
搜索的时间，以毫秒为单位，这个应该和pv一起发送。
node x
搜索到的x个节点，引擎应该定期发送这个信息。
pv …
找到的最佳线路
multipv x
这是在多pv模式下的信息。
它总是跟在pv后，表示该线路是第几好的线路
score
cp x
返回以百分兵值为单位的分数
mate x
表示在x步内有杀棋
lowerbound x
该分数是一个下限。
upperbound x
该分数是一个上限。
currmove …
目前正在搜索的走法。
currmovenumber x
当前搜索的棋步的编号，对于第一步棋，x应该是1而不是0。
hashfull x
Hash表的占用率（单位是千分之一），它也会隔一定时间显示出来。
nps x
每秒搜索x个节点，引擎应定期发送此信息。
tbhits x
在残局表中发现的位置数。
cpuload x
引擎的cpu使用率。
string …
返回一些额外信息（通常是调试信息）
这行其后的所有字符将被解释为string信息
currline …
这是引擎正在计算的当前行。
引擎在一个以上的cpu上运行。 = 1,2,3…
如果引擎只使用一个cpu，可以省略。
如果大于1，总是一起发送k个字符串中的所有k行。
只有当选项UCI_ShowCurrLine被设置为true时，引擎才应该发送这个。
    """
    
    def get_bestmove(self,node,nextCamp='w',thinktime=5000):
        app = MDApp.get_running_app()
        app.root.ids['id_screenmain'].ids['id_movesnote_input'].text = ""
        app.root.ids['id_screenmain'].ids['id_movesnote_input'].cancel_selection()

        #读取引擎返回的走法
        aimove = []

        xqfPos = node.data['situation']
        #print_situation("XQF situation",xqfPos)

        fenstr = sit2Fen(xqfPos)    
        fenstr = f'position fen {fenstr} {nextCamp} - - 0 1' #注意用空格隔开，“b”表示黑方，除此以外都表示红方
        Logger.debug(f'X-Chess UCIEngine:局面00==》{fenstr}')

        self.put_command(f'{fenstr}\n')

        Logger.debug(f'X-Chess UCIEngine:{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} 开始思考{thinktime/1000}秒')
        self.put_command(f"go movetime {thinktime}\n")

        last_result = ""
        bestmove = ""
        max_try_count = 0
        while True:
            self.eng_proc.poll() 
            Logger.debug(f'X-Chess UCIEngine: {self.eng_proc.poll()=}')
     
            line = self.eng_proc.stdout.readline()
            Logger.debug(f'X-Chess UCIEngine:line:<{line=}>')
            if line == "":
                time.sleep(1)
                max_try_count = max_try_count + 1
            else:
                max_try_count = 0
            
            if max_try_count > 3:
                break#避免陷入死循环
            
            if line.startswith('bestmove'):
                #txt = app.root.ids['id_screenmain'].ids['id_movesnote_input'].text 
                #app.root.ids['id_screenmain'].ids['id_movesnote_input'].text = f'{line}{txt}'
                #app.root.ids['id_screenmain'].ids['id_movesnote_input'].cancel_selection()
                bestmove = line
                break
            else:
                last_result = line

        Logger.debug(f'X-Chess UCIEngine:{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} 结束思考')
        Logger.debug(f'X-Chess UCIEngine:***<==bestmove:{last_result=}')
        Logger.debug(f'X-Chess UCIEngine:***<==bestmove:{bestmove=}')

        if bestmove.find('none') == -1:#有招        
            bestmove = bestmove.split()[1]
            bestmove = bestmove.replace('a','0')
            bestmove = bestmove.replace('b','1')
            bestmove = bestmove.replace('c','2')
            bestmove = bestmove.replace('d','3')
            bestmove = bestmove.replace('e','4')
            bestmove = bestmove.replace('f','5')
            bestmove = bestmove.replace('g','6')
            bestmove = bestmove.replace('h','7')
            bestmove = bestmove.replace('i','8')
            se = list(bestmove)
            for item in se:
                aimove.append(int(item))
        
        infolist = last_result.split(' ')
        #print(f'{infolist=}')
        score = wdl = depth =  nodes = nps = pv = mate = hashfull = ''
        i = 0
        matecount = None
        for item in infolist:
            #print(f'{item}')
            if item == 'score': 
                score = f'分数{infolist[i+2]}'
            elif item == 'wdl':
                wdl = f'胜率{infolist[i+1]} 和率{infolist[i+2]} 负率{infolist[i+3]}'
            elif item == 'depth':
                depth = f'深度{infolist[i+1]}'
            #elif item == 'nodes':
            #    nodes = f'节点数{infolist[i+1]}'
            elif item == 'nps':
                nps = f'引擎速度{infolist[i+1]}'
            elif item == 'hashfull':
                hashfull = f'Hash占用率{infolist[i+1]}'
            elif item == 'mate':
                matecount = int(infolist[i+1])
                if matecount == 0:
                    mate = f'已杀'
                else:
                    mate = f'{matecount}步成杀'
            
            i = i + 1
        #pv = last_result.split(' pv ')[1]
        if matecount != None and matecount == 0:
            app.root.ids['id_screenmain'].ids['id_movesnote_input'].text = f'胜负已定'
            app.gameover = True
        elif matecount != None and matecount >= 1:
            app.root.ids['id_screenmain'].ids['id_movesnote_input'].text = f'有杀 {wdl} {mate}\n{depth}'
        else:
            app.root.ids['id_screenmain'].ids['id_movesnote_input'].text = f'{score} {wdl} {mate}\n{depth} {hashfull} {nps}'
        app.root.ids['id_screenmain'].ids['id_movesnote_input'].cancel_selection()

        return aimove
    
    #请求最佳招法，该函数仅发送go指令，并不返回结果，需调用方循环主动查询结果
    def request_bestmove(self,fenstr,thinktime=5000):
        self.put_command(f'{fenstr}\n')

        Logger.debug(f'X-Chess UCIEngine:{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} 开始思考{thinktime/1000}秒')
        self.put_command(f"go movetime {thinktime}\n")
    
    #轮询最佳招法，若有，则画出最佳招法示意线
    def polling_bestmove(self,fenstr,dt):
        Logger.debug(f'X-Chess UCIEngine polling_bestmove:begin {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")} 开始本次轮询')
        Logger.debug(f'X-Chess UCIEngine polling_bestmove:{fenstr=}')

        app = MDApp.get_running_app()        
        
        Logger.debug(f'X-Chess UCIEngine polling_bestmove:before readline {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}')
        line = self.eng_proc.stdout.readline()
        Logger.debug(f'X-Chess UCIEngine polling_bestmove:{line=}')
        Logger.debug(f'X-Chess UCIEngine polling_bestmove:after readline {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}')        

        #局面是否发生变化
        bSituationChanged = False
        #由于readline会堵塞，在堵塞期间局面可能会发生变化，s0
        curFen = ""
        nodeid = app.root.ids['id_screenmoves'].ids.id_moveslist.children[0].id
        if nodeid:
            node = app.moves_tree.get_node(nodeid)
            xqfPos = node.data['situation']
            curFen = sit2Fen(xqfPos)
            nextCamp = app.next_camp
            curFen = f'position fen {curFen} {nextCamp} - - 0 1' #注意用空格隔开，“b”表示黑方，除此以外都表示红方
            Logger.debug(f'X-Chess UCIEngine polling_bestmove:{curFen=}')

            if curFen != fenstr:#局面发生了变化，忽略当前info的处理
                Logger.debug(f'X-Chess UCIEngine polling_bestmove:curFen != fenstr,局面发生了变化')
                bSituationChanged = True
        
        Logger.debug(f'X-Chess UCIEngine polling_bestmove:局面是否发生了变化：{bSituationChanged}')

        #是否是最佳招法
        bGetBestMove = False
        if line.startswith('bestmove'):#与go成对出现，至此引擎才发出下一次go的info
            bGetBestMove = True
            Logger.debug(f'X-Chess UCIEngine polling_bestmove:go{len(self.goCount)} bestmove')
            self.goCount.pop() #与go成对出现
        
        if bSituationChanged == True and bGetBestMove == False:#循环readline至到获取到bestmove
            while True:
                line = self.eng_proc.stdout.readline()
                Logger.debug(f'X-Chess UCIEngine:line:<{line=}>')
                if line.startswith('bestmove'):
                    bGetBestMove = True
                    Logger.debug(f'X-Chess UCIEngine polling_bestmove:go{len(self.goCount)} bestmove')
                    self.goCount.pop() #与go成对出现

                    Logger.debug(f'X-Chess UCIEngine polling_bestmove:curFen != fenstr,局面发生了变化，本轮go的info结束了，开启新局面的go')
                    self.put_command("stop")
                    #继续分析
                    self.goCount.append('go')
                    thinktime = 5000                        
                    if (f"ENGINE" in app.cfg_info) and (f"ai_think_time" in app.cfg_info['ENGINE']):
                        str1 = app.cfg_info['ENGINE']['ai_think_time']
                        if (str1.isdigit() == True) or (int(str1) >= 0):
                            thinktime = int(str1)
                    self.request_go_analyzing(fenstr=curFen,thinktime=thinktime)
                            
                    app.root.ids['id_screenmain'].ids.id_chessboard.remove_AllAIarrows()
                            
                    #定义1个定时器，1秒5次主动轮询结果至到获取到最佳招法
                    Logger.debug(f'X-Chess UCIEngine polling_bestmove: 定义定时器')
                    app.ai_infinite_event = Clock.schedule_interval(partial(self.polling_bestmove,curFen), 0.5)
                    return False#结束本次定时器的轮询
        else:
            if line.find('depth') == -1:
                if line.find('bestmove') != -1:
                    Logger.debug(f'X-Chess UCIEngine polling_bestmove: end {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")} 本轮go的info结束了，结束本轮轮询')
                    return False
                else:
                    Logger.debug(f'X-Chess UCIEngine polling_bestmove:不是分析产物 end {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")} 结束本次轮询')
                    return True

            infolist = line.split(' ')
            #print(f'{infolist=}')
            score = wdl = depth =  nodes = nps = pv = mate = hashfull = ''
            i = 0
            matecount = None
            for item in infolist:
                #print(f'{item}')
                if item == 'score': 
                    score = f'分数{infolist[i+2]}'
                elif item == 'wdl':
                    wdl = f'胜率{infolist[i+1]} 和率{infolist[i+2]} 负率{infolist[i+3]}'
                elif item == 'depth':
                    depth = f'深度{infolist[i+1]}'
                elif item == 'nodes':
                    nodes = f'节点数{infolist[i+1]}'
                elif item == 'nps':
                    nps = f'引擎速度{infolist[i+1]}'
                elif item == 'hashfull':
                    hashfull = f'Hash占用率{infolist[i+1]}'
                elif item == 'mate':
                    matecount = int(infolist[i+1])
                    if matecount == 0:
                        mate = f'已杀'
                    else:
                        mate = f'{matecount}步成杀'
                elif item == 'pv':
                    pv = f'{infolist[i+1]}'
                
                i = i + 1
            #end for item in infolist:
            
            esxy=[]
            #获取招法名称
            if pv != "":
                pv = pv.replace('\n','')
                nodeid = app.root.ids['id_screenmoves'].ids.id_moveslist.children[0].id
                node = app.moves_tree.get_node(nodeid)
                
                pv = pv.replace('a','0')
                pv = pv.replace('b','1')
                pv = pv.replace('c','2')
                pv = pv.replace('d','3')
                pv = pv.replace('e','4')
                pv = pv.replace('f','5')
                pv = pv.replace('g','6')
                pv = pv.replace('h','7')
                pv = pv.replace('i','8')
                se = list(pv)
                esxy=[]
                for item in se:
                    esxy.append(int(item))
                
                if (f"{esxy[0]},{esxy[1]}" in node.data['situation']) and isinstance(node.data['situation'][f'{esxy[0]},{esxy[1]}'],Piece):
                    p = node.data['situation'][f'{esxy[0]},{esxy[1]}']
                    if p is not None:
                        pv =p.getMoveName(esxy[2],esxy[3],node.data['situation'])
                    else:
                        Logger.debug(f'X-Chess UCIEngine polling_bestmove:end {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")} 结束本次轮询')
                        return True
                else:
                    Logger.debug(f'X-Chess UCIEngine polling_bestmove:end {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")} 结束本次轮询')
                    return True
                
            otherInf = None
            if matecount != None and matecount == 0:
                otherInf = f'胜负已定'
                app.gameover = True
            elif matecount != None and matecount >= 1:
                otherInf = f'有杀 {wdl} {mate} {depth}'
            else:
                otherInf = f'{depth} {pv} {score} {wdl} {mate} {hashfull} {nps}'
        
            if otherInf is not None:
                #txt = app.root.ids['id_screenmain'].ids['id_movesnote_input'].text
                app.root.ids['id_screenmain'].ids['id_movesnote_input'].text = f'{otherInf}'
                app.root.ids['id_screenmain'].ids['id_movesnote_input'].cancel_selection()
            
            if len(esxy) >= 4:
                #显示最佳招法
                app.root.ids['id_screenmain'].ids.id_chessboard.remove_AllAIarrows()
                #app.root.ids['id_screenmain'].ids.id_chessboard.add_aiarrow(esxy[0],esxy[1],esxy[2],esxy[3])
                s_board_x = s_board_y = e_board_x = e_board_y = None
                if app.root.ids['id_screenmain'].ids.id_chessboard.red_bottom == True:#红下黑上
                    s_board_x = esxy[0]
                    s_board_y = esxy[1]
                    e_board_x = esxy[2]
                    e_board_y = esxy[3]
                else:#红上黑下
                    s_board_x = abs(esxy[0]-8)
                    s_board_y = abs(esxy[1]-9)
                    e_board_x = abs(esxy[2]-8)
                    e_board_y = abs(esxy[3]-9)
                app.root.ids['id_screenmain'].ids.id_chessboard.add_aiarrow(s_board_x,s_board_y,e_board_x,e_board_y)
            
            Logger.debug(f'X-Chess UCIEngine polling_bestmove:end {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")} 结束本次轮询')
            return True#继续轮询
    
    #请求最佳招法，该函数仅发送go指令，并不返回结果，需调用方循环主动查询结果
    def request_go_analyzing(self,fenstr,thinktime):
        self.put_command(f'{fenstr}\n')

        Logger.debug(f'X-Chess UCIEngine request_go_analyzing:{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} 开始思考{thinktime/1000}秒')
        self.put_command(f"go movetime {thinktime}\n")
    
    """对uci协议还是理解不到位，发了第一个 go infinite后，当局面变化后，我先发stop，再发当前局面，再发go infinite后，
    此时我获取到的readline还是第一个go的info，过了一段时间后，才获取到第2个go的info，如何破？经分析：引擎一直到发出 bestmove后，才开始发第2次go的info
    """
    
    #根据thinktime参数可实现有限分析和无限AI分析直至杀招，实时画出不同depth以及最终的bestmove的AI招法
    def polling_aimove(self,fenstr,thinktime=None,dt=None):
        Logger.debug(f'X-Chess UCIEngine polling_aimove:begin')

        app = MDApp.get_running_app()
        app.root.ids['id_screenmain'].ids['id_movesnote_input'].text = ""
        app.root.ids['id_screenmain'].ids['id_movesnote_input'].cancel_selection()

        #获取起始局面fen
        rootNode = app.moves_tree.get_node(app.moves_tree.root)

        xqfPos = rootNode.data['situation']
        rootFen = sit2Fen(xqfPos)
        init_camp = app.init_camp
        rootFen = f'position fen {rootFen} {init_camp} - - 0 1' #注意用空格隔开，“b”表示黑方，除此以外都表示红方

        #获取自初始局面以来招法begin
        curNodeId = app.root.ids['id_screenmoves'].ids.id_moveslist.children[0].id
        roadshowid=[]
        for nodeid in app.moves_tree.rsearch(curNodeId):
            #Logger.debug(f"{app.moves_tree[nodeid].tag=}")
            roadshowid.append(nodeid)
        #把根节点弹出来
        roadshowid.pop()
        
        movesStr = ''
        #使用[::-1]来设置切片的步长为-1，从而实现了倒序遍历
        for id in roadshowid[::-1]:
            node = app.moves_tree.get_node(id)
            #Logger.debug(f"{node.tag=},sxyexy:{node.data['sx']}{node.data['sy']}{node.data['ex']}{node.data['ey']}")
            sx = node.data['sx']
            fsx = ''
            match sx:
                case 0:fsx='a'
                case 1:fsx='b'
                case 2:fsx='c'
                case 3:fsx='d'
                case 4:fsx='e'
                case 5:fsx='f'
                case 6:fsx='g'
                case 7:fsx='h'
                case 8:fsx='i'
            
            ex = node.data['ex']
            fex = ''
            match ex:
                case 0:fex='a'
                case 1:fex='b'
                case 2:fex='c'
                case 3:fex='d'
                case 4:fex='e'
                case 5:fex='f'
                case 6:fex='g'
                case 7:fex='h'
                case 8:fex='i'
            
            fmove = f"{fsx}{node.data['sy']}{fex}{node.data['ey']}"
            #Logger.debug(f"{fmove=}")

            movesStr = f"{movesStr}{fmove} "
        #end for
        #Logger.debug(f"{movesStr=}")
        #获取自初始局面以来招法end

        #如果传入moves应该传初始界面不应该是当前界面
        #self.put_command(f'{fenstr} moves {movesStr}\n') 
        self.put_command(f'{rootFen} moves {movesStr}\n') 

        if thinktime == None:
            Logger.debug(f'X-Chess UCIEngine polling_aimove:{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} 开始无限思考')
            self.put_command(f"go infinite\n") 
        else:
            Logger.debug(f'X-Chess UCIEngine polling_aimove:{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} 开始思考{thinktime/1000}秒')
            self.put_command(f"go movetime {thinktime}\n") 
        self.goCount.append('go') 
        self.goStop = False

        async def onebyone(self):
        #def onebyone(self):
            Logger.debug(f'X-Chess UCIEngine polling_aimove:onebyone begin {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")} 开始本次轮询')
            app.root.ids['id_screenmain'].ids['id_btn_analyzing'].disabled = True
            #app.root.ids['id_screenmain'].ids['id_btn_ai'].disabled = True
            app.root.ids['id_screenmain'].ids['id_btn_ai_red'].disabled = True
            app.root.ids['id_screenmain'].ids['id_btn_ai_black'].disabled = True

            dtSeconds = 0
            while True:
                last_result = ""
                bestmove = ""

                 #休息下让界面有所反应
                if dtSeconds > 1:#根据上次readline堵塞时间作为经验进行休息，以便让引擎准备info，下一次readline读到内容，至少需要dtSeconds，那就休息下，让界面不卡顿
                    Logger.debug(f'X-Chess UCIEngine polling_aimove:onebyone {dtSeconds=} 睡前 {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}')
                    dt = await ak.sleep(dtSeconds)
                    Logger.debug(f'X-Chess UCIEngine polling_aimove:onebyone {dt=},{dtSeconds=} 睡后 {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}')

                start_time = datetime.datetime.now()
                Logger.debug(f'X-Chess UCIEngine polling_aimove:readline before {start_time.strftime("%Y-%m-%d %H:%M:%S.%f")}')
                
                line = self.eng_proc.stdout.readline()                

                end_time = datetime.datetime.now()
                dtSeconds = (end_time - start_time).seconds
                Logger.debug(f'X-Chess UCIEngine polling_aimove:readline after {dtSeconds=},{end_time.strftime("%Y-%m-%d %H:%M:%S.%f")}')

                Logger.debug(f'X-Chess UCIEngine polling_aimove:line:<{line=}>')
                Logger.debug(f'X-Chess UCIEngine polling_aimove:稍息{self.asysleeptime=}，减轻卡顿')
                await ak.sleep(self.asysleeptime)

                if self.goStop == True:
                    if line.startswith('bestmove'):#与go成对串行出现
                        Logger.debug(f'X-Chess UCIEngine polling_aimove:已发出stop指令，已获取到bestmove')
                        self.goCount.pop() #与go成对出现
                        break#跳出while循环
                    else:
                        Logger.debug(f'X-Chess UCIEngine polling_aimove:已发出stop指令，忽略该info')
                        continue

                #如果info中没有depth也没有bestmove，忽略继续
                if (line.find('depth') == -1) and (line.find('bestmove') == -1):
                    Logger.debug(f'X-Chess UCIEngine polling_aimove:忽略')
                    continue

                #由于readline会堵塞，在堵塞期间局面可能会发生变化，so
                bSituationChanged = False
                curFen = ""
                nodeid = app.root.ids['id_screenmoves'].ids.id_moveslist.children[0].id
                if nodeid:
                    node = app.moves_tree.get_node(nodeid)
                    xqfPos = node.data['situation']
                    curFen = sit2Fen(xqfPos)
                    nextCamp = app.next_camp
                    curFen = f'position fen {curFen} {nextCamp} - - 0 1' #注意用空格隔开，“b”表示黑方，除此以外都表示红方
                    Logger.debug(f'X-Chess UCIEngine polling_aimove:{curFen=}')

                    if curFen != fenstr:#局面发生了变化，忽略当前info的处理
                        Logger.debug(f'X-Chess UCIEngine polling_aimove:curFen != fenstr,局面发生了变化')
                        bSituationChanged = True            
                #Logger.debug(f'X-Chess UCIEngine polling_aimove:局面是否发生了变化：{bSituationChanged}')

                #是否是最佳招法
                bGetBestMove = False
                if line.startswith('bestmove'):#与go成对串行出现
                    self.goCount.pop() #与go成对出现
                    bGetBestMove = True
                    bestmove = line
                    Logger.debug(f'X-Chess UCIEngine polling_aimove:go{len(self.goCount)} {bestmove=}')
                    break
                else:
                    last_result = line
                
                if bSituationChanged == True: #局面发生变化了
                    if bGetBestMove == False:#循环readline至到获取到bestmove
                        Logger.debug(f'X-Chess UCIEngine polling_aimove:curFen != fenstr,局面发生了变化，发出stop命令')
                        self.put_command("stop")
                        Logger.debug(f'X-Chess UCIEngine polling_aimove:局面发生了变化,循环readline至到获取到bestmove')
                        Logger.debug(f'X-Chess UCIEngine polling_aimove: begin {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}')
                        while True:
                            line = self.eng_proc.stdout.readline()
                            Logger.debug(f'X-Chess UCIEngine polling_aimove:go{len(self.goCount)} {line=}')
                            if line.startswith('bestmove'):
                                Logger.debug(f'X-Chess UCIEngine polling_aimove:局面发生了变化,终于获取到了bestmove')
                                bestmove = line
                                bGetBestMove = True
                                Logger.debug(f'X-Chess UCIEngine polling_aimove:go{len(self.goCount)} {bestmove=}')
                                self.goCount.pop() #与go成对出现

                                app.root.ids['id_screenmain'].ids['id_btn_analyzing'].disabled = False
                                #app.root.ids['id_screenmain'].ids['id_btn_ai'].disabled = False
                                app.root.ids['id_screenmain'].ids['id_btn_ai_red'].disabled = False
                                app.root.ids['id_screenmain'].ids['id_btn_ai_black'].disabled = False

                                app.show_ai_move_infinite = False
                                app.root.ids['id_screenmain'].ids['id_btn_ai'].icon_size = '28sp'

                                Logger.debug(f'X-Chess UCIEngine polling_aimove:onebyone end {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")} 结束本次轮询')
                                return
                    else:#这里执行不到，因为前面已经跳出循环了
                        app.root.ids['id_screenmain'].ids['id_btn_analyzing'].disabled = False
                        #app.root.ids['id_screenmain'].ids['id_btn_ai'].disabled = False
                        app.root.ids['id_screenmain'].ids['id_btn_ai_red'].disabled = False
                        app.root.ids['id_screenmain'].ids['id_btn_ai_black'].disabled = False

                        Logger.debug(f'X-Chess UCIEngine polling_aimove:onebyone end {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")} 结束本次轮询')
                        return
                
                #下面进入局面没有发生变化的处理，显示depth中的招法或者bestmove
                Logger.debug(f'X-Chess UCIEngine polling_aimove:go{len(self.goCount)} begin==>{last_result=}')
                infolist = last_result.split(' ')
                #print(f'{infolist=}')
                score = wdl = depth =  nodes = nps = pv = mate = hashfull = ''
                i = 0
                matecount = None
                for item in infolist:
                    #print(f'{item}')
                    if item == 'score': 
                        score = f'分数{infolist[i+2]}'
                    elif item == 'wdl':
                        wdl = f'胜率{infolist[i+1]} 和率{infolist[i+2]} 负率{infolist[i+3]}'
                    elif item == 'depth':
                        depth = f'深度{infolist[i+1]}'
                    elif item == 'nodes':
                        nodes = f'节点数{infolist[i+1]}'
                    elif item == 'nps':
                        nps = f'引擎速度{infolist[i+1]}'
                    elif item == 'hashfull':
                        hashfull = f'Hash占用率{infolist[i+1]}'
                    elif item == 'mate':
                        matecount = int(infolist[i+1])
                        if matecount == 0:
                            mate = f'已杀'
                        else:
                            mate = f'{matecount}步成杀'
                    elif item == 'pv':
                        pv = f'{infolist[i+1]}'
                    
                    i = i + 1
                #end for item in infolist:
                
                esxy=[]
                #获取招法名称
                if pv != "":
                    pv = pv.replace('\n','')
                    nodeid = app.root.ids['id_screenmoves'].ids.id_moveslist.children[0].id
                    node = app.moves_tree.get_node(nodeid)
                    
                    pv = pv.replace('a','0')
                    pv = pv.replace('b','1')
                    pv = pv.replace('c','2')
                    pv = pv.replace('d','3')
                    pv = pv.replace('e','4')
                    pv = pv.replace('f','5')
                    pv = pv.replace('g','6')
                    pv = pv.replace('h','7')
                    pv = pv.replace('i','8')
                    se = list(pv)
                    esxy=[]
                    for item in se:
                        esxy.append(int(item))
                    
                    if (f"{esxy[0]},{esxy[1]}" in node.data['situation']) and isinstance(node.data['situation'][f'{esxy[0]},{esxy[1]}'],Piece):
                        p = node.data['situation'][f'{esxy[0]},{esxy[1]}']
                        if p is not None:
                            pv =p.getMoveName(esxy[2],esxy[3],node.data['situation'])
                        else:
                            Logger.debug(f'X-Chess UCIEngine polling_aimove:111 出错了 p is None {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")} 结束本次轮询')
                            app.root.ids['id_screenmain'].ids['id_btn_analyzing'].disabled = False
                            #app.root.ids['id_screenmain'].ids['id_btn_ai'].disabled = False
                            app.root.ids['id_screenmain'].ids['id_btn_ai_red'].disabled = False
                            app.root.ids['id_screenmain'].ids['id_btn_ai_black'].disabled = False

                            Logger.debug(f'X-Chess UCIEngine polling_aimove:onebyone end {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")} 结束本次轮询')
                            return
                    else:
                        Logger.debug(f'X-Chess UCIEngine polling_aimove:222 出错了 p is None  {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")} 结束本次轮询')
                        app.root.ids['id_screenmain'].ids['id_btn_analyzing'].disabled = False
                        #app.root.ids['id_screenmain'].ids['id_btn_ai'].disabled = False
                        app.root.ids['id_screenmain'].ids['id_btn_ai_red'].disabled = False
                        app.root.ids['id_screenmain'].ids['id_btn_ai_black'].disabled = False

                        Logger.debug(f'X-Chess UCIEngine polling_aimove:onebyone end {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")} 结束本次轮询')
                        return
                    
                    otherInf = None
                    if matecount != None and matecount == 0:
                        otherInf = f'胜负已定'
                        app.gameover = True
                    elif matecount != None and matecount >= 1:
                        otherInf = f'有杀 {wdl} {mate} {depth}'
                    else:
                        otherInf = f'{depth} {pv} {score} {wdl} {mate} {hashfull} {nps}'
                
                    if otherInf is not None:
                        txt = app.root.ids['id_screenmain'].ids['id_movesnote_input'].text
                        app.root.ids['id_screenmain'].ids['id_movesnote_input'].text = f'{otherInf}\n{txt}'
                        app.root.ids['id_screenmain'].ids['id_movesnote_input'].cancel_selection()
                    
                    if len(esxy) >= 4:
                        #显示招法
                        Logger.debug(f'X-Chess UCIEngine polling_aimove:go{len(self.goCount)} 显示招法：{pv}')
                        app.root.ids['id_screenmain'].ids.id_chessboard.remove_AllAIarrows()

                        #app.root.ids['id_screenmain'].ids.id_chessboard.add_aiarrow(esxy[0],esxy[1],esxy[2],esxy[3])
                        s_board_x = s_board_y = e_board_x = e_board_y = None
                        if app.root.ids['id_screenmain'].ids.id_chessboard.red_bottom == True:#红下黑上
                            s_board_x = esxy[0]
                            s_board_y = esxy[1]
                            e_board_x = esxy[2]
                            e_board_y = esxy[3]
                        else:#红上黑下
                            s_board_x = abs(esxy[0]-8)
                            s_board_y = abs(esxy[1]-9)
                            e_board_x = abs(esxy[2]-8)
                            e_board_y = abs(esxy[3]-9)
                        app.root.ids['id_screenmain'].ids.id_chessboard.add_aiarrow(s_board_x,s_board_y,e_board_x,e_board_y)
                else:
                    otherInf = None
                    if matecount != None and matecount == 0:
                        otherInf = f'胜负已定'
                        app.gameover = True
                        toast("胜负已定")
                    elif matecount != None and matecount >= 1:
                        otherInf = f'有杀 {wdl} {mate} {depth}'
                    app.root.ids['id_screenmain'].ids['id_movesnote_input'].text = f'{otherInf}' 
                    app.root.ids['id_screenmain'].ids['id_movesnote_input'].cancel_selection()
               
                Logger.debug(f'X-Chess UCIEngine polling_aimove:go{len(self.goCount)} end==>{last_result=}')
            #end while
            txt = app.root.ids['id_screenmain'].ids['id_movesnote_input'].text
            app.root.ids['id_screenmain'].ids['id_movesnote_input'].text = f'AI思考结束：{txt}'
            app.root.ids['id_screenmain'].ids['id_movesnote_input'].cancel_selection()
            
            app.root.ids['id_screenmain'].ids['id_btn_analyzing'].disabled = False
            #app.root.ids['id_screenmain'].ids['id_btn_ai'].disabled = False
            app.root.ids['id_screenmain'].ids['id_btn_ai_red'].disabled = False
            app.root.ids['id_screenmain'].ids['id_btn_ai_black'].disabled = False

            Logger.debug(f'X-Chess UCIEngine polling_aimove:onebyone end {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")} 结束本次轮询')
        #end onebyone
        
        ak.start(onebyone(self))
        #t = threading.Thread(target=onebyone, name="polling_aimove_onebyone",args=(self,))
        #t.start()
        #Cannot change graphics instruction outside the main Kivy thread
        
        Logger.debug(f'X-Chess UCIEngine polling_aimove:end')
        return
    
    #轮询AI分析，实时画出不同depth以及最终的bestmove的AI招法
    #当本次go没有执行完时，局面发生变化时，会主动调用自身再次发起分析
    def polling_aimove2(self,fenstr,thinktime,dt=None):
        Logger.debug(f'X-Chess UCIEngine polling_aimove:begin')

        app = MDApp.get_running_app()
        app.root.ids['id_screenmain'].ids['id_movesnote_input'].text = ""
        app.root.ids['id_screenmain'].ids['id_movesnote_input'].cancel_selection()

        Logger.debug(f'X-Chess UCIEngine polling_aimove:{fenstr=}')

        #获取起始局面fen
        rootNode = app.moves_tree.get_node(app.moves_tree.root)

        xqfPos = rootNode.data['situation']
        rootFen = sit2Fen(xqfPos)
        init_camp = app.init_camp
        rootFen = f'position fen {rootFen} {init_camp} - - 0 1' #注意用空格隔开，“b”表示黑方，除此以外都表示红方

        #获取自初始局面以来招法begin
        curNodeId = app.root.ids['id_screenmoves'].ids.id_moveslist.children[0].id
        roadshowid=[]
        for nodeid in app.moves_tree.rsearch(curNodeId):
            #Logger.debug(f"{app.moves_tree[nodeid].tag=}")
            roadshowid.append(nodeid)
        #把根节点弹出来
        roadshowid.pop()
        
        movesStr = ''
        #使用[::-1]来设置切片的步长为-1，从而实现了倒序遍历
        for id in roadshowid[::-1]:
            node = app.moves_tree.get_node(id)
            #Logger.debug(f"{node.tag=},sxyexy:{node.data['sx']}{node.data['sy']}{node.data['ex']}{node.data['ey']}")
            sx = node.data['sx']
            fsx = ''
            match sx:
                case 0:fsx='a'
                case 1:fsx='b'
                case 2:fsx='c'
                case 3:fsx='d'
                case 4:fsx='e'
                case 5:fsx='f'
                case 6:fsx='g'
                case 7:fsx='h'
                case 8:fsx='i'
            
            ex = node.data['ex']
            fex = ''
            match ex:
                case 0:fex='a'
                case 1:fex='b'
                case 2:fex='c'
                case 3:fex='d'
                case 4:fex='e'
                case 5:fex='f'
                case 6:fex='g'
                case 7:fex='h'
                case 8:fex='i'
            
            fmove = f"{fsx}{node.data['sy']}{fex}{node.data['ey']}"
            #Logger.debug(f"{fmove=}")

            movesStr = f"{movesStr}{fmove} "
        #end for
        #Logger.debug(f"{movesStr=}")
        #获取自初始局面以来招法end

        #如果传入moves应该传初始界面不应该是当前界面
        #self.put_command(f'{fenstr} moves {movesStr}\n') 
        self.put_command(f'{rootFen} moves {movesStr}\n')     

        Logger.debug(f'X-Chess UCIEngine polling_aimove:{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} 开始思考{thinktime/1000}秒')
        self.put_command(f"go movetime {thinktime}\n") 
        self.goCount.append('go') 

        async def onebyone(self):
            Logger.debug(f'X-Chess UCIEngine polling_aimove:onebyone begin {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")} 开始本次轮询')
            while True:
                last_result = ""
                bestmove = ""

                line = self.eng_proc.stdout.readline()
                #Logger.debug(f'X-Chess UCIEngine polling_aimove:line:<{line=}>')

                #如果info中没有depth也没有bestmove，忽略继续
                if (line.find('depth') == -1) and (line.find('bestmove') == -1):
                    #Logger.debug(f'X-Chess UCIEngine polling_aimove:忽略')
                    continue

                #由于readline会堵塞，在堵塞期间局面可能会发生变化，so
                bSituationChanged = False
                curFen = ""
                nodeid = app.root.ids['id_screenmoves'].ids.id_moveslist.children[0].id
                if nodeid:
                    node = app.moves_tree.get_node(nodeid)
                    xqfPos = node.data['situation']
                    curFen = sit2Fen(xqfPos)
                    nextCamp = app.next_camp
                    curFen = f'position fen {curFen} {nextCamp} - - 0 1' #注意用空格隔开，“b”表示黑方，除此以外都表示红方
                    Logger.debug(f'X-Chess UCIEngine polling_aimove:{curFen=}')

                    if curFen != fenstr:#局面发生了变化，忽略当前info的处理
                        Logger.debug(f'X-Chess UCIEngine polling_aimove:curFen != fenstr,局面发生了变化')
                        bSituationChanged = True            
                Logger.debug(f'X-Chess UCIEngine polling_aimove:局面是否发生了变化：{bSituationChanged}')

                #是否是最佳招法
                bGetBestMove = False
                if line.startswith('bestmove'):#与go成对串行出现
                    self.goCount.pop() #与go成对出现
                    bGetBestMove = True
                    bestmove = line
                    Logger.debug(f'X-Chess UCIEngine polling_aimove:go{len(self.goCount)} {bestmove=}')
                    break
                else:
                    last_result = line
                
                if bSituationChanged == True: #局面发生变化了
                    if bGetBestMove == False:#循环readline至到获取到bestmove
                        Logger.debug(f'X-Chess UCIEngine polling_aimove:局面发生了变化,循环readline至到获取到bestmove')
                        while True:
                            line = self.eng_proc.stdout.readline()
                            #Logger.debug(f'X-Chess UCIEngine polling_aimove:go{len(self.goCount)} {line=}')
                            if line.startswith('bestmove'):
                                Logger.debug(f'X-Chess UCIEngine polling_aimove:局面发生了变化,终于获取到了bestmove')
                                bestmove = line
                                bGetBestMove = True
                                #Logger.debug(f'X-Chess UCIEngine polling_aimove:go{len(self.goCount)} {bestmove=}')
                                self.goCount.pop() #与go成对出现

                                #定义1个定时器，as soon as possible (usually next frame.)
                                #继续分析当前局面
                                curFen = ""
                                nodeid = app.root.ids['id_screenmoves'].ids.id_moveslist.children[0].id
                                if nodeid:
                                    node = app.moves_tree.get_node(nodeid)
                                    xqfPos = node.data['situation']
                                    curFen = sit2Fen(xqfPos)
                                    nextCamp = app.next_camp
                                    curFen = f'position fen {curFen} {nextCamp} - - 0 1' #注意用空格隔开，“b”表示黑方，除此以外都表示红方
                                    Logger.debug(f'X-Chess UCIEngine polling_aimove:{curFen=}')

                                    Logger.debug(f'X-Chess UCIEngine polling_aimove:局面发生了变化,启动一个定时继续分析最新局面')
                                    Clock.schedule_once(partial(self.polling_aimove2,curFen,thinktime))

                                return
                    else:#这里执行不到，因为前面已经跳出循环了
                        return
                
                #下面进入局面没有发生变化的处理，显示depth中的招法或者bestmove
                #Logger.debug(f'X-Chess UCIEngine polling_aimove:go{len(self.goCount)} begin==>{last_result=}')
                infolist = last_result.split(' ')
                #print(f'{infolist=}')
                score = wdl = depth =  nodes = nps = pv = mate = hashfull = ''
                i = 0
                matecount = None
                for item in infolist:
                    #print(f'{item}')
                    if item == 'score': 
                        score = f'分数{infolist[i+2]}'
                    elif item == 'wdl':
                        wdl = f'胜率{infolist[i+1]} 和率{infolist[i+2]} 负率{infolist[i+3]}'
                    elif item == 'depth':
                        depth = f'深度{infolist[i+1]}'
                    elif item == 'nodes':
                        nodes = f'节点数{infolist[i+1]}'
                    elif item == 'nps':
                        nps = f'引擎速度{infolist[i+1]}'
                    elif item == 'hashfull':
                        hashfull = f'Hash占用率{infolist[i+1]}'
                    elif item == 'mate':
                        matecount = int(infolist[i+1])
                        if matecount == 0:
                            mate = f'已杀'
                        else:
                            mate = f'{matecount}步成杀'
                    elif item == 'pv':
                        pv = f'{infolist[i+1]}'
                    
                    i = i + 1
                #end for item in infolist:
                
                esxy=[]
                #获取招法名称
                if pv != "":
                    pv = pv.replace('\n','')
                    nodeid = app.root.ids['id_screenmoves'].ids.id_moveslist.children[0].id
                    node = app.moves_tree.get_node(nodeid)
                    
                    pv = pv.replace('a','0')
                    pv = pv.replace('b','1')
                    pv = pv.replace('c','2')
                    pv = pv.replace('d','3')
                    pv = pv.replace('e','4')
                    pv = pv.replace('f','5')
                    pv = pv.replace('g','6')
                    pv = pv.replace('h','7')
                    pv = pv.replace('i','8')
                    se = list(pv)
                    esxy=[]
                    for item in se:
                        esxy.append(int(item))
                    
                    if (f"{esxy[0]},{esxy[1]}" in node.data['situation']) and isinstance(node.data['situation'][f'{esxy[0]},{esxy[1]}'],Piece):
                        p = node.data['situation'][f'{esxy[0]},{esxy[1]}']
                        if p is not None:
                            pv =p.getMoveName(esxy[2],esxy[3],node.data['situation'])
                        else:
                            Logger.debug(f'X-Chess UCIEngine polling_aimove:出错了 p is None {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")} 结束本次轮询')
                            return
                    else:
                        Logger.debug(f'X-Chess UCIEngine polling_aimove:出错了 p is None  {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")} 结束本次轮询')
                        return
                    
                    otherInf = None
                    if matecount != None and matecount == 0:
                        otherInf = f'胜负已定'
                        app.gameover = True
                    elif matecount != None and matecount >= 1:
                        otherInf = f'有杀 {wdl} {mate} {depth}'
                    else:
                        otherInf = f'{depth} {pv} {score} {wdl} {mate} {hashfull} {nps}'
                
                    if otherInf is not None:
                        #txt = app.root.ids['id_screenmain'].ids['id_movesnote_input'].text
                        #app.root.ids['id_screenmain'].ids['id_movesnote_input'].text = f'{otherInf}\n{txt}'
                        app.root.ids['id_screenmain'].ids['id_movesnote_input'].text = f'{otherInf}'
                        app.root.ids['id_screenmain'].ids['id_movesnote_input'].cancel_selection()
                    
                    if len(esxy) >= 4:
                        #显示招法
                        Logger.debug(f'X-Chess UCIEngine polling_aimove:go{len(self.goCount)} 显示招法：{pv}')
                        app.root.ids['id_screenmain'].ids.id_chessboard.remove_AllAIarrows()
                        #app.root.ids['id_screenmain'].ids.id_chessboard.add_aiarrow(esxy[0],esxy[1],esxy[2],esxy[3])
                        s_board_x = s_board_y = e_board_x = e_board_y = None
                        if app.root.ids['id_screenmain'].ids.id_chessboard.red_bottom == True:#红下黑上
                            s_board_x = esxy[0]
                            s_board_y = esxy[1]
                            e_board_x = esxy[2]
                            e_board_y = esxy[3]
                        else:#红上黑下
                            s_board_x = abs(esxy[0]-8)
                            s_board_y = abs(esxy[1]-9)
                            e_board_x = abs(esxy[2]-8)
                            e_board_y = abs(esxy[3]-9)
                        app.root.ids['id_screenmain'].ids.id_chessboard.add_aiarrow(s_board_x,s_board_y,e_board_x,e_board_y)

                        #休息下让界面有所反应
                        await ak.sleep(self.asysleeptime)
                else:
                    otherInf = None
                    if matecount != None and matecount == 0:
                        otherInf = f'胜负已定'
                        app.gameover = True
                        toast("胜负已定")
                    elif matecount != None and matecount >= 1:
                        otherInf = f'有杀 {wdl} {mate} {depth}'
                    app.root.ids['id_screenmain'].ids['id_movesnote_input'].text = f'{otherInf}' 
                    app.root.ids['id_screenmain'].ids['id_movesnote_input'].cancel_selection()
                
                Logger.debug(f'X-Chess UCIEngine polling_aimove:go{len(self.goCount)} end==>{last_result=}')
            #end while
            txt = app.root.ids['id_screenmain'].ids['id_movesnote_input'].text
            app.root.ids['id_screenmain'].ids['id_movesnote_input'].text = f'AI思考结束：{txt}'
            app.root.ids['id_screenmain'].ids['id_movesnote_input'].cancel_selection()

            Logger.debug(f'X-Chess UCIEngine polling_aimove:onebyone end {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")} 结束本次轮询')
        #end onebyone
        
        ak.start(onebyone(self))        
        
        Logger.debug(f'X-Chess UCIEngine polling_aimove:end')
        return
    
    #获取bestmove的AI招法，并走棋
    def go_bestmove(self,fenstr,thinktime,dt=None):
        Logger.debug(f'X-Chess UCIEngine go_bestmove:begin')

        app = MDApp.get_running_app()
        #app.root.ids['id_screenmain'].ids['id_movesnote_input'].text = ""
        #app.root.ids['id_screenmain'].ids['id_movesnote_input'].cancel_selection()

        #获取起始局面fen
        rootNode = app.moves_tree.get_node(app.moves_tree.root)

        xqfPos = rootNode.data['situation']
        rootFen = sit2Fen(xqfPos)
        init_camp = app.init_camp
        rootFen = f'position fen {rootFen} {init_camp} - - 0 1' #注意用空格隔开，“b”表示黑方，除此以外都表示红方

        #获取自初始局面以来招法begin
        curNodeId = app.root.ids['id_screenmoves'].ids.id_moveslist.children[0].id
        roadshowid=[]
        for nodeid in app.moves_tree.rsearch(curNodeId):
            #Logger.debug(f"{app.moves_tree[nodeid].tag=}")
            roadshowid.append(nodeid)
        #把根节点弹出来
        roadshowid.pop()
        
        movesStr = ''
        #使用[::-1]来设置切片的步长为-1，从而实现了倒序遍历
        for id in roadshowid[::-1]:
            node = app.moves_tree.get_node(id)
            #Logger.debug(f"{node.tag=},sxyexy:{node.data['sx']}{node.data['sy']}{node.data['ex']}{node.data['ey']}")
            sx = node.data['sx']
            fsx = ''
            match sx:
                case 0:fsx='a'
                case 1:fsx='b'
                case 2:fsx='c'
                case 3:fsx='d'
                case 4:fsx='e'
                case 5:fsx='f'
                case 6:fsx='g'
                case 7:fsx='h'
                case 8:fsx='i'
            
            ex = node.data['ex']
            fex = ''
            match ex:
                case 0:fex='a'
                case 1:fex='b'
                case 2:fex='c'
                case 3:fex='d'
                case 4:fex='e'
                case 5:fex='f'
                case 6:fex='g'
                case 7:fex='h'
                case 8:fex='i'
            
            fmove = f"{fsx}{node.data['sy']}{fex}{node.data['ey']}"
            #Logger.debug(f"{fmove=}")

            movesStr = f"{movesStr}{fmove} "
        #end for
        #Logger.debug(f"{movesStr=}")
        #获取自初始局面以来招法end

        #如果传入moves应该传初始界面不应该是当前界面
        #self.put_command(f'{fenstr} moves {movesStr}\n') 
        self.put_command(f'{rootFen} moves {movesStr}\n') 
            

        Logger.debug(f'X-Chess UCIEngine go_bestmove:{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} 开始思考{thinktime/1000}秒')
        self.put_command(f"go movetime {thinktime}\n") 
        self.goCount.append('go') 

        async def onebyone(self):
            #休息下让界面有所反应
            #await ak.sleep(self.asysleeptime)
            Logger.debug(f'X-Chess UCIEngine go_bestmove:onebyone begin {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")} 开始本次轮询')
            
            bestmove = ""
            last_result = ""
            while True:
                line = self.eng_proc.stdout.readline()
                #Logger.debug(f'X-Chess UCIEngine go_bestmove:line:<{line=}>')

                #如果info中没有depth也没有bestmove，忽略继续
                if (line.find('depth') == -1) and (line.find('bestmove') == -1):
                    Logger.debug(f'X-Chess UCIEngine go_bestmove:忽略')
                    continue

                #由于readline会堵塞，在堵塞期间局面可能会发生变化，so
                bSituationChanged = False
                curFen = ""
                nodeid = app.root.ids['id_screenmoves'].ids.id_moveslist.children[0].id
                if nodeid:
                    node = app.moves_tree.get_node(nodeid)
                    xqfPos = node.data['situation']
                    curFen = sit2Fen(xqfPos)
                    nextCamp = app.next_camp
                    curFen = f'position fen {curFen} {nextCamp} - - 0 1' #注意用空格隔开，“b”表示黑方，除此以外都表示红方
                    #Logger.debug(f'X-Chess UCIEngine go_bestmove:{curFen=}')

                    if curFen != fenstr:#局面发生了变化，忽略当前info的处理
                        Logger.debug(f'X-Chess UCIEngine go_bestmove:curFen != fenstr,局面发生了变化')
                        bSituationChanged = True            
                #Logger.debug(f'X-Chess UCIEngine go_bestmove:局面是否发生了变化：{bSituationChanged}')

                #是否是最佳招法
                bGetBestMove = False
                if line.startswith('bestmove'):#与go成对串行出现
                    self.goCount.pop() #与go成对出现
                    bGetBestMove = True
                    bestmove = line
                    Logger.debug(f'X-Chess UCIEngine go_bestmove:go{len(self.goCount)} {bestmove=}')
                    break
                else:
                    last_result = line
                
                #休息下让界面有所反应
                #如果发现有杀，就别休息了，尽快出招
                if line.find(" mate ") == -1:
                    Logger.debug(f'X-Chess UCIEngine go_bestmove:001 休息下让界面有所反应')
                    await ak.sleep(self.asysleeptime)
                
                if bSituationChanged == True: #局面发生变化了
                    if bGetBestMove == False:#循环readline至到获取到bestmove
                        Logger.debug(f'X-Chess UCIEngine go_bestmove:局面发生了变化,循环readline至到获取到bestmove')
                        while True:
                            line = self.eng_proc.stdout.readline()
                            Logger.debug(f'X-Chess UCIEngine go_bestmove:go{len(self.goCount)} {line=}')
                            if line.startswith('bestmove'):
                                Logger.debug(f'X-Chess UCIEngine go_bestmove:局面发生了变化,终于获取到了bestmove')
                                bestmove = line
                                bGetBestMove = True
                                Logger.debug(f'X-Chess UCIEngine go_bestmove:go{len(self.goCount)} {bestmove=}')
                                self.goCount.pop() #与go成对出现

                                Logger.debug(f'X-Chess UCIEngine go_bestmove:onebyone end {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")} 结束本次轮询')
                                #休息下让界面有所反应
                                Logger.debug(f'X-Chess UCIEngine go_bestmove:002 休息下让界面有所反应')
                                await ak.sleep(self.asysleeptime)
                                return
                    else:#这里执行不到，因为前面已经跳出循环了
                        Logger.debug(f'X-Chess UCIEngine go_bestmove:onebyone end {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")} 结束本次轮询')
                        return
                #Logger.debug(f'X-Chess UCIEngine go_bestmove:go{len(self.goCount)} end==>{last_result=}')
            #end while
            
            #下面进入局面没有发生变化的处理，显示depth中的招法或者bestmove
            Logger.debug(f'X-Chess UCIEngine go_bestmove:go{len(self.goCount)} begin==>{last_result=}')
            infolist = last_result.split(' ')
            #print(f'{infolist=}')
            score = wdl = depth =  nodes = nps = pv = mate = hashfull = ''
            i = 0
            matecount = None
            for item in infolist:
                #print(f'{item}')
                if item == 'score': 
                    score = f'分数{infolist[i+2]}'
                elif item == 'wdl':
                    wdl = f'胜率{infolist[i+1]} 和率{infolist[i+2]} 负率{infolist[i+3]}'
                elif item == 'depth':
                    depth = f'深度{infolist[i+1]}'
                elif item == 'nodes':
                    nodes = f'节点数{infolist[i+1]}'
                elif item == 'nps':
                    nps = f'引擎速度{infolist[i+1]}'
                elif item == 'hashfull':
                    hashfull = f'Hash占用率{infolist[i+1]}'
                elif item == 'mate':
                    matecount = int(infolist[i+1])
                    if matecount == 0:
                        mate = f'已杀'
                    else:
                        mate = f'{matecount}步成杀'
                elif item == 'pv':
                    pv = f'{infolist[i+1]}'                    
                i = i + 1
            #end for item in infolist:
                
            esxy=[]
            #获取招法名称
            if pv != "":
                pv = pv.replace('\n','')
                pv = pv.replace('a','0')
                pv = pv.replace('b','1')
                pv = pv.replace('c','2')
                pv = pv.replace('d','3')
                pv = pv.replace('e','4')
                pv = pv.replace('f','5')
                pv = pv.replace('g','6')
                pv = pv.replace('h','7')
                pv = pv.replace('i','8')
                se = list(pv)
                esxy=[]
                for item in se:
                    esxy.append(int(item))
                    
                otherInf = None
                if matecount != None and matecount == 0:
                    otherInf = f'胜负已定'
                    app.gameover = True
                    toast("胜负已定")
                elif matecount != None and matecount >= 1:
                    otherInf = f'有杀 {wdl} {mate} {depth}'
                else:
                    otherInf = f'{depth} {pv} {score} {wdl} {mate} {hashfull} {nps}'
                app.root.ids['id_screenmain'].ids['id_movesnote_input'].text = f'{otherInf}'
                app.root.ids['id_screenmain'].ids['id_movesnote_input'].cancel_selection() 

                if app.gameover != True:#走子
                    curNodeId = app.root.ids['id_screenmoves'].ids.id_moveslist.children[0].id
                    node = app.moves_tree.get_node(curNodeId)
                    if node != None:
                        p = node.data['situation'][f'{esxy[0]},{esxy[1]}'].pieceWidget
                        Logger.debug(f'X-Chess x-chessapp ai_go: {p.camp=},{p.identifier=},{p.bx=}.{p.by=}')                            
                        if p and isinstance(p,PieceWidget):
                            app.selected_piece = p                            
                            #app.root.ids['id_screenmain'].ids.id_chessboard.add_aiarrow(esxy[0],esxy[1],esxy[2],esxy[3])
                            s_board_x = s_board_y = e_board_x = e_board_y = None
                            if app.root.ids['id_screenmain'].ids.id_chessboard.red_bottom == True:#红下黑上
                                s_board_x = esxy[0]
                                s_board_y = esxy[1]
                                e_board_x = esxy[2]
                                e_board_y = esxy[3]
                            else:#红上黑下
                                s_board_x = abs(esxy[0]-8)
                                s_board_y = abs(esxy[1]-9)
                                e_board_x = abs(esxy[2]-8)
                                e_board_y = abs(esxy[3]-9)
                            app.root.ids['id_screenmain'].ids.id_chessboard.add_aiarrow(s_board_x,s_board_y,e_board_x,e_board_y)

                            Logger.debug(f'X-Chess UCIEngine go_bestmove:002 休息下让界面有所反应')
                            await ak.sleep(self.asysleeptime)
                            
                            #p.letsgo(esxy[2],esxy[3])
                            p.letsgo(e_board_x,e_board_y)
            else:
                otherInf = None
                if matecount != None and matecount == 0:
                    otherInf = f'胜负已定'
                    app.gameover = True
                    toast("胜负已定")
                elif matecount != None and matecount >= 1:
                    otherInf = f'有杀 {wdl} {mate} {depth}'
                app.root.ids['id_screenmain'].ids['id_movesnote_input'].text = f'{otherInf}'
                app.root.ids['id_screenmain'].ids['id_movesnote_input'].cancel_selection() 

            Logger.debug(f'X-Chess UCIEngine go_bestmove:onebyone end {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")} 结束本次轮询')
        #end onebyone
        
        ak.start(onebyone(self))        
        
        Logger.debug(f'X-Chess UCIEngine go_bestmove:end')
        return
                


        