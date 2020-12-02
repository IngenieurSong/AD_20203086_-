from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
import sys
import os.path
from player import *
from imgToText import Ocr
import scanPro

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.player = SoundPlayer(self)
        self.playlist = []
        self.selectedList = [0]
        self.fileText = ''
        self.playOption = QMediaPlaylist.Sequential  # 음성 파일 Play Option 설정

        self.setWindowTitle('Main Window')
        self.initUI()

    def initUI(self):  # issue. 버튼 만들 때 중복 줄이기
        
        self.setWindowIcon(QIcon('icon.jpg'))  # icon 설정

        vbox = QVBoxLayout()

        #  display
        box = QVBoxLayout()
        gb = QGroupBox('Display')
        vbox.addWidget(gb)

        self.display = QTextEdit(self.fileText)  # 글자 크기 조정할 QTextEdit 추가
        self.display.setReadOnly(True)  # 읽기 전용으로 설정
        box.addWidget(self.display)

        gb.setLayout(box)

        #  control text size
        box = QVBoxLayout()
        gb = QGroupBox('Control Text Size')
        vbox.addWidget(gb)

        self.textSize = QSlider(Qt.Horizontal)  # 글자 크기를 조정할 QSlider 추가
        self.textSize.setRange(12, 40)  # 글자 크기 변경 범위 12 ~ 40으로 설정
        self.textSize.setTickPosition(2)
        self.textSize.valueChanged.connect(self.changeFontSize)  # signal
        box.addWidget(self.textSize)

        gb.setLayout(box)

        # Clear Text, New Text
        hbox = QHBoxLayout()
        btnClear = QPushButton('Clear Text')  # display를 초기화하는 버튼 추가
        btnNew = QPushButton('Add New Text')  # 새로운 OCR 대상의 Text를 추가하는 버튼 추가
        btnClear.clicked.connect(self.clearText)  # signal
        btnNew.clicked.connect(self.newText)  # signal
        hbox.addWidget(btnClear)
        hbox.addWidget(btnNew)

        box.addLayout(hbox)
        gb.setLayout(box)

        # Sound List
        box = QVBoxLayout()
        gb = QGroupBox('Sound List')
        vbox.addWidget(gb)

        # OCR이 끝난 Text에 대한 음성 파일(.wav)이나 임의의 음성파일 추가하는 버튼 추가
        self.table = QTableWidget(0, 1, self)
        self.table.setHorizontalHeaderItem(0, QTableWidgetItem('Title'))  # Table 이름 설정
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 읽기 전용으로 변경
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)  # 선택했을 때 효과
        self.table.itemSelectionChanged.connect(self.tableChanged)  # signal
        box.addWidget(self.table)

        hbox = QHBoxLayout()

        btnAdd = QPushButton('Add List')  # 임의의 음성 파일을 추가하는 버튼 생성
        btnDel = QPushButton('Del List')  # Sound List에 있는 음성 파일을 삭제하는 버튼 생성

        # signal
        btnAdd.clicked.connect(self.addList)
        btnDel.clicked.connect(self.delList)

        hbox.addWidget(btnAdd)
        hbox.addWidget(btnDel)

        box.addLayout(hbox)
        gb.setLayout(box)

        # Play Control
        box = QHBoxLayout()
        gb = QGroupBox('Play Control')
        vbox.addWidget(gb)

        buttonList = ['▶', '⏸', '■']  # 중복 제거를 위해 button List 생성
        grp = QButtonGroup(self)
        for i in range(len(buttonList)):
            btn = QPushButton(buttonList[i], self)  # 음성 파일 재생에 관여하는 버튼들 추가
            grp.addButton(btn, i)
            box.addWidget(btn)

        # signal
        grp.buttonClicked[int].connect(self.btnClicked)

        # Control Volume
        self.slider = QSlider(Qt.Horizontal, self)  # Volume Control을 위한 QSlider 추가
        self.slider.setRange(0, 100)  # Volume 범위 지정
        self.slider.setValue(50)  #  50을 Default Volume 값으로 설정

        # signal
        self.slider.valueChanged[int].connect(self.volumeChanged)
        box.addWidget(self.slider)
        gb.setLayout(box)

        self.setLayout(vbox)
        self.show()

    #
    def changeFontSize(self):  # display 내의 Text의 크기를 변경하는 기능
        self.display.selectAll()  # display 내의 모든 Text를 선택
        self.display.setFontPointSize(self.textSize.value())  # Slider의 Value로 Text 크기 변경

    def clearText(self):  # display 내의 모든 Text를 삭제하는 기능
        self.display.clear()  # display 내의 모든 Text를 삭제

    def newText(self):
        fname = input("Enter File Name : ")  # gui 안에서 입력받는 방법은?
        
        if os.path.isfile(fname) == True:
            # OCR 기능 실행
            scanPro.adaptive_threshold(fname)
            ocr = Ocr('%s_gray.jpg' %fname)
            ocr.ocr_tesseract()
            ocr.textToSpeech()
            self.fileText = ocr.textResult

            self.display.append(self.fileText)

            # OCR 결과로 산출된 음성 파일을 Sound List에 추가
            files = ('%s.wav' %fname, None)
            row = self.table.rowCount()
            self.table.setRowCount(row + 1)
            self.table.setItem(row, 0, QTableWidgetItem(files[0]))

            self.createPlaylist()
            
        else:
            print('Try Again')
            self.newText()
            
    def tableChanged(self):
        self.selectedList.clear()
        for item in self.table.selectedIndexes():
            self.selectedList.append(item.row())

        self.selectedList = list(set(self.selectedList))

        if self.table.rowCount() != 0 and len(self.selectedList) == 0:
            self.selectedList.append(0)

    def addList(self):  # issue. 파일 경로가 Title로 추가됨
        files = QFileDialog.getOpenFileNames(self
                                             , 'Select one or more files to open'
                                             , ''
                                             , 'Sound (*.mp3 *.wav *.ogg *.flac *.wma)')
        cnt = len(files[0])
        row = self.table.rowCount()
        self.table.setRowCount(row + cnt)
        for i in range(row, row + cnt):
            self.table.setItem(i, 0, QTableWidgetItem(files[0][i - row]))

        self.createPlaylist()

    def delList(self):
        row = self.table.rowCount()

        index = []
        for item in self.table.selectedIndexes():
            index.append(item.row())

        index = list(set(index))
        index.reverse()
        for i in index:
            self.table.removeRow(i)

        self.createPlaylist()

    def btnClicked(self, id):

        if id == 0:  # ▶
            if self.table.rowCount() > 0:
                self.player.play(self.playlist, self.selectedList[0], self.playOption)
        elif id == 1:  # ⏸
            self.player.pause()
        else:  # ■
            self.player.stop()

    def volumeChanged(self):
        self.player.upateVolume(self.slider.value())

    def paintEvent(self, e):  # issue. 따로 지정하지 않으면 크기가 임의로 설정됨
       self.table.setColumnWidth(0, self.table.width() * 1)

    def createPlaylist(self):
        self.playlist.clear()
        for i in range(self.table.rowCount()):
            self.playlist.append(self.table.item(i, 0).text())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    sys.exit(app.exec_())
