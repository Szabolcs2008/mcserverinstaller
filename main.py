import datetime
import os
import sys
import requests

cmdline_args = sys.argv


class Logger:
    DEBUG = 0
    INFO = 1
    WARN = 2
    ERR = 3
    FATAL = 4
    SILENT = 5

    def __init__(self):
        super().__init__()
        self.loglevel = self.INFO
        self.logFile = "logs/" + datetime.datetime.now().strftime("%y_%m_%d - %H_%M_%S") + ".log"

        if not os.path.exists("logs/"):
            try:
                os.mkdir("logs/")
                self.log("Successfully created log folder", self.INFO)
            except:
                self.log("Failed to create log folder!", self.FATAL)
                os._exit(1)

    def setLogLevel(self, newLogLevel):
        if newLogLevel <= self.SILENT:
            self.loglevel = newLogLevel
        else:
            raise ValueError("Log level must be between 'DEBUG' and 'SILENT' (0-5)")

    # I don't want to use a proper logger, because it's easier for me like this
    def log(self, message, logLevel=INFO):
        if logLevel != self.SILENT:
            if logLevel >= self.loglevel:
                t = datetime.datetime.now().strftime("%H:%M:%S")
                if logLevel == self.INFO:
                    print(f"[{t} INFO] {message}")
                    self.__writeToFile(f"[{t} INFO] {message}")
                elif logLevel == self.WARN:
                    print(f"\033[33m[{t} WARNING] {message}\033[0m")
                    self.__writeToFile(f"[{t} WARNING] {message}")
                elif logLevel == self.ERR:
                    print(f"\033[31m[{t} ERROR] {message}\033[0m")
                    self.__writeToFile(f"[{t} ERROR] {message}")
                elif logLevel == self.FATAL:
                    print(f"\033[31;1m[{t} FATAL] {message}\033[0m")
                    self.__writeToFile(f"[{t} FATAL] {message}")
                elif logLevel == self.DEBUG:
                    print(f"\033[32m[{t} DEBUG] {message}\033[0m")
                    self.__writeToFile(f"[{t} DEBUG] {message}")
        else:
            raise ValueError("Log level cannot be 'SILENT'!")

    def __writeToFile(self, data, end="\n"):
        with open(self.logFile, "a+") as file:
            file.write(data+end)

logger = Logger()

def getDownloadSources():
    url = "https://raw.githubusercontent.com/Szabolcs2008/mcserverinstaller/master/sources.json"
    resp = requests.get(url)
    if resp.status_code == 200:
        pass
    else:
        if os.path.exists("sources.json"):
            logger.log("Failed to update the download sources! The downloaded files might be out of date! Proceed with caution", Logger.WARN)
        else:
            logger.log("Failed to download the file sources! The program will exit.", Logger.FATAL)

getDownloadSources()