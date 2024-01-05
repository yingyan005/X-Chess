<!--
 * @Author: Paoger
 * @Date: 2024-01-03 10:22:01
 * @LastEditors: Paoger
 * @LastEditTime: 2024-01-05 10:39:03
 * @Description: 
 * 
 * Copyright (c) 2024 by Paoger, All Rights Reserved. 
-->
# X-Chess：中国象棋打谱助手
## 作者
    3037609807@qq.com
    QQ群：780150228
    开源地址：https://github.com/yingyan005/X-Chess
## 缘由
    不胜其烦的广告，恰好接触到Kivy(Python cross-platform GUI)，那就练练手，学以致用，同时为象棋学习者提供一款小工具
## 定位
    学习象棋的打谱小工具
## 特点
    免费、无广告、不收集信息
    借助Kivy特点，同一套代码，通过打包工具，可打包成运行在Android, iOS, Linux, macOS and Windows的软件
    基于互联网精神，仅支持公开的XQF1.0格式棋谱

## 待实现
    接入免费开源引擎皮卡鱼
    支持开局库

## 版本0.02
    修复已知bug
    内置开源引擎XQPy：(象棋巫师非官方python实现,https://github.com/bupticybee/XQPy)
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


## 版本0.01
    实现基本xqf打谱功能


鸣谢：
        XQF作者：公开了1.0规范
        网络资料提供者：技术文档、象棋素材
        热心的棋友，不一一列举了