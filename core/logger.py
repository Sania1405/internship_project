# Importing standard Python logging library.
import logging
# Importing sys to access sys.stdout, which represents the terminal/command prompt window.
import sys
# Importing Path to create and check directories on the local system.
from pathlib import Path

# Creates a directory named "logs" in the project root if it does not already exist.
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Creates a custom logging object named "voicebot_logger".
logger = logging.getLogger("voicebot_logger")
# Sets the threshold to INFO. Logging levels lower than INFO are: DEBUG (used for fine-grained debugging details) and NOTSET.
# Since level is set to INFO, the logger will ignore all DEBUG messages.
logger.setLevel(logging.INFO)

# logging.StreamHandler(sys.stdout) is a standard built-in function used as-is to print logs to the terminal screen.
console_handler = logging.StreamHandler(sys.stdout)
# logging.FileHandler("logs/app.log") is a standard function used as-is to save logs into the logs/app.log file.
file_handler = logging.FileHandler("logs/app.log")

# Tells console_handler to print only INFO level or higher to the terminal window.
console_handler.setLevel(logging.INFO)
# Tells file_handler to write DEBUG level and higher to logs/app.log file (capturing more granular details on disk).
file_handler.setLevel(logging.DEBUG) 

# Sets the exact string layout for the log entry: Timestamp - Logger Name - Severity Level - Message.
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Adds handlers to the logger only if they aren't already added, avoiding duplicate printing in the terminal.
if not logger.handlers:
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)