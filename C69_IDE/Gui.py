from _thread import start_new_thread
from tkinter import filedialog
from tkinter import ttk
from tkinter import *
import subprocess
import UPL
import sys
import re
import os

CONFIG_PATH = "./json/config.json"
class CustomText(Text):

    def __init__(self, *args, **kwargs):
        """A text widget that report on internal widget commands"""
        Text.__init__(self, *args, **kwargs)

        # create a proxy for the underlying widget
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)

    def _proxy(self, command, *args):
        cmd = (self._orig, command) + args
        result = self.tk.call(cmd)
        if command in ("insert", "delete", "replace"):
            self.event_generate("<<TextModified>>")
        return result

class C69_IDE_main:
    def __init__(self, config:dict) -> None:
        
        self.config = config
        self.current_lang = "python"
        self.current_filename = ""
        
        self.current_syntax_settings = UPL.Core.file_manager.getData_json(self.config[self.current_lang])
        self.explorerPath = os.path.join(os.getenv('WINDIR'), 'explorer.exe')
        
        ## GUI Stuff
        self.Window = Tk()
        self.Window.configure(background="black")
        self.layout()
        
        self.Window.title("C69 IDE")
        self.Window.mainloop()
    
    def layout(self) -> None:
        self.panedwindow=ttk.Panedwindow(self.Window, orient=HORIZONTAL)  
        self.panedwindow.pack(fill=BOTH, expand=True) 
        self.WinMenu = Menu(self.Window)
        self.Window.config(menu=self.WinMenu)
        
        fileBar = Menu(self.WinMenu,tearoff=0)
        setMenu = Menu(self.WinMenu, tearoff=0)
        
        self.WinMenu.add_cascade(label="File", menu = fileBar)
        self.WinMenu.add_cascade(label="Settings", menu=setMenu)
        
        fileBar.add_command(label="Open File", command=self.open_File)
        fileBar.add_command(label="Open Folder", command=self.openFolder)
        fileBar.add_command(label="New File", command=self.newFile)
        fileBar.add_command(label="Save As", command=self.saveAs)
        fileBar.add_command(label="Save", command=self.saveFile)
        
        setMenu.add_command(label="Restart", command=self.restartProg)
        self.listContent = ttk.Frame(self.panedwindow,width=100,height=300, relief=SUNKEN)  
        self.editorFrame =ttk.Frame(self.panedwindow,width=400,height=400, relief=SUNKEN)  
        
        self.panedwindow.add(self.listContent, weight=1)  
        self.panedwindow.add(self.editorFrame, weight=4)  

        self.editorBox = CustomText(self.editorFrame, font=(self.config["font_name"], self.config["font_size"]))
         
        self.editorBox.pack(expand=1,fill=BOTH)
        ##Tree view

        self.currStrVar = StringVar()
        self.currStrVar.set("Test")
        self.currFile = Label(self.listContent,textvariable=self.currStrVar)
        self.tv=ttk.Treeview(self.listContent,show='tree')
       
        self.directory = os.getcwd()
        
        self.tv.heading('#0',text="Dir"+self.directory,anchor=W)
        self.path = os.path.abspath(self.directory)
        self.node = self.tv.insert('','end',text=self.path,open=True) 
        self.traverse_dir(self.node,self.path)
        
        self.tv.pack(expand=1,fill=BOTH,anchor=W)
        self.tv.bind('<Button-1>', self.selectItem)

        self.currFile.pack()
        for i in self.current_syntax_settings.keys():
            self.editorBox.tag_configure(i, foreground=self.current_syntax_settings[i]["foreground"])
        
        
        self.editorBox.bind("<<TextModified>>", self._textChanged)
    
    def selectItem(self, a):
        curItem = self.tv.focus()
        curItem = self.tv.item(curItem)
        item_iid = self.tv.selection()[0]
        parent_iid = self.tv.parent(item_iid)
        node = self.tv.item(parent_iid)['text']
        self.open_File(f'{self.path}/{curItem["text"]}')
        self.currStrVar.set(node)
        
    def displayFileText(self, filename:str) -> None:
        fileData = ""
        
        with open(filename, 'r+') as reader:
            fileData = reader.read()
            
        self.editorBox.delete("1.0", "end")
        self.editorBox.insert(END, fileData)
    
    def saveFile(self) -> None:
        print(self.current_filename)
        with open(self.current_filename, "w+") as writer:
            writer.write(self.editorBox.get('1.0', END))
    
    def newFile(self) -> None:
        file_path = filedialog.asksaveasfilename()
        
        try:
            with open(file_path, "w+"): pass
            self.refresh()
            self.open_File(fileName=file_path)
        
        except:
            print("some error")
    
    def saveAs(self):
        file_path = filedialog.asksaveasfilename()
        
        try:
            self.current_filename = file_path
            self.saveFile()
            self.refresh
        
        except FileNotFoundError:
            print("error")
    
    def open_File(self, fileName=None) -> None:
        if fileName == None:
            path = os.getcwd()
            fileName = self.explorer(path)
        
        if os.path.isfile(fileName):
            self.displayFileText(filename=fileName)
            self.current_filename = fileName
            self.currStrVar.set(self.current_filename)
        
        else:
            print("Not a file")
    
    def yview(self) -> None:
        pass
    
    def traverse_dir(self,parent,path):
        for d in os.listdir(path):
            full_path=os.path.join(path,d)
            isdir = os.path.isdir(full_path)
            pth = full_path.replace(os.getcwd(), "").replace('\\', '/').removeprefix('/')
            id=self.tv.insert(parent,'end',text=pth,open=False)
            if isdir:
                self.traverse_dir(id,full_path)
                
    def _textChanged(self, evt):
        for tag in evt.widget.tag_names():
            evt.widget.tag_remove(tag, '1.0', 'end')
        lines = evt.widget.get('1.0', 'end-1c').split('\n')
        
        for i, line in enumerate(lines):
            #print(line)
            for x in self.current_syntax_settings.keys():
                self._applytag(i, line, x, self.current_syntax_settings[x]["regex"], evt.widget) # your tags here

    def openFolder(self) -> None:
        self.directory = self.explorerFolder(os.getcwd())
        if self.directory == '': return
        
        os.chdir(self.directory)
        for i in self.tv.get_children():
            self.tv.delete(i)
        self.path = os.path.abspath(self.directory)
        self.node = self.tv.insert('','end',text=self.path,open=True) 
        self.traverse_dir(self.node,self.path)
    
    def refresh(self) -> None:
        for i in self.tv.get_children():
            self.tv.delete(i)
        self.path = os.path.abspath(self.directory)
        self.node = self.tv.insert('','end',text=self.path,open=True) 
        self.traverse_dir(self.node,self.path)
    
    @staticmethod
    def explorerFolder(path:str) -> str:
        newDir = filedialog.askdirectory(initialdir=path, title="Select a Folder")
        return newDir
    
    @staticmethod
    def restartProg() -> None:
        subprocess.Popen(f"{sys.executable} ./Gui.py")
        sys.exit(0)

    @staticmethod
    def explorer(path:str) -> str:
        filename = filedialog.askopenfilename(initialdir=path,
                                              title="Select a File")
        return filename
    
          
    def _applytag(self, line, text, tag, regex, widget):
        indexes = [(m.start(), m.end()) for m in re.finditer(regex, text)]
        for x in indexes:
            widget.tag_add(tag, f"{line+1}.{x[0]}", f"{line+1}.{x[1]}")
            

if __name__ == "__main__":
    config = UPL.Core.file_manager.getData_json(CONFIG_PATH)
    C69_IDE_main(config)
