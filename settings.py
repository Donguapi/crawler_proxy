from collections import namedtuple

MAX_SCORE = 30
TIMEOUT = 5

POOL_MAX = 30
WORKS = 20

Mysql = namedtuple("Mysql", "database host port username password")

# mysql数据库连接配置
mysql = Mysql(
    database="crawl_proxy",
    host="127.0.0.1",
    port="3306",
    username="root",
    password="mysql"
)



