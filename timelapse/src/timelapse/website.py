# from cherrypy import expose, request, response, tree, engine, server
# from contextlib import ExitStack
# from pathlib import Path
# from enum import StrEnum, auto
# from queue import Queue

# from .camera import Camera
# from .picture_format import PictureFormat
# from .timelapse import Timelapse


# class WorkerStatus(StrEnum):
#     WORKING = auto()

#     DONE = auto()


# class API():

#     def __init__(self, camera: Camera, timelapse: Timelapse):
#         self.camera = camera
#         self.timelapse = timelapse
#         self.

#     @expose
#     def pictures(self):
#         match request.method:
#             case "POST":
#                 response.headers["Content-Type"] = "image/png"
#                 picture = self.camera.take_picture(PictureFormat.PNG)
#                 return picture

#             case _:
#                 response.code = 404
#                 return None
        

#     @expose
#     def timelapses(self):
#         match request.method:
#             case "POST":
#                 worker = Worker()
#                 self.workers.append({ worker.id: worker })
#                 response.headers["Content-Type"] = "application/json"
#                 return {
#                     "id": worker.id,
#                 }

#             case _:
#                 response.code = 404
#                 return None

# class UI():
#     pass


# class Website:

#     DEFAULT_UI_FOLDER_PATH = Path("/usr/lib/timelapse/website/ui")

#     def __init__(self, fake: bool = False, port: int = 8080, ui_folder_path: Path | None = None):
#         self.exit_stack = ExitStack()
#         self.fake = fake
#         self.ui_folder_path = ui_folder_path or self.DEFAULT_UI_FOLDER_PATH

#     def __enter__(self):
#         camera = self.exit_stack.enter_context(Camera.create(self.fake))
#         tree.mount(UI(), "/", config={
#             "/": {
#                 "tools.staticdir.on": True,
#                 "tools.staticdir.dir": str(self.ui_folder_path.absolute()),
#                 "tools.staticdir.index": 'index.html',
#             },
#         })
#         tree.mount(API(camera), "/api")
#         server.socket_host = "0.0.0.0"
#         engine.start()
#         return self

#     def __exit__(self, type, value, traceback):
#         self.exit_stack.close()

#     @expose
#     def index(self):
#         return "Hello world! "

#     def wait_for(self):
#         engine.block()