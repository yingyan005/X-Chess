import os

from kivy.logger import Logger
from kivy.utils import platform
from kivy.uix.scatter import Scatter
from kivy.graphics.svg import Svg

from kivymd.app import MDApp
from kivymd.toast import toast

from onelinelistwithid import OneLineListWithId

from piece import Piece
from situation import check_situation

#棋子Widget
class PieceWidget(Scatter):
    #节省内存&更快的属性访问速度&不允许类实例调用方向实例随意添加属性
    #但要注意：对类属性重新赋值，会破坏寻址过程，影响实例属性取值
    __slots__ = ('svg_filename','camp','identifier','bx','by')

    #svg_filename = None
    ##阵营，红：r，黑：b
    #camp = None
    ##棋子标识符，车：ju，马：ma，象：xiang，士：shi，帅(将)：shuai，炮：pao，兵（卒）：bing
    ##决定走子规则
    #identifier = None
    ##camp + identifier 决定走子规则
    ##坐标原点左下角，棋盘横坐标,整数 0~8,变量不能是内部变量x，否则有冲突
    #bx = None
    ##纵坐标,整数 0~9
    #by = None
    
    #def __init__(self,svg_fn,camp,identifier,x,y,**kwargs):
    def __init__(self,svg_fn=None,camp=None,identifier=None,bx=None,by=None,**kwargs):
        #if platform == "android":
        #    self.scale = 0.8
        #else:
        #    self.scale = 0.3
        
        self.do_rotation = False
        self.do_scale = False
        self.do_translation = False
        self.auto_bring_to_front = True

        super(PieceWidget, self).__init__(**kwargs)
        
        self.svg_filename = svg_fn
        self.camp = camp
        self.identifier = identifier
        self.bx = bx
        self.by = by

        """
        canvas.before和canvas.after属性用法与canvas基本一致，主要差别就是在执行顺序先后上，其优先级如下：
        canvas.before > canvas > widget(canvas.before、canvas、canvas.after) > canvas.after
        """
        #with self.canvas.before:
        #    Color(0,1,1)#青色
        #    self.Backgroud = Rectangle(pos=self.pos,size=self.size)
        with self.canvas:
            filename = os.path.join( os.getcwd(),self.svg_filename)
            #print(f"{filename=}")
            #
            #anchor_x=0, anchor_y=0,The symbolic values ‘left’, ‘center’ and ‘right’ are also accepted.
            #0 1 2 外观上没发现有啥不同
            svg = Svg(filename)
            #app = MDApp.get_running_app()
            #print(f"{app.root.width=},{app.root.height=}")
            #print(f"{svg.width=},{svg.height=}")
            #self.size = svg.width * self.scale, svg.height * self.scale
            self.size = svg.width, svg.height

            app = MDApp.get_running_app()
            #使棋子宽度的1/2 等于 网格边长的 2/5
            self.scale = (app.root.ids['id_screenmain'].ids.id_chessboard.grid_side_len * 2 / 5) * ( 2 / svg.width)

            #Color(.5,1,1)#红色
            #self.Backgroud = Rectangle(center=self.center,size=self.size)
        #with self.canvas.after:
        #    Color(.1,.5,1)#蓝色
        #    self.Backgroud = Rectangle(center=self.center,size=self.size)
        
    def on_touch_up(self, touch):
        #print("PieceWidget.on_touch_up begin")
        app = MDApp.get_running_app()
        
        #selected_piece = None
        #print(f"{app.selected_piece=}")
        if self.collide_point(*touch.pos):
            self.pressed = touch.pos
            # we consumed the touch. return False here to propagate
            # the touch further to the children.
            #print("....PieceWidget.on_touch_up on me...静待花开")
            if app.selected_piece == None or app.selected_piece != self:#避免重复选择
            #if True:
                if self.camp ==  app.next_camp :#该己方走子,显示选择标记
                    app.selected_piece = self
                    app.selectedmask1.center=[self.center[0] - 0,self.center[1] + 0]
                    app.selectedmask2.center=[-1000,-1000]
            #print("PieceWidget.on_touch_up end 1")
            return True
        
        #print("PieceWidget.on_touch_up end 2")
        return super(PieceWidget, self).on_touch_up(touch)

    def moveToHide(self):
        self.center = [self.center_x - 1000,self.center_y - 1000]
        print(f"{self.identifier=} 被吃掉")
        #此时判断胜负，太low了，但也有必要留着
        if self.identifier == 'shuai':
            app = MDApp.get_running_app()
            app.gameover = True #局终
            if self.camp == 'r':
                toast("黑胜！！！")
            else:
                toast("红胜！！！")
    
    def moveToVisible(self):
        self.center = [self.center_x + 1000,self.center_y + 1000]

    def judgingWinner(self):
        print("静待花开：***判断是否胜负已定***")
    
    def movexy(self,sx,sy,ex,ey,direction,situation):
        #print("PieceWidget.movexy begin")
        #print(f"{sx=},{sy=},{ex=},{ey=}")
        app = MDApp.get_running_app()

        #basicUnitX = app.root.ids['id_screenmain'].ids.id_chessboard.width / 10
        #basicUnitY = app.root.ids['id_screenmain'].ids.id_chessboard.height / 11

        #原位置标记
        app.selectedmask1.center=[self.center[0] - 0,self.center[1] + 0]

        #print(f"before:{self.center=}")
        if sx == ex:#横坐标没变
            #self.center = [self.center[0],self.center[1] + basicUnitY * (ey - sy)]
            self.center = [self.center[0],self.center[1] + app.root.ids['id_screenmain'].ids.id_chessboard.grid_side_len * (ey - sy)]
        elif sy == ey:#纵坐标没变
            self.center = [self.center[0] + app.root.ids['id_screenmain'].ids.id_chessboard.grid_side_len * (ex - sx),self.center[1]]
        else:
            self.center = [self.center[0] + app.root.ids['id_screenmain'].ids.id_chessboard.grid_side_len * (ex - sx),self.center[1] + app.root.ids['id_screenmain'].ids.id_chessboard.grid_side_len * (ey - sy) ]

        #更新自己的棋盘坐标
        self.bx = ex
        self.by = ey
        
        #选择框跟随
        app.selectedmask2.center=[self.center[0] - 0,self.center[1] + 0]

        if direction == 'F':
            #将(ex,ey)处的棋子移走
            if f"{ex},{ey}" in situation:
                p = situation[f'{ex},{ey}']
                if p and p.pieceWidget and isinstance(p.pieceWidget,PieceWidget):
                    p.pieceWidget.moveToHide()
                    #是否需要更新其.bx by ???

            #该哪方走棋
            if self.camp == 'r':
                app.next_camp = 'b'
            else:
                app.next_camp = 'r'
            
            #判断是否胜负已定
            self.judgingWinner()

        elif direction == 'B':
            #将原(sx,sy)处的棋子移回
            if f"{sx},{sy}" in situation:
                p = situation[f'{sx},{sy}']
                if p and p.pieceWidget and isinstance(p.pieceWidget,PieceWidget):
                    p.pieceWidget.moveToVisible()
                    #是否需要更新其.bx by ???
                    
            
            #该哪方走棋
            app.next_camp = self.camp
        else:
            print("啥也不是")
        
        #print("PieceWidget.movexy end")

    def letsgo(self,to_x,to_y):
        print("PieceWidget.letsgo begin")
        print(f"{self.bx=},{self.by=},{to_x=},{to_y=}")
        
        app = MDApp.get_running_app()

        if app.selected_piece == None:
            print("没有选择棋子，或者该对方走子")
            return
        
        if app.selected_piece != self:
            print("所选棋子不是我，哪里的")
            return

        if self.bx == to_x and self.by == to_y:
            print("原位不动")
            return
        
        curNodeId = app.root.ids['id_screenmoves'].ids.id_moveslist.children[0].id
        curNode = app.moves_tree.get_node(curNodeId)
        curSit = curNode.data['situation']

        #print_situation("******走子前局面******",curSit)

        if self.checkmoves(to_x,to_y,curSit) == False:
            return
        
        
        """
        node struct:
            tag=movesname
            data={'pieceWidget':p.pieceWidget,
                  'sx':sx,
                  'sy':sy,
                  'ex':ex,
                  'ey':ey,
                  'flag':flag,
                  'situation':realtime_situation,
                  'note':note
                  }
        """
        nextNode = None
        #判断当前走法是否是招法树中下一步的招法
        for cNode in app.moves_tree.children(curNodeId):
            #起点和终点相同，就认为当前走法是招法树中下一步的招法
            if self.bx == cNode.data['sx'] and self.by == cNode.data['sy'] and to_x == cNode.data['ex'] and to_y == cNode.data['ey']:
                print("当前走法是招法树中下一步的招法")
                nextNode = cNode                
                break
        
        if nextNode == None:#需要新创建一个节点，并且加到招法树中
            n0 = curNode

            flag = '00'
            #if len(app.moves_tree.children(curNodeId)) >= 1:
            #    flag = '00'
            #print(f'{flag=}')

            #print_situation("******走子前局面******",n0.data['situation'])

            p = n0.data['situation'][f'{self.bx},{self.by}']
            #p.pieceWidget == self

            #获取招法名称
            movesname =p.getMoveName(to_x,to_y,n0.data['situation'])

            #保存当前招法走后的局面
            realtime_situation = {}
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
            realtime_situation[f'{self.bx},{self.by}'] = None
            #终点指向新的Piece实例，其x,y为ex ey
            realtime_situation[f'{to_x},{to_y}'] = Piece(self.camp,self.identifier,to_x,to_y,self)

            check_situation(realtime_situation)

            #print_situation("******走子后局面******",realtime_situation)
            sp = self.bx * 10 + self.by + 24
            sp = f'{sp:x}'#16进制
            sp = f'{sp:0>2}'#少于2位前补0

            ep = to_x * 10 + to_y + 32
            ep = f'{ep:x}'#16进制
            ep = f'{ep:0>2}'#少于2位前补0

            nextNode = app.moves_tree.create_node(tag=movesname,parent = n0.identifier,
                                            data={'sp':sp,'ep':ep,'flag':flag,'rsv':'00',
                                                  'notelen':'00000000','note':"",
                                                  'situation':realtime_situation,'pieceWidget':self,'sx':self.bx,'sy':self.by,'ex':to_x,'ey':to_y,
                                                  })
            
            #print(app.moves_tree)

            if n0.identifier != app.moves_tree.root:#根节点不用修改            
                #修改父节点的flag
                if n0.data['flag'] == '00' or n0.data['flag'] == '0f':
                    n0.data['flag'] = 'f0'
                elif n0.data['flag'] == 'f0':
                    n0.data['flag'] = 'ff'
            #修改兄弟中f0==>ff
            lastSibff = None
            lastSib0f = None
            for item in app.moves_tree.siblings(nextNode.identifier):
                if item.data['flag'] == 'f0':
                    lastSibff = item
                if item.data['flag'] == '00':
                    lastSib0f = item
            if lastSibff:
                Logger.debug(f"X-Chess letsgo : {lastSibff.tag=},{lastSibff.data['flag']=}")
                lastSibff.data['flag'] = 'ff'
            if lastSib0f:
                Logger.debug(f"X-Chess letsgo : {lastSib0f.tag=},{lastSib0f.data['flag']=}")
                lastSib0f.data['flag'] = '0f' 
                    

        
        #end #需要新创建一个节点，并且加到招法树中
        
        plus = ""
        if len(app.moves_tree.children(nextNode.identifier)) > 1:#其下有多个招法，添加一个+号
            plus = "+"
        num = len(app.root.ids['id_screenmoves'].ids.id_moveslist.children)
        app.root.ids['id_screenmoves'].ids.id_moveslist.add_widget(OneLineListWithId(id=nextNode.identifier,
                                                                        text=f"{plus}{num:<3}{nextNode.tag}",font_style="H6"))
        
        #显示招法注解
        app.root.ids['id_screenmain'].ids.id_movesnote.text = nextNode.data['note']
        
        #先让子动起来，还有很多要做
        self.movexy(self.bx,self.by,to_x,to_y,'F',curSit)

        #该对方走子了
        app.selected_piece = None

        #画出对方应对此招的走法示意线
        app.root.ids['id_screenmain'].ids.id_chessboard.remove_Allarrows()
        for item in app.moves_tree.children(nextNode.identifier):
            app.root.ids['id_screenmain'].ids.id_chessboard.add_arrow(item.data['sx'],item.data['sy'],item.data['ex'],item.data['ey'])
        
        print("PieceWidget.letsgo end")
    
    #这个函数有点长，要不要拆分下，抽象下，等等吧
    def checkmoves(self,to_x,to_y,curSit):
        """ 
        #不需要判断目标位置上是否有自己人，因为此时是选择切换
        #判断目标位置上是否有己方子力
        curNodeId = app.root.ids['id_screenmoves'].ids.id_moveslist.children[0].id
        curNode = app.moves_tree.get_node(curNodeId)
        curSit = curNode.data['situation']
       
        if (f"{to_x},{to_y}" in curSit) :
            p = curSit[f'f"{to_x},{to_y}']
            if p != None and p.pieceWidget != None and isinstance(p.pieceWidget,PieceWidget) and self.camp == p.camp:
                print("自己人")
                return 
        """

        #红下黑上，暂无实现翻转
        if self.camp == 'r':#红方
            if self.identifier == 'shuai':
                if to_x < 3 or to_x > 5 or to_y < 0 or to_y > 2:
                    print("超出移动范围")
                    return False
                if abs(to_x - self.bx) > 1 or abs(to_y - self.by) > 1 :
                    print("步子大了")
                    return False
                if to_x != self.bx and to_y != self.by :
                    print("只能走直线")
                    return False            
            elif self.identifier == 'shi':
                if to_x < 3 or to_x > 5 or to_y < 0 or to_y > 2:
                    print("超出移动范围")
                    return False
                if abs(to_x - self.bx) != 1 or abs(to_y - self.by) != 1:
                    print("步法不对")
                    return False
            elif self.identifier == 'xiang':
                if to_y < 0 or to_y > 4:
                    print("超出移动范围")
                    return False
                if abs(to_x - self.bx) != 2 or abs(to_y - self.by) != 2:
                    print("步法不对")
                    return False
                
                bCrazy = None#是否有塞象眼的
                cx = cy = None         
                cx = (self.bx + 1) if (to_x > self.bx) else (self.bx - 1)
                cy = (self.by + 1) if (to_y > self.by) else (self.by - 1)
                
                if (f"{cx},{cy}" in curSit):
                    bCrazy = curSit[f'{cx},{cy}']                
                
                if bCrazy:
                    print("有塞象眼的")
                    return False
            elif self.identifier == 'ma':
                if (abs(to_x - self.bx)**2 + abs(to_y - self.by)**2) !=5 :
                    print("步法不对")
                    return False
                
                bCrazy = None#是否有别马腿的
                cx = cy = None         
                if abs(to_x - self.bx) == 2:
                    if to_x > self.bx:
                        cx = self.bx + 1
                        cy = self.by
                    else:
                        cx = self.bx - 1
                        cy = self.by
                elif abs(to_y - self.by) == 2:
                    if to_y > self.by:
                        cx = self.bx
                        cy = self.by + 1
                    else:
                        cx = self.bx
                        cy = self.by - 1
                
                if (f"{cx},{cy}" in curSit):
                    bCrazy = curSit[f'{cx},{cy}']                
                
                if bCrazy:
                    print("有别马腿的")
                    return False
            elif self.identifier == 'ju':
                if self.bx != to_x and self.by != to_y:
                    print("车走直线")
                    return False
                
                bCrazy = None#是否有别车的
                if to_y > self.by: #向上
                    cx = self.bx
                    for cy in range(self.by+1,to_y,1):
                        if (f"{cx},{cy}" in curSit):
                            bCrazy = curSit[f'{cx},{cy}']
                            break
                elif to_y < self.by: #向下
                    cx = self.bx
                    for cy in range(to_y+1,self.by,1):
                        if (f"{cx},{cy}" in curSit):
                            bCrazy = curSit[f'{cx},{cy}']
                            break
                elif to_x > self.bx: #向右
                    cy = self.by
                    for cx in range(self.bx+1,to_x,1):
                        if (f"{cx},{cy}" in curSit):
                            bCrazy = curSit[f'{cx},{cy}']
                            break
                elif to_x < self.bx: #向左
                    cy = self.by
                    for cx in range(to_x+1,self.bx,1):
                        if (f"{cx},{cy}" in curSit):
                            bCrazy = curSit[f'{cx},{cy}']
                            break
                
                if bCrazy:
                    print("有别车的")
                    return False
            elif self.identifier == 'pao':
                if self.bx != to_x and self.by != to_y:
                    print("炮走直线")
                    return False
                
                #炮要打敌人
                target = None
                if (f"{to_x},{to_y}" in curSit) and isinstance(curSit[f'{to_x},{to_y}'],Piece):
                    target = curSit[f'{to_x},{to_y}']
                    if target.camp == self.camp:
                        print("炮要打敌人")
                        return False
                
                mount = 0 #炮架数
                if to_y > self.by: #向上
                    cx = self.bx
                    for cy in range(self.by+1,to_y,1):
                        if (f"{cx},{cy}" in curSit) and isinstance(curSit[f'{cx},{cy}'],Piece):
                            mount = mount + 1
                            if mount > 1:#有多个炮架
                                break
                elif to_y < self.by: #向下
                    cx = self.bx
                    for cy in range(to_y+1,self.by,1):
                        if (f"{cx},{cy}" in curSit) and isinstance(curSit[f'{cx},{cy}'],Piece):
                            mount = mount + 1
                            if mount > 1:#有多个炮架
                                break
                elif to_x > self.bx: #向右
                    cy = self.by
                    for cx in range(self.bx+1,to_x,1):
                        if (f"{cx},{cy}" in curSit) and isinstance(curSit[f'{cx},{cy}'],Piece):
                            mount = mount + 1
                            if mount > 1:#有多个炮架
                                break
                elif to_x < self.bx: #向左
                    cy = self.by
                    for cx in range(to_x+1,self.bx,1):
                        if (f"{cx},{cy}" in curSit) and isinstance(curSit[f'{cx},{cy}'],Piece):
                            mount = mount + 1
                            if mount > 1:#有多个炮架
                                break
                
                if (target != None and mount != 1)  or (target == None and mount > 0) :
                    print("炮架子不对")
                    return False
            
            elif self.identifier == 'bing':
                if self.bx != to_x and self.by != to_y:
                    print("兵走直线")
                    return False                
                if to_y < self.by:
                    print("不可后退")
                    return False
                if abs(to_x - self.bx) > 1 or abs(to_y - self.by) > 1:
                    print("最多1步")
                    return False
                if self.by < 5 and self.by == to_y:
                    print("兵没过河，不能横走")
                    return False              

        
        elif self.camp == 'b':#黑方
            if self.identifier == 'shuai':
                if to_x < 3 or to_x > 5 or to_y < 7 or to_y > 9:
                    print("超出移动范围")
                    return False
                if abs(to_x - self.bx) > 1 or abs(to_y - self.by) > 1 :
                    print("步子大了")
                    return False
                if to_x != self.bx and to_y != self.by :
                    print("只能走直线")
                    return False
            elif self.identifier == 'shi':
                if to_x < 3 or to_x > 5 or to_y < 7 or to_y > 9:
                    print("超出移动范围")
                    return False
                if abs(to_x - self.bx) != 1 or abs(to_y - self.by) != 1:
                    print("步法不对")
                    return False
            elif self.identifier == 'xiang':
                if to_y < 5 or to_y > 9:
                    print("超出移动范围")
                    return False
                if abs(to_x - self.bx) != 2 or abs(to_y - self.by) != 2:
                    print("步法不对")
                    return False
                
                bCrazy = None#是否有塞象眼的
                cx = cy = None         
                cx = (self.bx + 1) if (to_x > self.bx) else (self.bx - 1)
                cy = (self.by + 1) if (to_y > self.by) else (self.by - 1)
                
                if (f"{cx},{cy}" in curSit):
                    bCrazy = curSit[f'{cx},{cy}']                
                
                if bCrazy:
                    print("有塞象眼的")
                    return False
            elif self.identifier == 'ma':
                if (abs(to_x - self.bx)**2 + abs(to_y - self.by)**2) !=5 :
                    print("步法不对")
                    return False
                
                bCrazy = None#是否有别马腿的
                cx = cy = None         
                if abs(to_x - self.bx) == 2:
                    if to_x > self.bx:
                        cx = self.bx + 1
                        cy = self.by
                    else:
                        cx = self.bx - 1
                        cy = self.by
                elif abs(to_y - self.by) == 2:
                    if to_y > self.by:
                        cx = self.bx
                        cy = self.by + 1
                    else:
                        cx = self.bx
                        cy = self.by - 1
                
                if (f"{cx},{cy}" in curSit):
                    bCrazy = curSit[f'{cx},{cy}']                
                
                if bCrazy:
                    print("有别马腿的")
                    return False
            elif self.identifier == 'ju':
                if self.bx != to_x and self.by != to_y:
                    print("车走直线")
                    return False
                
                bCrazy = None#是否有别车的
                if to_y > self.by: #向上
                    cx = self.bx
                    for cy in range(self.by+1,to_y,1):
                        if (f"{cx},{cy}" in curSit):
                            bCrazy = curSit[f'{cx},{cy}']
                            break
                elif to_y < self.by: #向下
                    cx = self.bx
                    for cy in range(to_y+1,self.by,1):
                        if (f"{cx},{cy}" in curSit):
                            bCrazy = curSit[f'{cx},{cy}']
                            break
                elif to_x > self.bx: #向右
                    cy = self.by
                    for cx in range(self.bx+1,to_x,1):
                        if (f"{cx},{cy}" in curSit):
                            bCrazy = curSit[f'{cx},{cy}']
                            break
                elif to_x < self.bx: #向左
                    cy = self.by
                    for cx in range(to_x+1,self.bx,1):
                        if (f"{cx},{cy}" in curSit):
                            bCrazy = curSit[f'{cx},{cy}']
                            break
                
                if bCrazy:
                    print("有别车的")
                    return False
            elif self.identifier == 'pao':
                if self.bx != to_x and self.by != to_y:
                    print("炮走直线")
                    return False
                
                #炮要打敌人
                target = None
                if (f"{to_x},{to_y}" in curSit) and isinstance(curSit[f'{to_x},{to_y}'],Piece):
                    target = curSit[f'{to_x},{to_y}']
                    if target.camp == self.camp:
                        print("炮要打敌人")
                        return False
                
                mount = 0 #炮架数
                if to_y > self.by: #向上
                    cx = self.bx
                    for cy in range(self.by+1,to_y,1):
                        if (f"{cx},{cy}" in curSit) and isinstance(curSit[f'{cx},{cy}'],Piece):
                            mount = mount + 1
                            if mount > 1:#有多个炮架
                                break
                elif to_y < self.by: #向下
                    cx = self.bx
                    for cy in range(to_y+1,self.by,1):
                        if (f"{cx},{cy}" in curSit) and isinstance(curSit[f'{cx},{cy}'],Piece):
                            mount = mount + 1
                            if mount > 1:#有多个炮架
                                break
                elif to_x > self.bx: #向右
                    cy = self.by
                    for cx in range(self.bx+1,to_x,1):
                        if (f"{cx},{cy}" in curSit) and isinstance(curSit[f'{cx},{cy}'],Piece):
                            mount = mount + 1
                            if mount > 1:#有多个炮架
                                break
                elif to_x < self.bx: #向左
                    cy = self.by
                    for cx in range(to_x+1,self.bx,1):
                        if (f"{cx},{cy}" in curSit) and isinstance(curSit[f'{cx},{cy}'],Piece):
                            mount = mount + 1
                            if mount > 1:#有多个炮架
                                break
                
                if (target != None and mount != 1)  or (target == None and mount > 0) :
                    print("炮架子不对")
                    return False
            
            elif self.identifier == 'bing':
                if self.bx != to_x and self.by != to_y:
                    print("兵走直线")
                    return False                
                if to_y > self.by:
                    print("不可后退")
                    return False
                if abs(to_x - self.bx) > 1 or abs(to_y - self.by) > 1:
                    print("最多1步")
                    return False
                if self.by > 4 and self.by == to_y:
                    print("兵没过河，不能横走")
                    return False     
        
        return True

