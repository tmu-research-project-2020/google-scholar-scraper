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


def make_url(keyword, conf, author):
    """ make url for search papers
    :param keyword: str or None
    :param conf: str or None, conference information
    :param author: str or None, author information
    :return: url
    """
    assert (
        keyword is not None or conf is not None or author is not None
    ), "KeywordNotFoundError"
    url = "https://scholar.google.co.jp/scholar?&hl=ja&as_sdt=0%2C5"
    if keyword is not None:
        url += f"&as_q={keyword}"
    else:
        url += "&as_q="
    if conf is not None:
        url += f"&as_publication={conf}"
    if author is not None:
        author = "+".join(author.split())
        url += f"&as_sauthors={author}"
    return url


def get_snippet(soup):
    """ obtain snippet from soup
    :param soup: parsed html by BeautifulSoup
    :return: snippet_list
    """
    tags = soup.find_all("div", {"class": "gs_rs"})
    snippet_list = [tags[i].text for i in range(len(tags))]
    return snippet_list


def get_title_and_url(soup):
    """ obtain title and url from soup
    :param soup: parsed html by BeautifulSoup
    :return: title_list, url_list
    """
    tags1 = soup.find_all("h3", {"class": "gs_rt"})
    title_list = []
    url_list = []
    for tag1 in tags1:
        # タイトル取得
        # PDF, 書籍, B, HTML, 引用, Cのタグを除去
        title = re.sub(r"\[(PDF|書籍|B|HTML|引用|C)\]", "", tag1.text)
        # 空白区切りを廃止
        title = "_".join(title.split(" "))
        if title[0] == "_":
            title = title[1:]
        title_list.append(title)

        # url取得
        try:
            url = tag1.select("a")[0].get("href")
            url_list.append(url)
        except IndexError:
            url_list.append(None)
    return title_list, url_list


def get_writer_and_year(soup):
    """ obtain writer(author) and year from soup
    :param soup: parsed html by BeautifulSoup
    :return: writer_list, year_list
    """
    tags2 = soup.find_all("div", {"class": "gs_a"})
    writer_list = []
    year_list = []
    for tag2 in tags2:
        # 著者取得
        """
        writer = tag2.text
        writer = re.sub(r"\d", "", writer)
        for char in range(0, len(writer)):
            if writer[char] == "-":
                writer = writer[2 : char - 1]
                break
        """
        writer = tag2.text.split("\xa0- ")[0]
        writer_list.append(writer)

        # 論文発行年取得
        year = tag2.text
        year = re.sub(r"\D", "", year)
        # yearが5桁以上だった場合の例外処理
        if len(year) > 4:
            year_list.append(year[len(year)-4 : len(year)])
        else:
            year_list.append(year)
    return writer_list, year_list


def get_citations(soup):
    """ obtain number of citations from soup
    :param soup: parsed html by BeautifulSoup
    :return: ci_num_list
    """
    tags3 = soup.find_all(text=re.compile("引用元"))
    ci_num_list = []
    for tag3 in tags3:
        # 被引用数取得
        citation = tag3.replace("引用元", "")
        ci_num_list.append(int(citation))
    return ci_num_list


def get_id(soup):
    """ obtain paper id from soup
    :param soup: parsed html by BeautifulSoup
    :return: ci_num_list
    """
    tags4 = soup.find_all("div", {"class": "gs_fl"})
    p_id_list = []
    for tag4 in tags4:
        # 論文ID取得
        try:
            elem = tag4.find_all("a")[2]["href"]
            a = 15
            while True:
                if elem[a] == "&":
                    break
                a += 1
            p_id_list.append(elem[15:a])
        except:
            print("")
    return p_id_list


def scraping_papers(url):
    """ scrape 100 papers
    :param url: target url
    :return: title_list, url_list, writer_list, year_list, ci_num_list, p_id_list, snippet_list
    """
    url_each = url.split("&")
    url_each[0] = url_each[0] + "start={}"
    url_base = "&".join(url_each)

    title_list = []
    url_list = []
    writer_list = []
    year_list = []
    ci_num_list = []
    p_id_list = []
    snippet_list = []

    for page in range(0, 100, 10):
        print("Loading next {} results".format(page+10))
        url_tmp = url_base.format(page)
        html_doc = requests.get(url_tmp).text
        soup = BeautifulSoup(html_doc, "html.parser")

        title_list_tmp, url_list_tmp = get_title_and_url(soup)
        writer_list_tmp, year_list_tmp = get_writer_and_year(soup)
        ci_num_list_tmp = get_citations(soup)
        p_id_list_tmp = get_id(soup)
        snippet_list_tmp = get_snippet(soup)
        
        title_list.extend(title_list_tmp)
        url_list.extend(url_list_tmp)
        writer_list.extend(writer_list_tmp)
        year_list.extend(year_list_tmp)
        ci_num_list.extend(ci_num_list_tmp)
        p_id_list.extend(p_id_list_tmp)
        snippet_list.extend(snippet_list_tmp)

        sleep(np.random.randint(5, 10))
    return title_list, url_list, writer_list, year_list, ci_num_list, p_id_list, snippet_list



def write_csv(conf, title_list, url_list, writer_list, year_list, ci_num_list, p_id_list, snippet_list):
    """ write csv
    :param conf, title_list, url_list, writer_list, year_list, ci_num_list, snippet_list:
    :return:
    """
    labels = ["conference", "title", "writer", "year", "citations", "url", "paper ID", "snippet"]
    path = "conf_csv/" + conf + ".csv"
    with open(path, "w") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(labels)
        for title, url, writer, year, ci_num, p_id, snippet in zip(
            title_list, url_list, writer_list, year_list, ci_num_list, p_id_list, snippet_list
        ):
            csv_writer.writerow([conf, title, writer, year, ci_num, url, p_id,  snippet])

if __name__ == "__main__":
    conf = "ICASSP"
    url = make_url(keyword=None, conf=conf, author=None)
    print(f"url: {url}")
    title_list, url_list, writer_list, year_list, ci_num_list, p_id_list, snippet_list = scraping_papers(url)
    write_csv(conf, title_list, url_list, writer_list, year_list, ci_num_list, p_id_list, snippet_list)
