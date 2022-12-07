from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication, QDialog, QTableWidget, QMessageBox, QComboBox, QCheckBox, QSystemTrayIcon, QMenu, QAction
)
from PyQt5.QtCore import Qt
import sys

from qt_material import apply_stylesheet,list_themes
from hm3u8dl_gui import Ui_hm3u8dl_gui


class Hm3u8dl_gui(Ui_hm3u8dl_gui,QDialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(lambda :self.logic_UI('change_theme'))

        # self.setWindowFlags(Qt.WindowStaysOnTopHint) # 置顶
        # self.setWindowFlags(Qt.Widget)  # 取消置顶
        # self 定义变量

        # 界面的设置

        self.show()


        # logic UI
    def logic_UI(self,type):
        if type == 'change_theme':
            # apply_stylesheet(app, theme='default')
            print(list_themes())
    # logic run



if __name__ == '__main__':
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='default')
    hm3u8dl_gui = Hm3u8dl_gui()
    sys.exit(app.exec())