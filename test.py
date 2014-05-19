import json
import redis
import ConfigParser
import pprint


dict = json.loads('{"projectId":"11","stageId":"7","content":"azezaeae"}')
print dict.get("projectId")


config = ConfigParser.ConfigParser()
config.read('wapy.cfg')
redis_host = config.get('Redis', 'host')
redis_port = config.get('Redis', 'port')

pool = redis.ConnectionPool(host=redis_host, port=redis_port, db=0)
r = redis.Redis(connection_pool=pool)
r.set('tot', 'qsd')
