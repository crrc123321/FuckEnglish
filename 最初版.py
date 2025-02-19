#导入所需模块
import time
import requests
import random
import string
import os
import webbrowser
import shutil
import sys
import json
import difflib
from wxauto import *

#定义相似算法函数
def SimilarMatching(A,transback):
    a=difflib.SequenceMatcher(None,A,transback).quick_ratio()
    return a

#定义创建文件夹和文本文件函数
def checkandcreatefolder():
    #定义路径，文件名和path
    fway=r"C:\ProgramData\EnglishHelper"
    finame='Cookies.txt'
    fpath=os.path.join(fway,finame)
    #如果不存在，则创建，否则跳过
    if not os.path.exists(fway):
        os.makedirs(fway)
        file=open(fpath,'w')
    else:
        pass

#定义文件操作函数(获取用户输入的cookie并写入cookie.txt)
def writecookie():
    #定义路径，文件名和path
    fway=r"C:\ProgramData\EnglishHelper"
    finame='Cookies.txt'
    fpath=os.path.join(fway,finame)
    #接受cookie并写入文件
    cookie=input('请输入cookie：')
    with open(fpath,'w') as file:
        file.write(cookie)    
        file.close()

#定义报头函数
def Headers():
    #定义路径、文件名和path
    fway=r"C:\ProgramData\EnglishHelper"
    finame='Cookies.txt'
    fpath=os.path.join(fway,finame)
    #使用只读权限打开文件，设置content变量并作为报头一部分
    with open(fpath,'r') as file:
        content=file.read()
    headers={
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
    "Cookie": content 
    }
    return(headers)

#获取切片后的单词，以备发送
def GetWords():
    #设置起始位置
    start_index = lstmsg[1].find("【单选】") + len("【单选】")
    end_index = lstmsg[1].find("[")
    #获取字符串格式的单词本体并返回值
    gotword = lstmsg[1][start_index:end_index].strip()
    return gotword

#将获取到的单词发送至翻译提供商，并取得翻译结果
def GetAndSend(gottenword,Headers):
    try:
        response=requests.post(trans,headers=Headers,data={'kw':gottenword})
        response.raise_for_status()
        data=response.json().get('data')
        return data[0]['v'] if data else None
    except Exception as e:
        print(f"请求错误：{e}")
        return None

#引用创建文件夹和文本文件函数
checkandcreatefolder()

#引用文件操作函数
writecookie()

#引用报头函数
Headers()

#设置已背单词，目标数量和正确数变量
right=0
verify=0
answered=0
erroranswer=0
errorsit=0
gradeanswer=int(input('请输入要背单词的数量:'))

#设置翻译API提供商
trans='https://fanyi.baidu.com/sug'

#打开微信并打开在线签到助手聊天界面
wx=WeChat()
wx.ChatWith('在线签到助手')

#设置单词存储区
A=[]
B=[]
C=[]
D=[]

#如果已背单词数量+异常情况低于目标单词
while answered+errorsit<gradeanswer:
    #获取最后一条信息并储存
    lstmsg=wx.GetAllMessage()[-1]

    #获取单词并调用发送函数
    wd=GetWords()
    hd=Headers()
    transback=GetAndSend(wd,hd)

    #如果检测到“20秒....”，则为A、B、C、D分别设置切片变量
    if "请在20秒内回复答案" in lstmsg[1]:
        a_start=lstmsg[1].find("A. ")+len("A. ")
        a_end=lstmsg[1].find("B. ")
        b_start=lstmsg[1].find("B. ")+len("B. ")
        b_end=lstmsg[1].find("C. ")
        c_start=lstmsg[1].find("C. ")+len("C. ")
        c_end=lstmsg[1].find("D. ")
        d_start=lstmsg[1].find("D. ")+len("D. ")
        d_end=lstmsg[1].find("====================")

        #一个简单的异常处理
        if type(transback) != type('test'):
            print('出现错误，不算数，很有可能是cookie值错误')
            print('如果之前能背，那就是sb百度翻译又抽风🌶')
            errorsit+=1
            continue

        #打印当前已背数量
        print('已背单词数量：',answered)

        #检测单词正确数
        if "很棒！答题正确。"in lstmsg[1]:
            right+=1
            print('正确数量：',right)
        if "很棒！答题正确。" and '本轮答题已完成。' in lstmsg[1]:
            right+=1
            print('正确数量：',right)

        #检测单词错误数
        if "答题错误。正确答案" in lstmsg[1]:
            erroranswer+=1
            print('错误数量：',erroranswer)        

        #在单词存储区存储对应选项对应翻译
        A.append(lstmsg[1][a_start:a_end].strip())
        B.append(lstmsg[1][b_start:b_end].strip())
        C.append(lstmsg[1][c_start:c_end].strip())
        D.append(lstmsg[1][d_start:d_end].strip())

        #将选项分别转换为字符串
        strA="".join(A)
        strB="".join(B)
        strC="".join(C)
        strD="".join(D)

        #调用相似算法
        sima=SimilarMatching(strA,transback)
        simb=SimilarMatching(strB,transback)
        simc=SimilarMatching(strC,transback)
        simd=SimilarMatching(strD,transback)

        #微信内发送选项
        if sima>simb and sima>simc and sima>simd:
            print('算法匹配答案为A')
            wx.SendMsg("A")
        if simb>sima and simb>simc and simb>simd:
            print('算法匹配答案为B')
            wx.SendMsg("B")
        if simc>sima and simc>simb and simc>simd:
            print('算法匹配答案为C')
            wx.SendMsg("C")
        if simd>sima and simd>simb and simd>simc:
            print('算法匹配答案为D')
            wx.SendMsg("D")
            
    #如果上述条件不成立，则执行检测“验证...”的操作，切片验证码并发送
    elif "验证单词学习行为" in lstmsg[1]:
        #设置起始位置
        start_index = lstmsg[1].find("请回复") + len("请回复")
        end_index=lstmsg[1].find("验证单词学习行为")

        #发送字符串格式的切片(验证码)
        print('该死的验证码：',lstmsg[1][start_index:end_index].strip())
        print('又尼玛不算正确词')
        verify+=1
        wx.SendMsg(lstmsg[1][start_index:end_index].strip())

        #出现这个，计数-1，否则会提前结束程序，也会导致计数错误
        answered-=1

    #否则，发送“背单词”
    else:
        wx.SendMsg("背单词")
        answered-=1
    
    #每次回答后，清空单词存储区
    A.clear()
    B.clear()
    C.clear()
    D.clear()

    #每循环一次，已背单词数+1
    answered+=1

    #循环结束后，延迟2秒执行
    time.sleep(2)

print('总结')
print('已背单词数量：',gradeanswer)
print('错误数：',erroranswer)
print('正确数：',right)
print('验证码数：',verify)
print('错误情况：',errorsit)
