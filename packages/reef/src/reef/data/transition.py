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

__all__ = ["transition"]

TRANSITION_NAMESPACE = "reef/data/transition"
logger = logging.getLogger(TRANSITION_NAMESPACE)

class TransitionModel(BaseModel):
    """See https://github.com/Trioplane/reef/wiki/definition_schemas#transition"""
    frames: int
    switch_frame: int
    model: models.ResourceLocation

def create_reef_transition_data_namespace(ctx: Context, opts: ReefPluginOptions):
    class ReefTransitionData(JsonFileBase):
        
        model = TransitionModel
        scope: ClassVar[NamespaceFileScope] = ("reef", "transition")
        extension: ClassVar[str] = ".json"

        def bind(self, pack: DataPack, path: str):
            super().bind(pack, path)
            
            namespace, _, path = path.partition(":")
            
            # TODO: implement code-gen for transitions
            # temp variable to trigger deserialization
            _ = self.data
                
            raise Drop()
        
    return ReefTransitionData

@configurable("reef", validator=ReefPluginOptions)
def transition(ctx: Context, opts: ReefPluginOptions):
    """Adds support for Reef transition JSON files."""

    ctx.data.extend_namespace.append(create_reef_transition_data_namespace(ctx, opts))