import asyncio
import time

from celery import Celery

from utils import get_rabbitmq_auth, get_mysql_root_auth


rabbitmq_auth = get_rabbitmq_auth(True)
mysql_auth = get_mysql_root_auth(True)
app = Celery('match_app',
             backend=f'db+mysql://root:{mysql_auth["password"]}@{mysql_auth["host"]}/celery',
             broker=f'pyamqp://{rabbitmq_auth["login"]}:{rabbitmq_auth["password"]}@{rabbitmq_auth["host"]}//')


async def query_async(submission_id, subreddit):
    time_start = time.time()
    result = app.send_task('check_this_image', (submission_id, subreddit))
    while not result.ready():
        await asyncio.sleep(1)
    value = result.get()
    print(f"{result.id}: {value} ({time.time() - time_start:.2f} seconds)")


async def query2_async(id1, id2):
    time_start = time.time()
    result = app.send_task('compare_two_images', (id1, id2))
    while not result.ready():
        await asyncio.sleep(1)
    value = result.get()
    print(f"{result.id}: {value} ({time.time() - time_start:.2f} seconds)")


async def query3_async(submission_id, subreddit):
    result = app.send_task('check_this_image_hnsw', (submission_id, subreddit))
    while not result.ready():
        await asyncio.sleep(1)
    value = result.get()
    print(value)


async def run_queries(ids):
    tasks = [
        asyncio.create_task(query_async(sub_id, 'Animewallpaper'))
        for sub_id in ids
    ]
    await asyncio.gather(*tasks)


async def run_queries2(id_pairs):
    tasks = [
        asyncio.create_task(query2_async(id1, id2))
        for id1, id2 in id_pairs
    ]
    await asyncio.gather(*tasks)


async def run_queries3(ids):
    tasks = [
        asyncio.create_task(query3_async(sub_id, 'Animewallpaper'))
        for sub_id in ids
    ]
    await asyncio.gather(*tasks)
