from cherrypy import expose, request, response, tree, engine, server
from contextlib import ExitStack

from .camera import Camera
from .picture_format import PictureFormat


class API():

    def __init__(self, camera: Camera):
        self.camera = camera

    @expose
    def pictures(self):
        match request.method:
            case "POST":
                response.headers["Content-Type"] = "image/png"
                picture = self.camera.take_picture(PictureFormat.PNG)
                return picture

            case _:
                response.code = 404
                return None
        

class Root():

    @expose
    def index(self):
        return "Hello world! "


class Website:

    def __init__(self, fake: bool = False, port: int = 8080):
        self.exit_stack = ExitStack()
        self.fake = fake

    def __enter__(self):
        camera = self.exit_stack.enter_context(Camera.create(self.fake))
        tree.mount(Root(), "/")
        tree.mount(API(camera), "/api")
        server.socket_host = "0.0.0.0"
        engine.start()
        return self

    def __exit__(self, type, value, traceback):
        self.exit_stack.close()

    @expose
    def index(self):
        return "Hello world! "

    def wait_for(self):
        engine.block()