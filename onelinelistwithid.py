'''
Author: Paoger
Date: 2023-11-24 09:46:39
LastEditors: Paoger
LastEditTime: 2023-12-15 15:48:22
Description: 

Copyright (c) 2023 by Paoger, All Rights Reserved. 
'''
import uuid

from kivymd.app import MDApp
from kivymd.uix.list import OneLineListItem

class OneLineListWithId(OneLineListItem):
    #id应用应根据需要保持唯一性
    id = ""

    def __init__(self,id=None, **kwargs):
        super(OneLineListWithId, self).__init__(**kwargs)
        if id == None:
            id = uuid.uuid1()
        self.id = id#
    
    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            # we consumed the touch. return False here to propagate
            # the touch further to the children.
            print("....OneLineListWithId.on_touch_up on me...")            
            print(f"{self.id=},{self.text=}")

            app = MDApp.get_running_app()
            #app.cur_movies_id = self.id
  
            for child in app.root.ids['id_screenmoves'].ids.id_moveslist.children[:]:
                #print(f"{child.text}")
                if child.bg_color == [0,1,1,1]:
                    child.bg_color = app.theme_cls.bg_normal
            #self.bg_color = [0,1,1,1]
            self.bg_color = [0,1,1,1]

            app.root.ids['id_screenmoves'].ids.id_movesbranch.clear_widgets()
            if len(app.moves_tree.children(self.id)) > 1:#其下有多个招法，添加一个+号
                 for item in app.moves_tree.children(self.id):
                     num = len(app.root.ids['id_screenmoves'].ids.id_movesbranch.children)+1
                     app.root.ids['id_screenmoves'].ids.id_movesbranch.add_widget(OneLineListItem(id=item.identifier,
                                                                        text=f"{num:<2}{item.tag}",font_style="H6",divider='Inset'))
            
            #显示招法注解
            app.root.ids['id_screenmoves'].ids.id_movesnote2.text = app.moves_tree.get_node(self.id).data['note']

            return True
        
        return super().on_touch_up(touch)