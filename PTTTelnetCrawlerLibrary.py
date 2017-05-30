import sys
import telnetlib
import time
import re
import requests
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import PTTTelnetCrawlerLibraryUtil

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
WebRequest = requests.session()

class PushInformation(object):
    def __init__(self, PushType, PushID, PushContent, PushTime):
        self._PushType = PushType
        self._PushID = PushID
        self._PushContent = PushContent
        self._PostContent = PostContent
        self._PushTime = PushTime

class PostInformation(object):
    def __init__(self, Board, PostID, Index, Title, WebUrl, Money, PostContent):
        self._Board = Board
        self._PostID = PostID
        self._Index = Index
        self._Title = Title
        self._PostContent = PostContent
        self._Money = Money
        self._WebUrl = WebUrl

    def getPostID(self):
        return self._PostID
    def getPostIndex(self):
        return self._Index
    def getTitle(self):
        return self._Title
    def getPostContent(self):
        return self._PostContent
    def getMoney(self):
        return self._Money
    def getWebUrl(self):
        return self._WebUrl

class PTTTelnetCrawlerLibrary(object):
    def __init__(self, ID, password, kickOtherLogin):
 
        PTTTelnetCrawlerLibraryUtil.Log("ID: " + ID)

        TempPW = ''

        for i in range(len(password)):
            TempPW += "*"
        
        PTTTelnetCrawlerLibraryUtil.Log("Password: " + TempPW)
        if kickOtherLogin:
            PTTTelnetCrawlerLibraryUtil.Log("This connection will kick other login")
        else :
            PTTTelnetCrawlerLibraryUtil.Log("This connection will NOT kick other login")

        PTTTelnetCrawlerLibraryUtil.Log("Start connect to PTT")
        self._host = 'ptt.cc'
        self._user = ID.encode('big5')
        self._password = password.encode('big5')
        self._kickOtherLogin = kickOtherLogin
        self._telnet = telnetlib.Telnet(self._host)
        self._content = ''
        self._isConnected = False
        time.sleep(1)

        if self.connect():
            if self.login():
                self._isConnected = True
        
    @property
    def is_success(self):

        NeedWait = True

        while NeedWait:
        
            if u"密碼不對" in self._content:
                PTTTelnetCrawlerLibraryUtil.Log("Wrong password")
                sys.exit()
            elif u"您想刪除其他重複登入" in self._content:

                if self._kickOtherLogin:
                    self._telnet.write(b"y\r\n")
                    PTTTelnetCrawlerLibraryUtil.Log("Detect other login")
                    PTTTelnetCrawlerLibraryUtil.Log("Kick other login success")
                else :
                    self._telnet.write(b"n\r\n")
                    PTTTelnetCrawlerLibraryUtil.Log("Detect other login")

            elif u"請按任意鍵繼續" in self._content:
                self._telnet.write(b"\r\n")

            elif u"您要刪除以上錯誤嘗試" in self._content:
                PTTTelnetCrawlerLibraryUtil.Log("刪除以上錯誤嘗試...")
                self._telnet.write(b"y\r\n")
                    
            elif u"您有一篇文章尚未完成" in self._content:
                PTTTelnetCrawlerLibraryUtil.Log('刪除尚未完成的文章....')
                self._telnet.write(b"q\r\n")
            else:
                NeedWait = False
            if NeedWait:
                self.waitResponse()
        return True

    @property
    def input_user_password(self):
        if u"請輸入代號" in self._content:
            self._telnet.write(self._user + b"\r\n")
            self._telnet.write(self._password + b"\r\n")
            
            self.waitResponse()
                
            return self.is_success

        return False

    def isLoginSuccess(self):
        return self._isConnected
    def waitResponse(self):
        self._content = ''
        while len(self._content) == 0:
            time.sleep(1)
            self._content = self._telnet.read_very_eager().decode('big5', 'ignore')
    
    def connect(self):
        self._content = self._telnet.read_very_eager().decode('big5', 'ignore')
        if u"系統過載" in self._content:
            PTTTelnetCrawlerLibraryUtil.Log('System is overload')
            sys.exit(0)
        return True

    def login(self):

        result = self.input_user_password
        #self.toUserMenu()
        
        if result:
            PTTTelnetCrawlerLibraryUtil.Log('Login success')
        else :
            PTTTelnetCrawlerLibraryUtil.Log("Login fail")

        return result

    def toUserMenu(self):
        # q = 上一頁，直到回到首頁為止，g = 離開，再見

        self._telnet.write(b"qqqqqqqqqq\r\n")
        self.waitResponse()
            
    def toBoard(self, Board):
        # s 進入要發文的看板
        self._telnet.write(b's')
        self._telnet.write(Board.encode('big5') + b'\r\n')
        self.waitResponse()
        if u"動畫播放中" in self._content or u"請按任意鍵繼續" in self._content:
            #PTTTelnetCrawlerLibraryUtil.Log("First time into " + Board)
            self._telnet.read_very_eager().decode('big5', 'ignore')
            self._telnet.write(b'q')
            self.waitResponse()
        if u"看板《" + Board + u"》":
            return True
        else :
            return False

    def logout(self):
        self.toUserMenu()
        self._telnet.write(b"g\r\ny\r\n")
        self._telnet.close()
        PTTTelnetCrawlerLibraryUtil.Log("Logout success")

    def post(self, board, title, content, PostType, SignType):
        self.toUserMenu()
        if not self.toBoard(board):
            PTTTelnetCrawlerLibraryUtil.Log("Into " + board + " fail")
            return False

        # 請參考 http://donsnotes.com/tech/charsets/ascii.html#cntrl
        # Ctrl+P
        self._telnet.write(b'\x10')
        # 發文類別
        self._telnet.write(str(PostType).encode('big5') + b'\r\n')
        self._telnet.write(title.encode('big5') + b'\r\n')
        self.waitResponse()
        # Ctrl+X
        self._telnet.write(content.encode('big5') + b'\x18')
        self.waitResponse()
        # 儲存文章
        self._telnet.write(b's\r\n')
        # 不加簽名檔
        self._telnet.write(str(SignType).encode('big5') + b'\r\n')
        PTTTelnetCrawlerLibraryUtil.Log(title + " post success")

        return True
    
    def getPostInformationByID(self, Board, PostID):
        
        result = None   
    
        self.toUserMenu()
        if not self.toBoard(Board):
            PTTTelnetCrawlerLibraryUtil.Log("Into " + Board + " fail")
            return result
        self._telnet.write(b'#' + PostID.encode('big5') + b'\r\n')
        self.waitResponse()
        if u"找不到這個文章代碼(AID)" in self._content:
            PTTTelnetCrawlerLibraryUtil.Log("Find post id " + PostID + " fail")
            return result
        PTTTelnetCrawlerLibraryUtil.Log("Find post id " + PostID + " success")

        #Refresh screen
        self._telnet.write(b'\x0C')
        self.waitResponse()

        #PostID, Index, Title, WebUrl, Money, PostContent):
        PostIndex = -1
        PostTitle = ""
        PostWebUrl = ""
        PostMoney = -1
        PostContent = ""
        
        for InforTempString in self._content.split("\r\n"):
            if ">" in InforTempString:
                PostIndex = re.search(r'\d+', InforTempString).group()

        if PostIndex == -1:
            PTTTelnetCrawlerLibraryUtil.Log("Find PostIndex fail")
            return result
        
        #Query post information
        self._telnet.write(b'Q')
        self.waitResponse()

        for InforTempString in self._content.split("\r\n"):
            Line = InforTempString.replace("[1;37m", "")
            Line = Line.replace("[16;77H", "")
            Line = Line.replace("[15;77H", "")

            if u">" in Line:
                PostTitle = Line[Line.index("□ ") + len("□ "): len(Line)]
            if u"https" in Line:
                PostWebUrl = Line[Line.index("https://") : Line.index(".html") + len(".html")]
            if u"這一篇文章值" in Line:
                PostMoney = re.search(r'\d+', Line).group()
        
        if PostTitle == "":
            PTTTelnetCrawlerLibraryUtil.Log("Find PostTitle fail")
            return False
        if PostWebUrl == "":
            PTTTelnetCrawlerLibraryUtil.Log("Find PostWebUrl fail")
            return False
        if PostMoney == -1:
            PTTTelnetCrawlerLibraryUtil.Log("Find PostMoney fail")
            return False

        res = WebRequest.get(PostWebUrl, verify=False)
        if 'over18' in res.url:
            PTTTelnetCrawlerLibraryUtil.Log("Detect 18 web")
            load = {
                'from': '/bbs/{}/index.html'.format(Board),
                'yes': 'yes'
            }
            res = WebRequest.post('https://www.ptt.cc/ask/over18', verify=False, data=load)
		
        PostContent = res.text
        
        """PTTTelnetCrawlerLibraryUtil.Log("Post id: " + PostID)
        PTTTelnetCrawlerLibraryUtil.Log("Post index: " + PostIndex)
        PTTTelnetCrawlerLibraryUtil.Log("Post title: " + PostTitle)
        PTTTelnetCrawlerLibraryUtil.Log("Post web url: " + PostWebUrl)
        PTTTelnetCrawlerLibraryUtil.Log("Post money: " + PostMoney)"""
        
        result = PostInformation(Board, PostID, PostIndex, PostTitle, PostWebUrl, PostMoney, PostContent)

        return result
    
if __name__ == "__main__":

    print("PTT Telnet Crawler Library v 0.1.170528")
    print("PTT CodingMan")
