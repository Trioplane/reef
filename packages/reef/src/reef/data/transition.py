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
            self.generate_reef_transition_functions(pack, namespace, path)
                
            raise Drop()
        
        def generate_reef_transition_functions(
            self,
            pack: DataPack,
            namespace: str,
            path: str
        ):
            """Generate the transition registry functions at <ns>:reef/register/transition/<path>."""
            
            identifier = f"{namespace}:{path}"
            storage = f"{namespace}:reef"
            nbt_path = f'register.transition."{identifier}"'
            
            json_info: TransitionModel = self.data

            logger.debug("Building data %s", f"{namespace}:reef/{path}")
            
            log_prefix = ["", {"text": "[", "color": "#6e3787"}, {"text": "reef", "color": "#ed2de3"}, {"text": "] ", "color": "#6e3787"}]
            register_main = pack[namespace].functions.setdefault("reef/register_namespace", Function([
                f"tellraw @a[tag=reef.permissions.see_debug] {json.dumps([*log_prefix, {"text": f"Registering data for namespace '{namespace}'", "color": "#77d6ff"}])}",
            ]))
            
            function_contents = Function([
                f"data modify storage {storage} {nbt_path} set value {json_info.model_dump_json(exclude_none=True)}",
                f'function reef:api/register/transition {{identifier: "{identifier}", storage_path: \'{storage} {nbt_path}\'}}'
            ])
            
            if not opts.compress_functions:
                pack[namespace].functions[f"reef/register/transition/{path}"] = function_contents

                register_main.append([
                    f"function {namespace}:reef/register/transition/{path}"
                ])
            else:
                register_main.append(function_contents)
        
    return ReefTransitionData

@configurable("reef", validator=ReefPluginOptions)
def transition(ctx: Context, opts: ReefPluginOptions):
    """Adds support for Reef transition JSON files."""

    ctx.data.extend_namespace.append(create_reef_transition_data_namespace(ctx, opts))