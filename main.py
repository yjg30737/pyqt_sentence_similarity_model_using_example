import os, sys

from inputDialog import InputDialog
from script import get_top10_models, run_sentence_transformer

# Get the absolute path of the current script file
script_path = os.path.abspath(__file__)

# Get the root directory by going up one level from the script directory
project_root = os.path.dirname(os.path.dirname(script_path))

sys.path.insert(0, project_root)
sys.path.insert(0, os.getcwd())  # Add the current directory as well

from PyQt5.QtCore import QThread, QCoreApplication, Qt, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QMainWindow, QPushButton, QApplication, QVBoxLayout, QHBoxLayout, QSizePolicy, QSpacerItem, \
    QLabel, QComboBox, QWidget, QLineEdit, QFrame, QListWidget, QDialog, QTextBrowser

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)  # HighDPI support

QApplication.setFont(QFont('Arial', 12))


class Thread(QThread):
    generatedFinished = pyqtSignal(dict)

    def __init__(self, *args, **kwargs):
        super(Thread, self).__init__()
        self.__model = kwargs['model']
        self.__src_sentence = kwargs['src_sentence']
        self.__compare_sentences = kwargs['compare_sentences']

    def run(self):
        try:
            result = run_sentence_transformer(self.__model, self.__src_sentence, self.__compare_sentences)
            self.generatedFinished.emit(result)
        except Exception as e:
            raise Exception(e)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.__initUi()

    def __initUi(self):
        self.setWindowTitle('PyQt Sentence Similarity Model Using Example')

        self.__modelCmbBox = QComboBox()
        self.__modelCmbBox.addItems(get_top10_models())

        lay = QHBoxLayout()
        lay.addWidget(QLabel('Model'))
        lay.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.MinimumExpanding))
        lay.addWidget(self.__modelCmbBox)
        lay.setContentsMargins(0, 0, 0, 0)

        topWidget = QWidget()
        topWidget.setLayout(lay)

        self.__lineEdit = QLineEdit()
        self.__lineEdit.setPlaceholderText('Insert any word...')
        self.__lineEdit.setText('This is a cat.')

        self.__addBtn = QPushButton('Add')
        self.__delBtn = QPushButton('Delete')

        self.__addBtn.clicked.connect(self.__add)
        self.__delBtn.clicked.connect(self.__delete)

        lay = QHBoxLayout()
        lay.addWidget(QLabel('Sentences to Compare'))
        lay.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.MinimumExpanding))
        lay.addWidget(self.__addBtn)
        lay.addWidget(self.__delBtn)
        lay.setAlignment(Qt.AlignRight)
        lay.setContentsMargins(0, 0, 0, 0)

        menuWidget = QWidget()
        menuWidget.setLayout(lay)

        self.__listWidget = QListWidget()
        self.__listWidget.addItems(['This is a happy cat.', 'This is a dog.', 'This is not a cat.'])

        self.__runBtn = QPushButton('Run')
        self.__runBtn.clicked.connect(self.__run)

        self.__resultBrowser = QTextBrowser()
        self.__resultBrowser.setVisible(False)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFrameShadow(QFrame.Sunken)

        lay = QVBoxLayout()
        lay.addWidget(topWidget)
        lay.addWidget(self.__lineEdit)
        lay.addWidget(sep)
        lay.addWidget(menuWidget)
        lay.addWidget(self.__listWidget)
        lay.addWidget(self.__runBtn)
        lay.addWidget(self.__resultBrowser)
        lay.setAlignment(Qt.AlignTop)

        mainWidget = QWidget()
        mainWidget.setLayout(lay)

        self.setCentralWidget(mainWidget)

    def __add(self):
        dialog = InputDialog('Add', '', self)
        reply = dialog.exec()
        if reply == QDialog.Accepted:
            text = dialog.getText()
            self.__listWidget.addItem(text)

    def __delete(self):
        r_idx = self.__listWidget.currentRow()
        if r_idx != -1:
            self.__listWidget.takeItem(r_idx)

    def __run(self):
        model = self.__modelCmbBox.currentText()
        src_sentence = self.__lineEdit.text().split()
        compare_sentences = [self.__listWidget.item(i).text() for i in range(self.__listWidget.count()) if self.__listWidget.item(i)]
        self.__t = Thread(model=model
                        ,src_sentence=src_sentence
                        ,compare_sentences=compare_sentences)
        self.__t.started.connect(self.__started)
        self.__t.generatedFinished.connect(self.__generatedFinished)
        self.__t.finished.connect(self.__finished)
        self.__t.start()

    def __started(self):
        self.__runBtn.setEnabled(False)

    def __generatedFinished(self, dict):
        self.__resultBrowser.setVisible(True)
        self.__resultBrowser.append('\n'.join(dict['similarity']))
        self.__resultBrowser.append(f'Elapsed Time: {dict["elapsed_time"]}')

    def __finished(self):
        self.__runBtn.setEnabled(True)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())