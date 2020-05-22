import pandas as pd
import numpy as np
import requests
import re
import time as tm
import json
from bs4 import BeautifulSoup


###############   Url加载函数    #########################
# 实现：通过request模拟请求获取url的页面html数据，这里是比较完整的一个url请求函数
# 输入：url地址
# 返回：解析后的url文本内容r.text
##########################################################
def fetchURL(url):

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
    }
    try:
        r = requests.get(url, headers=headers)  # 模拟http请求
        r.raise_for_status()  # 请求结果状态
        return r.text
    except requests.HTTPError as e:
        print(e)
        print("HTTPError")
    except requests.RequestException as e:
        print(e)
    except:
        print("Unknown Error !")


###############   B站评论页面数据爬取函数    #########################
# 实现：通过json解析html文本，获取所需信息：从B站游戏评论中获取评论内容，评分，时间，赞/踩，用户名，用户等级
# 输入：html文本
# 返回：commentlist，包含10条上述结果的二维数组。（每个页面有10条评论）
##########################################################
def parserBiliHtml(html):
    s = json.loads(html)  # 用json解析html文本
    # 准备容器
    content = []
    grade = []
    publish_time = []
    up_count = []
    down_count = []
    user_name = []
    user_level = []
    # 抓取每一条评论记录的所需信息
    for i in range(10):
        try:
            comment = s['data']['list'][i]
            content.append(comment['content'])
            grade.append(comment['grade'])
            publish_time.append(comment['publish_time'])
            up_count.append(comment['up_count'])
            down_count.append(comment['down_count'])
            user_name.append(comment['user_name'])
            user_level.append(comment['user_level'])
        except:
            break
    # 将本页面的10条记录合并保存下来，变成一个二维表格
    commentlist = [content,
                   grade,
                   publish_time,
                   up_count,
                   down_count,
                   user_name,
                   user_level]
    return commentlist  # 返回这个页面的10条评论


###############   Tap评论页面数据爬取函数    #########################
# 实现：通过BS解析html文本，获取所需信息：从Tap游戏评论中获取评论内容，评分，时间
# 输入：html文本
# 返回：3个list对象：本页的内容，评分，评论时间（每个页面有10条评论）
##########################################################
def parserTapHtml(html):
    bs = BeautifulSoup(html, "html.parser")

    comment = bs.select(".review-item-text ")  # 选择页面中的评论模块内容
    pattern_content = '<div class.*?data-review.*?"contents">(.*?)</div>'  # 构建评论的正则表达，选取(.*?)中的内容
    content = re.findall(pattern_content, str(comment), re.S)  # 根据选中模块和正则，抓取需要的内容

    comment = bs.select(".review-item-text ")  # 选择页面中的评论模块内容
    pattern_score = '<i class.*?"width: (.*?)px"></i>'  # 构建评分的正则表达，选取(.*?)中的内容
    score = re.findall(pattern_score, str(comment), re.S)
    score_num = [int(x) / 14 for x in score]  # 抓出来的是字符串（像素宽度），转化为整型，并计算评分

    comment_header = bs.select(".review-item-text .item-text-header")  # 选择页面中评论模块的头部
    pattern_datetime = 'data-dynamic-time=".*?">(.*?)</span>'  # 构建评论日期的正则表达，选取(.*?)中的内容
    datetime = re.findall(pattern_datetime, str(comment_header), re.S)

    return content, score_num, datetime