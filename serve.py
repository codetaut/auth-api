import subprocess
import sys
from getopt import getopt

from waitress import serve

from app.main import wsgi_app


def main(argv):
    opts, args = getopt(argv, "hr")
    for opt, arg in opts:
        if opt in ("-r", "--live-reload"):
            subprocess.call(["hupper", "-m", "waitress", "--port=8000", "app.main:wsgi_app"])
    serve(wsgi_app, listen="*:8000")


if __name__ == "__main__":
    main(sys.argv[1:])
