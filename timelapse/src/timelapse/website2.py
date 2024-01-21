from contextlib import ExitStack

from cherrypy import expose, request, response, tree, engine, server, dispatch, NotFound
from dataclasses import dataclass
from pendulum import DateTime
import json

from typing import TypeAlias
from io import BytesIO
from pathlib import Path
from cherrypy import tools
import pendulum

from mimetypes import guess_type

from .controller import Controller
from .picture_format import PictureFormat

PictureID: TypeAlias = str


@dataclass
class Picture():

    id: PictureID

    date_time: DateTime



class APIEndpoint():

    pictures: list[Picture]

    def __init__(self, controller: Controller):
        self.controller = controller


    def list_pictures(self) -> list[dict]:
        response.headers["Content-Type"] = "application/json"

        objs = [
            dict(
                id=picture_path.stem,
                dateTime=pendulum.from_format(picture_path.stem, "YYYY-MM-DD_HH-mm-ss").to_iso8601_string(),
            )
            for picture_path in self.controller.list_pictures()
        ]
        return json.dumps([obj for obj in sorted(objs, key=lambda obj: obj["dateTime"], reverse=True)]).encode("utf-8")
    
    def take_picture(self) -> Picture:
        picture_content = self.controller.take_picture(PictureFormat.PNG)
        response.headers["Content-Type"] = "application/json"
        picture_path = self.controller.save_picture(picture_content)
        picture = dict(
            id=picture_path.stem,
            date_time=pendulum.from_format(picture_path.stem, "YYYY-MM-DD_HH-mm-ss").to_iso8601_string(),
        )
        return json.dumps(picture).encode("utf-8")
    
    def get_picture(self, id: PictureID) -> Picture:
        return f"Show picture info! (id={id})"
    
    def download_picture_content(self, id: PictureID):
        response.headers["Content-Type"] = "image/png"
        response.headers["Cache-Control"] = "max-age=31536000"

        return (self.controller.data_folder_path / "pictures" / f"{id}.png").open("rb")
    
    def download_picture_thumbnail(self, id: PictureID, extension: str | None = None):
        response.headers["Content-Type"] = "image/png"
        response.headers["Cache-Control"] = "max-age=31536000"
        if (self.controller.data_folder_path / "pictures" / "thumbnails" / f"{id}.png").exists():
            return (self.controller.data_folder_path / "pictures" / "thumbnails" / f"{id}.png").open("rb")
        else:
            file_path = self.controller.data_folder_path / "pictures" / f"{id}.png"
            return self.controller.load_tumbnail(file_path)
    
    def delete_picture(self, id: PictureID):
        return f"Deleting picture! (id={id})"


class UIEndpoint():

    folder_path: Path

    def __init__(self, folder_path: Path):
        self.folder_path = folder_path

    @expose
    def serve_index(self, url_path):
        file_path = self.folder_path / url_path
        if file_path.exists() and file_path.is_file():
            mime_type, _ = guess_type(str(file_path.absolute()))
            print(mime_type)
            response.headers["Content-Type"] = mime_type
            return file_path.open("rb")
        else:
            response.headers["Content-Type"] = "text/html"
            return (self.folder_path / "index.html").open("r")
    
    def serve_assets(self, url_path):
        file_path = self.folder_path / "assets" / url_path
        if file_path.exists() and file_path.is_file():
            mime_type, _ = guess_type(str(file_path.absolute()))
            response.headers["Content-Type"] = mime_type
            return file_path.open("rb")
        else:
            raise NotFound(url_path)
        

class Website():

    DEFAULT_UI_FOLDER_PATH = Path("/usr/lib/timelapse/website/ui")

    exit_stack: ExitStack
    ui_folder_path: Path

    def __init__(self, ui_folder_path: Path | None):
        self.exit_stack = ExitStack()
        self.ui_folder_path = ui_folder_path or self.DEFAULT_UI_FOLDER_PATH

    def mount_api(self, controller: Controller):
        api_endpoint = APIEndpoint(controller)
        api_dispatcher = dispatch.RoutesDispatcher()
        api_dispatcher.connect("api", "/pictures/:id", controller=api_endpoint, action="get_picture", conditions=dict(method=["GET"]))
        api_dispatcher.connect("api", "/pictures/:id", controller=api_endpoint, action="delete_picture", conditions=dict(method=["DELETE"]))
        api_dispatcher.connect("api", "/pictures/{id}/thumbnail", controller=api_endpoint, action="download_picture_thumbnail", conditions=dict(method=["GET"]))
        api_dispatcher.connect("api", "/pictures/{id}/thumbnail.{extension}", controller=api_endpoint, action="download_picture_thumbnail", conditions=dict(method=["GET"]))
        api_dispatcher.connect("api", "/pictures/:id/content", controller=api_endpoint, action="download_picture_content", conditions=dict(method=["GET"]))
        api_dispatcher.connect("api", "/pictures", controller=api_endpoint, action="take_picture", conditions=dict(method=["POST"]))
        api_dispatcher.connect("api", "/pictures", controller=api_endpoint, action="list_pictures", conditions=dict(method=["GET"]))
        tree.mount(None, "/api", config={
            "/": {
                "request.dispatch": api_dispatcher,
            },
        })

    def mount_ui(self):
        endpoint = UIEndpoint(self.ui_folder_path)
        dispatcher = dispatch.RoutesDispatcher()
        dispatcher.connect("ui", "/assets/{url_path:.*}", controller=endpoint, action="serve_assets", conditions=dict(method=["GET"]))
        dispatcher.connect("ui", "/{url_path:.*}", controller=endpoint, action="serve_index", conditions=dict(method=["GET"]))
        tree.mount(None, "/", config={
            "/": {
                "request.dispatch": dispatcher,
            },
        })

    def __enter__(self):
        controller = self.exit_stack.enter_context(Controller.create())

        self.mount_api(controller)
        self.mount_ui()
        
        server.socket_host = "0.0.0.0"
        engine.start()
        return self
    

    def __exit__(self, type, value, trackeback):
        self.exit_stack.close()

    def wait_for(self):
        engine.block()
