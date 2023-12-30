import random
import colorsys 
import fnmatch

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

# Main UI class and functions
def main_window():
    window_int = omui.MQtUtil.mainWindow()
    return wrapInstance(int(window_int), QtWidgets.QWidget)

class MaterialUI(QtWidgets.QDialog):
    def __init__(self, parent=main_window()):
        super(MaterialUI, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Window)
        self.setObjectName('MaterialIdUI')
        self.setWindowTitle('Material ID Generator')
        self.resize(400, 400)

        self.settings = QtCore.QSettings('KYBER', 'MaterialIDGenerator')
        max_col = self.load_column_settings()

        self.create_shaders()
        self.check_window_exists()
        self.create_ui(max_col)

    # Shader creation methods
    def rand_color(self):
        # comment out seed line to randomize palette on every run 
        # or change the seed to get different color palettes
        random.seed(80)

        # use HSV to get distinct colors
        color_list = [i/len(mat_list) for i in range(len(mat_list))]
        hsv_colors = [(random.choice(color_list), 1, random.random()) 
                      for i in range(len(mat_list))]

        # convert HSV to RGB
        rgb_colors = [colorsys.hsv_to_rgb(*hsv) for hsv in hsv_colors]
        return rgb_colors

    def populate_shader_dict(self):
        color_list = self.rand_color()
        shader_dict = {mat: color for mat, color in zip(mat_list, color_list)}
        return shader_dict

    def create_shaders(self):
        shader_dict = self.populate_shader_dict()
        for name, color in shader_dict.items():
            mat = cmds.shadingNode('lambert', asShader=True, n=name, 
                                   shared=True, ss=True)
            cmds.setAttr(name + '.color', *color)

            # Create shader groups only if they do not exist
            sg_list = cmds.ls(type='shadingEngine')
            sg_filter = fnmatch.filter(sg_list, f'{name}*')
            if len(sg_filter) == 0:
                sg = cmds.sets(n=name + 'SG', em=True, r=True, nss=True)
                cmds.connectAttr(mat + '.outColor', sg + '.surfaceShader',
                                 f=True)
            
    # Shader manipulation methods
    def apply_mat(self):
        clicked_button = self.sender()
        mat_name = clicked_button.findChild(QtWidgets.QLabel).text()
        cmds.hyperShade(a=mat_name)

    def reset_mat(self):
        cmds.hyperShade(a='lambert1')
    
    # Custom column methods
    def get_column_input(self):
        # Close main ui in order to refresh button layout
        if QtWidgets.QApplication.instance():
            for window in (QtWidgets.QApplication.allWindows()):
                if 'MaterialIdUI' in window.objectName():
                    window.close()
        
        settings = self.settings
        col_input, ok = QtWidgets.QInputDialog.getInt(
            self, 'Change Button Columns', 'Number of Button Columns:',
            settings.value('numOfColumns'), 1, 20, 1
            )
        
        if ok:
            settings.setValue('numOfColumns', col_input)

            # Reopen main ui with new settings
            ui = MaterialUI()
            ui.show()
        else:
            # Reopen main ui without changes
            ui = MaterialUI()
            ui.show()

    def load_column_settings(self):
        settings = self.settings
        if settings.contains('numOfColumns'):
            max_col = settings.value('numOfColumns')
        else:
            max_col = 2 # default numOfColumns
        return max_col

    # UI window methods
    # Prevent window duplication
    def check_window_exists(self):
        if QtWidgets.QApplication.instance():
            for window in (QtWidgets.QApplication.allWindows()):
                if 'MaterialIdUI' in window.objectName():
                    window.close()

    def create_ui(self, max_col):
        main_layout = QtWidgets.QVBoxLayout()
        
        # Menu bar
        menu_bar = QtWidgets.QMenuBar()
        options_menu = menu_bar.addMenu("Options")
        change_num_col = QtWidgets.QAction('Change Number of Columns',
                                           menu_bar)
        change_num_col.triggered.connect(self.get_column_input)
        options_menu.addAction(change_num_col)
        
        # Independent tools
        func_hbox = QtWidgets.QHBoxLayout()
        reset_btn = QtWidgets.QPushButton('Reset Material')
        reset_btn.clicked.connect(self.reset_mat)

        func_hbox.addWidget(reset_btn)

        # Shader scroll area and widgets
        # The maya port requires a window with a layout
        tempwin = cmds.window()
        cmds.columnLayout()
        
        self.grid_layout = QtWidgets.QGridLayout()
        scroll_area = QtWidgets.QScrollArea()
        shader_widget = QtWidgets.QWidget()
        row = 0
        col = 0

        # Create all shader buttons
        for mat in mat_list:
            if col == max_col:
                col = 0
                row += 1

            swatch = cmds.swatchDisplayPort(rs=32, wh=(32, 32), sn=mat)

            # Wrap port in a QtWidget 
            port = omui.MQtUtil.findControl(swatch)
            qport = wrapInstance(int(port), QtWidgets.QWidget)
            widget = QtWidgets.QWidget()
            qport.setParent(widget)

            # Initialize button and label
            shader_btn = ResizableButton()
            shader_btn.clicked.connect(self.apply_mat)
            shader_label = QtWidgets.QLabel(mat)

            # Add horizontal layout and port to button
            shader_hbox = QtWidgets.QHBoxLayout()
            widget.setLayout(shader_hbox)
            shader_btn.setLayout(shader_hbox)

            shader_hbox.addWidget(qport, alignment=QtCore.Qt.AlignLeft)
            shader_hbox.addWidget(shader_label, 
                                  alignment=QtCore.Qt.AlignCenter)

            self.grid_layout.addWidget(shader_btn, row, col)

            col += 1

        # Delete temp window after ports created
        cmds.deleteUI(tempwin)

        # Set shader area main layouts
        shader_widget.setLayout(self.grid_layout)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(shader_widget)
        
        main_layout.addWidget(menu_bar)
        main_layout.addLayout(func_hbox)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)
    
if __name__ == "__main__":
    ui = MaterialUI()
    ui.show()
