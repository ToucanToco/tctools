#!/usr/bin/env python
try:
    # Python 3
    from http.server import HTTPServer, SimpleHTTPRequestHandler
except ImportError:
    # Python 2
    from BaseHTTPServer import HTTPServer
    from SimpleHTTPServer import SimpleHTTPRequestHandler

import json
import os
import signal
import ssl
import sys

import colorama
import daemon
from daemon.pidfile import PIDLockFile

CONF_DIR = os.path.expanduser('~/.tctools/frontserver/')
REPO_DIR = os.path.expanduser('~/.tctools/repo/')
CONF_JSON_FILE = os.path.join(CONF_DIR, "config.json")
PEM_FILE = os.path.join(REPO_DIR, "frontserver", "pemfile.pem")
CWD = os.getcwd()
HTTP_PORT = 8800
PID_LOCK_FILE = PIDLockFile('/tmp/frontserver.pid')


def test(HandlerClass, ServerClass, port, protocol="HTTP/1.0"):
    server_address = ('', port)
    HandlerClass.protocol_version = protocol
    httpd = ServerClass(server_address, HandlerClass)
    httpd.socket = ssl.wrap_socket(httpd.socket, server_side=True,
                                   certfile=PEM_FILE)
    httpd.serve_forever()


class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        SimpleHTTPRequestHandler.end_headers(self)


def red(s):
    return colorama.Fore.RED + s + colorama.Style.RESET_ALL


def green(s):
    return colorama.Fore.GREEN + s + colorama.Style.RESET_ALL


def daemon_process(context):
    if not os.path.exists(os.path.join(CWD, 'front_config.cson')):
        print(red("No front_config.cson file found in the current folder: aborting"))
        sys.exit(-1)

    if not os.path.exists(PEM_FILE):
        print(red("Certicate pemfile.pem not found: aborting"))
        sys.exit(-1)

    print(green("Starting daemon with PID %d on port %d (serving %s)..." % (os.getpid(), HTTP_PORT, CWD)))
    print(green("Please visit https://localhost:%d/front_config.cson at least once for https connection to work." % HTTP_PORT))
    conf = {"port": HTTP_PORT, "cwd": CWD}
    json.dump(conf, open(CONF_JSON_FILE, 'w'))
    with context:
        test(CORSRequestHandler, HTTPServer, port=HTTP_PORT)


def control_process(context):
    try:
        pid = int(open(context.pidfile.path).read().strip())
    except Exception:
        print(red("No daemon running"))
        return

    conf = json.load(open(CONF_JSON_FILE, 'r'))
    port = conf['port']
    cwd = conf['cwd']

    if 'stop' in sys.argv:
        try:
            os.kill(pid, signal.SIGINT)
        except Exception:
            print(red("Error: no daemon running ?"))
            return
        print("Killed daemon with PID %d (serving %s on port %d)" % (pid, cwd, port))
    else:
        print("Daemon running with PID %d (serving %s on port %d)" % (pid, cwd, port))


def main():
    colorama.init()
    try:
        os.makedirs(CONF_DIR)
    except Exception:
        pass

    context = daemon.DaemonContext(
        pidfile=PID_LOCK_FILE,
        working_directory=CWD,
    )
    has_args = len(sys.argv) > 1

    if has_args or context.pidfile.is_locked():
        control_process(context)
    elif not context.pidfile.is_locked():
        daemon_process(context)


if __name__ == '__main__':
    main()
