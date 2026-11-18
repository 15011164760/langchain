'''
Author: yangdongxu
Date: 2026-11-18 14:51:03
LastEditors: yangdongxu
LastEditTime: 2026-11-18 20:03:08
FilePath: \langchain\webData.py
'''
# 导入所需的库
import requests  # 用于发送HTTP请求
from bs4 import BeautifulSoup  # 用于解析HTML内容
header={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36"
}
response = requests.get('https://movie.douban.com/top250',headers=header)  # 发送GET请求
# print(response.status_code)  # 打印响应状态码，200表示请求成功
# print(response.text)  # 打印响应内容
soup = BeautifulSoup(response.text, 'html.parser')  # 解析HTML内容
# print(soup)  # 打印解析后的HTML内容
titles = soup.find_all('span',class_='title')  # 查找所有的<span>标签
print(titles)  # 打印解析后的HTML内容
for title in titles:  # 遍历所有的<span>标签
    if title.string and  '/' not in title.string:
        print(title.string)  # 打印每个<span>标签的文本内容

