from pydantic import BaseModel
import pendulum
from pendulum import Time
from pathlib import Path
from typing import Annotated, Any
from types import SimpleNamespace
import json

from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core.core_schema import CoreSchema, chain_schema, str_schema, no_info_plain_validator_function, json_or_python_schema, union_schema, is_instance_schema, plain_serializer_function_ser_schema

from deepmerge import always_merger

class PydanticAnnotationForTime:

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        """
        We return a pydantic_core.CoreSchema that behaves in the following ways:

        * ints will be parsed as `ThirdPartyType` instances with the int as the x attribute
        * `ThirdPartyType` instances will be parsed as `ThirdPartyType` instances without any changes
        * Nothing else will pass validation
        * Serialization will always return just an int
        """

        def validate_from_str(value: str) -> Time:
            return pendulum.from_format(value, "HH:mm:ss").time()

        from_str_schema = chain_schema(
            [
                str_schema(),
                no_info_plain_validator_function(validate_from_str),
            ]
        )

        return json_or_python_schema(
            json_schema=from_str_schema,
            python_schema=union_schema(
                [
                    # check if it's an instance first before doing any further work
                    is_instance_schema(Time),
                    from_str_schema,
                ]
            ),
            serialization=plain_serializer_function_ser_schema(
                lambda instance: instance.format("HH:mm:ss")
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return handler(str_schema())
    

AnnotatedTimeForPydantic = Annotated[Time, PydanticAnnotationForTime]


def obj_to_dict(obj):
    if isinstance(obj, dict):
        res = {}
        for k, v in obj.items():
            res[k] = obj_to_dict(v)
        return res
    elif isinstance(obj, list):
        return [obj_to_dict(item) for item in obj]
    elif isinstance(obj, SimpleNamespace):
        return obj_to_dict(vars(obj))
    else:
        return obj

class Hotspot(BaseModel):

    enabled: bool

    ssid: str

class ConfigValues(BaseModel):

    hotspot: Hotspot


class Config():

    DEFAULT_FOLDER_PATH = Path("/etc/timelapse")

    DEFAULT_OBJ = {
        "hostspot": {
            "enabled": True,
            "ssid": "bamboo",
        }
    }

    obj: dict

    def __init__(self, obj: dict | SimpleNamespace | None = None, /, folder_path: Path | None = None):
        self.obj = obj_to_dict(obj) or self._read_obj(folder_path) or self.DEFAULT_OBJ

    @property
    def values(self) -> ConfigValues:
        return ConfigValues.model_validate(self.obj)

    @classmethod
    def _read_obj(cls, folder_path: Path | None = None) -> dict | None:
        file_path = ( folder_path or cls.DEFAULT_FOLDER_PATH ) / "config.json"
        if file_path.exists():
            with file_path.open("r") as f:
                obj = json.load(f)
                if isinstance(obj, dict):
                    return obj
                else:
                    return None
        else:
            return None
        
    def _write_obj(self, folder_path: Path | None = None) -> None:
        file_path = ( folder_path or self.DEFAULT_FOLDER_PATH ) / "config.json"
        with file_path.open("w") as f:
            f.write(self.values.model_dump_json())
    
    def override_with(self, other: "Config") -> "Config":
        return Config(
            always_merger.merge(self.obj, other.obj))
    
    def save_values(self, folder_path: Path | None = None):
        self._write_obj(folder_path)