from main import C69_IDE_main as main

class pluginMgr:
    def __init__(self, gui:main) -> None:
        self.gui = gui
        
    def list_plugins(self):
        print(self.gui.plugins)

def pluginMain(gui_obj:main) -> None:
    pMgr = pluginMgr(gui_obj)
    gui_obj.setMenu.add_command(label="List Plugins", command=pMgr.list_plugins)