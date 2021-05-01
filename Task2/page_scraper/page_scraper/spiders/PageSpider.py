import scrapy
import psycopg2
import validators
import numpy as np
import matplotlib.pyplot as plt
from defaultlist import defaultlist
from urllib.parse import urlparse
from pydispatch import dispatcher
from scrapy import signals
from pprint import pprint
from matplotlib import rcParams
import psycopg2.extras


class PageSpider(scrapy.Spider):
    name = 'page_spider'
    start_urls = ['https://www.apple.com/ru/']
    DEPTH_OF_SCRAPING = 3
    dictionary_with_urls = {}
    matrix_main = defaultlist(lambda: defaultlist(lambda: 0))

    def save_into_db(self, url_info, update=False):
        connection = psycopg2.connect(
            database='',
            user='postgres',
            password='aws48916011',
            host='dm-rg-database.cvjyc3nfgos9.us-east-1.rds.amazonaws.com',
            port='5432',
        )
        connection.autocommit = True
        cursor = connection.cursor()
        d = url_info
        keys = d.keys()
        columns = ','.join(keys)
        values = ','.join(['%({})s'.format(k) for k in keys])
        insert_query = 'INSERT INTO url_info ({0}) VALUES ({1})'.format(columns, values)
        cursor.execute(cursor.mogrify(insert_query, d))
        connection.commit()
        connection.close()

    def get_from_db(self, query):
        connection = psycopg2.connect(
            database='',
            user='postgres',
            password='aws48916011',
            host='dm-rg-database.cvjyc3nfgos9.us-east-1.rds.amazonaws.com',
            port='5432',
        )
        cur = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        connection.autocommit = True
        cur.execute(query)
        temp_ans = cur.fetchall()
        ans = []
        for row in temp_ans:
            ans.append(dict(row))
        connection.commit()
        connection.close()
        return ans

    def create_matrix(self):
        rows = self.get_from_db("SELECT url, referer FROM url_info")
        self.dictionary_with_urls = {}
        for row in rows:
            if self.dictionary_with_urls.get(row["url"]) is None:
                self.dictionary_with_urls[row["url"]] = len(self.dictionary_with_urls)
            if str(row["referer"]) != "None":
                if self.dictionary_with_urls.get(row["referer"]) is None:
                    self.dictionary_with_urls[row["referer"]] = len(self.dictionary_with_urls)
                referer_index = self.dictionary_with_urls[row["referer"]]
                url_index = self.dictionary_with_urls[row["url"]]
                self.matrix_main[referer_index][url_index] = 1

    def fill_with_zeros(self, m, number):
        for i in range(number):
            while len(m[i]) < number:
                m[i].append(0.0)

    def recalculate_dictionary(self, i):
        deleted = False
        for key in list(self.dictionary_with_urls):
            if self.dictionary_with_urls.get(key) == i:
                self.dictionary_with_urls.pop(key, None)
                deleted = True
            else:
                if deleted:
                    self.dictionary_with_urls[key] = self.dictionary_with_urls.get(key) - 1

    def filter_bad_links(self):
        is_empty_line = True
        while is_empty_line:
            is_empty_line = False
            i = 0
            while i < len(self.matrix_main):
                url_number = np.sum(self.matrix_main[i])
                if url_number == 0:
                    self.matrix_main = np.delete(self.matrix_main, (i,), axis=0)
                    self.matrix_main = np.delete(self.matrix_main, (i,), axis=1)
                    self.recalculate_dictionary(i)
                    is_empty_line = True
                i += 1

    def add_probability(self):
        for i in range(len(self.matrix_main)):
            url_number = np.sum(self.matrix_main[i])
            for j in range(len(self.matrix_main[i])):
                if self.matrix_main[i][j] == 1:
                    self.matrix_main[i][j] = 1. / url_number

    def create_pairs_of_url_rank(self, v, dictionary):
        pairs = {}
        i = 0
        for key, value in dictionary.items():
            pairs[key] = v[value]
            i += 1
            if i == len(v):
                break
        return pairs

    def damn_bar_graph(self, d):
        connection = psycopg2.connect(
            database='',
            user='postgres',
            password='aws48916011',
            host='dm-rg-database.cvjyc3nfgos9.us-east-1.rds.amazonaws.com',
            port='5432',
        )
        rcParams.update({'figure.autolayout': True})
        plt.autoscale()
        d = dict(sorted(d.items(), key=lambda item: item[1], reverse=True))
        list_values = d.values()
        list_keys = d.keys()
        list_values = list(list_values)[0:min(100, len(list_values))]
        list_keys = list(list_keys)[0:min(100, len(list_keys))]
        list_final_values_to_db = [(list_keys[i], list_values[i]) for i in range(0, 30)]
        print("INSERTED FINAL VALUES TO BD")
        pprint(list_final_values_to_db)
        final_records = ", ".join(["%s"] * len(list_final_values_to_db))
        insert_query = (
            f"INSERT INTO pager_rank (urls, ranks) VALUES {final_records}"
        )
        connection.autocommit = True
        cursor = connection.cursor()
        cursor.execute(insert_query, list_final_values_to_db)
        fig, ax = plt.subplots()
        ax.bar(list_keys, list_values)
        ax.set_facecolor('white')
        fig.set_facecolor('floralwhite')
        plt.xticks(rotation=90)
        o = urlparse(self.start_urls[0])
        png_name = o.netloc + '.png'
        plt.savefig(png_name, bbox_inches="tight")
        connection.commit()
        connection.close()

    def on_closed(self):
        self.create_matrix()
        self.fill_with_zeros(self.matrix_main, len(self.dictionary_with_urls))
        self.matrix_main = np.array(self.matrix_main)
        self.filter_bad_links()
        self.add_probability()
        self.matrix_main = self.matrix_main.transpose()
        final_matrix = np.linalg.matrix_power(self.matrix_main, len(self.matrix_main))
        vector = [1 / len(final_matrix)] * len(final_matrix)
        final_matrix = np.array(final_matrix)
        vector = np.array(vector)
        vector = final_matrix.dot(vector)
        pprint("THIS IF FINAL SUM OF (VECTOR)" + str(np.sum(vector)))
        pairs = self.create_pairs_of_url_rank(vector, self.dictionary_with_urls)
        pprint("DICTIONARY")
        self.damn_bar_graph(pairs)

    def spider_closed(self, spider):
        self.on_closed()

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url,
                                 callback=self.parse,
                                 meta={'depth': 1, 'referer': None})

    def parse(self, response, **kwargs):
        current_crawler_depth = response.meta['depth']
        next_crawler_depth = current_crawler_depth + 1
        next_urls = response.xpath('*//a/@href').extract()
        if response.meta['referer'] is None and response.request.url == self.start_urls[0]:
            row = {"url": response.request.url,
                   "referer": response.meta['referer'],
                   "is_good": 0,
                   "depth": current_crawler_depth
                   }
            self.save_into_db(row)
        for url in set(next_urls):
            valid = validators.url(url)
            if not valid:
                continue
            o = urlparse(url)
            url_without_query_string = o.scheme + "://" + o.netloc + o.path
            if current_crawler_depth <= self.DEPTH_OF_SCRAPING:
                row = {"url": url_without_query_string,
                       "referer": response.request.url,
                       "is_good": 0,
                       "depth": current_crawler_depth
                       }
                self.save_into_db(row)
            else:
                continue
            yield scrapy.Request(url=url_without_query_string,
                                 callback=self.parse,
                                 meta={'depth': next_crawler_depth, 'referer': response.request.url})
