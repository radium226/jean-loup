from contextlib import ExitStack

from cherrypy import expose, response, tree, engine, server, dispatch, NotFound
from dataclasses import dataclass
from pendulum import DateTime
import json

from typing import TypeAlias
from pathlib import Path
import pendulum

from mimetypes import guess_type

from .controller import Controller
from .models import (
    PictureIntent
)
from .config import Config

PictureID: TypeAlias = str


@dataclass
class Picture():

    id: PictureID

    date_time: DateTime



class APIEndpoint():

    pictures: list[Picture]

    def __init__(self, controller: Controller):
        self.controller = controller


    def list_pictures(self) -> bytes:
        response.headers["Content-Type"] = "application/json"

        objs = [
            dict(
                id=picture.file_path.stem,
                dateTime=pendulum.from_format(picture.file_path.stem, "YYYY-MM-DD_HH-mm-ss").to_iso8601_string(),
            )
            for picture in self.controller.list_pictures()
        ]
        return json.dumps([obj for obj in sorted(objs, key=lambda obj: obj["dateTime"], reverse=True)]).encode("utf-8")
    
    def take_picture(self) -> bytes:
        picture, content, _ = self.controller.take_picture(PictureIntent.AD_HOC)
        response.headers["Content-Type"] = "application/json"
        return json.dumps(content).encode("utf-8")
    
    def get_picture(self, id: PictureID) -> str:
        return f"Show picture info! (id={id})"
    
    def download_picture_content(self, id: PictureID):
        response.headers["Content-Type"] = "image/png"
        response.headers["Cache-Control"] = "max-age=31536000"

        return self.controller.load_picture_content(id)
    
    def download_picture_thumbnail(self, id: PictureID, extension: str | None = None):
        response.headers["Content-Type"] = "image/png"
        response.headers["Cache-Control"] = "max-age=31536000"

        return self.controller.load_picture_thumbnail(id)
    
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

    def __init__(self, ui_folder_path: Path | None, config: Config):
        self.exit_stack = ExitStack()
        self.ui_folder_path = ui_folder_path or self.DEFAULT_UI_FOLDER_PATH
        self.config = config

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
        controller = self.exit_stack.enter_context(Controller.create(self.config))

        self.mount_api(controller)
        self.mount_ui()
        
        server.socket_host = "0.0.0.0"
        engine.start()
        return self
    

    def __exit__(self, type, value, trackeback):
        self.exit_stack.close()

    def serve_forever(self):
        engine.block()
