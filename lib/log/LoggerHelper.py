import logging
from logging.handlers import TimedRotatingFileHandler
import os

logger = logging.getLogger('timed_logger')
logger.setLevel(logging.INFO)

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

# 每天午夜生成一个新日志文件，并保留最近7天的日志
log_file = os.path.join(log_dir, "app.log")

# 创建带有UTF-8编码的TimedRotatingFileHandler
handler = TimedRotatingFileHandler(
    log_file,
    when="midnight",  # 每天午夜
    interval=1,
    backupCount=7,
    encoding='utf8'  # 使用UTF-8编码
)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)

logger.info("初始日志消息 - 这是一个UTF-8测试: 😊✔️你好世界")  # 包含emoji和中文字符