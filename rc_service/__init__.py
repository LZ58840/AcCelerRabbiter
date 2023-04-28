from celery import Celery

from .matcher import get_descriptors, build_matcher, match_descriptors
from utils import get_rabbitmq_auth, get_mysql_root_auth


rabbitmq_auth = get_rabbitmq_auth(True)
mysql_auth = get_mysql_root_auth(True)
app = Celery('match_app',
             backend=f'db+mysql://root:{mysql_auth["password"]}@{mysql_auth["host"]}/celery',
             broker=f'pyamqp://{rabbitmq_auth["login"]}:{rabbitmq_auth["password"]}@{rabbitmq_auth["host"]}//')


@app.task(name='check_this_image', ignore_result=False)
def match_image(submission_id: str, subreddit: str):
    query_descriptors = get_descriptors(submission_id)
    query_matcher, image_idx = build_matcher(submission_id, subreddit)
    results = {
        image_id: match_descriptors(image_descriptors, query_matcher, image_idx)
        for image_id, image_descriptors in query_descriptors
    }
    return results
