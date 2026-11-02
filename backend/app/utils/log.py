from pathlib import Path
from app.config import Settings
from datetime import datetime

class Log:
    def __init__(self):
        self.log_file_path = Settings.LOG_FILE
        Path.touch(self.log_file_path)

    def info(self, msg: str):
        with open(self.log_file_path, '+w') as f:
            f.write(f"{datetime()} [INFO] {msg}\n")
            
    def error(self, msg: str):
            with open(self.log_file_path, '+w') as f:
                f.write(f"{datetime()} [ERROR] {msg}\n")

    def warn(self, msg: str):
            with open(self.log_file_path, 'a+') as f:
                f.write(f"{datetime()} [WARN] {msg}\n")
