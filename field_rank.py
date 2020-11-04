from bs4 import BeautifulSoup
import requests
import pandas as pd
import re

def get_h5(html):
    soup = BeautifulSoup(html, "html.parser")
    h5s = soup.find_all("a", {"class": "gs_ibl gsc_mp_anchor"})
    list_h5 = []
    for h5 in h5s:
        list_h5.append(int(h5.text))
    ave_h5 = sum(list_h5) / len(list_h5)
    return ave_h5

def search_sub_category(main_category):
    html_home = requests.get("https://scholar.google.com/citations?view_op=top_venues&hl=ja&vq=" + main_category).text
    soup = BeautifulSoup(html_home, "html.parser")
    tags = soup.select("[class='gs_md_li']")
    columns = ["field", "average"]
    df = pd.DataFrame(columns=columns)
    for a in tags:
        url = re.findall('eng_.*', a['href'])[0]
        field = a.text
        html = requests.get("https://scholar.google.com/citations?view_op=top_venues&hl=ja&vq=" + url).text
        ave_h5 = get_h5(html)
        se = pd.Series([field, ave_h5], columns)
        df = df.append(se, columns)
    df.sort_values('average', ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

main_category="eng"
result_df = search_sub_category(main_category)
filename = "Field_rank.csv"
result_df.to_csv(filename, encoding="utf-8")
