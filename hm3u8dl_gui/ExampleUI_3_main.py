# coding=utf-8
import json
import re, sys, os, subprocess
import time
import webbrowser
from multiprocessing import cpu_count
from queue import Queue
import requests
from PyQt5 import QtGui
from PyQt5.QtGui import QIcon
from urllib3.util import parse_url
from webbrowser import open_new_tab

from PyQt5.QtCore import (
    QThread, pyqtSignal, Qt, QSize
)
from PyQt5.QtWidgets import (
    QApplication, QDialog, QTabBar, QMessageBox, QFileDialog, QWidget,
    QListWidgetItem, QSystemTrayIcon, QMenu, QAction, qApp
)

from hm3u8dl_cli import merge, m3u8download, util, SeverClient,version,M3U8InfoObj
from ExampleUI_3 import Ui_ExampleUI_3
from ProcessBar_Widget import Ui_ProcessBar_Widget

q = Queue(1000)  # 最大同时队列量
is_downloading = False


class ExampleUI_3(Ui_ExampleUI_3, QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, )  # 去除标题框
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # 设置窗口透明
        self.addSystemTray()  # 最小化到托盘

        self.setupUi(self)

        # self.setFixedSize(self.width(), self.height())  # 禁止拉长
        # server 启动
        self.worker_server = Server()
        self.worker_server.start()
        # 界面的设置
        self.start_x = None
        self.start_y = None

        self.tabBar = self.tabWidget.findChild(QTabBar)
        self.tabBar.hide()
        self.is_pin = False

        if sys.argv[0].endswith('exe'):
            basePath = os.path.dirname(os.path.realpath(sys.argv[0])).replace('\\', '/')  # 当前路径
        else:
            basePath = '/'.join(os.path.realpath(__file__).split('\\')[:-1])  # python 安装包使用
        workDir = basePath + '/Downloads'
        if not os.path.exists(workDir):
            os.makedirs(workDir)

        self.lineEdit_workDir.setText(workDir)
        self.label_version.setText(version) # 设置版本号


        self.pushButton_close.clicked.connect(self.close)
        # self.pushButton_max.clicked.connect(self.max_normal)
        self.pushButton_min.clicked.connect(self.showMinimized)

        self.tabBar = self.tabWidget.findChild(QTabBar)
        self.tabBar.hide()
        self.listWidget_leftWidget.clicked.connect(lambda: self.logic_run_UI('leftWidget_clicked'))
        self.pushButton_toTools2.clicked.connect(lambda: self.logic_run_UI('toTools2_clicked'))  # tools 多窗口切换
        self.pushButton_toTools1.clicked.connect(lambda: self.logic_run_UI('toTools1_clicked'))
        self.pushButton_pin.clicked.connect(lambda: self.logic_run_UI('pushButton_pin_clicked'))  # 窗口置顶

        self.lineEdit_threadNumber.setText(str(cpu_count()))  # 线程数
        if self.checkBox_checkUpdateWhenStart.isChecked():
            self.logic_run_UI('checkUpdate')
        self.pushButton_checkUpdate.clicked.connect(lambda: self.logic_run_UI('checkUpdate'))  # 检查更新
        self.pushButton_feedback.clicked.connect(lambda: self.logic_run_UI('feedback'))  # 问题反馈

        self.pushButton_videoAudioMerge_audioFileOpen.clicked.connect(
            lambda: self.logic_run_UI('pushButton_videoAudioMerge_audioFileOpen_clicked'))
        self.pushButton_videoAudioMerge_videoFileOpen.clicked.connect(
            lambda: self.logic_run_UI('pushButton_videoAudioMerge_videoFileOpen_clicked'))
        self.pushButton_workDir.clicked.connect(lambda: self.logic_run_UI('pushButton_workDir_clicked'))
        self.pushButton_videoAudioMerge.clicked.connect(
            lambda: self.logic_run_UI('pushButton_videoAudioMerge_clicked'))  # 音视频合并
        self.pushButton_mergeTsToMp4DirOpen.clicked.connect(
            lambda: self.logic_run_UI('pushButton_mergeTsToMp4DirOpen_clicked'))
        self.pushButton_mergeTsTomp4.clicked.connect(lambda: self.logic_run_UI('pushButton_mergeTsTomp4_clicked'))

        self.lineEdit_search.returnPressed.connect(lambda: self.logic_run_UI('lineEdit_search_returnPressed'))
        self.pushButton_title.clicked.connect(lambda: self.logic_run_UI('pushButton_title_clicked'))  # logo点击
        self.lineEdit_nonce.textChanged.connect(lambda: self.logic_run_UI('lineEdit_nonce_textChanged'))  # CHACHA 使iv为空
        self.comboBox_method.currentIndexChanged.connect(
            lambda: self.logic_run_UI('comboBox_mergerMode_changeEvent'))  # 合并方式
        QApplication.clipboard().changed.connect(lambda: self.logic_run_UI('clipboard_changed'))  # 检测剪切板
        self.lineEdit_m3u8url.textChanged.connect(
            lambda: self.logic_run_UI('lineEdit_m3u8url_textChanged'))  # m3u8url 内容改变
        self.logic_run_UI('clipboard_changed')  # 监控剪切板
        self.pushButton_GO.clicked.connect(lambda: self.logic_run_UI('pushButton_GO_clicked'))

        self.show()

        # self 定义变量

    def mousePressEvent(self, event):
        try:
            super(ExampleUI_3, self).mousePressEvent(event)
            if event.button() == Qt.LeftButton:
                self.start_x = event.x()
                self.start_y = event.y()

        except:
            pass

    def mouseMoveEvent(self, event):
        try:
            super(ExampleUI_3, self).mouseMoveEvent(event)
            dis_x = event.x() - self.start_x
            dis_y = event.y() - self.start_y
            if abs(dis_x) < 30 and abs(dis_y) < 30:  # 可能有问题的写法
                self.move(self.x() + dis_x, self.y() + dis_y)
        except:
            pass

    def addSystemTray(self):

        self.tray = QSystemTrayIcon(self)
        self.icon = QIcon('.png')  # 托盘图标
        self.tray.setIcon(self.icon)
        self.setWindowIcon(self.icon)
        self.tray.activated.connect(self.slot_iconActivated)

        # 右击托盘中图标时弹出的菜单
        self.tray_menu = QMenu(QApplication.desktop())
        self.RestoreAction = QAction(u'还原', self, triggered=self.showNormal)  # 添加一级菜单动作选项(还原主窗口)
        self.QuitAction = QAction(u'退出', self, triggered=qApp.quit)  # 添加一级菜单动作选项(退出程序)
        self.tray_menu.addAction(self.RestoreAction)  # 为菜单添加动作
        self.tray_menu.addAction(self.QuitAction)
        self.tray.setContextMenu(self.tray_menu)  # 设置系统托盘菜单
        self.tray.show()

    def slot_iconActivated(self, reason):
        if QSystemTrayIcon.Trigger == reason:
            self.activateWindow()
            self.showNormal()

        elif QSystemTrayIcon.DoubleClick == reason:
            self.activateWindow()
            self.showNormal()

    def changeEvent(self, event):
        if not event.WindowStateChange:
            QDialog.changeEvent(event)
            return
        if Qt.WindowMinimized == self.windowState():  # 点击“最小化”按钮
            self.hide()  # 在任务栏不显示
            event.ignore()

    # logic
    # logic run
    @util.Util.safeRun
    def logic_run_UI(self, type):
        if type == 'leftWidget_clicked':
            currentRow = self.listWidget_leftWidget.currentIndex().row()
            self.tabWidget.setCurrentIndex(currentRow)
        elif type == 'toTools2_clicked':
            self.stackedWidget.setCurrentIndex(1)
        elif type == 'toTools1_clicked':
            self.stackedWidget.setCurrentIndex(0)
        elif type == 'checkUpdate':
            self.worker = CheckUpdate(self.label_version.text())
            self.worker.start()

            def show_verison(version) -> None:
                if version != self.label_version.text():
                    self.label_version.hide()
                    self.label_currentVersion.setText(f'检测到更新！ v{version}')
                else:
                    QMessageBox.information(self, '更新', f'当前为最新版 v{version}')
                # self.label_version.setText(version)

            self.worker.my_signal.connect(show_verison)
        elif type == 'feedback':
            feedback_url = 'https://github.com/hecoter/hm3u8dl_cli/issues'
            open_new_tab(feedback_url)
        elif type == 'pushButton_videoAudioMerge_audioFileOpen_clicked':
            filepath, filetype = QFileDialog.getOpenFileName(self, '选择文件', os.getcwd(), '')
            if filetype:
                self.lineEdit_videoAudioMerege_audioPath.setText(filepath)
        elif type == 'pushButton_videoAudioMerge_videoFileOpen_clicked':
            filepath, filetype = QFileDialog.getOpenFileName(self, '选择文件', os.getcwd(), '')
            if filetype:
                self.lineEdit_videoAudioMerege_videoPath.setText(filepath)
        elif type == 'pushButton_workDir_clicked':
            filepath = QFileDialog.getExistingDirectory(self, '选择文件夹', os.getcwd())
            if filepath:
                self.lineEdit_workDir.setText(filepath)
        elif type == 'pushButton_videoAudioMerge_clicked':
            status = merge.merge_video_audio(self.lineEdit_videoAudioMerege_videoPath.text(),
                                             self.lineEdit_videoAudioMerege_audioPath.text(),
                                             self.lineEdit_workDir.text() + '/' +
                                             self.lineEdit_videoAudioMerege_videoPath.text().split('/')[-1],
                                             enableDel=False)
            if status:
                QMessageBox.information(self, '提示', '合并完成！')
            else:
                QMessageBox.warning(self, '提示', f'合并失败！')
        elif type == 'pushButton_mergeTsToMp4DirOpen_clicked':
            filepath = QFileDialog.getExistingDirectory(self, '选择文件夹', os.getcwd())
            if filepath:
                self.lineEdit_mergeTsToMp4_dirPath.setText(filepath)
        elif type == 'pushButton_mergeTsTomp4_clicked':
            self.worker = MergeTsTomp4(self.lineEdit_mergeTsToMp4_dirPath.text())
            self.worker.start()

            def get_status(status) -> None:
                if status:
                    QMessageBox.information(self, '提示', '合并完成！')
                else:
                    QMessageBox.warning(self, '提示', '合并失败！')

            self.worker.my_signal.connect(get_status)

        elif type == 'lineEdit_search_returnPressed':
            try:
                searchurl = 'https://github.com/hecoter/hecoter.github.io/discussions?discussions_q=' + self.lineEdit_search.text()
                searchurl = parse_url(searchurl)
                webbrowser.open(searchurl)
            except:
                pass
        elif type == 'pushButton_pin_clicked':
            self.is_pin = not self.is_pin
            if self.is_pin:
                icon6 = QtGui.QIcon()
                icon6.addPixmap(QtGui.QPixmap("imags/pin_after.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                self.pushButton_pin.setIcon(icon6)

            else:
                icon6 = QtGui.QIcon()
                icon6.addPixmap(QtGui.QPixmap("imags/pin.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                self.pushButton_pin.setIcon(icon6)
        elif type == 'pushButton_title_clicked':
            github_url = 'https://github.com/hecoter/hm3u8dl_cli'
            open_new_tab(github_url)
        elif type == 'lineEdit_nonce_textChanged':
            if self.lineEdit_nonce != '':
                self.comboBox_method.setCurrentText('CHACHA')
                self.lineEdit_iv.setEnabled(False)
        elif type == 'comboBox_mergerMode_changeEvent':
            if self.comboBox_method.currentText() == 'CHACHA' or self.comboBox_method.currentText() == 'AES-128-ECB':
                self.lineEdit_iv.setEnabled(False)
            else:
                self.lineEdit_iv.setEnabled(True)
        elif type == 'clipboard_changed':
            if '.m3u8' in QApplication.clipboard().text():
                self.lineEdit_m3u8url.setText(QApplication.clipboard().text())
        elif type == 'lineEdit_m3u8url_textChanged':
            if self.lineEdit_title.text() == '':
                title = util.Util.guessTitle(self.lineEdit_m3u8url.text())
                self.lineEdit_title.setText(title)
        elif type == 'pushButton_GO_clicked':

            # 构造M3u8InfoObj对象
            m3u8InfoObj = M3U8InfoObj()
            m3u8InfoObj.m3u8url = self.lineEdit_m3u8url.text()
            if not m3u8InfoObj.m3u8url:
                QMessageBox.warning(self, '警告', 'm3u8链接为必填项')
                return
            m3u8InfoObj.title = self.lineEdit_title.text() if self.lineEdit_title.text() else None
            m3u8InfoObj.method = self.comboBox_method.currentText() if self.comboBox_method.currentText() != 'None' else None
            m3u8InfoObj.key = self.lineEdit_key.text() if self.lineEdit_key.text() else None
            m3u8InfoObj.iv = self.lineEdit_iv.text() if self.lineEdit_iv.text() else None
            m3u8InfoObj.nonce = self.lineEdit_nonce.text() if self.lineEdit_nonce.text() else None
            m3u8InfoObj.enable_del = self.checkBox_enable_del.isChecked()
            m3u8InfoObj.merge_mode = self.comboBox_mergerMode.currentIndex() + 1
            m3u8InfoObj.base_uri = self.lineEdit_base_uri.text() if self.lineEdit_base_uri.text() else None

            try:
                if self.lineEdit_headers.text():
                    m3u8InfoObj.headers = json.loads(self.lineEdit_headers.text())
                else:
                    m3u8InfoObj.headers = None
            except:
                QMessageBox.warning(self, '提示', '请求头应为字典格式，例如：{"refer":"http://test.com","cookie":""}')
            m3u8InfoObj.work_dir = self.lineEdit_workDir.text() if self.lineEdit_workDir.text() else None
            try:
                if self.lineEdit_proxy.text():
                    m3u8InfoObj.proxy = json.loads(self.lineEdit_proxy.text())
                else:
                    m3u8InfoObj.proxy = None
            except:
                QMessageBox.warning(self, '提示',
                                    '代理应为字典格式，例如：{"https":"127.0.0.1:8888","http":"127.0.0.1:8888"}')
            m3u8InfoObj.threads = int(self.lineEdit_threadNumber.text()) if self.lineEdit_threadNumber.text() else None
            m3u8InfoObj.server = True
            m3u8InfoObj.server_id = int(time.time() * 1000)

            if not is_downloading:
                test = add_widget(m3u8InfoObj)
                a = QListWidgetItem()
                a.setSizeHint(QSize(511, 140))
                self.listWidget.addItem(a)
                self.listWidget.setItemWidget(a, test)
                # self.listWidget_leftWidget.setCurrentIndex(2)
                self.tabWidget.setCurrentIndex(2)
            else:
                QMessageBox.warning(self, '提示',
                                    '当前仅支持单个任务下载')

    @util.Util.safeRun
    def logic_run(self, type):
        pass


class CheckUpdate(QThread):
    my_signal = pyqtSignal(str)  # 发送信号的数据类型

    def __init__(self, nowVersion):
        super().__init__()
        self.nowVersion = nowVersion

    def run(self) -> None:
        """
        在这里写逻辑
        """
        try:
            url = 'https://ghproxy.com/https://raw.githubusercontent.com/hecoter/hm3u8dl_cli/main/hm3u8dl_cli/version.py'
            response = requests.get(url).text
            version0 = re.findall("version = '(.+?)'", response)[0]
            version = int(version0.replace('.', ''))

            nowVersion = int(self.nowVersion.replace('.', ''))

            if version > nowVersion:
                result = f'{version0}'
            else:
                result = self.nowVersion
        except:
            result = '0.0.0'

        print(result)
        self.my_signal.emit(result)


class MergeTsTomp4(QThread):
    my_signal = pyqtSignal(bool)  # 发送信号的数据类型

    @util.Util.safeRun
    def __init__(self, mergeDir):
        super().__init__()
        self.mergeDir = mergeDir

    @util.Util.safeRun
    def run(self) -> None:
        """
        在这里写逻辑
        """
        file_list = []

        for root, dirs, files in os.walk(self.mergeDir):
            for f in files:
                file = os.path.join(root, f)
                if os.path.isfile(file) and file.endswith('ts'):
                    file_list.append(file)
        with open(self.mergeDir + '/filelist.txt', 'w') as f:
            for i in file_list:
                f.write(f"file '{i}'")
                f.write('\n')
            f.close()
        cmd = f'ffmpeg -f concat -safe 0 -i "{self.mergeDir + "/filelist.txt"}" -c copy "{self.mergeDir + ".mp4"}" -y -loglevel panic'
        subprocess.call(cmd, shell=True)
        if os.path.exists(self.mergeDir + ".mp4"):
            status = True
        else:
            status = False
        self.my_signal.emit(status)


class M3u8download(QThread):
    my_signal = pyqtSignal(str)  # 发送信号的数据类型

    def __init__(self, m3u8InfoObj):
        super().__init__()
        self.m3u8InfoObj = m3u8InfoObj

    def get_info(self):
        while True:
            try:
                response = requests.get('http://127.0.0.1:8000/get_basic_info').json()
                if response != []:
                    # print(response)
                    self.my_signal.emit(response)
                    time.sleep(0.5)
                    # SERVER_ID = []
                    # for res in response:
                    #     SERVER_ID.append(res['server_id'])
                    # index = SERVER_ID.index(self.server_id)
                    # if response[index]['END'] is True:
                    #     break
            except:
                pass

    def run(self):
        """
        在这里写逻辑
        """
        global is_downloading
        is_downloading = True
        if isinstance(self.m3u8InfoObj, util.M3U8InfoObj):
            try:
                m3u8download(self.m3u8InfoObj)
                is_downloading = False
            except Exception as e:
                is_downloading = False
                self.my_signal.emit(str(e))


class add_widget(QWidget, Ui_ProcessBar_Widget):
    def __init__(self, m3u8InfoObj):
        super(add_widget, self).__init__()
        self.setupUi(self)
        # self.show()

        # M3u8download线程启动
        self.worker_M3u8download = M3u8download(m3u8InfoObj)
        self.worker_M3u8download.start()

        # 处理下载错误信息
        def get_error_M3u8download(error):
            QMessageBox.warning(self, '警告', error)

        self.worker_M3u8download.my_signal.connect(get_error_M3u8download)

        self.add_thread = ProcessBarThread(m3u8InfoObj)  # 都在自定义widget里面处理信号
        self.add_thread.my_signal.connect(self.up)
        self.add_thread.start()

    @util.Util.safeRun
    def up(self, basic_info):
        # 更新界面信息
        # self.abab.setText(str(i)) # 我文本框命名是abab
        # self.progressBar.setValue(i*10)
        self.label_videoTitle.setText(basic_info['title'])
        if 'DONE_COUNT' not in basic_info:
            return
        self.progressBar.setValue(int(basic_info['DONE_COUNT'] / basic_info['ALL_COUNT'] * 100))
        self.label_duration.setText(f"{basic_info['durations']}")
        self.label_method.setText(f"{basic_info['method']}")
        all_size = util.Util.sizeFormat((basic_info['DONE_SIZE'] / basic_info['DONE_COUNT']) * basic_info['ALL_COUNT'])
        done_size = util.Util.sizeFormat(basic_info['DONE_SIZE'])
        self.label_doneSize.setText(f"{done_size}/{all_size}")
        end_time = time.time()
        time_start = basic_info['time_start']
        speed = f'{util.Util.sizeFormat(basic_info["DONE_SIZE"] / (end_time - time_start))}/s'
        self.label_speed.setText(speed)
        self.label_bit.setText(basic_info['tsinfo']['tsinfo'])
        image = QtGui.QPixmap(basic_info['tsinfo']['thumbPicPath']).scaled(1182, 1182)
        self.label_thumbPic.setPixmap(image)
        self.label_thumbPic.setScaledContents(True)
        self.server_id.setText(str(basic_info['server_id']))
        if basic_info['DONE_COUNT'] == basic_info['ALL_COUNT'] and basic_info['END'] is False:
            self.server_id.setText('合并中……')
        elif basic_info['END']:
            self.server_id.setText('下载完成！')


class ProcessBarThread(QThread):
    my_signal = pyqtSignal(dict)

    def __init__(self, m3u8InfoObj):
        super(ProcessBarThread, self).__init__()
        self.m3u8InfoObj = m3u8InfoObj

    def get_index(self, server_id):
        try:
            basic_infos = requests.get('http://127.0.0.1:8000/get_basic_info', timeout=1, verify=False).json()
            SERVER_ID = []
            for bi in basic_infos:
                SERVER_ID.append(bi['server_id'])
            if server_id not in SERVER_ID:
                return self.get_index(server_id)
            else:
                index = SERVER_ID.index(server_id)
                return index
        except:
            return self.get_index(server_id)

    def run(self):
        # 逻辑部分
        server_id = self.m3u8InfoObj.server_id
        index = self.get_index(server_id)

        basic_info = requests.get('http://127.0.0.1:8000/get_basic_info', timeout=1, verify=False).json()[index]
        while not basic_info['END']:
            try:
                basic_info = requests.get('http://127.0.0.1:8000/get_basic_info', timeout=1, verify=False).json()[index]
            except:
                pass
            self.my_signal.emit(basic_info)
            time.sleep(0.3)
        basic_info['END'] = True
        self.my_signal.emit(basic_info)


# server
class Server(QThread):
    my_signal = pyqtSignal(str)  # 发送信号的数据类型

    def __init__(self, ):
        super().__init__()

    def run(self):
        SeverClient.run()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    exampleUI_3 = ExampleUI_3()
    sys.exit(app.exec())
