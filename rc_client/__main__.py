import asyncio
import time

from . import run_queries

from utils import get_mysql_auth, database_ctx

time.sleep(20)

with database_ctx(get_mysql_auth(True)) as db:
    db.execute('SELECT DISTINCT(s.id) '
               'FROM submissions s JOIN images i ON s.id=i.submission_id '
               'WHERE s.subreddit=%s AND NOT s.deleted AND NOT s.removed '
               'AND i.sift IS NOT NULL ORDER BY RAND() LIMIT 10',
               'Animewallpaper')
    rows = db.fetchall()
    ids = [row['id'] for row in rows]

asyncio.run(run_queries(ids))
