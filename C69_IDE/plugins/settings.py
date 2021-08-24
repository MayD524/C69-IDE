from main import C69_IDE_main as main
import tkinter

class settings:
    def __init__(self, gui:main) -> None:
        self.gui = gui
        
        
    def settingsMain(self) -> None:
        self.fontSize = tkinter.StringVar()
        self.fontName = tkinter.StringVar()
        self.bgColor = tkinter.StringVar()
        self.fgColor = tkinter.StringVar()
        
        self.settingsWin = tkinter.Toplevel()
        self.fontSizeIn = tkinter.Entry(self.settingsWin,textvariable=fontSize)
def pluginMain(gui_obj:main) -> None:
    setting = settings(gui_obj)
    gui_obj.setMenu.add_command(label="Run current file (Py)", command=setting.settingsMain)