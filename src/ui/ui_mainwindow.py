# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindowenULHf.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QHeaderView, QLabel, QMainWindow,
    QMenuBar, QPushButton, QSizePolicy, QStatusBar,
    QTableWidget, QTableWidgetItem, QTextEdit, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1052, 719)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.tableWidget = QTableWidget(self.centralwidget)
        self.tableWidget.setObjectName(u"tableWidget")
        self.tableWidget.setGeometry(QRect(-60, -30, 1171, 791))
        self.tableWidget.setStyleSheet(u"QWidget {\n"
"    background-color: #F9FAFB;\n"
"}")
        self.labelTitle = QLabel(self.centralwidget)
        self.labelTitle.setObjectName(u"labelTitle")
        self.labelTitle.setGeometry(QRect(300, -10, 481, 151))
        font = QFont()
        font.setFamilies([u"Nanum Square R"])
        font.setBold(False)
        self.labelTitle.setFont(font)
        self.labelTitle.setStyleSheet(u"QWidget {font-size: 30px;\n"
"letter-spacing: -1px;\n"
"line-height: 20px;\n"
"text-transform: uppercase;\n"
"color: #2f2f2e;\n"
"font-family: \"Nanum Square R\";\n"
"}")
        self.labelSubtitle = QLabel(self.centralwidget)
        self.labelSubtitle.setObjectName(u"labelSubtitle")
        self.labelSubtitle.setGeometry(QRect(340, 60, 381, 121))
        self.labelSubtitle.setStyleSheet(u"QWidget {font-size: 15px;\n"
"letter-spacing: -1px;\n"
"line-height: 20px;\n"
"text-transform: uppercase;\n"
"color: #063895;\n"
"font-family: \"Nanum Square R\";\n"
"}")
        self.labelQR = QLabel(self.centralwidget)
        self.labelQR.setObjectName(u"labelQR")
        self.labelQR.setGeometry(QRect(890, 540, 101, 91))
        self.labelQR.setStyleSheet(u"border: 1px dashed #999999;\n"
"background-color: rgba(47, 128, 237, 0.06);\n"
"border-radius: 6px;")
        self.btnCopySpecs = QPushButton(self.centralwidget)
        self.btnCopySpecs.setObjectName(u"btnCopySpecs")
        self.btnCopySpecs.setGeometry(QRect(80, 580, 181, 51))
        font1 = QFont()
        font1.setFamilies([u"Nanum Square R"])
        font1.setPointSize(15)
        self.btnCopySpecs.setFont(font1)
        self.btnCopySpecs.setStyleSheet(u"QWidget {\n"
"letter-spacing: -1px;\n"
"line-height: 20px;\n"
"text-transform: uppercase;\n"
"color: #000000;\n"
"font-family: \"Nanum Square R\";\n"
"}")
        self.btnOpenHomepage = QPushButton(self.centralwidget)
        self.btnOpenHomepage.setObjectName(u"btnOpenHomepage")
        self.btnOpenHomepage.setGeometry(QRect(280, 580, 301, 51))
        font2 = QFont()
        font2.setFamilies([u"Nanum Square R"])
        font2.setPointSize(15)
        font2.setBold(False)
        self.btnOpenHomepage.setFont(font2)
        self.btnOpenHomepage.setStyleSheet(u"QWidget {\n"
"letter-spacing: -1px;\n"
"line-height: 20px;\n"
"text-transform: uppercase;\n"
"color: #000000;\n"
"font-family: \"Nanum Square R\";\n"
"}")
        self.btnOpenKakao = QPushButton(self.centralwidget)
        self.btnOpenKakao.setObjectName(u"btnOpenKakao")
        self.btnOpenKakao.setGeometry(QRect(600, 580, 241, 51))
        self.btnOpenKakao.setFont(font1)
        self.btnOpenKakao.setStyleSheet(u"QWidget {\n"
"letter-spacing: -1px;\n"
"line-height: 20px;\n"
"text-transform: uppercase;\n"
"color: #000000;\n"
"font-family: \"Nanum Square R\";\n"
"}")
        self.textSpecs = QTextEdit(self.centralwidget)
        self.textSpecs.setObjectName(u"textSpecs")
        self.textSpecs.setGeometry(QRect(100, 170, 871, 351))
        self.textSpecs.setStyleSheet(u"QTextEdit {\n"
"    background-color: #F9FAFB;\n"
"    border: 1px solid #6BB6FF;\n"
"}")
        self.labelLogo = QLabel(self.centralwidget)
        self.labelLogo.setObjectName(u"labelLogo")
        self.labelLogo.setGeometry(QRect(70, 50, 181, 91))
        self.labelLogo.setStyleSheet(u"border: 1px dashed #999999;\n"
"background-color: rgba(47, 128, 237, 0.06);\n"
"border-radius: 6px;")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1052, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.labelTitle.setText(QCoreApplication.translate("MainWindow", u"\ub098\ub178\uba54\ubaa8\ub9ac PC \uc0ac\uc591 \ud655\uc778 \ud504\ub85c\uadf8\ub7a8", None))
        self.labelSubtitle.setText(QCoreApplication.translate("MainWindow", u"\uc678\uc7a5\ud615 \uc800\uc7a5\uc7a5\uce58 SSD, HDD, USB\ub97c \uc81c\uac70 \ud6c4 \uc2e4\ud589 \ud574\uc8fc\uc138\uc694.", None))
        self.labelQR.setText(QCoreApplication.translate("MainWindow", u"QRcode", None))
        self.btnCopySpecs.setText(QCoreApplication.translate("MainWindow", u"PC \uc0ac\uc591 \ubcf5\uc0ac", None))
        self.btnOpenHomepage.setText(QCoreApplication.translate("MainWindow", u"\ud648\ud398\uc774\uc9c0 \ub9e4\uc785 \uacac\uc801 \ubb38\uc758 \uac8c\uc2dc\ud310", None))
        self.btnOpenKakao.setText(QCoreApplication.translate("MainWindow", u"\uce74\uce74\uc624\ud1a1 \ubb38\uc758 \ubc14\ub85c\uac00\uae30", None))
        self.textSpecs.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'\ub9d1\uc740 \uace0\ub515'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">CPU : Intel(R) Core(TM) i5-14400F @ 2.50GHz</p>\n"
"<hr />\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">RAM :</p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">32598 MB ( 31.83 GB ) SAMSUNG DDR5 5600MHz 16gb (2024\ub1441\uc6d4"
                        ") SAMSUNG DDR5 5600MHz 16gb (2024\ub1441\uc6d4)</p>\n"
"<hr />\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">M/B : Gigabyte B760M AORUS ELITE AX x.x</p>\n"
"<hr />\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">VGA :</p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">NVIDIA GeForce RTX 3050 ( 6G / NVIDIA ) NVIDIA GeForce RTX 3050 ( 6G / NVIDIA )</p>\n"
"<hr />\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">SSD : SAMSUNG MZVL4256HBJD-00B07 ( 238.47 GB )</p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">HDD : SAMSUNG MZVL4256HBJD-00B07 ( 238.47 GB ) </p></body></html>", None))
        self.labelLogo.setText(QCoreApplication.translate("MainWindow", u"logo", None))
    # retranslateUi

