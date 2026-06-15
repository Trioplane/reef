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
    
ElementModel = Annotated[
    Union[
        GraphicElementModel,
        TextElementModel,
        AnimatedGraphicElementModel
    ],
    Field(discriminator="type")
]

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
            
            self.generate_reef_page_functions(pack, namespace, path)
                
            raise Drop()
        
        def generate_reef_page_functions(
            self,
            pack: DataPack,
            namespace: str,
            path: str
        ):
            """Generate the page registry functions at <ns>:reef/register/page/<path>."""
            
            identifier = f"{namespace}:{path}"
            storage = f"{namespace}:reef"
            nbt_path = f'register.page."{identifier}"'
            
            json_info: PageModel = self.data

            logger.debug("Building data %s", f"{namespace}:reef/{path}")
            
            log_prefix = ["", {"text": "[", "color": "#6e3787"}, {"text": "reef", "color": "#ed2de3"}, {"text": "] ", "color": "#6e3787"}]
            register_main = pack[namespace].functions.setdefault("reef/register_namespace", Function([
                f"tellraw @a[tag=reef.permissions.see_debug] {json.dumps([*log_prefix, {"text": f"Registering data for namespace '{namespace}'", "color": "#77d6ff"}])}",
            ]))
            
            function_contents = Function([
                f"data modify storage {storage} {nbt_path} set value {json_info.model_dump_json(exclude_none=True)}",
                f'function reef:api/register/page {{identifier: "{identifier}", storage_path: \'{storage} {nbt_path}\'}}'
            ])
            
            if not opts.compress_functions:
                pack[namespace].functions[f"reef/register/page/{path}"] = function_contents

                register_main.append([
                    f"function {namespace}:reef/register/page/{path}"
                ])
            else:
                register_main.append(function_contents)
        
    return ReefPageData

@configurable("reef", validator=ReefPluginOptions)
def page(ctx: Context, opts: ReefPluginOptions):
    """Adds support for Reef page JSON files."""

    ctx.data.extend_namespace.append(create_reef_page_data_namespace(ctx, opts))