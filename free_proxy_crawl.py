from basespider import BaseSpider


#  西刺代理
class XiciProxy(BaseSpider):
    urls = ["https://www.xicidaili.com/"]
    group_xpath = '//*[@id="ip_list"]/tr[position()>2]'
    son_xpath = {
        "ip": './td[2]/text()',
        "port": './td[3]/text()',
        "region": './td[4]/text()'
    }


class Ip3366Spider(BaseSpider):
    urls = ['http://www.ip3366.net/free/?stype={}&page={}'.format(i, j) for j in range(1, 10) for i in range(1, 4, 2)]
    group_xpath = '//*[@id="list"]/table/tbody/tr'
    son_xpath = {'ip': './td[1]/text()', 'port': './td[2]/text()', 'region': './td[5]/text()'}


class IphaiSpider(BaseSpider):
    urls = ['http://www.iphai.com/free/ng', 'http://www.iphai.com/free/wg']
    group_xpath = '//table/tr[position()>1]'
    son_xpath = {'ip': './td[1]/text()', 'port': './td[2]/text()', 'region': './td[5]/text()'}


if __name__ == '__main__':

    # obj = XiciProxy()
    obj = IphaiSpider()
    for info in obj.get_results():
        info[0] = info[0].strip('\n').strip(' ')
        info[1] = info[1].strip('\n').strip(' ')
        info[2] = info[2].strip('\n').strip(' ')
        print(info)


