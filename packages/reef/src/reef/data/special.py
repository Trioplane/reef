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
from ..models import ResourceLocation
from ..options import ReefPluginOptions

__all__ = ["special", "ReefSpecialData"]

SPECIAL_NAMESPACE = "reef/data/special"
logger = logging.getLogger(SPECIAL_NAMESPACE)

class ReefBaseSpecialDataModel(BaseModel):
    transition: ResourceLocation | None = None
    """Resource location of a transition"""
    
    page_count: int
    """Page count of the slideshow"""

class ReefSpecialDataPdfModel(ReefBaseSpecialDataModel):
    """A Reef Mini definition using PDF files."""
    
    type: Literal["reef:pdf"]
    """A Reef Mini definition using PDF files."""
    
    pdf: ResourceLocation
    """Resource location pointing to the PDF file in `assets/<namespace>/reef/<path>`."""
    
class ReefSpecialDataItemModelModel(ReefBaseSpecialDataModel):
    """A Reef Mini definition using an item model definition file."""
    
    type: Literal["reef:item_model"]
    """A Reef Mini definition using an item model definition file."""
    
    item_model: ResourceLocation
    """Resource location pointing to the item model definition in `assets/<namespace>/items/<path>`."""

class ReefSpecialDataModel(RootModel[Annotated[
    Union[
        ReefSpecialDataPdfModel,
        ReefSpecialDataItemModelModel
    ],
    Field(discriminator="type")
]]):
    pass

class ReefSpecialData(JsonFileBase):
    """Class representing Reef Special files in data/ns/reef/special"""
    
    model = ReefSpecialDataModel
    scope: ClassVar[NamespaceFileScope] = ("reef", "special")
    extension: ClassVar[str] = ".json"
    
    def bind(self, pack: DataPack, path: str):
        super().bind(pack, path)
        
        print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
        
        namespace, _, path = path.partition(":")
        
        self.generate_reef_mini_functions(pack, namespace, path)
            
        raise Drop()
            
    def generate_reef_mini_functions(
        self, 
        pack: DataPack,
        namespace: str, 
        path: str
    ):
        """Generates the function files to register a Reef Mini definition from a PDF or an Item Model."""
        
        identifier = f"{namespace}:{path}"
        storage = f"{namespace}:reef"
        nbt_path = f'register.mini."{identifier}"'
        
        json_info: ReefSpecialDataPdfModel | ReefSpecialDataItemModelModel = self.data.root
        
        logger.debug("Building data %s", f"{namespace}:reef/{path}")
        
        log_prefix = ["", {"text": "[", "color": "#6e3787"}, {"text": "reef", "color": "#ed2de3"}, {"text": "] ", "color": "#6e3787"}]
        register_main = pack[namespace].functions.setdefault("reef/register_namespace", Function([
            f"tellraw @a[tag=reef.permissions.see_debug] {json.dumps([*log_prefix, {"text": f"Registering data for namespace '{namespace}'", "color": "#77d6ff"}])}",
        ]))
        
        mini_definition = {
            "page_count": json_info.page_count,
            **({"transition": json_info.transition} if json_info.transition is not None else {})
        }
        
        match(json_info.type):
            case "reef:pdf":
                pdf_namespace, _, pdf_path = json_info.pdf.partition(":")
                mini_definition["model"] = f"{pdf_namespace}:reef/mini/{pdf_path}"
            case "reef:item_model":
                mini_definition["model"] = json_info.item_model
        
        function_contents = Function([
            f'data modify storage {storage} {nbt_path} set value {json.dumps(mini_definition)}',
            f'function reef:api/register/mini {{identifier: "{identifier}", storage_path: \'{storage} {nbt_path}\'}}'
        ])
        
        if not state.opts.compress_functions:
            pack[namespace].functions[f"reef/register/page/{path}"] = function_contents

            register_main.append([
                f"function {namespace}:reef/register/page/{path}"
            ])
        else:
            register_main.append(function_contents)

@configurable("reef", validator=ReefPluginOptions)
def special(ctx: Context, opts: ReefPluginOptions):
    """Adds support for Reef special JSON files."""

    ctx.data.extend_namespace.append(ReefSpecialData)