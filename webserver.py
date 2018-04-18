import sys
import re
import socket
from multiprocessing import Process


class WebServer():
    def __init__(self, app):
        self.main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.main_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.app = app

    # bind the port
    def bind(self, port):
        self.main_socket.bind(("", port))

    # response header
    def start_response(self, status, headers):
        server_headers = [
            ("Server", "My Server")
        ] + headers
        response_headers = "HTTP1.1" + status + "\r\n"
        for header in headers:
            response_headers += "{0}:{1}\r\n".format(header[0], header[1])
        self.response_headers = response_headers

    # start the server
    def start(self):
        print("--server start--")
        self.main_socket.listen(50)
        try:
            while True:
                new_socket, client_addr = self.main_socket.accept()
                print("client request: {}".format(client_addr))
                p = Process(target=self.client_handler, args=(new_socket,))
                p.start()
                new_socket.close()
        finally:
            print("--server offline--")
            self.main_socket.close()

    # client handler
    def client_handler(self, new_socket):
        try:
            req_data = new_socket.recv(1024)
            if len(req_data)>0:
                # parse the request
                req_headers = req_data.decode("utf-8").splitlines()
                # requested path
                req_path = re.match(r"\w+ +(/[^ ]*)", req_headers[0]).group(1)
                # request method
                http_method = re.match(r"[^\s]+", req_headers[0]).group(0)
                # store request headers into env (WSGI)
                env = {
                    'req_path': req_path,
                    'method': http_method,
                }
                # pass env and start_response method to Application
                res_body = self.app(env, self.start_response)
                res = self.response_headers + "\r\n" + res_body
                # send the response to client
                new_socket.send(bytes(res, "utf-8"))

        finally:
            new_socket.close()


def main():
    # create web application object
    if len(sys.argv)<2:
        sys.exit("python3 webserver.py module:app")
    else:
        module_name, app_name = sys.argv[1].split(":")
        m = __import__(module_name)
        app = getattr(m, app_name)

    # pass the application object to the web server and start it
    my_server = WebServer(app)
    my_server.bind(7788)
    my_server.start()

if __name__ == "__main__":
    main()