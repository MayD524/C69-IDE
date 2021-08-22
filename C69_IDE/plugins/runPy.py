from main import C69_IDE_main as main
import sys
import os


class runPy:
    def __init__(self, gui:main) -> None:
        self.gui = gui
        
    def run(self):
        print(f"{sys.executable} {self.gui.current_filename}")
        os.system(f"{sys.executable} {self.gui.current_filename}")

def pluginMain(gui_obj:main) -> None:
    rPy = runPy(gui_obj)
    gui_obj.setMenu.add_command(label="Run current file (Py)", command=rPy.run)