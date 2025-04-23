import logging
from logging.handlers import TimedRotatingFileHandler
import os

logger = logging.getLogger('timed_logger')
logger.setLevel(logging.INFO)

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# 每天午夜生成一个新日志文件，并保留最近 7 天的日志
log_file = os.path.join(log_dir, "app.log")
handler = TimedRotatingFileHandler(
    log_file,
    when="midnight",  # 每天午夜
    interval=1,
    backupCount=7
)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)

logger.info("初始日志消息")  # 每天会生成一个新的日志文件，如 app.log.2024-01-01
