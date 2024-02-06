import pathlib

from typing import Annotated, Any

from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core.core_schema import (
    CoreSchema, 
    chain_schema, 
    str_schema, 
    no_info_plain_validator_function, 
    json_or_python_schema, 
    union_schema, 
    is_instance_schema, 
    plain_serializer_function_ser_schema,
)


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

        def validate_from_str(value: str) -> pathlib.Path:
            return pathlib.Path(value)

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
                    is_instance_schema(pathlib.Path),
                    from_str_schema,
                ]
            ),
            serialization=plain_serializer_function_ser_schema(
                lambda instance: str(instance)
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return handler(str_schema())
    

Path = Annotated[pathlib.Path, PydanticAnnotationForTime]