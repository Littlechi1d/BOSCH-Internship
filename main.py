import sys
import time
from PyQt5.QtCore import QThread,QTimer
from PyQt5.QtGui import QTextCursor,QColor
import PyQt5.QtWidgets as qw
import serial_ui
import threading
from serial_thread import Serial_Qthread_function
from PyQt5.QtSerialPort import QSerialPortInfo
from format_string import check_string

class thread_class_test(threading.Thread):

    def __init__(self,parent):
        threading.Thread.__init__(self)
        self.parent = parent

    def run(self):
         print ("运行线程:", threading.current_thread().ident)

class SerialForm(qw.QWidget):
    def __init__(self):
        super().__init__()
        self.ui = serial_ui.Ui_Serial()
        self.ui.setupUi(self)
        self.Interface_Init()
        self.UI_Init()
        self.setWindowTitle("测试")

        print("主线程id:",threading.current_thread().ident)
        
        self.Serial_QThread = QThread()
        self.Serial_QThread_Function = Serial_Qthread_function()
        self.Serial_QThread_Function.moveToThread(self.Serial_QThread)
        self.Serial_QThread.start()
        self.Serial_QThread_Function.signal_Serialstart_function.connect(self.Serial_QThread_Function.SerialInit_function)
        self.Serial_QThread_Function.signal_Serialstart_function.emit()
        self.Serial_QThread_Function.signal_PushButton_Open.connect(self.Serial_QThread_Function.Slot_PushButton_Open)
        self.Serial_QThread_Function.signal_PushButton_Open_flag.connect(self.Slot_PushButton_Open_flag)
        self.Serial_QThread_Function.signal_ReadData.connect(self.Slot_ReadData)
        self.Serial_QThread_Function.signal_RTS.connect(self.Serial_QThread_Function.slot_RTS)
        self.Serial_QThread_Function.signal_DTR.connect(self.Serial_QThread_Function.slot_DTR)
        self.Serial_QThread_Function.signal_SendData.connect(self.Serial_QThread_Function.Slot_Send_data)
        # self.thread_class = thread_class_test(self)
        # self.thread_class.start()

        self.port_name = []
        self.time_scan = QTimer()
        self.time_scan.timeout.connect(self.TimeOut_Scan)
        self.time_scan.start(1000)

    def TimeOut_Scan(self):
        availablePort = QSerialPortInfo.availablePorts()
        new_port = []
        for port in availablePort:
            new_port.append(port.portName())
        if len(self.port_name) != len(new_port):
            self.port_name = new_port
            self.ui.comboBox_Com.clear()
            self.ui.comboBox_Com.addItems(self.port_name)
    
    def Interface_Init(self):
        self.Baud = ('115200','4800','9600','57600')
        self.Stop = ('1','1.5','2')
        self.Data = ('8','7','6','5')
        self.Check = ('None','Odd','Even')
        self.ScanType = ('Active','Passive')
        self.ui.comboBox_Baud.addItems(self.Baud)
        self.ui.comboBox_Stop.addItems(self.Stop)
        self.ui.comboBox_Data.addItems(self.Data)
        self.ui.comboBox_Check.addItems(self.Check)
        self.ui.comboBox_ScanType.addItems(self.ScanType)
        self.ui.checkBox_RTS.stateChanged.connect(self.checkBox_RTS)
        self.ui.checkBox_DTR.stateChanged.connect(self.checkBox_DTR)
        self.ui.checkBox_TimeView.stateChanged.connect(self.checkBox_TimeView)
        self.ui.pushButton_Update.clicked.connect(self.pushButton_Update)
        self.ui.pushButton_Clean.clicked.connect(self.pushButton_Clean)
    
    def UI_Init(self):
        self.ui.pushButton_Open.clicked.connect(self.PushButton_Open)
    
    def PushButton_Open(self):
        self.set_parameter = {}
        self.set_parameter['comboBox_Com'] = self.ui.comboBox_Com.currentText()
        self.set_parameter['comboBox_Baud'] = self.ui.comboBox_Baud.currentText()
        self.set_parameter['comboBox_Stop'] = self.ui.comboBox_Stop.currentText()
        self.set_parameter['comboBox_Data'] = self.ui.comboBox_Data.currentText()
        self.set_parameter['comboBox_Check'] = self.ui.comboBox_Check.currentText()
        self.Serial_QThread_Function.signal_PushButton_Open.emit(self.set_parameter)

    def Slot_PushButton_Open_flag(self,state):
        print("串口打开状态", state)
        if state == 0:
            qw.QMessageBox.warning(self,'错误信息','串口已被占用，打开失败')
        elif state == 1:
            self.ui.pushButton_Open.setStyleSheet("color:red")
            self.ui.pushButton_Open.setText("关闭串口")
        else:
            self.ui.pushButton_Open.setStyleSheet("color:black")
            self.ui.pushButton_Open.setText("打开串口")
            self.time_scan.start(1000)

    def Slot_ReadData(self,data):
        # print(data)
        if self.ui.checkBox_TimeView.checkState():
            time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()) + "\r\n"
            self.ui.textEdit_receive.setTextColor(QColor(0,162,0))
            self.ui.textEdit_receive.insertPlainText(time_str)
            self.ui.textEdit_receive.setTextColor(QColor(0,0,0))

        Byte_data = bytes(data)
        
        if self.ui.checkBox_HexView.checkState():
            View_data = ''
            for i in range(0,len(Byte_data)):
                View_data = View_data + '{:02x}'.format(Byte_data[i]) + ' '
            self.ui.textEdit_receive.insertPlainText(View_data)
        else:
            self.ui.textEdit_receive.insertPlainText(Byte_data.decode('utf-8','ignore'))
            self.ui.textEdit_receive.moveCursor(QTextCursor.End)

    def checkBox_RTS(self,state):
        self.Serial_QThread_Function.signal_RTS.emit(state)

    def checkBox_DTR(self,state):
        self.Serial_QThread_Function.signal_DTR.emit(state)

    def checkBox_TimeView(self,state):
        print("时间戳状态改变")

    def pushButton_Update(self):

        print("Update")
        send_list = []
        start_byte = 254
        end_byte = 173
        advInterval_list = []
        advDuration_list = []
        advData_list = []
        scanType_list = []
        other_list = []
        reserve_list = [0] * 20
        send_data = {}
        
        send_data['advInterval'] = check_string(self.ui.advInterval.text())
        send_data['advDuration'] = check_string(self.ui.advDuration.text())
        send_data['advData'] = check_string(self.ui.advData.toPlainText())
        send_data['scanType'] = self.ui.comboBox_ScanType.currentText()
        send_data['scanInterval'] = check_string(self.ui.scanInterval.text())
        send_data['scanWindow'] = check_string(self.ui.scanWindow.text())
        send_data['scanDuration'] = check_string(self.ui.scanDuration.text())
        send_data['connLatency'] = check_string(self.ui.connLatency.text())
        send_data['connTimeout'] = check_string(self.ui.connTimeout.text())
        send_data['intervalMin'] = check_string(self.ui.intervalMin.text())
        send_data['intervalMax'] = check_string(self.ui.intervalMax.text())

        print(send_data['advData'])
        print(send_data['scanType'])
        for key in send_data:

            if send_data[key] == '':
                qw.QMessageBox.warning(self,'错误信息','输入参数不能为空')
                return
            
            if (key == 'advInterval') or (key == 'advDuration'):
                if len(send_data[key]) > 8:
                    qw.QMessageBox.warning(self,'错误信息','输入参数超出范围')
                    return
                else:
                    send_data[key] = f"{send_data[key]:0>8}"
                
                if key == 'advInterval':
                    i = 0
                    while i <= 6:
                        data = int(send_data[key][i:i+2],16)
                        advInterval_list.append(data)
                        i += 2
                else:
                    i = 0
                    while i <= 6:
                        data = int(send_data[key][i:i+2],16)
                        advDuration_list.append(data)
                        i += 2

            elif key == 'advData':
                if len(send_data[key]) > 62:
                    qw.QMessageBox.warning(self,'错误信息','输入参数超出范围')
                    return
                else:
                    send_data[key] = f"{send_data[key]:0<62}"
                
                i = 0
                while i <= 60:
                    data = int(send_data[key][i:i+2],16)
                    advData_list.append(data)
                    i += 2

            elif key == 'scanType':
                if send_data[key] == 'Active':
                    send_data[key] = '10'
                else:
                    send_data[key] = '11'

                data = int(send_data[key][0:2],16)
                scanType_list.append(data)

            else:
                if len(send_data[key]) > 4:
                    qw.QMessageBox.warning(self,'错误信息','输入参数超出范围')
                    return
                else:
                    send_data[key] = f"{send_data[key]:0>4}"
                
                i = 0
                while i <= 2:
                    data = int(send_data[key][i:i+2],16)
                    other_list.append(data)
                    i += 2

        print(send_data)
        print(send_data['advInterval'])
        # advInterval_data = int(self.ui.advInterval.text()[0:2],16)
        # advDuration_data = int(self.ui.advDuration.text()[0:2],16)
        send_list.append(start_byte)
        send_list.extend(advInterval_list)
        send_list.extend(advDuration_list)
        send_list.extend(advData_list)
        send_list.extend(scanType_list)
        send_list.extend(other_list)
        send_list.extend(reserve_list)
        send_list.append(end_byte)
        input_s = bytes(send_list)
        print(input_s)
        self.Serial_QThread_Function.signal_SendData.emit(input_s)
    
    def pushButton_Clean(self):
        print("清除接收")
        self.ui.textEdit_receive.clear()
    
    def closeEvent(self, event):
        print("窗体关闭")
        
if __name__ == "__main__":
    app = qw.QApplication(sys.argv)
    w1 = SerialForm()
    w1.show()
    sys.exit(app.exec_())