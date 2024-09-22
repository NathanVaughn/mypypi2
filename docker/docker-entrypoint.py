import multiprocessing
import subprocess

# first, intialize the database
import app.wsgi

app.wsgi.init_app()

# now, start the server
worker_count = (multiprocessing.cpu_count() * 2) + 1

subprocess.run(
    [
        "gunicorn",
        "--bind=0.0.0.0:80",
        f"--workers={min(worker_count, 10)}",
        "app.wsgi:create_app()",
    ]
)
