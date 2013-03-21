# -*- coding: utf-8 -*-

#短址生成小工具

import wx
import sys
import win32clipboard as w 
import win32con
import urllib2
import json
import urllib
import threading
import re

APIKEY = "dccc5e397bde4bcf9a6c1c07bbcbcd12"
API_URL = "http://126.am/api!shorten.action"

#读取剪贴板
def getClipboardText(): 
    w.OpenClipboard() 
    d = w.GetClipboardData(win32con.CF_TEXT) 
    w.CloseClipboard() 
    return d

#写入剪贴板    
def setClipboardText(text): 
    w.OpenClipboard() 
    w.EmptyClipboard() 
    w.SetClipboardData(win32con.CF_TEXT, text) 
    w.CloseClipboard()

    
def get_long_url():
    long_url = getClipboardText()
    long_url = long_url.strip()
    if not re.findall(r'^[http://|https://].*',long_url):
        long_url = 'http://'+long_url
    return long_url

    
def request_url(url,data):
    response = None
    for i in range(3):
        try:
            if data:
                post_data = urllib.urlencode(data)
                response = urllib2.urlopen(url,timeout=5,data=post_data)
            else:
                response = urllib2.urlopen(url,timeout=5)
            break
        except Exception,e:
            print 'downlad error: '+str(e)
    return response

    
def get_short_url(url):
    response = request_url(API_URL,{"key":APIKEY,"longUrl":url})
    if response != None:
        json_response = response.read()
        try:
            json_object = json.loads(json_response)
            if json_object['status_code'] == 200:
                return json_object['url']
        except Exception,e:
            print 'loads json error: '+str(e)        
    
    
def main():
    long_url = get_long_url()
    short_url = get_short_url(long_url)
    if short_url != None:        
        setClipboardText(short_url.encode('gbk'))
        
class WorkThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        main()
        
class TaskBarIcon(wx.TaskBarIcon):
    ID_Play = wx.NewId()
    ID_About = wx.NewId()
    ID_Closeshow=wx.NewId()
    
    def __init__(self, frame):
        wx.TaskBarIcon.__init__(self)
        self.frame = frame
        self.SetIcon(wx.Icon(name=u'short_url.ico', type=wx.BITMAP_TYPE_ICO), u'桌面短址生成器')
        self.Bind(wx.EVT_MENU, self.OnPlay, id=self.ID_Play)
        self.Bind(wx.EVT_MENU, self.OnAbout, id=self.ID_About)
        self.Bind(wx.EVT_MENU, self.OnCloseshow, id=self.ID_Closeshow)

    def OnPlay(self, event):
        wx.MessageBox(u'拷贝地址后按组合键ALT+`即可将剪贴板的地址转换为短地址，粘贴就可以得到短地址^_^', u'帮助')

    def OnAbout(self,event):
        wx.MessageBox(u'桌面短址生成器 by 李瑾', u'关于')

    def OnCloseshow(self,event):
        self.frame.Close(True)

    # 右键菜单
    def CreatePopupMenu(self):
        menu = wx.Menu()
        menu.Append(self.ID_Play, u'帮助')
        menu.Append(self.ID_About, u'关于')
        menu.Append(self.ID_Closeshow, u'退出')
        return menu        
                                                   
class FrameWithHotKey(wx.Frame):              
    def __init__(
            self, parent=None, id=wx.ID_ANY, title='', pos=wx.DefaultPosition,
            size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE
            ):
        wx.Frame.__init__(self, parent, id, title, pos, size, style) 

        self.SetIcon(wx.Icon(u'short_url.ico', wx.BITMAP_TYPE_ICO))
        self.taskBarIcon = TaskBarIcon(self)
  
        #注册热键shift+`
        self.hotKeyId_start = 100  
        self.RegisterHotKey(self.hotKeyId_start, win32con.MOD_ALT, 192)           
        
        # 绑定事件
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_ICONIZE, self.OnIconfiy)
        self.Bind(wx.EVT_HOTKEY, self.OnHotKeyStart, id=self.hotKeyId_start)
        
        self.work = None                  
        
    def OnHide(self, event):
        self.Hide()
        
    def OnIconfiy(self, event):
        self.Hide()
        event.Skip()
        
    def OnClose(self, event):
        self.taskBarIcon.Destroy()
        self.Destroy()
                   
    def OnHotKeyStart(self, evt):   
        if not self.work:
            self.work = WorkThread()
            self.work.setDaemon(True)
            self.work.start()
            self.work = None
           
app = wx.App()
FrameWithHotKey(None)   
app.MainLoop()  
