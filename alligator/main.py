import sys
import logging
import secrets
import shutil
import socketserver
from pathlib import Path

from stem.control import Controller


log = logging.getLogger(__name__)

server_config = {}


class TCPHandler(socketserver.StreamRequestHandler):
    def actually_handle(self):
        global server_config
        print("newcomer")
        first_line = self.rfile.readline().strip().decode()
        print(first_line)
        # http time
        verb, path, http_1_1 = first_line.split(" ")
        if verb != "GET":
            self.wfile.write(b"HTTP 1.1 405 Method not Allowed\r\n\r\n")
            print("405")
            return

        if Path(path).name != server_config.name:
            self.wfile.write(b"HTTP 1.1 404 Not Found\r\n\r\n")
            print("404")
            return

        self.wfile.write(b"HTTP/1.1 200 OK\r\n")
        # transfer time!
        with server_config.open(mode="rb") as fd:
            size = server_config.stat().st_size
            print("size", size)
            self.wfile.write(f"Content-Length: {size}\r\n".encode())
            self.wfile.write("\r\n".encode())
            chunk = fd.read(4096)
            while chunk:
                print("send", len(chunk))
                self.wfile.write(chunk)
                chunk = fd.read(4096)

        print("file sent!")
        self.server.shutdown()

    def handle(self):
        try:
            self.actually_handle()
        except:
            log.exception("shit")
            self.wfile.write(b"HTTP 1.1 500 Internal Server Error\r\n\r\n")
            return


def send_file(path):
    global server_config
    with Controller.from_port() as controller:
        controller.authenticate()
        hidden_service_dir = (
            Path(controller.get_conf("DataDirectory", "/tmp"))
            / f"alli_{secrets.token_hex(5)}"
        )

        print(f" * Creating our hidden service in {hidden_service_dir}")
        result = controller.create_hidden_service(
            str(hidden_service_dir), 80, target_port=5000
        )
        if not result.hostname:
            raise RuntimeError("unable to read hidden service directory from tor")

        print(f"available on http://{result.hostname}/_alli/{path.name}")

        server_config = path

        try:
            socketserver.TCPServer.allow_reuse_address = True
            with socketserver.TCPServer(("localhost", 5000), TCPHandler) as server:
                server.serve_forever()
        finally:
            # Shut down the hidden service and clean it off disk. Note that you *don't*
            # want to delete the hidden service directory if you'd like to have this
            # same *.onion address in the future.

            print(" * Shutting down our hidden service")
            controller.remove_hidden_service(hidden_service_dir)
            shutil.rmtree(hidden_service_dir)


import requests
import urllib.parse


def receive_file(onion_address):
    parsed = urllib.parse.urlparse(onion_address)
    assert parsed.netloc.endswith(".onion")

    path = Path(parsed.path)
    assert path.parent.name == "_alli"

    resp = requests.get(
        onion_address,
        proxies=dict(http="socks5h://localhost:9150", https="socks5h://localhost:9150"),
    )
    print("downloading to", path.name)
    with open(path.name, "wb") as fd:
        length = resp.headers["content-length"]
        print("length", length)
        for chunk in resp.iter_content(chunk_size=128):
            print("chunk", len(chunk))
            fd.write(chunk)

    print("ok!")


def main():
    if len(sys.argv) == 1:
        print(f"usage: {sys.argv[0]} send|receive path|code")
        return

    if sys.argv[1] in ("send", "tx"):
        file_to_send = Path(sys.argv[2]).resolve()
        send_file(file_to_send)
    elif sys.argv[1] in ("receive", "rx"):
        receive_code = sys.argv[2]
        receive_file(receive_code)
    else:
        print(f"usage: {sys.argv[0]} send|receive path|code")
        return
