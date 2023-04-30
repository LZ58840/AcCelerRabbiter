import logging
import math
import pickle
import time
from collections import Counter
from io import BytesIO

import cv2
import imutils
import numpy as np

from utils import database_ctx, get_mysql_auth

FLANN_INDEX_KDTREE = 1  # way faster than 0
THUMBNAIL_SIZE = 256
sift_detector = cv2.SIFT_create()
orb_detector = cv2.ORB_create()
mysql_auth = get_mysql_auth(True)


def get_matcher():
    flann_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=1)
    search_params = dict(checks=50)
    flann_matcher = cv2.FlannBasedMatcher(flann_params, search_params)
    return flann_matcher


def get_matcher2():
    flann_params = dict(algorithm=6, table_number=6, key_size=12, multi_probe_level=1)
    search_params = dict(checks=50)
    flann_matcher = cv2.FlannBasedMatcher(flann_params, search_params)
    return flann_matcher


def build_matcher2(submission_id: str, subreddit: str):
    flann_params = dict(algorithm=6, table_number=6, key_size=12, multi_probe_level=1)
    search_params = dict(checks=50)
    flann_matcher = cv2.FlannBasedMatcher(flann_params, search_params)
    image_idx = []

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

    return flann_matcher, image_idx


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


# def build_matcher3(submission_id: str, subreddit: str):
#     with database_ctx(mysql_auth) as db:
#         db.execute('SELECT i.id, i.sift '
#                    'FROM images i JOIN submissions s ON i.submission_id = s.id '
#                    'WHERE i.submission_id!=%s AND s.subreddit=%s '
#                    'AND NOT s.removed AND NOT s.deleted AND i.sift IS NOT NULL',
#                    (submission_id, subreddit))
#         images = db.fetchall()
#
#     image_idx = []
#     image_data = np.empty((1, 128))
#
#     for image in images:
#         descriptors = pickle.loads(image["sift"])
#         image_data = np.concatenate((image_data, descriptors), axis=0)
#         image_idx.extend([image['id']] * len(descriptors))
#
#     image_data = image_data[1:]
#
#     hnsw_matcher = hnswlib.Index(space='l2', dim=128)
#     hnsw_matcher.init_index(max_elements=len(image_idx), ef_construction=200, M=64)
#     hnsw_matcher.add_items(image_data)
#
#     return hnsw_matcher, image_idx


def build_descriptors(image_bytes: BytesIO, size=THUMBNAIL_SIZE):
    current_image = cv2.imdecode(np.frombuffer(image_bytes.read(), np.uint8), 1)
    resized_image = imutils.resize(current_image, width=size) \
        if current_image.shape[0] >= current_image.shape[1] else imutils.resize(current_image, height=size)
    _, descriptors = sift_detector.detectAndCompute(resized_image, None)
    descriptors_blob = np.ndarray.dumps(descriptors)
    return descriptors_blob


def build_descriptors2(image_bytes: BytesIO, size=THUMBNAIL_SIZE):
    current_image = cv2.imdecode(np.frombuffer(image_bytes.read(), np.uint8), 1)
    resized_image = imutils.resize(current_image, width=size) \
        if current_image.shape[0] >= current_image.shape[1] else imutils.resize(current_image, height=size)
    _, descriptors = orb_detector.detectAndCompute(resized_image, None)
    descriptors_blob = np.ndarray.dumps(descriptors)
    return descriptors_blob


def build_descriptors_from_file(filename, size=THUMBNAIL_SIZE):
    current_image = cv2.imread(filename)

    resized_image = imutils.resize(current_image, width=size) \
        if current_image.shape[0] >= current_image.shape[1] else imutils.resize(current_image, height=size)
    # resized_image = cv2.resize(current_image, (size, size))
    _, descriptors = sift_detector.detectAndCompute(resized_image, None)
    descriptors_blob = np.ndarray.dumps(descriptors)
    return descriptors_blob


def build_descriptors_from_file2(filename, size=THUMBNAIL_SIZE):
    current_image = cv2.imread(filename)

    resized_image = imutils.resize(current_image, width=size) \
        if current_image.shape[0] >= current_image.shape[1] else imutils.resize(current_image, height=size)
    _, descriptors = orb_detector.detectAndCompute(resized_image, None)
    descriptors_blob = np.ndarray.dumps(descriptors)
    return descriptors_blob


def get_descriptors(submission_id: str):
    with database_ctx(mysql_auth) as db:
        db.execute('SELECT id, sift FROM images WHERE submission_id=%s', submission_id)
        images = db.fetchall()
    got_descriptors = [(image['id'], pickle.loads(image['sift'])) for image in images]
    return got_descriptors


def get_descriptor_by_id(image_id: int):
    with database_ctx(mysql_auth) as db:
        db.execute('SELECT sift FROM images WHERE id=%s', image_id)
        descriptors = db.fetchall()
    return pickle.loads(descriptors[0]['sift'])


# def sigmoid(x, b=(0.3*512**2)/(THUMBNAIL_SIZE**2), o=(40*THUMBNAIL_SIZE**2)/(512**2)) -> float:
#     return 1. / (1 + math.exp(-b * (x - o)))


def sigmoid(x, b=0.5, o=20) -> float:
    return 1. / (1 + math.exp(-b * (x - o)))


def match_descriptors(descriptors, matcher, image_idx, ratio=.75, threshold=0):
    start_time = time.time()
    matches = matcher.knnMatch(descriptors, k=2)
    logging.info(f"Input image matched in {time.time() - start_time} seconds.")
    good = [m.imgIdx for m, n in matches if m.distance / n.distance < ratio]
    tally = Counter(good)
    results = [(image_idx[idx], value) for idx, value in tally.items() if (pct := sigmoid(value)) > threshold]
    return results


def match_descriptors2(descriptors, matcher, image_idx, ratio=.75, threshold=0):
    matches = matcher.knnMatch(descriptors, k=2)
    matches = [match for match in matches if len(match) == 2]
    good = [m.imgIdx for m, n in matches if n.distance != 0 and m.distance / n.distance < ratio]
    tally = Counter(good)
    second_round_descriptors = [(image_idx[idx], get_descriptor_by_id(image_idx[idx])) for idx, _ in tally.items()]
    second_round_matcher = get_matcher()
    second_round_results = [
        (image_id, value, "{:.2%} certainty".format(pct)) for image_id, aux_descriptors in second_round_descriptors
        if (pct := sigmoid((value := match_two_descriptors(descriptors, aux_descriptors, second_round_matcher, ratio)))) > threshold
    ]
    return second_round_results


# def match_descriptors3(descriptors, matcher: hnswlib.Index, image_idx, ratio=.75, threshold=0):
#     labels, distances = matcher.knn_query(descriptors, k=2, filter=None)
#     good = [image_idx[labels[i][0]] for i, dists in enumerate(distances) if dists[1] != 0 and dists[0] / dists[1] < ratio]
#     tally = Counter(good)
#     second_round_descriptors = [(idx, get_descriptor_by_id(idx)) for idx, _ in tally.items()]
#     second_round_matcher = get_matcher()
#     second_round_results = [
#         (image_id, value, "{:.2%} certainty".format(pct)) for image_id, aux_descriptors in second_round_descriptors
#         if (pct := sigmoid((value := match_two_descriptors(descriptors, aux_descriptors, second_round_matcher, ratio)))) > threshold
#     ]
#     return second_round_results


def match_two_descriptors(descriptors1, descriptors2, matcher, ratio=.75):
    matches = matcher.knnMatch(descriptors1, descriptors2, k=2)
    matches = [match for match in matches if len(match) == 2]
    good = [m.imgIdx for m, n in matches if n.distance != 0 and m.distance / n.distance < ratio]
    return len(good)
