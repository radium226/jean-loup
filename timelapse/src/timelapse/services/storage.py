from typing import Protocol, overload
from pathlib import Path
import pendulum
from pendulum import DateTime
from io import BytesIO
from subprocess import run, PIPE


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

    def save_picture(self, date_time: DateTime, intent: PictureIntent, content: BytesIO) -> Picture:
        ...

    @overload
    def load_picture_content(self, __picture: Picture) -> BytesIO:
        ...

    @overload
    def load_picture_content(self, __picture_id: PictureID) -> BytesIO:
        ...

    def load_picture_thumbnail(self, picture_or_picture_id: Picture | PictureID) -> BytesIO:
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
            for picture_file_path in (self.folder_path / "pictures").glob("*.png"):
                yield Picture(
                    date_time=pendulum.from_format(picture_file_path.stem, "YYYY-MM-DD_HH-mm-ss"),
                    intent=PictureIntent.TIMELAPSE,
                    file_path=picture_file_path.relative_to(self.folder_path),
                )
        
        return list(iter_pictures())
    
    def save_picture(self, date_time: DateTime, intent: PictureIntent, content: BytesIO) -> Picture:
        file_path = self.folder_path / "pictures" / f"{date_time.format('YYYY-MM-DD_HH-mm-ss')}.png"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(content.read())
        return Picture(
            date_time=date_time,
            intent=intent,
            file_path=file_path.relative_to(self.folder_path),
        )
    
    def load_picture_content(self, picture_or_picture_id: Picture | PictureID) -> BytesIO:
        raise Exception("Not implemented! ")
    
    def load_picture_thumbnail(self, picture_or_picture_id: Picture | PictureID) -> BytesIO:
        raise Exception("Not implemented! ")

    def generate_tumbnail(self, file_path: Path) -> BytesIO:
        command = [
            "ffmpeg",
            "-hide_banner", "-loglevel", "error",
            "-i", f"{file_path}",
            "-vf",
            "scale=320:-1",
            "-frames:v", "1",
            "-f", "image2", 
            "-c", "png",
            "-",
        ]
        
        return BytesIO(run(command, stdout=PIPE, check=True).stdout)
    

class _FakeStorage(Storage):

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        pass

    def save_picture(self, date_time: DateTime, intent: PictureIntent, content: BytesIO) -> Picture:
        return Picture(
            date_time=date_time,
            intent=intent,
            file_path=Path("fake.png"),
        )
    
    def load_picture_content(self, picture_or_picture_id: Picture | PictureID) -> BytesIO:
        raise Exception("Not implemented! ")
    
    def load_picture_thumbnail(self, picture_or_picture_id: Picture | PictureID) -> BytesIO:
        raise Exception("Not implemented! ")

    def list_pictures(self) -> list[Picture]:
        return []