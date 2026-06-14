from pydantic import BaseModel, Field, TypeAdapter, RootModel
from typing import Any, ClassVar, Literal, Annotated, Union

__all__ = [
    "DisplayTransformationRotation", 
    "ResourceLocation", 
    "TextComponent", 
    "Vector3", 
    "Vector4"
]

type ResourceLocation = Annotated[str, Field(pattern=r'^[0-9a-z_\-.]+:[0-9a-z_\-./]+$')]
"""Resource locations are a way to declare and specify game objects in Minecraft, which can identify built-in and user-defined objects without potential ambiguity or conflicts."""

type Vector3 = tuple[float, float, float]
type Vector4 = tuple[float, float, float, float]

class DisplayTransformationRotationAxisAngle(BaseModel):
    angle: float
    axis: Vector3
    
type DisplayTransformationRotation = Vector4 | DisplayTransformationRotationAxisAngle

type TextComponent = str | list[TextComponent] | dict[str, Any]