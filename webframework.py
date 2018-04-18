import time

HTML_ROOT_DIR = "./static"

class Application():
    def __init__(self, urls):
        self.urls = urls

    # treat this object like a function
    def __call__(self, env, start_response):
        req_path = env.get("req_path", "/")

        # static pages
        if req_path.startswith("/static"):
            # read and return static pages in the directory
            file_name = req_path[7:]
            try:
                f = open(HTML_ROOT_DIR + file_name, "rb")
            except IOError:
                status = "404 Not Found"
                headers = []
                start_response(status, headers)
                return("Not Found")
            else:
                file_data = f.read()
                f.close()
                status = "200 OK"
                headers = []
                start_response(status, headers)
                return(file_data.decode("utf-8"))

        # dynamic pages
        else:
            for url, handler in self.urls:
                if req_path == url:
                    # call handler
                    return handler(env, start_response)
            # if no url matched, return 404
            status = "404 Not Found"
            headers = []
            start_response(status, headers)
            return ("Not Found")


# handlers
def home(env, start_response):
    status = "200 OK"
    headers = []
    start_response(status, headers)
    return("Homepage!")

def show_ctime(env, start_response):
    status = "200 OK"
    headers = []
    start_response(status, headers)
    return(time.ctime())


# router
urls = [
    ("/", home),
    ("/ctime", show_ctime)
]

# create application object with router
app = Application(urls)