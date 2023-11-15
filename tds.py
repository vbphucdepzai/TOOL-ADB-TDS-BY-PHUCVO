from PIL import Image
from PyQt5 import QtCore, QtGui, QtWidgets 
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QMessageBox
import os
import sys
import time
import json
import requests
from functools import partial
import subprocess
import shutil
import numpy as np
import random
from datetime import datetime
# from By import By
from adbutils import adb
from selenium import webdriver
import threading
from PyQt5.QtWidgets import QMessageBox
timestamp = str(datetime.timestamp(datetime.now())).replace('.', '')
current_folder_count = 0
button = {}
button['follow1'] = Image.open('image/fl1.png')
# Click

class By:
    MA_MAY = "Mã máy"
    TOKEN = "token"
    ID_TIK = "id tiktok"
    TONG_XU = "Tổng xu"
    XU_THEM = "Xu nhận"
    job_dead = "job die"
    TONG_JOB = "Tổng số job làm được"
    TRANG_THAI = "Trạng thái"
    ACTION = "Hành động"
def thatim_random(device_id):
    try:
        dt = adb.device(device_id)
        start_x1 = 1000
        start_y1 = 1024
        dt.click(start_x1, start_y1)

    except Exception as e:
        print('lỗi click:', e)


def luot_video(device_id):
    try:
        dt = adb.device(device_id)
        start_x1 = random.randint(400, 500)
        start_y1 = random.randint(900, 1000)

        # Tọa độ kết thúc (tọa độ 2)
        end_x2 = random.randint(400, 500)
        end_y2 = random.randint(400, 500)

        # Thực hiện vuốt màn hình từ (start_x1, start_y1) đến (end_x2, end_y2)
        dt.shell(
            f"input touchscreen swipe {start_x1} {start_y1} {end_x2} {end_y2} 100")
    except Exception as e:
        print('lỗi vuôt:', e)


def click1(device, x, y):
    subprocess.call(
        f'scrcpy\\adb.exe -s {device} shell input tap {x} {y} ', shell=True)
# Find Image


def find_image(im, tpl):
    im = np.atleast_3d(im)
    tpl = np.atleast_3d(tpl)
    H, W, D = im.shape[:3]
    h, w = tpl.shape[:2]

    sat = im.cumsum(1).cumsum(0)
    tplsum = np.array([tpl[:, :, i].sum()
                       for i in range(D)])
    iA, iB, iC, iD = sat[:-h, :-w], sat[:-
                                        h, w:], sat[h:, :-w], sat[h:, w:]
    lookup = iD - iB - iC + iA
    possible_match = np.where(np.logical_and.reduce(
        [lookup[..., i] == tplsum[i] for i in range(D)]))
    for y, x in zip(*possible_match):
        if np.all(im[y+1:y+h+1, x+1:x+w+1] == tpl):
            return (x+1, y+1)
    return (-1, -1)
# Search position


def search_position(device, action):

    subprocess.call(
        f'scrcpy\\adb.exe -s {device} shell screencap -p /sdcard/screen.png', shell=True)
    subprocess.call(
        f'scrcpy\\adb.exe -s {device} pull /sdcard/screen.png screen{device}.png', shell=True)
    subprocess.call(
        f'scrcpy\\adb.exe -s {device} shell rm /sdcard/screen.png', shell=True)
    img = button[action]
    template = Image.open(f'screen{device}.png')
    position = find_image(template, img)

    return position


class CodeExecutionThread(QThread):

    result_ready = pyqtSignal(int)
    signal_finished = pyqtSignal(int, str, int)
    stop_thread = pyqtSignal(int)
    status = pyqtSignal(int, str, object)

    def __init__(self, row):
        super().__init__()
        self.is_running = False
        self.row = row
        
    def hien_thi(self, name, message):
        self.status.emit(self.row, name, message)

    def signal_finished(self, xu, cong_them, tongjob,jobdie):
        self.hien_thi(By.TONG_XU, xu)
        self.hien_thi(By.XU_THEM, cong_them)
        self.hien_thi(By.TONG_JOB, tongjob)
        self.hien_thi(By.job_dead, jobdie)
        
    def read_setting(self):
        with open("Setting.json", "r") as config_file:
            config_data = json.load(config_file)  #json.load để dành đọc file và mode r
            return config_data
    def count(self, times: int):
        for i in range(times, 0, -1):
            self.hien_thi(By.TRANG_THAI, f"Làm job sau {i}")
            time.sleep(1)

    def timexu(self, times: int):
        for i in range(times, 0, -1):
            self.hien_thi(By.TRANG_THAI, f"Nhận xu sau {i}")
            time.sleep(1)

    def run(self):
        self.is_running = True
        try:

            while self.is_running:
                with open('account.txt', 'r') as file:
                    lines = file.readlines()
                device, TDS_token, nick_run = lines[self.row].strip().split('|')
                time.sleep(1)
                tongjob = 0
                total_job_die = 0
                self.hien_thi(By.TRANG_THAI, f"RUNNING...")
                # while self.is_running:
                folow = 0
                like = 0
                cau_hinh = requests.get(f'https://traodoisub.com/api/?fields=tiktok_run&id={nick_run}&access_token={TDS_token}').json() # add cau hinh
                if 'error' in cau_hinh:
                    error_cauhinh = cau_hinh['error']
                    self.hien_thi(By.TRANG_THAI,error_cauhinh)
                    break
                elif cau_hinh['success'] == 200:
                    id_tiktok = cau_hinh['data']['uniqueID']
                    msg = cau_hinh['data']['msg']
                    self.hien_thi(By.TRANG_THAI,f"Nick:{id_tiktok} {msg}")
                    time.sleep(5)

                while True:   
                    taking_mision = requests.get(
                        f'https://traodoisub.com/api/?fields=tiktok_follow&access_token={TDS_token}').json()#get job
                    if 'error' and 'countdown' in taking_mision:
                        error_message = taking_mision['error']
                        self.hien_thi(By.TRANG_THAI,error_message)
                        time.sleep(5)
                        countdown = int(taking_mision['countdown'])                      
                        for i in range(countdown, 0, -1):
                            self.hien_thi(By.TRANG_THAI,f"Vui lòng chờ {i}")
                            time.sleep(1)
                    elif 'data' in taking_mision:
                        for job in taking_mision['data']:
                            folow = folow + 1
                            uid = job['id']
                            link = job['link']
                            data = "access_token"+TDS_token
                            requests.post(link, data=data)
                            subprocess.call(f'scrcpy\\adb.exe -s {device} shell am start {link}')
                            config = self.read_setting()
                            min_delay = config['MIN_DELAY']
                            max_delay = config['MAX_DELAY']
                            delay_FL = random.randint(min_delay, max_delay)
                            self.count(delay_FL)
                            fl1 = search_position(device, 'follow1')
                            if fl1 != (-1, -1):
                                click1(device, fl1[0], fl1[1])
                                time.sleep(1)
                            subprocess.call(
                                f'scrcpy\\adb.exe -s {device} shell input keyevent KEYCODE_BACK')
                            os.remove(f'screen{device}.png')
                            done_job = requests.get(
                                f'https://traodoisub.com/api/coin/?type=TIKTOK_FOLLOW_CACHE&id={uid}&access_token={TDS_token}').json()
                            if "cache" in done_job:
                                self.hien_thi(
                                    By.TRANG_THAI, f"Done follow {done_job['cache']}")
                                time.sleep(1)
                                if done_job['cache'] == 10:
                                    r = requests.get(
                                        f'https://traodoisub.com/api/coin/?type=TIKTOK_FOLLOW&id=TIKTOK_FOLLOW_API&access_token={TDS_token}').json()
                                    xu = r['data']['xu']
                                    job_success = r['data']['job_success']
                                    tongjob += job_success
                                    cong_them = f'+{tongjob*1300} Xu'
                                    job_die = 10 - job_success
                                    total_job_die += job_die
                                    self.timexu(5)
                                    self.signal_finished(xu, cong_them, tongjob,total_job_die)
                            if folow ==2:
                                break
                            if int(tongjob / 400) > 0:
                                self.stop_thread.emit(self.row)
                                self.hien_thi(
                                    By.TRANG_THAI, f"Đã Hoàn Thành {tongjob} job .")
                                return

                            elif 'error' in done_job:
                                self.hien_thi(By.TRANG_THAI,done_job)
                                self.stop_thread.emit(self.row)
                            elif 'cache' in done_job and done_job['cache'] <10:
                                continue
                    
        except Exception as e:
            self.hien_thi(
                By.TRANG_THAI, f" {e}.")
        print("runing row:", self.row)

    def stop(self):
        self.is_running = False
        self.terminate()


class Ui_Dialog(object):
    def __init__(self):
        self.threads = {}
        self.collum = [By.MA_MAY, By.TOKEN, By.ID_TIK, By.TONG_XU, By.XU_THEM,
                       By.TONG_JOB, By.job_dead, By.TRANG_THAI, By.ACTION]
        self.row = 0
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setMaximumSize(QtCore.QSize(1376, 601))
        Dialog.setMinimumSize(QtCore.QSize(1376, 601))
        icon = QtGui.QIcon()
        
        icon.addPixmap(QtGui.QPixmap("icon.ico").scaled(48,48), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        self.tableWidget = QtWidgets.QTableWidget(Dialog)
        self.tableWidget.setGeometry(QtCore.QRect(15, 160, 1346, 411))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(9)
        self.tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setBackground(QtGui.QColor(194, 197, 194))
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(7, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(8, item)
        self.tableWidget.setColumnWidth(0, 150)
        self.tableWidget.setColumnWidth(3, 120)
        self.tableWidget.setColumnWidth(4, 120)
        self.tableWidget.setColumnWidth(5, 120)
        self.tableWidget.setColumnWidth(6, 120)
        self.tableWidget.setColumnWidth(7, 320)
        self.groupBox = QtWidgets.QGroupBox(Dialog)
        self.groupBox.setGeometry(QtCore.QRect(40, 20, 400, 121))
        self.groupBox.setObjectName("groupBox")
        self.label_7 = QtWidgets.QLabel(self.groupBox)
        self.label_7.setGeometry(QtCore.QRect(260, 80, 100, 21))
        self.label_7.setObjectName("label_7")
        #dungkhitren = QtGui.Q
        self.label_6 = QtWidgets.QLabel(self.groupBox)
        self.label_6.setGeometry(QtCore.QRect(20, 80, 100, 21))
        self.label_6.setObjectName("label_6")
        self.spinBox_2 = QtWidgets.QSpinBox(self.groupBox)
        self.spinBox_2.setGeometry(QtCore.QRect(220, 20, 42, 22))
        self.spinBox_2.setObjectName("spinBox_2")
        self.spinBox = QtWidgets.QSpinBox(self.groupBox)
        self.spinBox.setGeometry(QtCore.QRect(110, 20, 42, 22))
        self.spinBox.setObjectName("spinBox")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(160, 20, 21, 21))
        self.label.setObjectName("label")
         # Nút lưu cài đặt
        self.saveButton = QtWidgets.QPushButton(self.groupBox)
        self.saveButton.setGeometry(QtCore.QRect(290, 14, 100, 100))
        self.saveButton.setObjectName("saveButton")
        self.saveButton.clicked.connect(self.save_settings)
        self.lineEdit = QtWidgets.QLineEdit(self.groupBox)
        self.lineEdit.setGeometry(QtCore.QRect(120, 80, 110, 22))
        self.lineEdit.setObjectName("lineEdit")
        self.label_12 = QtWidgets.QLabel(self.groupBox)
        self.label_12.setGeometry(QtCore.QRect(20, 20, 81, 21))
        self.label_12.setObjectName("label_12")
        #cauhinh.set
        self.groupBox_2 = QtWidgets.QGroupBox(Dialog)
        self.groupBox_2.setGeometry(QtCore.QRect(550, 20, 401, 121))
        self.groupBox_2.setObjectName("groupBox_2")
        self.lineEdit_2 = QtWidgets.QLineEdit(self.groupBox_2)
        self.lineEdit_2.setGeometry(QtCore.QRect(150, 20, 201, 22))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setKerning(True)
        self.lineEdit_2.setFont(font)
        self.lineEdit_2.setMouseTracking(True)
        self.lineEdit_2.setFrame(False)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.label_13 = QtWidgets.QLabel(self.groupBox_2)
        self.label_13.setGeometry(QtCore.QRect(20, 20, 100, 21))
        self.label_13.setObjectName("label_13")
        self.label_14 = QtWidgets.QLabel(self.groupBox_2)
        self.label_14.setGeometry(QtCore.QRect(20, 50, 100, 21))
        self.label_14.setObjectName("label_14")
        self.lineEdit_3 = QtWidgets.QLineEdit(self.groupBox_2)
        self.lineEdit_3.setGeometry(QtCore.QRect(150, 50, 201, 22))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setKerning(True)
        self.lineEdit_3.setFont(font)
        self.lineEdit_3.setMouseTracking(True)
        self.lineEdit_3.setFrame(False)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.label_15 = QtWidgets.QLabel(self.groupBox_2)
        self.label_15.setGeometry(QtCore.QRect(20, 80, 100, 21))
        self.label_15.setObjectName("label_15")
        self.lineEdit_4 = QtWidgets.QLineEdit(self.groupBox_2)
        self.lineEdit_4.setGeometry(QtCore.QRect(150, 80, 201, 22))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setKerning(True)
        self.lineEdit_4.setFont(font)
        self.lineEdit_4.setMouseTracking(True)
        self.lineEdit_4.setFrame(False)
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.label_16 = QtWidgets.QLabel(Dialog)
        self.label_16.setGeometry(QtCore.QRect(10, 575, 281, 21))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_16.setFont(font)
        self.label_16.setObjectName("label_16")
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(1000, 40, 101, 31))
        self.submit_button = self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.on_submit)
        self.pushButton_2 = QtWidgets.QPushButton(Dialog)
        self.pushButton_2.setGeometry(QtCore.QRect(1000, 100, 101, 31))
        self.pushButton_2.clicked.connect(self.delete_data)
        self.erase_button = self.pushButton_2.setObjectName("pushButton_2")
        self.tableWidget.itemChanged.connect(self.update_total_xu)
        #menu token
        self.tableWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableWidget.customContextMenuRequested.connect(self.show_menu)
        self.tableWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableWidget.customContextMenuRequested.connect(self.saveid)
        # Lấy dữ liệu từ các trường nhập liệu
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        self.retranslateUi(Dialog)
        self.load_account()
    def save_settings(self):
        min_delay = self.spinBox.value()
        max_delay = self.spinBox_2.value()
        data = {
        "MIN_DELAY": min_delay,
        "MAX_DELAY": max_delay
        }
        with open("Setting.json", "w") as config_file:
            json.dump(data,config_file,indent=4)
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Cài đặt đã được lưu.")
        msg.setWindowTitle("Thông báo")
        msg.exec_()
    def show_menu(self, pos):
        selected_item = self.tableWidget.itemAt(pos)
        if selected_item is not None and selected_item.column() == self.collum.index(By.TOKEN):
            menu = QtWidgets.QMenu()
            view_chrome_action = menu.addAction("View Chrome")#menu single action
            # view_chrome_action = QtWidgets.QMenu("View Chrome")#menu multiple action
            # Thêm các mục menu phụ
            # sub_action1 = view_chrome_action.addAction("Sub Action 1")
            # sub_action2 = view_chrome_action.addAction("Sub Action 2")
            # Thêm menu phụ vào menu chính
            action = menu.exec_(self.tableWidget.mapToGlobal(pos)) 
            if action == view_chrome_action:
                cauhinh = selected_item.text()
                def run_chrome():
                    driver = webdriver.Chrome()
                    driver.get(f"https://traodoisub.com/api/autoclick/abcd/3202/?access_token={cauhinh}&type=tiktok_follow")
                    try:
                        while True:
                            # Kiểm tra xem trình duyệt có bị đóng hay chưa
                            if not driver.title:
                                break
                    except KeyboardInterrupt:
                        pass
                    finally:
                        driver.quit()
                # Tạo một luồng mới để chạy trình duyệt Chrome
                chrome_thread = threading.Thread(target=run_chrome)
                chrome_thread.start()
    def saveid(self,pos):
        selected_item = self.tableWidget.itemAt(pos)
        selected_row = self.tableWidget.currentRow()
        if selected_row >= 0 and selected_item is not None and selected_item.column() == self.collum.index(By.ID_TIK):
            menu = QtWidgets.QMenu()
            view_id = menu.addAction("Save id")
            action = menu.exec_(self.tableWidget.mapToGlobal(pos))
            if action == view_id:
                id_tiktok = selected_item.text()
                self.update_id_tiktok(id_tiktok, selected_row)
    def update_id_tiktok(self, id_tiktok, selected_row):
        with open('account.txt', 'r') as file:
            lines = file.readlines()
        if selected_row < len(lines):
            parts = lines[selected_row].strip().split("|")
            if len(parts) >= 3:
                parts[2] = id_tiktok
                lines[selected_row] = '|'.join(parts) + '\n'
                with open('account.txt', 'w') as file:
                    file.writelines(lines)

    def calculate_total_xu(self):
        total_xu = 0
        for row in range(self.tableWidget.rowCount()):
            item = self.tableWidget.item(row, self.collum.index(By.TONG_XU))
            if item is not None:
                total_xu += int(item.text())
        return total_xu

    def update_total_xu(self):
        total_xu = self.calculate_total_xu()
        self.label_16.setText(f"<span style='color: green;'>Tổng xu: {total_xu}</span>")
        self.label_16.setGeometry(QtCore.QRect(10, 575, 281, 21))

    def load_account(self):
        with open("account.txt", "r") as f:
            datas = f.readlines()
        self.tableWidget.setRowCount(len(datas))
        self.tableWidget.setRowCount(0)
        for acc in datas:
            device, TDS_token, Cau_hinh = acc.strip().split("|")
            row = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row)
            self.tableWidget.setItem(
                row, 0, QtWidgets.QTableWidgetItem(device))
            self.tableWidget.setItem(
                row, 1, QtWidgets.QTableWidgetItem(TDS_token))
            self.tableWidget.setItem(
                row, 2, QtWidgets.QTableWidgetItem(Cau_hinh))
            self.button = QtWidgets.QPushButton("Start")
            self.button.setStyleSheet("background-color: green;")
            self.button.clicked.connect(
                lambda checked, row=row: self.on_button_click(row))
            self.tableWidget.setCellWidget(row, 8, self.button)
        self.update_total_xu()
        
    def on_submit(self):
        device = self.lineEdit_4.text()
        TDS_token = self.lineEdit_2.text()
        Cau_hinh = self.lineEdit_3.text()
        row = self.tableWidget.rowCount()
        self.tableWidget.insertRow(row)
        with open("account.txt", "a") as f:
            f.write(f"{device}|{TDS_token}|{Cau_hinh}\n")
        self.lineEdit_4.setText("")
        self.lineEdit_2.setText("")
        self.lineEdit_3.setText("")
        self.button = QtWidgets.QPushButton("Start")
        self.button.setStyleSheet("background-color: green;")
        self.button.clicked.connect(
            lambda checked, row=row: self.on_button_click(row))
        self.tableWidget.setItem(row, 0, QtWidgets.QTableWidgetItem(device))
        self.tableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem(TDS_token))
        self.tableWidget.setItem(row, 2, QtWidgets.QTableWidgetItem(Cau_hinh))
        self.tableWidget.setCellWidget(row, 8, self.button)

    def on_button_click(self, row):
        if row not in self.threads or not self.threads[row].isRunning():
            # Create a new thread instance for the given row
            thread = CodeExecutionThread(row)
            self.threads[row] = thread
            # self.threads[row].signal_finished.connect(partial(self.on_execution_finished, row=row))
            self.threads[row].status.connect(self.status)
            self.threads[row].stop_thread.connect(self.stop)

            # Start the thread
            self.threads[row].start()
            self.tableWidget.cellWidget(row, 8).setText("Stop")
            self.tableWidget.cellWidget(row, 8).setStyleSheet("background-color: red;")
        else:
            self.stop(row)

    def stop(self, row):
        self.status(row, By.TRANG_THAI, "Đã Dừng")
        self.threads[row].stop()
        self.threads.pop(row)
        self.tableWidget.cellWidget(row, 8).setText("Start")
        self.tableWidget.cellWidget(row, 8).setStyleSheet("background-color: green;")
        

    def status(self, row, name_row, message):
        self.tableWidget.setItem(row, self.collum.index(
            name_row), QtWidgets.QTableWidgetItem(str(message)))

    def delete_data(self):
        selected_row = self.tableWidget.currentRow()
        if selected_row >= 0:
            # Get the data from the selected row
            device = self.tableWidget.item(
                selected_row, self.collum.index(By.MA_MAY)).text()
            TDS_token = self.tableWidget.item(
                selected_row, self.collum.index(By.TOKEN)).text()
            Cau_hinh = self.tableWidget.item(
                selected_row, self.collum.index(By.ID_TIK)).text()

            # Remove the row from the table widget
            self.tableWidget.removeRow(selected_row)

            # Delete the corresponding data from account.txt
            with open("account.txt", "r") as f:
                lines = f.readlines()

            with open("account.txt", "w") as f:
                for line in lines:
                    d, t, c = line.strip().split("|")
                    if d != device or t != TDS_token or c != Cau_hinh:
                        f.write(line)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "AUTO TDS ADB BY PHUSCVOX "))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("Dialog", "Mã Máy "))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("Dialog", "Token TDS"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("Dialog", "ID tiktok"))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("Dialog", "Tổng xu"))
        item = self.tableWidget.horizontalHeaderItem(4)
        item.setText(_translate("Dialog", "Xu thêm"))
        item = self.tableWidget.horizontalHeaderItem(5)
        item.setText(_translate("Dialog", "Tổng job"))
        item = self.tableWidget.horizontalHeaderItem(6)
        item.setText(_translate("Dialog", "Job die"))
        item = self.tableWidget.horizontalHeaderItem(7)
        item.setText(_translate("Dialog", "Trạng thái"))
        item = self.tableWidget.horizontalHeaderItem(8)
        item.setText(_translate("Dialog", "Action"))
        self.groupBox.setTitle(_translate("Dialog", "Setting"))
        self.label_7.setText(_translate("Dialog", "Xu"))
        self.label_6.setText(_translate("Dialog", "Dừng khi trên "))
        self.label.setText(_translate("Dialog", "đến"))
        self.label_12.setText(_translate("Dialog", "Follow từ "))
        self.groupBox_2.setTitle(_translate("Dialog", "Cấu Hình"))
        self.label_13.setText(_translate("Dialog", "TOKEN TDS"))
        self.label_14.setText(_translate("Dialog", "ID TIKTOK "))
        self.label_15.setText(_translate("Dialog", "MÃ MÁY "))
        self.label_16.setText(_translate("Dialog", "Tổng xu :"))
        self.pushButton.setText(_translate("Dialog", "Thêm "))
        self.pushButton_2.setText(_translate("Dialog", "Xóa"))
        self.saveButton.setText("Lưu cài đặt")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Dialog()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
