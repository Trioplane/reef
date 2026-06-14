import json
import logging
from pathlib import Path
from pydantic import BaseModel, Field, TypeAdapter, RootModel
from typing import Any, ClassVar, Literal, Annotated, Union

from beet import (
    Context,
    configurable,
    DataPack,
    Drop,
    Function,
    JsonFileBase,
    NamespaceFileScope,
)

from .. import models
from ..options import ReefPluginOptions

__all__ = ["page"]

PAGE_NAMESPACE = "reef/data/page"
logger = logging.getLogger(PAGE_NAMESPACE)

class ElementCommandsModel(BaseModel):
    on_enter: list[str] | None = None
    on_exit: list[str] | None = None

class ElementBaseModel(BaseModel):
    commands: ElementCommandsModel | None = None
    pos: models.Vector3 | None = None
    
    translation: models.Vector3 | None = None
    scale: models.Vector3 | None = None
    left_rotation: models.DisplayTransformationRotation | None = None
    right_rotation: models.DisplayTransformationRotation | None = None
    
    components: dict[str, Any] | None = None
    
class GraphicElementModel(ElementBaseModel):
    type: Literal["graphic"]
    model: models.ResourceLocation
    
class TextElementModel(ElementBaseModel):
    type: Literal["text"]
    text: models.TextComponent
    background: int | None = None
    alignment: Literal["left", "center", "right"] | None = None
    line_width: int | None = None
    
class AnimatedGraphicElementModel(ElementBaseModel):
    type: Literal["animated_graphic"]
    model: models.ResourceLocation
    frames: int
    
class ElementModel(RootModel[Annotated[
    Union[
        GraphicElementModel,
        TextElementModel,
        AnimatedGraphicElementModel
    ],
    Field(discriminator="type")
]]):
    """See https://github.com/Trioplane/reef/wiki/definition_schemas#element"""
    pass

class PageCommandsModel(BaseModel):
    on_load: list[str] | None = None
    on_enter: list[str] | None = None
    on_unload: list[str] | None = None

class PageModel(BaseModel):
    """See https://github.com/Trioplane/reef/wiki/definition_schemas#page"""
    
    commands: PageCommandsModel | None = None
    transition: models.ResourceLocation | None = None
    sequence: list[list[ElementModel]]

def create_reef_page_data_namespace(ctx: Context, opts: ReefPluginOptions):
    class ReefPageData(JsonFileBase):
        
        model = PageModel
        scope: ClassVar[NamespaceFileScope] = ("reef", "page")
        extension: ClassVar[str] = ".json"
        
        def bind(self, pack: DataPack, path: str):
            super().bind(pack, path)
            
            namespace, _, path = path.partition(":")
            
            # TODO: implement code-gen for pages
            # temp variable to trigger deserialization
            _ = self.data
                
            raise Drop()
        
    return ReefPageData

@configurable("reef", validator=ReefPluginOptions)
def page(ctx: Context, opts: ReefPluginOptions):
    """Adds support for Reef page JSON files."""

    ctx.data.extend_namespace.append(create_reef_page_data_namespace(ctx, opts))