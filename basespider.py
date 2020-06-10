import requests
from lxml import etree

from utils import get_request_header


class BaseSpider(object):
    urls = []
    group_xpath = ""
    son_xpath = {}

    def __init__(self, group_xpath='', son_xpath={}, urls=[]):
        if group_xpath:
            self.group_xpath = group_xpath
        if son_xpath:
            self.son_xpath = son_xpath
        if urls:
            self.urls = urls

    def handle_no_data(self, li):
        return li[0] if len(li) != 0 else ''

    def get_page(self, url):
        try:
            return requests.get(url, headers=get_request_header()).content.decode()
        except Exception as e:
            return requests.get(url, headers=get_request_header()).content.decode("GBK")

    def get_son_info(self, trs):
        for tr in trs:
            ip = self.handle_no_data(tr.xpath(self.son_xpath["ip"])).strip('\n').strip(' ')
            port = self.handle_no_data(tr.xpath(self.son_xpath["port"])).strip('\n').strip(' ')
            region = self.handle_no_data(tr.xpath(self.son_xpath["region"])).strip('\n').strip(' ')

            yield [ip, port, region]

    def parse_page(self, page):
        element = etree.HTML(page)
        trs = element.xpath(self.group_xpath)
        return trs

    def get_results(self):

        for url in self.urls:
            page = self.get_page(url)
            trs = self.parse_page(page)
            yield from self.get_son_info(trs)


if __name__ == "__main__":
    #  测试爬取66ip网的代理ip
    obj = BaseSpider(
        group_xpath='//*[@id="main"]/div/div[1]/table/tr[position()>1]',
        urls=[f"http://www.66ip.cn/{i}.html" for i in range(1, 4)],
        son_xpath={
            "ip": './td[1]/text()',
            "port": './td[2]/text()',
            "region": './td[3]/text()'
        }
    )
    for info in obj.get_results():
        print(info)
