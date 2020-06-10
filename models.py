from tortoise import fields, Model, Tortoise
from enum import IntEnum
from settings import mysql


async def init_db(create_db: bool = False):
    await Tortoise.init(
        db_url=f"mysql://{mysql.username}:{mysql.password}@{mysql.host}:{mysql.port}/{mysql.database}",
        modules={"models": ["__main__"]},
        _create_db=create_db
    )
    await Tortoise.generate_schemas()


class Anonymity(IntEnum):
    unknown = 100  # 未知
    high_anonymity = 0  # 高匿
    anonymity = 1  # 匿名
    transparency = 2  # 透明


class Protocol(IntEnum):
    unknown = 100  # 未知
    http = 0  # 支持http
    https = 1  # 支持https
    all = 2  # 支持http/https


class ProxyModel(Model):
    id = fields.IntField(pk=True)
    ip = fields.CharField(max_length=25)
    port = fields.IntField()
    area = fields.CharField(max_length=20)
    speed = fields.FloatField()
    anonymity: Anonymity = fields.IntEnumField(Anonymity, default=Anonymity.unknown)
    protocol: Protocol = fields.IntEnumField(Protocol, default=Protocol.unknown)
    score = fields.IntField()

    class Meta:
        table = "tb_proxy"

    def __str__(self):
        return f"{self.id}--{self.ip}:{self.port} | {self.area}"



