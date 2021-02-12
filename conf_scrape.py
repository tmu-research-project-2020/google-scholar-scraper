from scraping_utils import make_url,scraping_papers,write_csv
import sys
import csv
import os

if __name__ == "__main__":
    
    conf = input('Enter conference name: ')
    url = make_url(keyword=None, conf=conf, author=None, year=None)
    print(f"url: {url}")
    title_list, url_list, writer_list, year_list, ci_num_list, p_id_list, snippet_list = scraping_papers(url)
    write_csv(conf, title_list, url_list, writer_list, year_list, ci_num_list, p_id_list, snippet_list)

    files = os.listdir("./data/conf_csv")
    files = [c.replace(".csv", "") for c in files]
    path_save = "data/papers.csv"

    # make papers.csv
    try:
        with open(path_save) as f:
            pass
    except:
        labels = ["conference", "title", "writer", "year", "citations", "url", "paper ID", "snippet"]
        with open(path_save, "w") as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow(labels)

    # read existing data
    with open(path_save, "r") as f:
        csv_reader = csv.reader(f)
        conf_list = [row for row in csv_reader]
    conf_list =  [list(x) for x in zip(*conf_list)]
    conf_list = conf_list[0]

    # write new data
    for c in files:
        if c not in conf_list:
            path_read = "data/conf_csv/" + c + ".csv"
            with open(path_read, "r") as f:
                csv_reader = csv.reader(f)
                p_data = [row for row in csv_reader]
                p_data = p_data[1:]
            with open(path_save, "a") as f:
                csv_writer = csv.writer(f)
                csv_writer.writerows(p_data)
        else:
            pass

