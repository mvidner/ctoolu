#!/usr/bin/env python3
from PyQt5.QtCore import (Qt, QPoint)
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import (QApplication, QMenu, QAction)

def clicked():
    print("CLICKED")

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    menu = QMenu()
    # must assign a variable, passing directly does not work
    # see https://stackoverflow.com/questions/57807036
    action = QAction("&Click me", triggered=clicked)
    menu.addAction(action)
    # menu.show()
    menu.exec_(QCursor().pos() + QPoint(10, 20))
    #sys.exit(app.exec_())
