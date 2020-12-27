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
from bs4 import BeautifulSoup
from sklearn.linear_model import LinearRegression


def get_conf(keyword0, key_conf, conference=None):
    keyword = keyword0.replace(" ", "+")
    number = 10
    html_doc = requests.get(
        "https://scholar.google.co.jp/scholar?hl=ja&as_sdt=0%2C5as_vis=1&num="
        + str(number)
        + "&q="
        + keyword
        + "+"
        + key_conf
    ).text
    soup = BeautifulSoup(html_doc, "html.parser")
    tags1 = soup.find_all("h3", {"class": "gs_rt"})
    tags2 = soup.find_all("div", {"class": "gs_a"})
    tags3 = soup.find_all(text=re.compile("引用元"))
    tags4 = soup.find_all("div", {"class": "gs_fl"})
    thre_diff = 0.1
    title_list = []
    author_list = []
    conf_list = []
    year_list = []
    p_id_list = []
    ci_num_list = []
    for i in range(number):
        conf = tags2[i].text
        year = re.sub(r"\D", "", conf)
        conf = re.sub(r"\d", "", conf)
        if conference is not None:
            diff = difflib.SequenceMatcher(None, conf, conference).ratio()
            if diff > thre_diff:
                conf_list.append(i)
                year_list.append(int(year[0:4]))
        else:
            conf_list.append(i)
            year_list.append(int(year[0:4]))
    tags3 = soup.find_all(text=re.compile("引用元"))
    for i in conf_list:
        citations = tags3[i].replace("引用元", "")
        ci_num_list.append(int(citations))
        # PDF, 書籍, B, HTML のタグを除去
        title = re.sub(r"\[(PDF|書籍|B|HTML)\]", "", tags1[i].text)
        # 空白区切りを廃止
        title = "_".join(title.split(" "))
        # 空欄で始まる場合は詰める
        if title[0] == "_":
            title = title[1:]
        title_list.append(title)
        try:
            elem = elem = tags4[i * 2 + 1].find_all("a")[2]["href"]
            a = 15
            while True:
                if elem[a] == "&":
                    break
                a += 1
            p_id_list.append(elem[15:a])
        except:
            print("")
    cite_years, citations = get_cite(
        conf_list, title_list, year_list, ci_num_list, p_id_list
    )
    return cite_years, citations


def get_cite(conf_list, title_list, year_list, ci_num_list, p_id_list):
    for i in range(len(conf_list)):
        print("paper number: " + str(i))
        print("論文タイトル: " + title_list[i])
        print("発行年: " + str(year_list[i]))
        print("被引用回数: " + str(ci_num_list[i]))
        print("----------------------------------")
    num = input("Select paper number: ")
    num = int(num)

    sleep(1)
    # 引用論文発行年獲得、listに格納
    base_url = "https://scholar.google.com/scholar?start={}&hl=ja&as_sdt=2005&sciodt=0,5&cites={}&scipsc="
    year = year_list[num]  # 対象論文発行年
    ci_num = ci_num_list[num]
    title = title_list[num]
    if ci_num > 100:
        ci_num = input("Number of citations: ")
        ci_num = int(ci_num)
    p_id = p_id_list[num]

    count = [0 for i in range(2020 - year + 1)]  # 発行年から2020年までの引用数格納用のlist作成
    # c = 0
    for n in range(0, ci_num, 10):
        url = base_url.format(str(n), p_id)
        html_doc = requests.get(url).text
        soup = BeautifulSoup(html_doc, "html.parser")
        tags5 = soup.find_all("div", {"class": "gs_a"})
        for tag5 in tags5:
            p_year = tag5.text
            result = re.findall(r"\d+", p_year)

            if len(result) == 0:
                continue
            if len(result) == 1:
                p_year = int(float(result[0]))  # 対象論文を引用した論文の発行年 p_year

            flag = True
            if len(result) > 1:
                for r in result:
                    if len(r) == 4 and int(float(r)) >= year and int(float(r)) <= 2020:
                        p_year = int(float(r))
                        flag = False
                        break
                if flag:
                    continue

            if p_year - year < 0:
                continue
            else:
                print(p_year)
                count[p_year - year] += 1

        sleep(1)

    x = [[year + i] for i in range(2020 - year + 1)]  # 対象論文発行年から2020年までを要素として持つリスト作成

    # plt.plot(x, count)
    # plt.xlabel("引用年")
    # plt.ylabel("引用数")

    # plt.show()
    # print(c)
    plot_citations(title, year, count)
    # print(x) #countに対応する年
    # print(count) #各年毎の引用数

    return x, count


def fit_reg(cite_years, citations, reg):
    """fit a regression model to cumulative_citations
    :param cite_years: int, year when a target paper has been published
    :param cumulative_citations: list, cumulative sum of citations
    :param reg: object, regression model from sklearn
    :return coef: numpy, slope of regression model
    """
    coef = reg.fit(cite_years, citations).coef_
    return coef


def plot_citations(title, cite_years, citations):
    """plot cumulative citations
    :param title: str, title of target paper
    :param cite_years: int, year when a target paper has been published
    :param citations: list, year of citations
    """
    plt.xlabel("year")
    plt.ylabel("citations")
    plt.title(title)
    plt.xlim(cite_years, 2020)
    plt.gca().get_xaxis().get_major_formatter().set_useOffset(False)
    plt.gca().get_xaxis().set_major_locator(ticker.MaxNLocator(integer=True))
    plt.plot(range(cite_years, 2021), citations)
    plt.savefig(f"{title}.png")
    return


if __name__ == "__main__":
    keyword0 = ""
    key_conf = "VLDB"
    conference = "International Conference on Very Large Data Bases"
    cite_years, citations = get_conf(keyword0, key_conf, conference)
    coef = fit_reg(cite_years, citations, reg=LinearRegression())
    print(f"coef: {coef}")
    cite_years = [i[0] for i in cite_years]
    with open("cite_years.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(cite_years)
        writer.writerow(citations)
