import os,sys
from comptondisplay import ComptonDisplay
from pyqtgraph.Qt import QtGui, QtCore

if __name__ == "__main__":
    
    app = QtGui.QApplication([])
    
    display = ComptonDisplay()
    display.show()
    
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
