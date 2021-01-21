from scraping_utils import *
import csv


def write_paper_csv(keyword, paper, label):
    path = "data/cite_paper.csv"
    data = [keyword, label]
    data.extend(list(paper.values()))
    with open(path, "a") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(data)

def write_years_csv(paper_id, years):
    path = "data/cite_years/"+ paper_id +".csv"
    with open(path, "w") as f:
        csv_writer = csv.writer(f)
        csv_writer.writerows(years)

keyword = input("Keyword?: ")
url_leg = make_url(keyword=keyword, conf=None, author=None, year=None)
url_buz = make_url(keyword=keyword, conf=None, author=None, year="2018")
print("Please select LEGEND paper")
leg_paper = grep_candidate_papers(url_leg)

write_paper_csv(keyword, leg_paper, "legend")

url_cite_leg = make_url(keyword=None, conf=None, author=None, year=None, paper_id=leg_paper["paper_id"])
(
    titles_leg,
    urls_leg,
    writers_leg,
    years_leg,
    ci_num_leg,
    p_ids_leg,
    snippets_leg,
) = scraping_papers(url_cite_leg)
cite_year_leg = year_list_to_cite_years(years_leg, int(leg_paper['year']))
write_years_csv(cite_year_leg)

print("Please select BUZZ paper")
buz_paper = grep_candidate_papers(url_buz)

write_paper_csv(keyword, buz_paper, "buzz")

url_cite_buz = make_url(keyword=None, conf=None, author=None, year=None, paper_id=buz_paper["paper_id"])
(
    titles_buz,
    urls_buz,
    writers_buz,
    years_buz,
    ci_num_buz,
    p_ids_buz,
    snippets_buz,
) = scraping_papers(url_cite_buz)
cite_year_buz = year_list_to_cite_years(years_buz, int(buz_paper['year']))
write_years_csv(buz_paper['paper_id'], cite_year_buz)

