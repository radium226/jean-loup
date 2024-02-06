from typing import Protocol
from pathlib import Path
import pendulum
from pendulum import DateTime
from subprocess import run, PIPE
from PIL import (
    Image,
    ImageDraw,
    ImageFont,
)
from io import BytesIO


from ..models import (
    Picture,
    PictureIntent,
    PictureID,
)


class Storage(Protocol):

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        pass

    def list_pictures(self) -> list[Picture]:
        ...

    def save_picture(self, date_time: DateTime, intent: PictureIntent, content: bytes) -> Picture:
        ...

    def load_picture_content(self, id: PictureID) -> bytes | None:
        ...

    def load_picture_thumbnail(self, id: PictureID) -> bytes | None:
        ...
    
    @classmethod
    def genuine(cls, folder_path: Path) -> "Storage":
        return _GenuineStorage(folder_path)
    
    @classmethod
    def fake(cls) -> "Storage":
        return _FakeStorage()
    

class _GenuineStorage(Storage):
    
    folder_path: Path

    def __init__(self, folder_path: Path) -> None:
        self.folder_path = folder_path
    
    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        pass

    def list_pictures(self) -> list[Picture]:
        def iter_pictures():
            for picture_file_path in (self.folder_path / "pictures").glob("**/*.png"):
                id = picture_file_path.stem
                intent = PictureIntent(picture_file_path.parent.name)
                yield Picture(
                    id=id,
                    date_time=pendulum.from_format(picture_file_path.stem, "YYYY-MM-DD_HH-mm-ss"),
                    intent=intent,
                )
        
        return list(iter_pictures())
    
    def save_picture(self, date_time: DateTime, intent: PictureIntent, content: bytes) -> Picture:
        id = date_time.format("YYYY-MM-DD_HH-mm-ss")

        content_file_path = self.folder_path / "pictures" / f"{intent}" / f"{id}.png"
        content_file_path.parent.mkdir(parents=True, exist_ok=True)
        content_file_path.write_bytes(content)
        
        thumbnail = self.generate_tumbnail(content)
        thumbnail_file_path = self.folder_path / ".thumbnails" / f"{id}.png"
        thumbnail_file_path.parent.mkdir(parents=True, exist_ok=True)
        thumbnail_file_path.write_bytes(thumbnail)
        
        return Picture(
            id=id,
            date_time=date_time,
            intent=intent,
        )
    
    def lookup_picture(self, id: PictureID) -> Picture | None:
        pictures = self.list_pictures()
        for picture in pictures:
            if picture.id == id:
                return picture
        
        return None
    
    def load_picture_content(self, id: PictureID) -> bytes | None:
        if picture := self.lookup_picture(id):
            return (self.folder_path / "pictures" / f"{picture.intent}" / f"{picture.id}.png").read_bytes()
        
        return None
    
    def load_picture_thumbnail(self, id: PictureID) -> bytes | None:
        if picture := self.lookup_picture(id):
            return (self.folder_path / ".thumbnails" / f"{picture.id}.png").read_bytes()
        
        return None

    def generate_tumbnail(self, content: bytes) -> bytes:
        command = [
            "ffmpeg",
                "-hide_banner", "-loglevel", "error",
                "-i", "-",
                "-vf",
                "scale=320:-1",
                "-frames:v", "1",
                "-f", "image2", 
                "-c", "png",
                "-",
        ]
        
        thubnail = run(command, stdout=PIPE, input=content, check=True).stdout
        return thubnail
    

class _FakeStorage(Storage):

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        pass

    def save_picture(self, date_time: DateTime, intent: PictureIntent, content: bytes) -> Picture:
        return Picture(
            id=date_time.format("YYYY-MM-DD_HH-mm-ss"),
            date_time=date_time,
            intent=intent,
        )
    
    def load_picture_content(self, id: PictureID) -> bytes | None:
        content = (Path(__file__).parent / "fake.png").read_bytes()
        image = Image.open(BytesIO(content))
        draw = ImageDraw.Draw(image)
        draw.text((10, 10), f"{id}", fill=(0, 0, 0), font_size=100)
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()
    
    def load_picture_thumbnail(self, id: PictureID) -> bytes | None:
        return self.load_picture_content(id)

    def list_pictures(self) -> list[Picture]:
        def iter_pictures():
            for i in range(100):
                yield Picture(
                    id=f"{i}",
                    date_time=pendulum.now().subtract(minutes=100 - i),
                    intent=PictureIntent.TIME_LAPSE,
                )
        return list(iter_pictures())