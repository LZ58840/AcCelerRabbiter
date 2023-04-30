import asyncio
import time

from . import run_queries, run_queries2, run_queries3

from utils import get_mysql_auth, database_ctx

time.sleep(10)

# with database_ctx(get_mysql_auth(True)) as db:
#     db.execute('SELECT DISTINCT(s.id) '
#                'FROM submissions s JOIN images i ON s.id=i.submission_id '
#                'WHERE s.subreddit=%s AND NOT s.deleted AND NOT s.removed '
#                'AND i.sift IS NOT NULL ORDER BY RAND() LIMIT 10',
#                'Animewallpaper')
#     rows = db.fetchall()
#     ids = [row['id'] for row in rows]

ids = ['d1f4667b', 'ab5b6627', 'c1ceba87', '7569bc5e', '2b5c35c7', '5292ab59', '59d73738', '8760451f', '65445838', 'b0e0a78b']

# ids = ['d1f4667b']

# id_pairs = [(1877, 1869)]

asyncio.run(run_queries(ids))

# asyncio.run(run_queries2(id_pairs))
