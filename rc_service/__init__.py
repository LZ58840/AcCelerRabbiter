from celery import Celery

from .matcher import get_descriptors, build_matcher, match_descriptors, get_descriptor_by_id, get_matcher, \
    match_two_descriptors, match_descriptors2, build_matcher2
from utils import get_rabbitmq_auth, get_mysql_root_auth


rabbitmq_auth = get_rabbitmq_auth(True)
mysql_auth = get_mysql_root_auth(True)
app = Celery('match_app',
             backend=f'db+mysql://root:{mysql_auth["password"]}@{mysql_auth["host"]}/celery',
             broker=f'pyamqp://{rabbitmq_auth["login"]}:{rabbitmq_auth["password"]}@{rabbitmq_auth["host"]}//')
threshold = .75  # .85  # .9


@app.task(name='check_this_image', ignore_result=False)
def match_image(submission_id: str, subreddit: str):
    query_descriptors = get_descriptors(submission_id)
    query_matcher, image_idx = build_matcher(submission_id, subreddit)
    results = {
        image_id: match_descriptors2(image_descriptors, query_matcher, image_idx, threshold=threshold)
        for image_id, image_descriptors in query_descriptors
    }
    return results


@app.task(name='compare_two_images', ignore_result=False)
def match_image2(image_id1: int, image_id2: int):
    query_descriptors1 = get_descriptor_by_id(image_id1)
    query_descriptors2 = get_descriptor_by_id(image_id2)
    query_matcher = get_matcher()
    return match_two_descriptors(query_descriptors1, query_descriptors2, query_matcher)


@app.task(name='check_this_image_orb', ignore_result=False)
def match_image3(submission_id: str, subreddit: str):
    query_descriptors = get_descriptors(submission_id)
    query_matcher, image_idx = build_matcher2(submission_id, subreddit)
    results = {
        image_id: match_descriptors2(image_descriptors, query_matcher, image_idx, threshold=threshold)
        for image_id, image_descriptors in query_descriptors
    }
    return results


# @app.task(name='check_this_image_hnsw', ignore_result=False)
# def match_image4(submission_id: str, subreddit: str):
#     query_descriptors = get_descriptors(submission_id)
#     query_matcher, image_idx = build_matcher3(submission_id, subreddit)
#     results = {
#         image_id: match_descriptors3(image_descriptors, query_matcher, image_idx, threshold=threshold)
#         for image_id, image_descriptors in query_descriptors
#     }
#     return results
