import maya.OpenMayaUI as omui
import maya.cmds as cmds 
import colorsys
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from PySide2 import QtCore, QtWidgets
from shiboken2 import wrapInstance

# Initial Materials 
mat_list = ['BlueButton', 'BlueButtonOFF',
               'BlueLight', 'Catwalk01', 
               'Chrome', 'Concrete', 
               'ControlPanelBlack', 'ControlPanelGrey', 
               'DarkBlueButton', 'FoilAluminum', 
               'GeneratorPulse', 'GreenLight',
               'HangerFloor', 'Hologram01', 
               'Hologram02', 'ImpBoxBlue', 
               'ImpBoxBlue02', 'ImpBoxRed', 
               'ImpBoxRed02', 'ImpGrid', 
               'ImpGridRed', 'ImpTrimDetails01', 
               'KejimRock01', 'Landscape_Kejim',
               'OrangeButton', 'PipeMetalBlack', 
               'PipeMetalGrey', 'PipeMetalImpGrey', 
               'PipeMetalRed', 'RedButton', 
               'RedButtonOFF', 'RedLight', 
               'RoughMetal', 'RubberFloor', 
               'StripesPipe', 'StripesPipePOM', 
               'Trim01POM', 'WallGrid01', 
               'WhiteButton', 'WhiteButtonOFF']

def main_window():
    window_int = omui.MQtUtil.mainWindow()
    return wrapInstance(int(window_int), QtWidgets.QWidget)

class MaterialUI(MayaQWidgetDockableMixin, QtWidgets.QDialog):
    def __init__(self, parent=main_window()):
        super(MaterialUI, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setObjectName('MaterialIdUI')
        self.setWindowTitle('Material ID Generator')
        self.check_window_exists()
        self.create_ui()
        # self.create_default_mats()

    # prevent window duplication
    def check_window_exists(self):
        if QtWidgets.QApplication.instance():
            for window in (QtWidgets.QApplication.allWindows()):
                if 'MaterialIdUI' in window.objectName():
                    window.close()

    def create_ui(self):
        main_layout = QtWidgets.QVBoxLayout()

    def create_shaders(self):
        cmds.shadingNode('lambert', asShader=True, n='MI_BlueButton')

def populate_shader_dict():
    color_list = rand_color()
    shader_dict = {}
    shader_dict = {'MI_' + mat: color for mat, color in zip(mat_list, color_list)}
    print(shader_dict)
    
def rand_color():
    # use HSV to get distinct colors
    hsv_colors = [(i/len(mat_list), 1, 1) for i in range(len(mat_list))]

    # convert HSV to RGB
    rgb_colors = [colorsys.hsv_to_rgb(*hsv) for hsv in hsv_colors]
    return rgb_colors


# ui = MaterialUI()
# ui.show()
def create_shaders():
    cmds.shadingNode('lambert', asShader=True, n='MI_BlueButton', shared=True, ss=True)
    cmds.setAttr('MI_BlueButton.color', 85/255, 107/255, 47/255)       

populate_shader_dict()


