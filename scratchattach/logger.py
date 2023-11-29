from .textcolors import textcolors
from datetime import datetime

istime24hour = True


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
