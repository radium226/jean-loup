from pathlib import Path
from cherrypy import (
    expose, 
    NotFound,
    response
)
from mimetypes import guess_type


class UI():

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