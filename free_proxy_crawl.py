from basespider import BaseSpider


class XiciProxy(BaseSpider):
    urls = ["https://www.xicidaili.com/"]
    group_xpath = '//*[@id="ip_list"]/tr[position()>2]'
    son_xpath = {
        "ip": './td[2]/text()',
        "port": './td[3]/text()',
        "region": './td[4]/text()'
    }


if __name__ == '__main__':

    xc = XiciProxy()
    for info in xc.get_results():
        print(info)



