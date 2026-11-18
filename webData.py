'''
Author: yangdongxu
Date: 2026-11-18 14:51:03
LastEditors: yangdongxu
LastEditTime: 2026-11-18 14:57:29
FilePath: \langchain\webData.py
'''
# 导入所需的库
import requests  # 用于发送HTTP请求
from bs4 import BeautifulSoup  # 用于解析HTML文档
import pandas as pd  # 用于数据处理和CSV文件生成
import time  # 用于程序延时
import random
