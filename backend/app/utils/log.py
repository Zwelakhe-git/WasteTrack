from pathlib import Path
from app.config import settings
from datetime import datetime

class Log:
    def __init__(self):
        self.log_file_path: Path = Path(settings.LOG_FILE)
        self.log_file_path.parent.mkdir(parents=True, exist_ok=True)
        Path.touch(self.log_file_path, exist_ok=True)

    def info(self, msg: str):
        with open(self.log_file_path, '+w') as f:
            f.write(f"{datetime.now().isoformat()} [INFO] {msg}\n")

    def error(self, msg: str):
            with open(self.log_file_path, '+w') as f:
                f.write(f"{datetime.now().isoformat()} [ERROR] {msg}\n")

    def warn(self, msg: str):
            with open(self.log_file_path, 'a+') as f:
                f.write(f"{datetime.now().isoformat()} [WARN] {msg}\n")

log = Log()