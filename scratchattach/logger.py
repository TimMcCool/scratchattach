from datetime import datetime
import io
import sys

istime24hour = False

"""
This logging system was made by mas6y6

To import logger use (from .logger import log)

Functions:

log.info(<TEXT>,process=<CHILD_PROCESS>)

log.warning(<TEXT>,process=<CHILD_PROCESS>)

log.error(<TEXT>,process=<CHILD_PROCESS>)

log.fatul(<TEXT>,process=<CHILD_PROCESS>)

log.success(<TEXT>,process=<CHILD_PROCESS>)
"""

class textcolors:
    """ANSI color codes"""

    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    BROWN = "\033[33m"
    BLUE = "\033[34m"
    PURPLE = "\033[35m"
    CYAN = "\033[36m"
    YELLOW = "\033[33m"
    LIGHT_GRAY = "\033[0;37m"
    DARK_GRAY = "\033[1;30m"
    LIGHT_RED = "\033[1;31m"
    LIGHT_GREEN = "\033[1;32m"
    LIGHT_YELLOW = "\033[1;33m"
    LIGHT_BLUE = "\033[1;34m"
    LIGHT_PURPLE = "\033[1;35m"
    LIGHT_CYAN = "\033[1;36m"
    LIGHT_WHITE = "\033[1;37m"
    BOLD = "\033[1m"
    FAINT = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    NEGATIVE = "\033[7m"
    CROSSED = "\033[9m"
    END = "\033[0m"

def _gettime():
    global istime24hour
    if istime24hour:
        return datetime.now().strftime("%H:%M:%S")
    else:
        if datetime.now().hour > 12:
            return f"{datetime.now().hour - 12}:{datetime.now().minute}:{datetime.now().second}"
        else:
            return (
                f"{datetime.now().hour}:{datetime.now().minute}:{datetime.now().second}"
            )
            

class log:
    def config(use_24_hour=False):
        global istime24hour
        istime24hour = use_24_hour
    
    def fatul(text, process=None):
        if process == None:
            processname = "UNKNOWN"
            print(
                textcolors.RED
                + textcolors.BOLD
                + "["
                + _gettime()
                + "] "
                + "[FATUL] "
                + text
                + textcolors.END
            )
        else:
            processname = process
            print(
                textcolors.RED
                + "["
                + _gettime()
                + "] "
                + f"[{processname}] "
                + textcolors.BOLD
                + "[FATUL] "
                + text
                + textcolors.END
            )

    def error(text, process=None):
        if process == None:
            print(
                textcolors.RED
                + "["
                + _gettime()
                + "] "
                + "[ERROR] "
                + text
                + textcolors.END
            )
        else:
            processname = process
            print(
                textcolors.RED
                + "["
                + _gettime()
                + "] "
                + f"[{processname}] "
                + "[ERROR] "
                + text
                + textcolors.END
            )

    def warning(text, process=None):
        if process == None:
            print(
                textcolors.YELLOW
                + "["
                + _gettime()
                + "] "
                + "[WARNING] "
                + text
                + textcolors.END
            )
        else:
            processname = process
            print(
                textcolors.YELLOW
                + "["
                + _gettime()
                + "] "
                + f"[{processname}] "
                + "[WARNING] "
                + text
                + textcolors.END
            )

    def success(text, process=None):
        if process == None:
            print(
                textcolors.GREEN
                + "["
                + _gettime()
                + "] "
                + "[SUCCESS] "
                + text
                + textcolors.END
            )
        else:
            processname = process
            print(
                textcolors.GREEN
                + "["
                + _gettime()
                + "] "
                + f"[{processname}] "
                + "[SUCCESS] "
                + text
                + textcolors.END
            )

    def log(text, process=None):
        if process == None:
            print("[" + _gettime() + "] " + "[INFO] " + text)
        else:
            processname = process
            print("[" + _gettime() + "] " + f"[{processname}] " + "[INFO] " + text)

    def info(text, process=None):
        if process == None:
            print("[" + _gettime() + "] " + "[INFO] " + text)
        else:
            processname = process
            print("[" + _gettime() + "] " + f"[{processname}] " + "[INFO] " + text)
