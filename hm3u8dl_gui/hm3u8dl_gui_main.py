import json
import os
import sys
import time

import requests
from PyQt6.QtWidgets import (
    QApplication, QDialog,QMessageBox
)
from PyQt6.QtCore import QThread, QMutex, pyqtSignal
from hm3u8dl_gui import Ui_hm3u8dl_gui

import hm3u8dl_cli
import hm3u8dl_ServerCilent

# 实例化线程锁对象
mutex = QMutex()

DATA = {}

class MyHm3u8dlGui(Ui_hm3u8dl_gui, QDialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.show()

        # faskApi 线程
        self.work_fastApi = WorkThread_fastApi()
        self.work_postData = WorkThread_postData()

        # 逻辑
        self.fastApiLoad()

        self.lineEdit_verison.setText(hm3u8dl_cli.version.version)
        self.lineEdit_workDir.setText(os.getcwd() + r'\Downloads')

        self.pushButton_start.clicked.connect(self.pushButton_start_clicked)

    # 函数
    def display_postData(self, str):
        # 由于自定义信号时自动传递一个字符串参数，所以在这个槽函数中要接受一个参数
        self.lineEdit_data.setText(str)

    def fastApiLoad(self):
        self.work_fastApi.start()
        # 线程自定义信号连接的槽函数
        self.work_fastApi.trigger.connect(self.display_postData)

    def pushButton_start_clicked(self):
        global DATA

        DATA = {
            'm3u8url': self.lineEdit_m3u8url.text(),
            'title': self.lineEdit_title.text() if self.lineEdit_title.text() else None,
            'method': self.comboBox_key.currentText() if self.comboBox_key.currentText() != 'None' else None,
            'key': self.lineEdit_key.text() if self.lineEdit_key.text() else None,
            'iv': self.lineEdit_iv.text() if self.lineEdit_iv.text() else None,
            'nonce': self.lineEdit_nonce.text() if self.lineEdit_nonce.text() else None,
            'enable_del': self.checkBox_enableDel.isChecked(),
            'merge_mode': int(self.comboBox_mergeMode.currentText()),
            'base_uri': self.lineEdit_baseurl.text() if self.lineEdit_baseurl.text() else None,
            'threads': int(self.lineEdit_thread.text()),
            'headers': self.lineEdit_headers.text() if self.lineEdit_headers.text() else {},
            'work_dir': self.lineEdit_workDir.text() if self.lineEdit_workDir.text() else './Downloads',
            'proxy': self.lineEdit_proxy.text() if self.lineEdit_proxy.text() else None
        }
        DATA['work_dir'] = DATA['work_dir'].replace('\\','/')
        if DATA['m3u8url'] == '':
            QMessageBox.warning(self,'','m3u8url为必填项')
            return

        self.work_postData.start()
        # 线程自定义信号连接的槽函数
        self.work_postData.trigger.connect(self.display_postData)

        # res = requests.post("http://127.0.0.1:8000/info", json=DATA)
        # print(res.json())


class WorkThread_fastApi(QThread):
    # 自定义信号对象。参数str就代表这个信号可以传一个字符串
    trigger = pyqtSignal(str)

    def __int__(self):
        # 初始化函数
        super(WorkThread_fastApi, self).__init__()

    def run(self):
        # 重写线程执行的run函数
        # 触发自定义信号
        # config =
        # self.trigger.emit(str(i))
        hm3u8dl_ServerCilent.run()
        # sum = 0
        #
        # for i in range(100000):
        #     sum += i
        #     # 通过自定义信号把待显示的字符串传递给槽函数
        #     self.trigger.emit(str(i))


class WorkThread_postData(QThread):
    # 自定义信号对象。参数str就代表这个信号可以传一个字符串
    trigger = pyqtSignal(str)

    def __int__(self):
        # 初始化函数
        super(WorkThread_postData, self).__init__()

    def run(self):
        # 重写线程执行的run函数
        # 触发自定义信号
        res = requests.post("http://127.0.0.1:8000/info", json=DATA)
        # print(res.json())
        # self.trigger.emit(str(data))

        # sum = 0
        #
        # for i in range(100000):
        #     sum += i
        #     # 通过自定义信号把待显示的字符串传递给槽函数
        #     self.trigger.emit(str(i))


if __name__ == '__main__':
    app = QApplication(sys.argv)

    myhm3u8dl_gui = MyHm3u8dlGui()

    sys.exit(app.exec())
