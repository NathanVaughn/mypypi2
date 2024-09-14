import os

import gunicorn.arbiter
import gunicorn.workers.base


def post_fork(server: gunicorn.arbiter.Arbiter, worker: gunicorn.workers.base.Worker) -> None:
    worker_id = worker.pid
    os.environ["GUNICORN_WORKER_ID"] = str(worker_id)
