import random
import colorsys 

import maya.OpenMayaUI as omui
import maya.cmds as cmds 
from PySide2 import QtCore, QtWidgets
from shiboken2 import wrapInstance

# Initial Materials 
mat_list = ['BlueButton', 'BlueButtonOFF', 'BlueLight', 'Catwalk01',
            'Chrome', 'Concrete', 'ControlPanelBlack', 'ControlPanelGrey', 
            'DarkBlueButton', 'FoilAluminum', 'GeneratorPulse', 'GreenLight',
            'HangerFloor', 'Hologram01', 'Hologram02', 'ImpBoxBlue', 
            'ImpBoxBlue02', 'ImpBoxRed', 'ImpBoxRed02', 'ImpGrid', 
            'ImpGridRed', 'ImpTrimDetails01', 'KejimRock01', 
            'Landscape_Kejim','OrangeButton', 'PipeMetalBlack', 
            'PipeMetalGrey', 'PipeMetalImpGrey', 'PipeMetalRed', 'RedButton', 
            'RedButtonOFF', 'RedLight', 'RoughMetal', 'RubberFloor', 
            'StripesPipe', 'StripesPipePOM', 'Trim01POM', 'WallGrid01', 
            'WhiteButton', 'WhiteButtonOFF']

# Custom UI class and functions
class ResizableButton(QtWidgets.QPushButton):
    def sizeHint(self):
        if self.layout():
            # if btn has layout, return sizeHint so it sizes based on contents
            return self.layout().sizeHint()
        # no layout set, return default sizeHint
        return super().sizeHint()

def main_window():
    window_int = omui.MQtUtil.mainWindow()
    return wrapInstance(int(window_int), QtWidgets.QWidget)

# UI Class
class MaterialUI(QtWidgets.QDialog):
    def __init__(self, parent=main_window()):
        super(MaterialUI, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setObjectName('MaterialIdUI')
        self.setWindowTitle('Material ID Generator')
        self.setGeometry(1450, 350, 400, 400)

        self.create_shaders()
        self.check_window_exists()
        self.create_ui()

    # prevent window duplication
    def check_window_exists(self):
        if QtWidgets.QApplication.instance():
            for window in (QtWidgets.QApplication.allWindows()):
                if 'MaterialIdUI' in window.objectName():
                    window.close()

    def create_shaders(self):
        shader_dict = self.populate_shader_dict()
        for name, color in shader_dict.items():
            cmds.shadingNode('lambert', asShader=True, n=name, shared=True, ss=True)
            cmds.setAttr(name + '.color', *color)

    def create_ui(self):
        main_layout = QtWidgets.QVBoxLayout()

        # Independent tools
        tool_hbox = QtWidgets.QHBoxLayout()
        remove_btn = QtWidgets.QPushButton('Remove Material')

        tool_hbox.addWidget(remove_btn)

        # The shader port requires a window with a layout
        tempwin = cmds.window()
        cmds.columnLayout()
        
        # Initialize shader area layouts and variables
        grid_layout = QtWidgets.QGridLayout()
        scroll_area = QtWidgets.QScrollArea()
        shader_widget = QtWidgets.QWidget()
        row = 0
        col = 0

        # Create all shader buttons
        for mat in mat_list:
            if col == 2:
                col = 0
                row += 1

            swatch = cmds.swatchDisplayPort(rs=32, wh=(32, 32), sn=mat)

            # Wrap port in a QtWidget 
            port = omui.MQtUtil.findControl(swatch)
            qport = wrapInstance(int(port), QtWidgets.QWidget)
            widget = QtWidgets.QWidget()
            qport.setParent(widget)

            # Initialize button with horizontal layout and add port to btn
            shader_btn = ResizableButton()
            shader_hbox = QtWidgets.QHBoxLayout()
            widget.setLayout(shader_hbox)
            shader_btn.setLayout(shader_hbox)

            label = QtWidgets.QLabel(mat)

            shader_hbox.addWidget(qport, alignment=QtCore.Qt.AlignLeft)
            shader_hbox.addWidget(label, alignment=QtCore.Qt.AlignCenter)

            grid_layout.addWidget(shader_btn, row, col)

            col += 1

        # Delete temp window after ports created
        cmds.deleteUI(tempwin)

        # Set main layouts
        shader_widget.setLayout(grid_layout)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(shader_widget)

        main_layout.addLayout(tool_hbox)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)
    
    def rand_color(self):
        # comment out seed line to randomize palette on every run or
        # change the seed to get different color palettes
        random.seed(80)

        # use HSV to get distinct colors
        color_list = [i/len(mat_list) for i in range(len(mat_list))]
        hsv_colors = [(random.choice(color_list), 1, random.random()) for i in range(len(mat_list))]

        # convert HSV to RGB
        rgb_colors = [colorsys.hsv_to_rgb(*hsv) for hsv in hsv_colors]
        return rgb_colors

    def populate_shader_dict(self):
        color_list = self.rand_color()
        shader_dict = {mat: color for mat, color in zip(mat_list, color_list)}
        return shader_dict

ui = MaterialUI()
ui.show()
