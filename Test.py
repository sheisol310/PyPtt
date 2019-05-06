﻿import sys
import time
import json
import getpass
import traceback
import PTTLibrary
from PTTLibrary import PTT


def Init():

    print('===正向===')
    print('===預設值===')
    PTT.Library()
    print('===中文顯示===')
    PTT.Library(Language=PTT.Language.Chinese)
    print('===英文顯示===')
    PTT.Library(Language=PTT.Language.English)
    print('===Telnet===')
    PTT.Library(ConnectMode=PTT.ConnectMode.Telnet)
    print('===WebSocket===')
    PTT.Library(ConnectMode=PTT.ConnectMode.WebSocket)
    print('===Log DEBUG===')
    PTT.Library(LogLevel=PTT.LogLevel.DEBUG)
    print('===Log INFO===')
    PTT.Library(LogLevel=PTT.LogLevel.INFO)
    print('===Log SLIENT===')
    PTT.Library(LogLevel=PTT.LogLevel.SLIENT)
    print('===Log SLIENT======')

    print('===負向===')
    try:
        print('===語言 99===')
        PTT.Library(Language=99)
    except ValueError:
        print('通過')
    except:
        print('沒通過')
        return
    print('===語言放字串===')
    try:
        PTT.Library(Language='PTT.Language.English')
    except TypeError:
        print('通過')
    except:
        print('沒通過')
        return
    # print('===Telnet===')
    # PTT.Library(ConnectMode=PTT.ConnectMode.Telnet)
    # print('===WebSocket===')
    # PTT.Library(ConnectMode=PTT.ConnectMode.WebSocket)
    # print('===Log DEBUG===')
    # PTT.Library(LogLevel=PTT.LogLevel.DEBUG)
    # print('===Log INFO===')
    # PTT.Library(LogLevel=PTT.LogLevel.INFO)
    # print('===Log SLIENT===')
    # PTT.Library(LogLevel=PTT.LogLevel.SLIENT)
    # print('===Log SLIENT======')


def Loginout():
    PTTBot = PTT.Library(
        ConnectMode=PTT.ConnectMode.WebSocket
    )
    try:
        PTTBot.login(ID, Password, KickOtherLogin=True)
    except PTTLibrary.ConnectCore.LoginError:
        PTTBot.log('登入失敗')
        sys.exit()
    PTTBot.log('登入成功')
    PTTBot.logout()

    for i in reversed(range(5)):
        time.sleep(1)
        print(i + 1)

    PTTBot = PTT.Library(
        ConnectMode=PTT.ConnectMode.Telnet,
        LogLevel=PTT.LogLevel.DEBUG
    )
    try:
        PTTBot.login(ID, Password, KickOtherLogin=True)
    except PTTLibrary.ConnectCore.LoginError:
        PTTBot.log('登入失敗')
        sys.exit()
    PTTBot.log('登入成功')
    PTTBot.logout()


def PerformanceTest():

    PTTBot = PTT.Library(
        ConnectMode=PTT.ConnectMode.WebSocket,
        LogLevel=PTT.LogLevel.SLIENT
    )
    try:
        PTTBot.login(ID, Password)
    except PTTLibrary.ConnectCore.LoginError:
        PTTBot.log('登入失敗')
        sys.exit()
    PTTBot.log('登入成功')

    TestTime = 100

    StartTime = time.time()
    for _ in range(TestTime):
        PTT_TIME = PTTBot.getTime()

        if PTT_TIME is None:
            print('PTT_TIME is None')
            break
        # print(PTT_TIME)
    EndTime = time.time()
    PTTBot.logout()
    print('Performance Test WebSocket', round(EndTime - StartTime, 2), 's')

    PTTBot = PTT.Library(
        ConnectMode=PTT.ConnectMode.Telnet,
        LogLevel=PTT.LogLevel.SLIENT
    )
    try:
        PTTBot.login(ID, Password)
    except PTTLibrary.ConnectCore.LoginError:
        PTTBot.log('登入失敗')
        sys.exit()
    PTTBot.log('登入成功')

    StartTime = time.time()
    for _ in range(TestTime):
        PTT_TIME = PTTBot.getTime()

        if PTT_TIME is None:
            print('PTT_TIME is None')
            break
        # print(PTT_TIME)
    EndTime = time.time()
    PTTBot.logout()
    print('Performance Test Telnet', round(EndTime - StartTime, 2), 's')

    print('Performance Test finish')

if __name__ == '__main__':
    print('Welcome to PTT Library v ' + PTT.Version + ' test case')

    if len(sys.argv) == 2:
        if sys.argv[1] == '-ci':
            print('CI test run success!!')
            sys.exit()

    try:
        with open('Account.txt') as AccountFile:
            Account = json.load(AccountFile)
            ID = Account['ID']
            Password = Account['Password']
    except FileNotFoundError:
        ID = input('請輸入帳號: ')
        Password = getpass.getpass('請輸入密碼: ')

    try:
        Loginout()
        # PerformanceTest()
        

        pass
    except Exception as e:

        traceback.print_tb(e.__traceback__)
        print(e)
