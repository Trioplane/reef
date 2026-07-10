import json
import logging
from pathlib import Path
from typing import ClassVar

from beet import (
    Context,
    configurable,
    DataPack,
    Drop,
    Function,
    File,
    NamespaceFileScope,
)

from odfdo import Document, DrawPage

from .. import state
from ..models import ResourceLocation
from ..options import ReefPluginOptions

__all__ = ["odp", "ReefSpecialOdpData"]

ODP_NAMESPACE = "reef/data/odp"
logger = logging.getLogger(ODP_NAMESPACE)

# Conversion Units
PT_TO_CM = 0.03528

class ReefSpecialOdpData(File):
    """Class representing OpenDocument files inside data/ns/reef/special"""
    
    scope: ClassVar[NamespaceFileScope] = ("reef", "special")
    extension: ClassVar[str] = ".odp"
    
    def bind(self, pack: DataPack, path: str):
        super().bind(pack, path)
        
        namespace, _, path = path.partition(":")
        
        self.generate_odp_resources(pack, namespace, path)
            
        raise Drop()
         
    def generate_odp_resources(
        self, 
        pack: DataPack,
        namespace: str, 
        path: str
    ):
        """Generates the resources to make a Reef presentation from an ODP file."""
        
        identifier = f"{namespace}:{path}"
        storage = f"{namespace}:reef"
        nbt_path = f'register.mini."{identifier}"'
        
        source_path = Path(self.ensure_source_path())
        
        logger.debug(source_path)
        
        doc = Document(source_path)
        content = doc.content
        
        page: DrawPage = content.get_element("//office:presentation/draw:page") # type: ignore
        text_boxes = page.get_elements("//draw:custom-shape")
        text_contents = [box.text_content for box in text_boxes]
        text_positions = [(box.get_attribute("svg:x"), box.get_attribute("svg:y")) for box in text_boxes]
        text_box_dimensions = [(box.get_attribute("svg:width"), box.get_attribute("svg:height")) for box in text_boxes]
        text_style_names = [box.get_span().style for box in text_boxes] # type: ignore
        text_styles = [doc.get_style("text", name_or_element=style_name) for style_name in text_style_names]
        text_properties = [style.get_text_properties() for style in text_styles] # type: ignore
        
        logger.debug("---------------------ODP TESTING----------------------")
        logger.debug(identifier)
        logger.debug("TEXT CONTENTS: %s", text_contents)
        logger.debug("TEXT POSITIONS: %s", text_positions)
        logger.debug("TEXT BOX DIMENSIONS: %s", text_box_dimensions)
        logger.debug("TEXT STYLE NAMES: %s", text_style_names)
        logger.debug("TEXT STYLES: %s", text_styles)
        #logger.debug("TEXT PROPERTIES: %s", text_properties)
        logger.debug("----")
        for box in text_boxes:
            text_position = (box.get_attribute("svg:x"), box.get_attribute("svg:y"))
            text_style_name = box.get_span().style # type: ignore
            text_properties = doc.get_style("text", name_or_element=text_style_name).get_text_properties() # type: ignore
            
            font_size_in_cm = int(text_properties["fo:font-size"][:-2]) * PT_TO_CM # type: ignore
            
            logger.debug("Text '%s' positioned %s with font size of %s or %s", box.text_content, text_position, text_properties["fo:font-size"], font_size_in_cm)
            
        logger.debug("------------------------------------------------------")

@configurable("reef", validator=ReefPluginOptions)
def odp(ctx: Context, opts: ReefPluginOptions):
    """Adds support for Reef odp JSON files."""

    ctx.data.extend_namespace.append(ReefSpecialOdpData)