import multiprocessing
import subprocess

worker_count = (multiprocessing.cpu_count() * 2) + 1

subprocess.run(
    [
        "gunicorn",
        "--bind=0.0.0.0:80",
        f"--workers={min(worker_count, 10)}",
        "--worker-class=eventlet",
        "app.wsgi:create_app()",
    ]
)
