from bs4 import BeautifulSoup
import argparse
import csv
import datetime
import difflib
import os
import pprint
import re
import time
import timeit
import warnings
from time import sleep

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import requests
from sklearn.linear_model import LinearRegression

def get_snippet(soup):
    tags = soupl.find_all("div", {"class": "gs_rs"})
    snippet_list = [tags[i].text for i in range(len(tags))]
    return snippet_list

def get_title_and_url(soup):
    tags1 = soup.find_all("h3", {"class": "gs_rt"})
    title_list = []
    url_list = []
    for tag1 in tags1:
        # タイトル取得
        # PDF, 書籍, B, HTML のタグを除去
        title = re.sub(r"\[(PDF|書籍|B|HTML)\]", "", tag1.text)
        # 空白区切りを廃止
        title = "_".join(title.split(" "))
        if title[0] == "_":
            title = title[1:]
        title_list.append(title)

        # url取得
        url = tag1.select("a")[0].get("href")
        url_list.append(url)
    return title_list,url_list

def get_writer_and_year(soup):
    tags2 = soup.find_all("div", {"class": "gs_a"})
    writer_list = []
    year_list = []
    for tag2 in tags2:
        # 著者取得
        writer = tag2.text
        writer = re.sub(r'\d', '', writer)
        for char in range(0,len(writer)):
          if writer[char] == '-':
            writer = writer[2:char-1]
            break
        writer_list.append(writer)

        # 論文発行年取得
        year = tag2.text
        year = re.sub(r'\D', '', year)
        year_list.append(year)
    return writer_list,year_list

def get_citations(soup):
    tags3 = soup.find_all(text=re.compile("引用元"))
    ci_num_list = []
    for tag3 in tags3:
        # 被引用数取得
        citation = tag3.replace("引用元", "")
        ci_num_list.append(int(citation))
    return ci_num_list

def get_id(soup):
    tags4 = soup.find_all("div", {"class": "gs_fl"})
    p_id_list = []
    for tag4 in tags4:
        # 論文ID取得
        try:
            elem =  tag4.find_all("a")[2]["href"]
            a = 15
            while True:
                if elem[a] == "&":
                    break
                a += 1
            p_id_list.append(elem[15:a])
        except:
            print("")
    return p_id_list

  
if __name__ == "__main__":
    number = 5
    keyword = "machine learning"
    html_doc = requests.get("https://scholar.google.co.jp/scholar?hl=ja&as_sdt=0%2C5&num=" + str(number) + "&q=" + keyword).text
    soup = BeautifulSoup(html_doc, "html.parser") # BeautifulSoupの初期化
    title_list,url_list = get_title_and_url(soup)
    writer_list,year_list = get_writer_and_year(soup)
    ci_num_list = get_citations(soup)
    p_id_list = get_id(soup)

    print(title_list,url_list)
    print(writer_list,year_list)
    print(ci_num_list)
    print(p_id_list)


