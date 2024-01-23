import json
from cherrypy import (
    response
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


    def list_pictures(self) -> str:
        response.headers["Content-Type"] = "application/json"

        return json.dumps([picture.model_dump() for picture in self.controller.list_pictures()])
    
    def take_picture(self) -> str:
        response.headers["Content-Type"] = "application/json"

        picture = self.controller.take_picture(PictureIntent.AD_HOC)
        return json.dumps(picture.model_dump())
    
    def download_picture_content(self, id: PictureID):
        response.headers["Content-Type"] = "image/png"
        response.headers["Cache-Control"] = "max-age=31536000"

        return self.controller.load_picture_content(id).read()
    
    def download_picture_thumbnail(self, id: PictureID, extension: str | None = None):
        response.headers["Content-Type"] = "image/png"
        response.headers["Cache-Control"] = "max-age=31536000"

        return self.controller.load_picture_thumbnail(id).read()