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

from .. import state
from .. import models
from ..options import ReefPluginOptions

__all__ = ["slideshow", "ReefSlideshowData"]

SLIDESHOW_NAMESPACE = "reef/data/slideshow"
logger = logging.getLogger(SLIDESHOW_NAMESPACE)

class SlideshowModel(RootModel[list[models.ResourceLocation]]):
    """See https://github.com/Trioplane/reef/wiki/definition_schemas#slideshow"""
    pass

class ReefSlideshowData(JsonFileBase):
    """Class representing Reef Slideshow files in data/ns/reef/slideshow"""
    
    model = SlideshowModel
    scope: ClassVar[NamespaceFileScope] = ("reef", "slideshow")
    extension: ClassVar[str] = ".json"

    def bind(self, pack: DataPack, path: str):
        super().bind(pack, path)
        
        namespace, _, path = path.partition(":")
        
        # TODO: implement code-gen for slideshows
        # temp variable to trigger deserialization
        self.generate_reef_slideshow_functions(pack, namespace, path)
            
        raise Drop()
    
    def generate_reef_slideshow_functions(
        self,
        pack: DataPack,
        namespace: str,
        path: str
    ):
        """Generate the slideshow registry functions at <ns>:reef/register/slideshow/<path>."""
        
        identifier = f"{namespace}:{path}"
        storage = f"{namespace}:reef"
        nbt_path = f'register.slideshow."{identifier}"'
        
        json_info: SlideshowModel = self.data
        
        logger.debug("Building data %s", f"{namespace}:reef/{path}")
        
        log_prefix = ["", {"text": "[", "color": "#6e3787"}, {"text": "reef", "color": "#ed2de3"}, {"text": "] ", "color": "#6e3787"}]
        register_main = pack[namespace].functions.setdefault("reef/register_namespace", Function([
            f"tellraw @a[tag=reef.permissions.see_debug] {json.dumps([*log_prefix, {"text": f"Registering data for namespace '{namespace}'", "color": "#77d6ff"}])}",
        ]))
        
        function_contents = Function([
            f"data modify storage {storage} {nbt_path} set value {json_info.model_dump_json(exclude_none=True)}",
            f'function reef:api/register/slideshow {{identifier: "{identifier}", storage_path: \'{storage} {nbt_path}\'}}'
        ])
        
        if not state.opts.compress_functions:
            pack[namespace].functions[f"reef/register/slideshow/{path}"] = function_contents

            register_main.append([
                f"function {namespace}:reef/register/slideshow/{path}"
            ])
        else:
            register_main.append(function_contents)

@configurable("reef", validator=ReefPluginOptions)
def slideshow(ctx: Context, opts: ReefPluginOptions):
    """Adds support for Reef slideshow JSON files."""

    ctx.data.extend_namespace.append(ReefSlideshowData)