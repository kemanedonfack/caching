import os
import json

import redis
import cx_Oracle


class DB:
    def __init__(self, **params):
        self.oracle = cx_Oracle.connect(**params)

    def query(self, sql):
        with self.oracle.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()

    def record(self, sql, values):
        with self.oracle.cursor() as cursor:
            cursor.execute(sql, values)
            return cursor.fetchone()


# Time to live for cached data
TTL = 10

# Read the Redis URL from environment variable.
REDIS_URL = os.environ.get('REDIS_URL', 'redis://oracle-redis.agf95j.clustercfg.eun1.cache.amazonaws.com:6379')

# Read the Oracle DB credentials from environment variables.
DB_USER = os.environ.get('DB_USER', 'admin')
DB_PASS = os.environ.get('DB_PASS', 'EIXpHo1KZASlBE1iyyFt')
DB_DSN = os.environ.get('DB_DSN', 'database-1.cnglh3wgxitt.eu-north-1.rds.amazonaws.com:1521/caching')

# Initialize the database
Database = DB(user=DB_USER, password=DB_PASS, dsn=DB_DSN)

# Initialize the cache
Cache = redis.Redis.from_url(REDIS_URL)


def fetch(sql):
    """Retrieve records from the cache, or else from the database."""
    res = Cache.get(sql)

    if res:
        return json.loads(res)

    res = Database.query(sql)
    Cache.setex(sql, TTL, json.dumps(res))
    return res

def check_cache(key):
    """Check if data is present in the cache for a given key."""
    if Cache.exists(key):
        print(f"Data for key '{key}' found in cache.")
        return True
    else:
        print(f"Data for key '{key}' not found in cache.")
        return False

def get_cache_data(cache_key):
    """Retrieve data from the cache for a given key."""
    cache_data = Cache.hgetall(cache_key)
    
    if cache_data:
        print(f"Cache data for key '{cache_key}':")
        for field, value in cache_data.items():
            print(f"{field}: {value}")
    else:
        print(f"No cache data found for key '{cache_key}'")


def student(student_id):
    """Retrieve a record from the cache, or else from the database."""
    key = f"student:{student_id}"
    res = Cache.hgetall(key)

    if res:
        return res

    sql = 'SELECT * FROM student WHERE id = :student_id'  # Use double quotes and single quotes
    values = {"student_id": student_id}
    res = Database.record(sql, values)  # Provide values using dictionary

    if res:
        # Set individual hash field-value pairs using indexing
        Cache.hset(key, "id", res[0])
        Cache.hset(key, "nom", res[1])
        Cache.hset(key, "prenom", res[2])
        Cache.expire(key, TTL)

    return res


# Display the result of some queries
student_id = 1
student_data = student(student_id)

# Check if student data is in the cache
check_cache(f"student:{student_id}")
print(fetch("SELECT * FROM student"))
print(student(1))
print(student(2))

get_cache_data("student:1")
