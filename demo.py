'''
Author: yangdongxu
Date: 2026-11-03 17:32:39
LastEditors: yangdongxu
LastEditTime: 2026-11-17 16:33:36
FilePath: \langchain\demo.py
'''
print("hello world")
# height=float(input('你的身高是多少：'))
# weight=float(input('你的体重是多少kg：'))
# BMI=weight/(height*height)
# print(float(BMI))
# #计算加减乘除
# sum = weight+height
# print(sum)
# shopList = ['电脑', '键盘']
# shopList.append('鼠标')
# shopList.remove(shopList[0])
# print(shopList)
# nums = [1, 2, 3, 4]
#
# if 3 in nums:
#     print("存在")
# else:
#     print("不存在")
# slang_dict = {}
# slang_dict["向数组"] = "源于小说《意林》的科幻概念，现指在XR(扩展现实)、数字孪生、区块链和AI..." # 部分截断，随便补全
# slang_dict["绝绝子"] = "该词流行于某网络节目，节目中一些粉丝用“绝绝子”为选手加油。多用于赞美，表示“好极了”、“太棒了”。"
# slang_dict["躺平"] = "该词指人在面对t压力时，内心再无波澜，主动放弃，不做任何反抗。“躺平”更像是年轻人的一种解压和调整方式。"
# slang_dict["伤害性不高，侮辱性极强"] = "一段网络视频中，两名男子相互夹菜，而同桌的另一名女子则显得十分孤单。于是有网友评论：伤害性不高，侮辱性极强。"
# slang_dict["我看不懂，但我大受震撼"] = "源自导演李安在纪录片《打扰伯格曼》（2013）里评价一部影视作品的话。"
# slang_dict["强国有我"] = "源自建党百年天安门广场庆典上青年学子的庄严宣誓。“请党放心，强国有我”是青年一代对党和人民许下的庄重誓言。"
# print(slang_dict)
shopPrice={
    'computer':100,
    'computer2':200,
    'computer3':300,
}
# for key, value in shopPrice.items():
#     if value > 200:
#         print(key)
# searchWord=input('请输入需要查找的字典数据是:')
# if searchWord in slang_dict:
#     print("您要查找的词语是"+searchWord+" 含义是："+slang_dict[searchWord])
# else:
#     print('您要查找的:'+searchWord+'词语暂时不存在字典中')
#     print("当前字典收录数据条数为："+str(len(slang_dict)))
# sum=0
# for i in range(1,101):
#     sum+=i
# print(sum)
# count=0
# sum=0
# item=input('请输入一个数输入数字，停止输入q:')
# while item!='q':
#     item=float(item)
#     sum+=item
#     count+=1
#     item = input('请输入一个数输入数字，停止输入q:')
# if count==0:
#     result=0
# else:
#     result=sum/count
# print("平均值是"+str(result))

from pathlib import Path

# 1. 获取当前脚本所在的绝对目录（最常用）
current_dir = Path(__file__).resolve().parent
print(f"脚本所在目录: {current_dir}")

# 2. 获取当前脚本的完整绝对路径
current_file = Path(__file__).resolve()
print(f"脚本完整路径: {current_file}")

# 3. 获取终端运行程序时的当前工作目录
cwd = Path.cwd()
print(f"终端工作目录: {cwd}")