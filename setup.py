import asyncio
import re
import time
from io import BytesIO

import cv2
from aiohttp import ClientSession
from aiohttp_retry import RetryClient

from rc_service.matcher import build_descriptors
from utils import database_ctx, get_mysql_auth

images_dir = "images"

image_size = 128

mysql_auth = get_mysql_auth()

headers = {"User-Agent": "python:awb:v2.0b (by u/AnimewallpaperBot)"}


async def download_image(image_id, url, client_session):
    if re.match(r"(https?://.*\.(?:png|jpg|jpeg))", url) is None:
        return None, image_id
    client = RetryClient(raise_for_status=False, client_session=client_session)
    try:
        async with client.request(method='GET', allow_redirects=False, url=url, headers=headers) as response:
            if response.status != 200:
                print(f"Could not download {url}, got: {response.status}")
                return None, image_id
            image_bytes = await response.content.read()
            return build_descriptors(BytesIO(image_bytes), size=image_size), image_id
    except Exception as e:
        print(f"Could not download {url}, got: {e}")
        return None, image_id


async def download_images(images_sql_rows):
    async with ClientSession(auto_decompress=False) as cs:
        tasks = [asyncio.create_task(download_image(row['id'], row['url'], cs)) for row in images_sql_rows]
        results = await asyncio.gather(*tasks)
    return results


if __name__ == "__main__":
    sift_detector = cv2.SIFT_create()
    start_time = time.time()
    with database_ctx(mysql_auth) as db:
        db.execute('SELECT i.id, i.url '
                   'FROM images i JOIN submissions s ON s.id=i.submission_id '
                   'WHERE NOT s.deleted AND i.sift IS NULL')
        rows = db.fetchall()
        print(f"Downloading {len(rows)} images...")
        downloaded_images = asyncio.run(download_images(rows))
        db.executemany('UPDATE images SET sift=%s WHERE id=%s', downloaded_images)
    print(f"Processed {len(downloaded_images)} images in {time.time() - start_time} seconds.")
