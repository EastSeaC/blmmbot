import random
import string
from datetime import datetime, timedelta


def generate_verification_code():
    # 生成包含数字和大写字母的字符集
    characters = string.digits + string.ascii_uppercase

    # 从字符集中随机选择6个字符作为验证码
    verification_code = ''.join(random.choices(characters, k=6))

    return verification_code


def add_minutes_to_current_time(minutes=5):
    # 获取当前时间
    current_time = datetime.now()

    # 加上指定分钟数
    new_time = current_time + timedelta(minutes=minutes)

    return new_time


# 调用函数并打印结果
if __name__ == '__main__':
    result = add_minutes_to_current_time(5)
    print("加上5分钟后的时间:", result)
