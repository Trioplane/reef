import logging
from pydantic import BaseModel, Field, RootModel
from typing import ClassVar, Literal, Annotated, Union

from beet import (
    Context,
    configurable,
    ResourcePack,
    Drop,
    ItemModel,
    JsonFileBase,
    Model,
    NamespaceFileScope,
)

from .. import state
from .. import models
from ..options import ReefPluginOptions

__all__ = ["element"]

ELEMENT_NAMESPACE = "reef/assets/element"
logger = logging.getLogger(ELEMENT_NAMESPACE)

class GraphicAssetModel(BaseModel):
    type: Literal["reef:graphic"]
    texture: models.ResourceLocation
    size: tuple[int, int]

class AnimatedElementAssetModel(BaseModel):
    type: Literal["reef:animated_element"]
    texture: models.ResourceLocation
    size: tuple[int, int]
    frames: int

class ElementAssetModel(RootModel[Annotated[
    Union[
        GraphicAssetModel,
        AnimatedElementAssetModel
    ],
    Field(discriminator="type")
]]):
    pass

class ReefElementAsset(JsonFileBase):
    """Class representing a Reef Element file in assets/ns/reef/element"""
    
    model = ElementAssetModel
    scope: ClassVar[NamespaceFileScope] = ("reef", "element")
    extension: ClassVar[str] = ".json"
    
    def bind(self, pack: ResourcePack, path: str):
        super().bind(pack, path)
        
        namespace, _, path = path.partition(":")
        
        data: ElementAssetModel = self.data
        
        match data.root.type:
            case "reef:graphic":
                self.generate_graphic_element(pack, namespace, path)
                
            case "reef:animated_element":
                self.generate_animated_element(pack, namespace, path)
            
        raise Drop()
    
    def generate_graphic_element(
        self,
        pack: ResourcePack,
        namespace: str,
        path: str
    ):
        json_data: GraphicAssetModel = self.data.root
        
        pack[namespace].models[f"item/reef/{path}"] = Model({
            "credit": "Generated with Reef",
            "parent": "reef:item/element_base",
            "textures": {
                "image": json_data.texture,
            }
        })
        logger.debug("Generated model for graphic asset")
        
        translation_offset = (
            0.5 - json_data.size[0] / 16,
            0.5 - json_data.size[1] / 16
        )
        
        pack[namespace].item_models[path] = ItemModel({
            "type": "minecraft:model",
            "model": f"{namespace}:item/reef/{path}",
            "transformation": [
                json_data.size[0],  0,                 0,       translation_offset[0], 
                0,                  json_data.size[1], 0,       translation_offset[1], 
                0,                  0,                 1,                         0.5, 
                0,                  0,                 0,                           1
            ],
            **({"tints": [{ "type": "minecraft:constant", "value": state.opts.tint }]} if state.opts.tint is not None else {})
        })
        logger.debug("Generated item model definition for graphic asset")
    
    def generate_animated_element(
        self,
        pack: ResourcePack,
        namespace: str,
        path: str
    ):
        json_data: AnimatedElementAssetModel = self.data.root
        
        translation_offset = (
            0.5 - json_data.size[0] / 16,
            0.5 - json_data.size[1] / 16
        )
        
        entries = [{
            "threshold": 0,
            "model": {
                "type": "minecraft:model",
                "model": "minecraft:air"
            }
        }]
        
        for i in range(1, json_data.frames + 1):
            pack[namespace].models[f"item/reef/{path}/{i}"] = Model({
                "credit": "Generated with Reef",
                "parent": "reef:item/element_base",
                "textures": {
                    "image": f"json_data.texture/{i}",
                }
            })
            
            entries.append({
                "threshold": i,
                "model": {
                    "type": "minecraft:model",
                    "model": f"{namespace}:item/reef/{path}/{i}",
                    **({"tints": [{ "type": "minecraft:constant", "value": state.opts.tint }]} if state.opts.tint is not None else {})
                }
            })
        logger.debug("Generated models for animated element asset")
            
        pack[namespace].item_models[path] = ItemModel({
            "type": "minecraft:range_dispatch",
            "model": f"{namespace}:item/reef/{path}",
            "property": "minecraft:custom_model_data",
            "index": 0,
            "entries": entries,
            "transformation": [
                json_data.size[0],  0,                 0,       translation_offset[0], 
                0,                  json_data.size[1], 0,       translation_offset[1], 
                0,                  0,                 1,                         0.5, 
                0,                  0,                 0,                           1
            ]
        })
        logger.debug("Generated item model definition for animated element asset")

@configurable("reef", validator=ReefPluginOptions)
def element(ctx: Context, opts: ReefPluginOptions):
    """Adds support for Reef page JSON files."""

    ctx.assets.extend_namespace.append(ReefElementAsset)