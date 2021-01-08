from scraping_utils import make_url,scraping_papers,write_csv
import sys

if __name__ == "__main__":
    argv = sys.argv
    argc = len(argv)
    if argc == 1:#コマンドライン引数が1つも無い場合
        print ('Please enter conference name')
        quit()
    if argc > 2:#コマンドライン引数が2つ以上の場合終了
        print ('Usage: python3 %s arg1' %argv[0])
        quit()
    conf = argv[1]
    url = make_url(keyword=None, conf=conf, author=None)
    print(f"url: {url}")
    title_list, url_list, writer_list, year_list, ci_num_list, p_id_list, snippet_list = scraping_papers(url)
    write_csv(conf, title_list, url_list, writer_list, year_list, ci_num_list, p_id_list, snippet_list)
