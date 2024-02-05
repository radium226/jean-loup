import json
from cherrypy import (
    response,
    NotFound,
)

from ....models import (
    Picture,
    PictureID,
    PictureIntent,
)
from ....controller import Controller


class API():

    pictures: list[Picture]

    def __init__(self, controller: Controller):
        self.controller = controller


    def list_pictures(self) -> bytes:
        response.headers["Content-Type"] = "application/json"

        return json.dumps([picture.model_dump() for picture in self.controller.list_pictures()]).encode("utf-8")
    
    def take_picture(self) -> bytes:
        response.headers["Content-Type"] = "application/json"

        picture = self.controller.take_picture(PictureIntent.AD_HOC)
        return json.dumps(picture.model_dump()).encode("utf-8")
    
    def download_picture_content(self, id: PictureID) -> bytes:
        response.headers["Content-Type"] = "image/png"
        response.headers["Cache-Control"] = "max-age=31536000"

        if not (content := self.controller.load_picture_content(id)):
            raise NotFound()
        
        return content
    
    def download_picture_thumbnail(self, id: PictureID, extension: str | None = None) -> bytes:
        response.headers["Content-Type"] = "image/png"
        response.headers["Cache-Control"] = "max-age=31536000"

        if not (thumbnail := self.controller.load_picture_thumbnail(id)):
            raise NotFound()
        
        return thumbnail
    
    def generate_time_lapse(self) -> bytes:
        response.headers["Content-Type"] = "video/mp4"
        return self.controller.generate_time_lapse()
        
    def read_config_values(self) -> bytes:
        response.headers["Content-Type"] = "application/json"
        return json.dumps(self.controller.config.values.model_dump()).encode("utf-8")