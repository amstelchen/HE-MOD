# File: main.py
import sys
import os
# import xdg
import subprocess
import logging
import contextlib

from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene, QMessageBox, QFileDialog, 
                               QGraphicsItem, QGraphicsLineItem, QGraphicsTextItem, QGraphicsSimpleTextItem)
from PySide6.QtCore import QFile, QIODevice, QCoreApplication, Qt
from PySide6.QtGui import QImage, QPixmap, QPainter, QIcon, QStandardItemModel, QStandardItem, QFont, QColor

PROG = "Hacker Evolution - Mod Editor"
VERSION = "0.1.0"
AUTHOR = "Copyright (C) 2023, by Michael John"
DESC = "A Python port of the Hacker Evolution Mod Editor MFC application"
GithubLink = "https://github.com/amstelchen/HE-MOD"

sheet = """
QGroupBox {
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #E0E0E0, stop: 1 #FFFFFF);
    border: 2px solid gray;
    border-radius: 5px;
    margin-top: 1ex; /* leave space at the top for the title */
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center; /* position at the top center */
    padding: 0 3px;
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #FF0ECE, stop: 1 #FFFFFF);
}"""

def main():

    ModFilePath = ""

    def ReadModFile(ModFilePath):
        logging.debug(f"Reading {ModFilePath}...")
        with open(ModFilePath, "rt") as mod_file:
            try:
                mod_name, mod_path, mod_desc, mod_author = mod_file.readlines() # .split("\n")
            except ValueError:
                mod_file.seek(0)
                mod_name, mod_path, mod_desc, _, _, _ = mod_file.readlines() # .split("\n")
            finally:
                #print(mod_author)
                window.lineEdit_Mod_name.setText(mod_name)
                window.lineEdit_Mod_desc.setText(mod_desc)
        ModFilePath = os.path.join(os.path.dirname(os.path.realpath(ModFilePath)), mod_path.strip())
        with open(os.path.join(ModFilePath, "level-list"), "rt") as level_file:
            num_levels = level_file.readline().strip()
            level_names = level_file.readlines()
            logging.debug(f"num_levels: {num_levels}")
            model_Level_list = QStandardItemModel()
            model_Server_list = QStandardItemModel()
            window.listView_Level_list.setModel(model_Level_list)
            window.listView_Server_list.setModel(model_Server_list)
            model_Service_list = QStandardItemModel()
            window.listView_Service_list.setModel(model_Service_list)
            model_Files_list = QStandardItemModel()
            window.listView_File_list.setModel(model_Files_list)
        # for level in range(1, int(num_levels) + 1):
        for level in level_names:
            #LevelPath = os.path.join(ModFilePath, f"level-{level}")
            LevelPath = os.path.join(ModFilePath, level.strip())
            item_level = QStandardItem(f"{level.strip()}")
            model_Level_list.appendRow(item_level)
            image_big_b = QPixmap(os.path.join(LevelPath, "targetmap.bmp"))
            image_sml_b = QPixmap(os.path.join(LevelPath, "introimage.bmp"))
            scene_big.addPixmap(image_big_b)
            scene_sml.addPixmap(image_sml_b)

            with open(LevelPath + '/levelinfo') as levelinfo_file:
                local = levelinfo_file.readline().split(" ")
                local_x, local_y = local[0], local[1]

                text_item = QGraphicsTextItem("LOCALHOST")
                greenColor = QColor(Qt.green);
                text_item.setDefaultTextColor(greenColor)
                text_item.setPos(float(local_x), float(local_y))
                scene_big.addItem(text_item)

            with open(LevelPath + '/hostlist') as hostlist_file:
                num_hosts = hostlist_file.readline().strip()
                logging.debug(f"num_hosts: {num_hosts}")
                #hostlist_file.seek(0)
                for host in hostlist_file.readlines():
                    if host == "\n":
                        logging.debug("skipping empty line.")
                        break

                    item_host = QStandardItem(f"{host.strip()}")
                    model_Server_list.appendRow(item_host)
                    logging.debug(host.strip())
                    host_name = host.split(" ")[0]

                    with open(os.path.join(LevelPath, host_name, "info")) as info_file:
                        x, y = info_file.readline().strip().split(" ")
                        money = int(info_file.readline().strip())
                        encryption = int(info_file.readline().strip())

                    text_item = QGraphicsTextItem(host_name)
                    greenColor = QColor(Qt.green);
                    text_item.setDefaultTextColor(greenColor)
                    text_item.setPos(float(x), float(y))
                    scene_big.addItem(text_item)

                    with open(os.path.join(LevelPath, host_name, "services"), encoding="iso8859-1") as services_file:
                        num_svc = services_file.readline().strip()
                        for service in services_file.readlines():
                            try:
                                port, svc_name, _ = service.split(" ")
                                item_svc = QStandardItem(f"Port {port}: \t{svc_name}")
                                model_Service_list.appendRow(item_svc)
                                logging.debug(f"Port {port}: \t{svc_name}")
                            except ValueError:
                                logging.debug("skipping empty line.")
                    with open(os.path.join(LevelPath, host_name, "filerules")) as rules_file:
                        num_rules = rules_file.readline().strip()
                        for rule in rules_file.readlines():
                            try:
                                port, file_name = rule.strip().split(" ")
                                item_rule = QStandardItem(f"Port {port}: \t{file_name}")
                                model_Files_list.appendRow(item_rule)
                                logging.debug(f"Port {port}: \t{file_name}")
                            except ValueError:
                                logging.debug("skipping empty line.")

            #scene_big.setForegroundBrush(QColor(255, 255, 255, 0))
            #scene_big.addText("foo", QFont("Times", 100))
            #scene_big.addText(text_item)

            #window.graphicsView = view_big

            #view_big = window.graphicsView
            view_big.setScene(scene_big)
            view_sml.setScene(scene_sml)

            #view_big = window.graphicsView

            #view_big.setRenderHint(QPainter.Antialiasing)
            #view_big.setRenderHint(QPainter.SmoothPixmapTransform)
            #view_big.setRenderHint(QPainter.TextAntialiasing)

            #window.graphicsView.show()

    def action_Open_mod_clicked(s):
        dialog = QFileDialog()
        #dialog.setFileMode(QFileDialog.Directory)
        dialog.setFileMode(QFileDialog.ExistingFile)
        #dialog.setOption(QFileDialog.ShowDirsOnly)
        #dialog.exec()
        #directory = dialog.getExistingDirectory(window, 'Choose Directory', os.curdir)
        ModFilePath, _ = dialog.getOpenFileName(window)
        #print(directory)
        #ModFilePath = directory
        if ModFilePath != "":
            ReadModFile(ModFilePath)

    def actionVisit_clicked(s):
        if sys.platform == "linux":
            subprocess.run(["xdg-open", GithubLink])

    def actionAbout_clicked(s):
        QMessageBox.about(window, PROG + " " + VERSION, PROG + "\n" + VERSION  + "\n" + DESC + "\n" + AUTHOR)

    def actionExit_clicked(s):
        sys.exit()

    #def actionAbout_clicked(s):
    #    pass

    if len(sys.argv) > 1:
        loglevel = sys.argv[1]
    else:
        loglevel = "INFO"
    numeric_level = getattr(logging, loglevel.upper(), logging.INFO)
    # print(loglevel, numeric_level)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)
    logging.basicConfig(format='%(levelname)s:%(message)s', level=numeric_level)

    #os.environ["PYSIDE_DESIGNER_PLUGINS"]=os.path.dirname(__file__)
    #print(os.path.dirname(__file__))
    #app = QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    #app = QApplication.setAttribute(Qt.AA_ShareOpenGLContexts, False)
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

    app = QApplication(sys.argv)
    #QCoreApplication.setAttribute(QtCore Application.Qt", True)
    #app.Set
    #app.setAttribute(attribute) # Qt::AA_ShareOpenGLContexts
    #app.setStyleSheet(sheet)
    #view = QGraphicsView()
    scene_big = QGraphicsScene()
    scene_sml = QGraphicsScene()

    ui_file_name = os.path.dirname(__file__) + "/HE_MOD.ui"
    ui_file = QFile(ui_file_name)
    if not ui_file.open(QIODevice.ReadOnly):
        print(f"Cannot open {ui_file_name}: {ui_file.errorString()}")
        sys.exit(-1)
    loader = QUiLoader()
    window = loader.load(ui_file)
    ui_file.close()
    if not window:
        print(loader.errorString())
        sys.exit(-1)

    # Read an image from file and creates an ARGB32 string representing the image
    #img = QImage()
    #img.load('/steam/SteamLibrary/steamapps/common/Hacker Evolution/hemod-hackerevolution/he-level-1/targetmap.bmp' )
    #imgAsByteArray = img.ToBytes()

    image_big = QPixmap("/steam/SteamLibrary/steamapps/common/Hacker Evolution/hemod-hackerevolution/he-level-1/targetmap.bmp")
    image_sml = QPixmap("/steam/SteamLibrary/steamapps/common/Hacker Evolution/hemod-hackerevolution/he-level-1/introimage.bmp")

    scene_big.addPixmap(image_big)
    scene_sml.addPixmap(image_sml)

    #view.setScene(scene)
    #view.show()

    icon = QIcon(os.path.dirname(__file__) + "/he_mod.ico")

    window.setWindowTitle(PROG + " " + VERSION)

    # Displays the image using PySide
    #label = QLabel()

    #imgQT = QImage( imgAsByteArray, img.width, img.height, QImage.Format_ARGB32 )
    #pixMap = QPixmap.fromImage( img )

    #window.graphicsView.setPixmap( pixMap )
    #graphicsView.show()

    #window.graphicsView.setScene(scene)

    view_big = window.graphicsView
    view_sml = window.graphicsView_2

    view_big.setScene(scene_big)
    view_sml.setScene(scene_sml)

    view_big.setRenderHint(QPainter.Antialiasing)
    view_big.setRenderHint(QPainter.SmoothPixmapTransform)
    view_big.setRenderHint(QPainter.TextAntialiasing)
    #view.setRenderHint(QPainter.HighQualityAntialiasing)

    window.graphicsView = view_big
    window.graphicsView_2 = view_sml

    window.graphicsView.show()

    #window.windowIcon = icon
    window.setWindowIcon(icon)

    window.show()

    window.action_Visit.triggered.connect(actionVisit_clicked)
    window.action_About.triggered.connect(actionAbout_clicked)
    window.action_Exit.triggered.connect(actionExit_clicked)
    window.action_Open_mod.triggered.connect(action_Open_mod_clicked)

    #if loglevel == "DEBUG":
    #    ReadModFile("/home/mic/Projekte/HE-MOD/Hacker Evolution (symlink)/hemod-Reinsertion.mod")

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
