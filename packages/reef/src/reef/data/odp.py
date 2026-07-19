import json
import logging
import math
from pathlib import Path
from typing import Any, ClassVar

from beet import (
    Context,
    configurable,
    DataPack,
    Drop,
    Function,
    File,
    NamespaceFileScope,
)

from odfdo import Document, DrawPage, AnimPar, Element, Frame

from .. import state
from ..models import ResourceLocation
from ..options import ReefPluginOptions
from .page import ReefPageData
from .slideshow import ReefSlideshowData

__all__ = ["odp", "ReefSpecialOdpData"]

ODP_NAMESPACE = "reef/data/odp"
logger = logging.getLogger(ODP_NAMESPACE)

class ReefSpecialOdpData(File):
    """Class representing Google Slides OpenDocument Presentation files inside data/ns/reef/special"""
    
    scope: ClassVar[NamespaceFileScope] = ("reef", "special")
    extension: ClassVar[str] = ".odp"
    PT_TO_CM = 0.03528
    PT_TO_BLOCKS: float
    
    def bind(self, pack: DataPack, path: str):
        super().bind(pack, path)
        
        # magic number = scale 1 text display height
        self.PT_TO_BLOCKS = self.PT_TO_CM * (state.opts.odp.cm_per_block * 3.5)
        
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
        
        source_path = Path(self.ensure_source_path())
        doc = Document(source_path)

        pages: list[DrawPage] = doc.content.get_elements("//office:presentation/draw:page") # type: ignore
        page_ids: list[str] = []
        
        for i in range(0, len(pages)):
            current_page = pages[i]    
            page_ids.append(self.generate_page(pack, namespace, path, doc, current_page, i))
            
        pack[ReefSlideshowData][identifier] = ReefSlideshowData(json.dumps(page_ids))
        
            
        logger.debug("------------------------------------------------------")
        
    def generate_page(
        self, 
        pack: DataPack, 
        namespace: str, 
        path: str,
        doc: Document, 
        page: DrawPage, 
        index: int
    ) -> str:
        # TODO: rewrite this whole thing to support all kinds of text boxes 😭
        # TODO: probably just get every span and find their parent or smth
        # TODO: gawd this is so complicated
        # TODO: then uh, somehow make this page independent
        identifier = f"{namespace}:{path}/page_{index}"
        
        # First index is always elements that show up immediately
        page_sequence = [[]]
        
        # Filter the anim pars to only get stuff that use the appear animation
        valid_anim_pars: list[AnimPar] = [element for element in doc.content.get_elements("//anim:set/..") if element.get_attribute("presentation:preset-id") == "ooo-entrance-appear"] # type: ignore
        anim_par_target_element_ids = []
        
        # build them and group them accordingly
        for anim_par in valid_anim_pars:
            # TODO: modify this to accept text and graphics
            target_element_id = anim_par.children[0].get_attribute("smil:targetElement")
            node_type = anim_par.get_attribute("presentation:node-type")
            text_box = doc.content.get_element(f"//draw:custom-shape[@xml:id='{target_element_id}']")
            
            if text_box is None:
                raise AttributeError(f"Text box {target_element_id} does not exist")
            
            if node_type == "on-click": page_sequence.append([])
            page_sequence[-1].append(self.generate_text_element(doc, text_box))
            anim_par_target_element_ids.append(target_element_id)
        
        # Now build the elements that'll show up first
        # TODO: modify this to accept text and graphics
        valid_initial_elements: list[Element | Frame] = [element for element in doc.content.get_elements(f"//draw:page[position()={index}]/draw:custom-shape | //draw:page[position()={index}]/draw:frame[draw:text-box]") if element.get_attribute("xml:id") not in anim_par_target_element_ids]
        #logger.debug(valid_initial_elements)
        
        for text_box in valid_initial_elements:
            if isinstance(text_box, Frame):
                page_sequence[0].append(self.generate_text_element(doc, text_box))
            else:
                page_sequence[0].append(self.generate_text_element(doc, text_box))
            
        logger.debug(json.dumps(page_sequence, indent=2))
        pack[ReefPageData][identifier] = ReefPageData(json.dumps({
            "sequence": page_sequence
        }))
        
        # texts = [element["text"] for element in page_sequence[0]]
        # logger.debug("%s | %s", identifier, texts)
        
        return identifier
    
    def generate_text_element(
        self,
        doc: Document,
        text_box: Element
    ) -> dict:
        try:
            generated = self._generate_text_element(doc, text_box)
        except AttributeError:
            logger.warning("!! TEXT BOX ERRORED !!")
            logger.debug(text_box.get_attribute("draw:text-style-name"))
            
            generated = {}
            
        return generated
            
    
    def _generate_text_element(
        self,
        doc: Document,
        text_box: Element
    ) -> dict:
        text_content = text_box.text_content
        text_position = (
            self._get_number_from_attribute(text_box.get_attribute("svg:x")), # type: ignore
            self._get_number_from_attribute(text_box.get_attribute("svg:y")) # type: ignore
        )
        
        # WARN: this is just a temporary fix to skip shape elements
        text_span = text_box.get_span()
        if text_span is None:
            return {
            "type": "text",
            "text": "!! VECTOR SHAPE ELEMENT !!",
            "pos": [text_position[0] * state.opts.odp.cm_per_block, -text_position[1] * state.opts.odp.cm_per_block, 0],
        }
            
        text_style_name = text_span.style        
        text_properties = doc.get_style("text", name_or_element=text_style_name).get_text_properties() # type: ignore
        
        font_size_in_blocks = self._get_number_from_attribute(text_properties["fo:font-size"]) * self.PT_TO_BLOCKS # type: ignore
        
        # TODO: actually calculate the offsets like frfr
        # estimated_text_width = 7 * self._get_number_from_attribute(text_box.get_attribute("svg:width")) * state.opts.odp.cm_per_block # type: ignore
        # x_offset = 0.5 - estimated_text_width / 7
        
        return {
            "type": "text",
            "text": text_content,
            # "line_width": math.floor(estimated_text_width),
            "pos": [text_position[0] * state.opts.odp.cm_per_block, -text_position[1] * state.opts.odp.cm_per_block, 0],
            "scale": [font_size_in_blocks, font_size_in_blocks, 1],
            # "translation": [-x_offset, 0, 0]
        }
    
    def _get_number_from_attribute(self, attribute: str) -> float:
        return float(attribute[:-2])

@configurable("reef", validator=ReefPluginOptions)
def odp(ctx: Context, opts: ReefPluginOptions):
    """Adds support for Reef Google Slides ODP files."""

    ctx.data.extend_namespace.append(ReefSpecialOdpData)
    
# AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA