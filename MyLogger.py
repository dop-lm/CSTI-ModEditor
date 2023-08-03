# -*- coding: utf-8 -*- 

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from PyQt5 import QtCore
import traceback

logFile = None
logStream = None

def log_exception(MsgBox: bool=False):
    def decorator(func):
        def inner_function(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except Exception as ex:
                msg = traceback.format_exc()
                if MsgBox:
                    QMessageBox.warning(None, "Warning", msg, QMessageBox.Yes, QMessageBox.Yes)
                QtCore.qWarning(bytes(msg, encoding="utf-8"))
        return inner_function
    return decorator

def qt_message_handler(mode, context, message):
    global logFile, logStream
    if mode == QtCore.QtInfoMsg:
        mode = 'INFO'
    elif mode == QtCore.QtWarningMsg:
        mode = 'WARNING'
    elif mode == QtCore.QtCriticalMsg:
        mode = 'CRITICAL'
    elif mode == QtCore.QtFatalMsg:
        mode = 'FATAL'
    else:
        mode = 'DEBUG'
    
    if logFile is not None and logStream is not None:
        logStream << 'line: %d, func: %s(), file: %s\n' % (context.line, context.function, context.file)
        logStream << '  %s: %s\n' % (mode, message)
        logStream.flush()
        # logFile.write(bytes('line: %d, func: %s(), file: %s' % (context.line, context.function, context.file), "utf-8"))
        # logFile.write(bytes('  %s: %s\n' % (mode, message), "utf-8"))
    else:
        print('line: %d, func: %s(), file: %s' % (
            context.line, context.function, context.file))
        print('  %s: %s\n' % (mode, message))

def logInit(log_path: str):
    global logFile, logStream
    logFile = QFile(log_path)
    if not logFile.open(QIODevice.OpenModeFlag.WriteOnly | QIODevice.OpenModeFlag.Text):
        return
    logStream = QTextStream(logFile)
    QtCore.qInstallMessageHandler(qt_message_handler)