import json
import time

import requests
import asyncio

import settings
import utils
from proxy_ip import Proxy
from free_proxy_crawl import XiciProxy, Ip3366Spider, IphaiSpider
from concurrent.futures import ThreadPoolExecutor
from models import ProxyModel, init_db
import logging

logging.basicConfig(level=logging.DEBUG)


def fetch(proxy, ishttp=True):
    nick_type = -1
    speed = -1
    proxies = {
        'http': f"http://{proxy.ip}:{proxy.port}",
        'https': f"https://{proxy.ip}:{proxy.port}"
    }
    # headers = utils.get_request_header()
    if ishttp:
        url = 'http://httpbin.org/get'
    else:
        url = 'https://httpbin.org/get'
    try:
        start = time.time()
        r = requests.get(url=url, headers=utils.get_request_header(), timeout=settings.TIMEOUT, proxies=proxies)
        if r.ok:
            # 计算响应速度, 保留两位小数
            speed = round(time.time() - start, 2)
            # 把响应内容转换为字典
            content = json.loads(r.text)
            # 获取请求头
            headers = content['headers']
            # 获取origin, 请求来源的IP地址
            ip = content['origin']
            # 获取请求头中 `Proxy-Connection` 如果有, 说明匿名代理
            proxy_connection = headers.get('Proxy-Connection', None)

            if ',' in ip:
                # 如果 `origin` 中有','分割的两个IP就是透明代理IP
                nick_type = 2  # 透明
            elif proxy_connection:
                # 如果 `headers` 中包含 `Proxy-Connection` 说明是匿名代理IP
                nick_type = 1  # 匿名
            else:
                #  否则就是高匿代理IP
                nick_type = 0  # 高匿
            return True, nick_type, speed
        else:
            return False, nick_type, speed
    except Exception as e:
        return False, nick_type, speed


async def save_proxy(proxy):
    try:
        if await ProxyModel.get_or_none(ip=proxy.ip) == None:
            await ProxyModel.create(
                ip=proxy.ip,
                port=proxy.port,
                area=proxy.area,
                speed=proxy.speed,
                anonymity=proxy.anonymity,
                protocol=proxy.protocol,
                score=proxy.score
            )
        else:
            logging.warning(f"{proxy.ip}:{proxy.area} 已经存在！")
    except Exception as e:
        print(e)


async def proxy_count():
    try:
        return await ProxyModel.all().count()
    except Exception as e:
        print(e)


async def validate(name, q, pool, event):
    loop = asyncio.get_running_loop()
    while not event.is_set() or not q.empty():
        proxy = await q.get()
        http, http_nick_type, http_speed = await loop.run_in_executor(pool, fetch, proxy)
        https, https_nick_type, https_speed = await loop.run_in_executor(pool, fetch, proxy, False)

        if http and https:
            # 如果http 和 https 都可以请求成功, 说明支持http也支持https, 协议类型为2
            proxy.protocol = 2
            proxy.anonymity = http_nick_type
            proxy.speed = http_speed
            if isinstance(proxy, ProxyModel):
                await proxy.save(update_fields=["protocol", "anonymity", "speed"])

        elif http:
            # 如果只有http可以请求成功, 说明支持http协议, 协议类型为 0
            proxy.protocol = 0
            proxy.anonymity = http_nick_type
            proxy.speed = http_speed
            if isinstance(proxy, ProxyModel):
                await proxy.save(update_fields=["protocol", "anonymity", "speed"])

        elif https:
            # # 如果只有https可以请求成功, 说明支持https协议, 协议类型为 1
            proxy.protocol = 1
            proxy.anonymity = https_nick_type
            proxy.speed = https_speed
            if isinstance(proxy, ProxyModel):
                await proxy.save(update_fields=["protocol", "anonymity", "speed" ])
        else:
            if isinstance(proxy, ProxyModel):
                if proxy.score <= 0:
                    await proxy.delete()
                else:
                    proxy.score -= 1
                    proxy.speed = -1
                    await proxy.save(update_fields=["score", "speed"])
            proxy.protocol = -1
            proxy.anonymity = -1
            proxy.speed = -1

        if not isinstance(proxy, ProxyModel) and proxy.speed > 0:
            await save_proxy(proxy)

        q.task_done()


async def get_proxy(q, xc):
    if not isinstance(xc, list):
        for info in xc.get_results():
            print(info)
            if info[0] != '':
                proxy = Proxy(info[0], int(info[1]), area=info[2] if info[2] != '' else "未知")
                await q.put(proxy)
    else:
        for proxy in xc:
            await q.put(proxy)


async def main():
    await init_db()
    shutdown_event = asyncio.Event()
    pool = ThreadPoolExecutor(settings.POOL_MAX)
    q = asyncio.Queue()
    if await proxy_count():
        obj = await ProxyModel.all()
        product = [get_proxy(q, obj)]
    else:
        obj_li = [XiciProxy(), Ip3366Spider(), IphaiSpider()]
        product = [get_proxy(q, obj) for obj in obj_li]
    works = [validate(f"worker_{i}", q, pool, shutdown_event) for i in range(settings.WORKS)]
    coros = asyncio.gather(
        *product,
        *works,
        return_exceptions=True
    )
    try:
        await coros

    except KeyboardInterrupt:
        shutdown_event.set()
        coros.cancel()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("press ctrl+c")
