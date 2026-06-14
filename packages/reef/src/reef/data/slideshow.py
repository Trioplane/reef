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

__all__ = ["slideshow"]

SLIDESHOW_NAMESPACE = "reef/data/slideshow"
logger = logging.getLogger(SLIDESHOW_NAMESPACE)

class SlideshowModel(RootModel[list[models.ResourceLocation]]):
    """See https://github.com/Trioplane/reef/wiki/definition_schemas#slideshow"""
    pass

def create_reef_slideshow_data_namespace(ctx: Context, opts: ReefPluginOptions):
    class ReefSlideshowData(JsonFileBase):
        
        model = SlideshowModel
        scope: ClassVar[NamespaceFileScope] = ("reef", "slideshow")
        extension: ClassVar[str] = ".json"

        def bind(self, pack: DataPack, path: str):
            super().bind(pack, path)
            
            namespace, _, path = path.partition(":")
            
            # TODO: implement code-gen for slideshows
            # temp variable to trigger deserialization
            _ = self.data
                
            raise Drop()
        
    return ReefSlideshowData

@configurable("reef", validator=ReefPluginOptions)
def slideshow(ctx: Context, opts: ReefPluginOptions):
    """Adds support for Reef slideshow JSON files."""

    ctx.data.extend_namespace.append(create_reef_slideshow_data_namespace(ctx, opts))