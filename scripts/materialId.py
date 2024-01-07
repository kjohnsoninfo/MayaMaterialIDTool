import colorsys 
import fnmatch
import random

import maya.OpenMayaUI as omui
import maya.cmds as cmds 
from PySide2 import QtCore, QtWidgets
from shiboken2 import wrapInstance

# Custom UI class and functions
class ResizableButton(QtWidgets.QPushButton):
    def sizeHint(self):
        if self.layout():
            # if btn has layout, return sizeHint so it sizes based on contents
            return self.layout().sizeHint()
        # no layout set, return default sizeHint
        return super().sizeHint()

class NoEmptyStringDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, window_name='', label='Material Name'):
        super(NoEmptyStringDialog, self).__init__(parent)

        self.dialog_box = QtWidgets.QDialog()
        self.dialog_box.setWindowTitle(window_name)
        self.dialog_box.setObjectName('NoEmptyStringDialog')

        self.mat_name = QtWidgets.QLineEdit()
        self.error_msg = QtWidgets.QLabel()

        btn_box = QtWidgets.QDialogButtonBox()
        btn_box.setStandardButtons((QtWidgets.QDialogButtonBox.Cancel 
                                      | QtWidgets.QDialogButtonBox.Ok))
        self.btn_accept = btn_box.button(QtWidgets.QDialogButtonBox.Ok)

        self.btn_accept.setEnabled(False)

        layout = QtWidgets.QFormLayout(self.dialog_box)
        layout.addRow(label, self.mat_name)
        layout.addRow(self.error_msg)
        layout.addWidget(btn_box)

        self.mat_name.textChanged.connect(self.on_text_changed)
        btn_box.accepted.connect(self.dialog_box.accept)
        btn_box.rejected.connect(self.dialog_box.reject)

        self.dialog_box.deleteLater()

    def get_mat_name(self):
        if self.dialog_box.exec_():
            # print(self.mat_name.text())
            return self.mat_name.text()
    
    def on_text_changed(self, text):
        if not text:
            self.btn_accept.setEnabled(False)
        else:
            self.btn_accept.setEnabled(True)

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
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose) # Ensures cleanup

        self.settings = QtCore.QSettings('KYBER', 'MaterialIDGenerator')
        self.mat_list = self.create_material_list()
        max_col = self.load_column_settings()

        self.create_shaders()
        self.close_window_if_exists()
        self.create_ui(max_col)
    
    # Material file functions
    def no_mat_path_popup(self):
        msg = QtWidgets.QMessageBox(self)
        msg.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        msg.setWindowTitle('Material ID File Path Installation')
        msg.setObjectName('NoMatPathPopup')

        msg.setText(('The script needs a reference to a pregenerated '  
                     'Material ID text file.\n\n' 
                     'Press OK to select a .txt file.\n\n'
                     'NOTE: This file path will be saved and you should only '
                     'see this message when running the script for the first '
                     'time. The path can be changed in the options menu at '
                     'any time.'))
        msg.setStandardButtons(msg.Ok | msg.Cancel)

        msg_return = msg.exec()
        if msg_return == msg.Ok:
            return True
        else:
            raise Exception(('No Material ID File path was specified. Please '
                             'rerun and select a text file.'))
        
    def load_material_path(self):
        settings = self.settings
        
        # Get path if it already exists
        if settings.contains('matListPath'):
            mat_path = settings.value('matListPath')
        
        # Ask user for path if does not exist
        else:
            msg_return = self.no_mat_path_popup()
            if msg_return is True:
                choose_file = QtWidgets.QFileDialog.getOpenFileName(
                    self, 'Choose File', filter="*.txt")
                mat_path = choose_file[0]

                # If file is selected, save path. If canceled, alert user. 
                if mat_path:
                    settings.setValue('matListPath', mat_path)
                else:
                    raise Exception(('No Material ID File path was specified. ' 
                                    'Please rerun and select a text file.'))
        
        return mat_path

    def create_material_list(self):
        mat_path = self.load_material_path()
        with open(mat_path, 'r') as mat_file:
            mat_list = mat_file.read().splitlines()
        return mat_list

    def update_mat_file(self):
        choose_file = QtWidgets.QFileDialog.getOpenFileName(self, 'Choose File')
        mat_path = choose_file[0]
        settings = self.settings

        if mat_path:
            self.close_window_if_exists()
            settings.setValue('matListPath', mat_path)
            ui = MaterialUI()
            ui.show()
        
    # Shader creation methods
    def rand_color(self):
        # comment out seed line to randomize palette on every run 
        # or change the seed to get different color palettes
        random.seed(80)

        # use HSV to get distinct colors
        color_list = [i/len(self.mat_list) for i in range(len(self.mat_list))]
        hsv_colors = [(random.choice(color_list), 1, random.random()) 
                      for i in range(len(self.mat_list))]

        # convert HSV to RGB
        rgb_colors = [colorsys.hsv_to_rgb(*hsv) for hsv in hsv_colors]
        return rgb_colors

    def populate_shader_dict(self):
        color_list = self.rand_color()
        shader_dict = {mat: color for mat, color in zip(self.mat_list, color_list)}
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
    def apply_mat(self, btn):
        mat_name = btn.findChild(QtWidgets.QLabel).text()
        cmds.hyperShade(a=mat_name)

    def reset_mat(self):
        cmds.hyperShade(a='lambert1')

    def select_obj(self, btn):
        mat_name = btn.findChild(QtWidgets.QLabel).text()
        cmds.hyperShade(o=mat_name)

    def add_new_mat(self):        
        # Get user input within popup UI
        dlg = NoEmptyStringDialog(self, 'Add New Material', 
                                  'New Material Name:')

        def exists_error(text):
            if text in self.mat_list:
                dlg.error_msg.setText('Material already exists!')
                dlg.btn_accept.setEnabled(False)
            if text and text not in self.mat_list:
                dlg.error_msg.setText('')
                dlg.btn_accept.setEnabled(True)
        
        dlg.mat_name.textChanged.connect(exists_error)
        new_mat = dlg.get_mat_name()
        # Add new material to txt file
        if new_mat:
            with open(self.settings.value('matListPath'), 'a') as mat_file:
                mat_file.write('\n' + new_mat)

            # Rerun main UI with new material added
            added = False
            with open(self.settings.value('matListPath'), 'r') as mat_file:
                if new_mat in mat_file:
                    added = True
            if added:
                self.close_window_if_exists()          
                ui = MaterialUI()
                ui.show()

    def delete_mat(self):
        # Get user input within popup UI
        dlg = NoEmptyStringDialog(self, 'Delete Material', 
                                  'Material to Delete:')
        
        def not_exists_error(text):
            if text not in self.mat_list:
                dlg.error_msg.setText('Material name does not exist!')
                dlg.btn_accept.setEnabled(False)
            if text in self.mat_list:
                dlg.error_msg.setText('')
                dlg.btn_accept.setEnabled(True)
        
        dlg.mat_name.textChanged.connect(not_exists_error)
        mat_to_del = dlg.get_mat_name()
        
        if mat_to_del:
            corr_lines = []

            with open(self.settings.value('matListPath'), 'r+') as mat_input:
                lines = mat_input.readlines()

            # Delete material from txt file
            with open(self.settings.value('matListPath'), 'w') as mat_output:
                for line in lines:
                    if line.strip('\n') != mat_to_del:
                        corr_lines.append(line)
                
                # Remove extra empty line if deleted name is at end of file
                # Empty lines will break shader creation
                for i in range(len(corr_lines)):
                    if i == len(corr_lines)-1:
                        corr_lines[i] = corr_lines[i].strip('\n')
                
                for name in corr_lines:
                    mat_output.write(name)
          
            # Delete material from Maya
            cmds.delete(mat_to_del)
            cmds.delete(mat_to_del + 'SG')

            # Rerun main UI with material deleted
            deleted = False
            with open(self.settings.value('matListPath'), 'r') as mat_file:
                if mat_to_del not in mat_file:
                    deleted = True

            if deleted:
                self.close_window_if_exists()
                ui = MaterialUI()
                ui.show()

    # Custom shader button mouse events
    def eventFilter(self, QObject, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            if event.button() == QtCore.Qt.RightButton:
                clicked_button = QObject
                self.select_obj(clicked_button)
            if event.button() == QtCore.Qt.LeftButton:
                if event.modifiers() == QtCore.Qt.ShiftModifier:
                    clicked_button = QObject
                    self.select_obj(clicked_button)
                else:
                    clicked_button = QObject
                    self.apply_mat(clicked_button)
        return False
           
    # Custom column methods
    def get_column_input(self):
        settings = self.settings
        col_input, ok = QtWidgets.QInputDialog.getInt(
            self, 'Change Button Columns', 'Number of Button Columns:',
            settings.value('numOfColumns'), 1, 20, 1
            )
        
        if ok:
            settings.setValue('numOfColumns', col_input)
            self.close_window_if_exists()
            ui = MaterialUI()
            ui.show()

    def load_column_settings(self):
        settings = self.settings
        if settings.contains('numOfColumns'):
            max_col = settings.value('numOfColumns')
        else:
            max_col = 2 # default numOfColumns
        return max_col

    # Help menu methods
    def info_popup(self):
        msg = QtWidgets.QMessageBox(self)
        msg.setWindowTitle('Material Info')
        msg.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        msg.setModal(False)

        settings = self.settings
        mat_path_text = ('Material ID File Path:' + 
                         settings.value('matListPath') + '\n\n')
        mat_list_text = 'Material List:\n' + str(self.mat_list)
        msg.setText(mat_path_text + mat_list_text)
        msg.show()

    # UI window methods
    def close_window_if_exists(self):
        if QtWidgets.QApplication.instance():
            for window in (QtWidgets.QApplication.allWindows()):
                if 'MaterialIdUI' in window.objectName():
                    window.close()

    def create_ui(self, max_col):
        main_layout = QtWidgets.QVBoxLayout()
        
        # Menu bar
        menu_bar = QtWidgets.QMenuBar()
        about_menu = menu_bar.addMenu('About')
        mat_info = QtWidgets.QAction('Show Material Info',
                                             menu_bar)
        mat_info.triggered.connect(self.info_popup)
        about_menu.addAction(mat_info)

        options_menu = menu_bar.addMenu('Options')
        change_num_col = QtWidgets.QAction('Change Number of Columns',
                                           menu_bar)
        change_mat_path = QtWidgets.QAction('Change Material ID File Path',
                                    menu_bar)
        change_num_col.triggered.connect(self.get_column_input)
        change_mat_path.triggered.connect(self.update_mat_file)
        options_menu.addAction(change_num_col)
        options_menu.addAction(change_mat_path)

        # Independent tools
        func_hbox = QtWidgets.QHBoxLayout()
        
        reset_btn = QtWidgets.QPushButton('Reset Material')
        add_btn = QtWidgets.QPushButton('Add New Material')
        delete_btn = QtWidgets.QPushButton('Delete Material')

        reset_btn.clicked.connect(self.reset_mat)
        add_btn.clicked.connect(self.add_new_mat)
        delete_btn.clicked.connect(self.delete_mat)

        func_hbox.addWidget(reset_btn)
        func_hbox.addWidget(add_btn)
        func_hbox.addWidget(delete_btn)

        # Shader scroll area and widgets
        # The maya port requires a window with a layout
        tempwin = cmds.window()
        cmds.columnLayout()
        
        grid_layout = QtWidgets.QGridLayout()
        scroll_area = QtWidgets.QScrollArea()
        shader_widget = QtWidgets.QWidget()
        row = 0
        col = 0

        # Create all shader buttons
        for mat in self.mat_list:
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
            shader_btn.installEventFilter(self)
            shader_btn.setStatusTip('Left Click to Apply Material, ' 
                                    'Right Click to Select Objects...')
            shader_label = QtWidgets.QLabel(mat)

            # Add horizontal layout and port to button
            shader_hbox = QtWidgets.QHBoxLayout()
            widget.setLayout(shader_hbox)
            shader_btn.setLayout(shader_hbox)

            shader_hbox.addWidget(qport, alignment=QtCore.Qt.AlignLeft)
            shader_hbox.addWidget(shader_label, 
                                  alignment=QtCore.Qt.AlignCenter)

            grid_layout.addWidget(shader_btn, row, col)

            col += 1

        # Delete temp window after ports created
        cmds.deleteUI(tempwin)

        # Set shader area main layouts
        shader_widget.setLayout(grid_layout)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(shader_widget)
        
        main_layout.addWidget(menu_bar)
        main_layout.addLayout(func_hbox)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)
    
if __name__ == "__main__":
    ui = MaterialUI()
    ui.show()
