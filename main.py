

import win32
import win32event
import win32clipboard


# def intercept():
#   win32clipboard.OpenClipboard()
#   data = win32clipboard.GetClipboardData()
#   win32clipboard.CloseClipboard()
#   print(data)


# win32clipboard.AddClipboardFormatListener()

# #win32clipboard.SetClipboardViewer
# m = win32clipboard.GetMessage()
# print(m)
# #h = win32clipboard.SetClipboardViewer()



# # w = win32clipboard.ChangeClipboardChain()
# # print(w)
# #win32event.CreateEvent

import win32con
import win32gui
import sys,os
from io import BytesIO
from PIL import Image
from datetime import datetime
from duplicated_image import DuplicatedImageService
import json

class ClipboardListeneer:

  def on_destroy(self,hwdn,msg,wparam,lparam):
    self.my_log('on_destroy')
    #win32gui.ChangeClipboardChain(hwdn,self.hwndNextViewer)
    win32clipboard.ChangeClipboardChain(hwdn,self.hwndNextViewer)
    win32gui.PostQuitMessage(0)
    return lparam

  def on_hotkey(self,hwdn,msg,wparam,lparam):
    self.my_log('on_hotkey',hwdn,msg,wparam,lparam)

  def my_log(self,message:str):
    if self.params['is_view_log']:
      print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] {message}')

  def wndProc(self, hWnd, message, wParam, lParam):
    self.my_log('wndProc',hWnd,message,wParam,lParam)
    if message == win32con.WM_CLOSE:  # Пример: закрытие окна
        win32gui.PostQuitMessage(0)  # Выходим из цикла обработки сообщений
    return win32gui.DefWindowProc(hWnd, message, wParam, lParam)
  
  def __init__(self,params,duplicatedImageService):
    self.params = params

    if not os.path.isdir(self.params['path_text_files']):
      os.makedirs(self.params['path_text_files'])

    self.duplicatedImageService = duplicatedImageService
    mess_map = {
      win32con.WM_DRAWCLIPBOARD:self.on_draw_cliboard,
      win32con.WM_CHANGECBCHAIN:self.on_change,
      win32con.WM_DESTROY:self.on_destroy,
      win32con.WM_HOTKEY:self.on_hotkey,
    }
    wc = win32gui.WNDCLASS()
    #print(dir(wc))
    #print(vars(wc))
    hinst = wc.hInstance = win32gui.GetModuleHandle(None)
    wc.lpszClassName = 'ClipboardListener'
    wc.lpfnWndProc = mess_map
    #wc.lpfnWndProc = self.wndProc
    self.class_atom = win32gui.RegisterClass(wc)
    #print(win32gui.CreateWindow.__str__)
    self.hwnd = win32gui.CreateWindow(self.class_atom,'ClipboardListener',0,0,0,0,0,0,0,hinst,None)
    #wc.style
    #print(print(dir(win32clipboard)))#(self.)

  def add_buff_to_file(self,format_data,data):
    if isinstance(data,bytes):
      self.my_log('decode')
      self.my_log(f'{data=}')
      data = data.decode('UTF-16').replace('\x00','')
      self.my_log(f'{data=}, {type(data)}')
    
    full_path = os.path.join(self.params['path_text_files'],f'{datetime.now().strftime("%Y%m%d")}.buf')
    with open(full_path,'a',encoding='UTF-8') as f:
      obj = {
        'data':data,
        'length':len(data),
        'time':f'{datetime.now().strftime("%H:%M:%S")}',
        'format_data':format_data
      }
      j_str = json.dumps(obj,indent=2,ensure_ascii=False)
      f.write(j_str+'\n')

    self.my_log(f'get {format_data=}: {data}')


  def on_draw_cliboard(self,hwdn,msg,wparam,lparam):
    #print('on_draw_cliboard',msg, msg ==  win32con.WM_DRAWCLIPBOARD)
    # win32clipboard.OpenClipboard()
    # #FormatName = win32clipboard.GetClipboardFormatName()
    # #print('FormatName',FormatName)
    # data = win32clipboard.GetClipboardData()
    # win32clipboard.CloseClipboard()
    # print('from buffer:',data)
    # if self.hwndNextViewer is not None:
    #win32gui.SendMessage(self.hwndNextViewer,msg,wparam,lparam)

    is_use_html_format = self.params['is_use_html_format']
    try:
        win32clipboard.OpenClipboard()
        if is_use_html_format and win32clipboard.IsClipboardFormatAvailable(49446):
          data = win32clipboard.GetClipboardData(49446)
          #print('from buffer HTML format:',data)
          self.add_buff_to_file(format_data='HTML',data=data)
        elif win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
          data = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
          #print('from buffer:',data)
          self.add_buff_to_file(format_data='CF_UNICODETEXT',data=data)
        elif win32clipboard.IsClipboardFormatAvailable(win32con.CF_TEXT):
          data = win32clipboard.GetClipboardData(win32con.CF_TEXT)
          #print('from buffer:',data)
          self.add_buff_to_file(format_data='CF_TEXT',data=data)
        elif win32clipboard.IsClipboardFormatAvailable(win32con.CF_DIB):
          data = win32clipboard.GetClipboardData(win32con.CF_DIB)
          image_stream = BytesIO(data)
          image = Image.open(image_stream)
          if not self.duplicatedImageService.is_duplicated(image):
            full_path = os.path.join(self.params['path_dir_images'],f'image_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
            image.save(full_path)
            self.duplicatedImageService.add_image(image)
            self.add_buff_to_file(format_data='CF_DIB',data=full_path)
        
        elif win32clipboard.IsClipboardFormatAvailable(win32con.CF_LOCALE):
            data = win32clipboard.GetClipboardData(win32con.CF_LOCALE)
            #print('from buffer CF_LOCALE:',data)
            self.add_buff_to_file(format_data='CF_LOCALE',data=data)
        
        elif win32clipboard.IsClipboardFormatAvailable(win32con.CF_OEMTEXT):
            data = win32clipboard.GetClipboardData(win32con.CF_OEMTEXT)
            #print('from buffer CF_OEMTEXT:',data)
            self.add_buff_to_file(format_data='CF_OEMTEXT',data=data)
        elif win32clipboard.IsClipboardFormatAvailable(49159):
            data = win32clipboard.GetClipboardData(49159)
            #print('from buffer FileName:',data.decode('UTF-8'))
            self.add_buff_to_file(format_data='FileName',data=data)
        else:
          self.my_log('get other type data from clipboard')
        # else: 
        #   data = win32clipboard.GetClipboardData()
        #   print('from buffer OTHER FORMAT:',data)

    finally:
        win32clipboard.CloseClipboard()
    return wparam
  
  def on_change(self,msg,wparam,lparam):
    self.my_log('on_change')
    if msg ==  win32con.WM_DRAWCLIPBOARD:
      win32clipboard.OpenClipboard(win32clipboard.CF_UNICODETEXT)

      FormatName = win32clipboard.GetClipboardFormatName()
      self.my_log(f'{FormatName=}')
      data = win32clipboard.GetClipboardData()

      win32clipboard.get

      win32clipboard.CloseClipboard()
      self.my_log(f'from buffer: {data}')
    win32gui.SendMessage(self.hwndNextViewer,msg,wparam,lparam)

  def start(self):
    self.my_log('start')
    self.hwndNextViewer = win32clipboard.SetClipboardViewer(self.hwnd)
    #msg = win32gui.GetMessage()
    #print('msg',msg)
    # try:
    #   win32gui.PumpMessages()
    #   print('done')
    # finally:
    #   print('finally')
    #   win32gui.ChangeClipboardChain(self.hwnd,self.hwndNextViewer)
    try:
      while not win32gui.PumpWaitingMessages():
        #print('PumpWaitingMessages')
        pass
      self.my_log('done start')
    except KeyboardInterrupt:
      self.my_log('Выход из программы по нажатию Ctrl+C')
      win32gui.DestroyWindow(self.hwnd)
      win32gui.UnregisterClass(self.class_atom, None)
      sys.exit(0)

if __name__ == '__main__':
  with open('params.json','r') as f:
    obj = json.load(f)
  print(obj)
  # path_db_images = r'c:\Users\aakorobov\Pictures\Screenshots\images.db'
  duplicatedImageService = DuplicatedImageService(obj['path_db_images'])
  lister = ClipboardListeneer(obj,duplicatedImageService)
  lister.start()
