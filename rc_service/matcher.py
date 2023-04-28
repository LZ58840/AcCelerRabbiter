import logging
import math
import pickle
import time
from collections import Counter
from io import BytesIO

import cv2
import numpy as np

from utils import database_ctx, get_mysql_auth

FLANN_INDEX_KDTREE = 0
THUMBNAIL_SIZE = 256
sift_detector = cv2.SIFT_create()
mysql_auth = get_mysql_auth(True)


def build_matcher(submission_id: str, subreddit: str):
    flann_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    flann_matcher = cv2.FlannBasedMatcher(flann_params, search_params)
    image_idx = []

    start_time = time.time()

    with database_ctx(mysql_auth) as db:
        db.execute('SELECT i.id, i.sift '
                   'FROM images i JOIN submissions s ON i.submission_id = s.id '
                   'WHERE i.submission_id!=%s AND s.subreddit=%s '
                   'AND NOT s.removed AND NOT s.deleted AND i.sift IS NOT NULL',
                   (submission_id, subreddit))
        images = db.fetchall()

    for image in images:
        descriptors = pickle.loads(image["sift"])
        flann_matcher.add([descriptors])
        image_idx.append(image['id'])

    flann_matcher.train()

    logging.info(f"Loaded {len(images)} images in {time.time() - start_time} seconds.")

    return flann_matcher, image_idx


def build_descriptors(image_bytes: BytesIO, size=THUMBNAIL_SIZE):
    current_image = cv2.imdecode(np.frombuffer(image_bytes.read(), np.uint8), 1)
    resized_image = cv2.resize(current_image, (size, size))
    _, descriptors = sift_detector.detectAndCompute(resized_image, None)
    descriptors_blob = np.ndarray.dumps(descriptors)
    return descriptors_blob


def get_descriptors(submission_id: str):
    with database_ctx(mysql_auth) as db:
        db.execute('SELECT id, sift FROM images WHERE submission_id=%s', submission_id)
        images = db.fetchall()
    got_descriptors = [(image['id'], pickle.loads(image['sift'])) for image in images]
    return got_descriptors


def sigmoid(x, b=(0.3*512**2)/(THUMBNAIL_SIZE**2), o=(40*THUMBNAIL_SIZE**2)/(512**2)) -> float:
    return 1. / (1 + math.exp(-b * (x - o)))


def match_descriptors(descriptors, matcher, image_idx, ratio=.75, threshold=.9):
    start_time = time.time()
    matches = matcher.knnMatch(descriptors, k=2)
    logging.info(f"Input image matched in {time.time() - start_time} seconds.")
    good = [m.imgIdx for m, n in matches if m.distance / n.distance < ratio]
    tally = Counter(good)
    results = [(image_idx[idx], pct) for idx, value in tally.items() if (pct := sigmoid(value)) > threshold]
    return results
