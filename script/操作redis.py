import redis

conn = redis.Redis("127.0.0.1",port=6379)

result = conn.get('+8613681354685')

print(result)
print(conn.keys(),)