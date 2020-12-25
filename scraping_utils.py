from bs4 import BeautifulSoup

def get_snippet(soup):
    tags = soupl.find_all("div", {"class": "gs_rs"})
    snippet_list = [tags[i].text for i in range(len(tags))]
    return snippet_list
