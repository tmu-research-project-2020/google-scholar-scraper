import requests, os, datetime, argparse
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import pandas as pd
from time import sleep
import warnings,re
from matplotlib import pyplot as plt
import time
import timeit
import numpy as np
from sklearn.linear_model import LinearRegression


def get_cite(keyword):
    number = 1
    html_doc = requests.get("https://scholar.google.co.jp/scholar?hl=ja&as_sdt=0%2C5&num=" + str(number) + "&q=" + keyword).text
    soup = BeautifulSoup(html_doc, "html.parser") # BeautifulSoupの初期化

    #論文タイトル取得
    tag1 = soup.find("h3", {"class": "gs_rt"})
    title = tag1.text.replace("[HTML]","")

    #発行年取得
    tag2 = soup.find("div", {"class": "gs_a"})
    year = tag2.text
    year = re.sub(r'\D', '', year)
    

    #引用数取得
    tags3 = soup.find_all(text=re.compile("引用元"))  # citation
    for tag3 in tags3:
        citations = tag3.replace("引用元","")
        ci_num = int(citations)

    print('論文タイトル: ' + title)
    print('発行年: ' + year)
    print('被引用回数: ' + str(ci_num))

    #論文ID取得(IDは引用元をクロールするのに必要)
    tags4 = soup.find_all("div", {"class": "gs_fl"})
    for tag4 in tags4:
        try:
            elem = tag4.find_all('a')[2]['href']
            a = 15
            while True:
                if elem[a] == '&':
                    break
                a+=1
            p_id = elem[15:a]
        except:
            print('')

    sleep(1)

    #引用論文発行年獲得、listに格納

    base_url = 'https://scholar.google.com/scholar?start={}&hl=ja&as_sdt=2005&sciodt=0,5&cites={}&scipsc='
    year = int(year) #対象論文発行年


    count = [0 for i in range(2020-year+1)] #発行年から2020年までの引用数格納用のlist作成
    #c = 0
    for n in range(0, ci_num, 10):
        url = base_url.format(str(n), p_id)
        html_doc = requests.get(url).text
        soup = BeautifulSoup(html_doc, "html.parser")
        tags2 = soup.find_all("div", {"class": "gs_a"})
        for tag2 in tags2:
            p_year = tag2.text
            result = re.findall(r"\d+", p_year)

            if len(result) == 0:
                continue
            if len(result) == 1:
              p_year = int(float(result[0])) #対象論文を引用した論文の発行年 p_year
            
            flag = True
            if len(result) > 1:
              for r in result:
                if len(r) == 4 and int(float(r)) >= year and  int(float(r)) <= 2020:
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

    x = [[year+i] for i in range(2020-year+1)] #対象論文発行年から2020年までを要素として持つリスト作成

    #plt.plot(x, count)
    #plt.xlabel("引用年")
    #plt.ylabel("引用数")

    #plt.show()
    #print(c)
    plot_citations(title, year, count)
    #print(x) #countに対応する年
    #print(count) #各年毎の引用数

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
    plt.plot(range(cite_years, 2021), citations)
    plt.savefig(f"{title}.png")
    return


keyword = "microphone array beamforming tutorial"
cite_years, citations = get_cite(keyword)
coef = fit_reg(cite_years, citations, reg=LinearRegression())
print(f"coef: {coef}")
