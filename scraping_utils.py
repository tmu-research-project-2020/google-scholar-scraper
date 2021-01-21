# import argparse
import csv
# import datetime
# import difflib
# import os
# import pprint
import re
import time
# import timeit
# import warnings
from time import sleep

# import matplotlib.pyplot as plt
# import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup

# from sklearn.linear_model import LinearRegression


def make_url(keyword, conf, author, year, paper_id=None):
    """make url for search papers
    normal search (keyword, conf, author, year) or target search (paper_id)
    :param keyword: str or None
    :param conf: str or None, conference information
    :param author: str or None, author information
    :param year: int or None, published year
    :param paper_id: None or int, paper information
    :return: url
    """
    assert (
        keyword is not None
        or conf is not None
        or author is not None
        or year is not None
        or paper_id is not None
    ), "KeywordNotFoundError"
    url = "https://scholar.google.co.jp/scholar?"
    if paper_id is not None:
        url += f"&cites={paper_id}"
    else:
        url += "&as_sdt=0%2C5"
        if keyword is not None:
            url += f"&as_q={'%20'.join(keyword.split())}"
        else:
            url += "&as_q="
        if conf is not None:
            url += f"&as_publication={'%20'.join(conf.split())}"
        if author is not None:
            author = "+".join(author.split())
            url += f"&as_sauthors={'%20'.join(author.split())}"
        if year is not None:
            url += f"&as_ylo={year}"
    return url


def get_snippet(soup):
    """obtain snippet from soup
    :param soup: parsed html by BeautifulSoup
    :return: snippet_list
    """
    tags = soup.find_all("div", {"class": "gs_rs"})
    snippet_list = [tags[i].text for i in range(len(tags))]
    return snippet_list


def get_title_and_url(soup):
    """obtain title and url from soup
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
    """obtain writer(author) and year from soup
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
            year_list.append(year[len(year) - 4 : len(year)])
        else:
            year_list.append(year)
    return writer_list, year_list


def get_citations(soup):
    """obtain number of citations from soup
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
    """obtain paper id from soup
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

def year_list_to_cite_years(year_list,p_year):
    """convert year_list into cite_years
    :param year_list,p_year:
    :return: cite_years
    """
    year_list_int = []
    for s in year_list:
        try:
            year_list_int.append(int(s))
        except:
            pass
    y = [p_year+i for i in range(2021 - p_year + 1)]
    cite_years = [0 for _ in range(2021 - p_year + 1)]
    for year in year_list_int:
        if year >= p_year and year <= 2021:
            cite_years[year - p_year] += 1
    list_return = [y, cite_years]
#    cite_years = pd.DataFrame(cite_years,
#                       index=y,
#                       columns=['total'])
#    cite_years  = cite_years.T
    return list_return

def grep_candidate_papers(url):
    """scrape first 10 papers and choose one
    :param url:
    :return: target paper information (title, writer, year, citations, url, paper_id, snippet)
    """
    html_doc = requests.get(url).text
    soup = BeautifulSoup(html_doc, "html.parser")

    title_list, url_list = get_title_and_url(soup)
    writer_list, year_list = get_writer_and_year(soup)
    ci_num_list = get_citations(soup)
    p_id_list = get_id(soup)
    snippet_list = get_snippet(soup)

    for i in range(len(title_list)):
        print("-" * 20)
        print(f"paper number: {str(i)}")
        print(f"paper title: {title_list[i]}")
        print(f"published year: {year_list[i]}")
        print(f"citations: {ci_num_list[i]}")

    target_paper_num = -1
    while target_paper_num < 0 or target_paper_num >= len(title_list):
        target_paper_num = int(input("Select paper number: "))
        if target_paper_num < 0 or target_paper_num >= len(title_list):
            print("Index out of range! Please re-enter")

    target_paper = {
            "title": title_list[target_paper_num],
        "writer": writer_list[target_paper_num],
        "year": year_list[target_paper_num],
        "citations": ci_num_list[target_paper_num],
        "url": url_list[target_paper_num],
        "paper_id": p_id_list[target_paper_num],
        "snippet": snippet_list[target_paper_num],
    }
    return target_paper


def scraping_papers(url):
    """scrape 100 papers
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
        print("Loading next {} results".format(page + 10))
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
    return (
        title_list,
        url_list,
        writer_list,
        year_list,
        ci_num_list,
        p_id_list,
        snippet_list,
    )


def write_csv(
    conf,
    title_list,
    url_list,
    writer_list,
    year_list,
    ci_num_list,
    p_id_list,
    snippet_list,
):
    """write csv
    :param conf, title_list, url_list, writer_list, year_list, ci_num_list, snippet_list:
    :return:
    """
    labels = [
        "conference",
        "title",
        "writer",
        "year",
        "citations",
        "url",
        "paper ID",
        "snippet",
    ]
    path = "conf_csv/" + conf + ".csv"
    with open(path, "w") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(labels)
        for title, url, writer, year, ci_num, p_id, snippet in zip(
            title_list,
            url_list,
            writer_list,
            year_list,
            ci_num_list,
            p_id_list,
            snippet_list,
        ):
            csv_writer.writerow([conf, title, writer, year, ci_num, url, p_id, snippet])


if __name__ == "__main__":
    #conf = "ICASSP"
    conf = 'arxiv'
    keyword = "pretraining bert"
    year = "2018"
    url = make_url(keyword=keyword, conf=conf, author=None, year=year)
    print(f"url: {url}")

    # select target paper
    target_paper = grep_candidate_papers(url)
    print(f"target paper: {target_paper}")

    # create paper list about target paper's citation
    url_cite = make_url(
        keyword=None, conf=None, author=None, year=None, paper_id=target_paper["paper_id"]
    )
    (
        title_list,
        url_list,
        writer_list,
        year_list,
        ci_num_list,
        p_id_list,
        snippet_list,
    ) = scraping_papers(url_cite)

    cite_year = year_list_to_cite_years(year_list,int(target_paper['year']))
    print(cite_year)
