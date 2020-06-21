import subprocess
from waitress import serve as start
from app.main import wsgi_app


def serve():
    start(wsgi_app, listen="*:8000")


def live():
    subprocess.call(["hupper", "-m", "waitress", "--port=8000", "app.main:wsgi_app"])


if __name__ == '__main__':
    serve()
