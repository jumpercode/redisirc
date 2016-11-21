from redis.sentinel import Sentinel
sentinel = Sentinel([('10.14.0.12', 26379), ('10.14.0.13', 26379), ('10.14.0.14', 26379) ], socket_timeout=0.5, password='upc2016')
print(sentinel.discover_master('mymaster'))
print(sentinel.discover_slaves('mymaster'))

