import logging
import json
import shutil
from pathlib import Path
import re
from tempfile import TemporaryDirectory
from typing import Any, ClassVar

import pdf2image
from beet import (
    Context,
    DataPack,
    Drop,
    File,
    Function,
    ItemModel,
    Model,
    NamespaceFileScope,
    ResourcePack,
    Texture,
    configurable,
)
from PIL import Image

from .. import state
from ..options import ReefPluginOptions

__all__ = ["pdf"]

PDF_NAMESPACE = "reef/assets/pdf"
logger = logging.getLogger(PDF_NAMESPACE)

class ReefPdfAsset(File):
    """Class representing a Reef PDF file in assets/ns/reef/pdf"""

    scope: ClassVar[NamespaceFileScope] = ("reef", "pdf")
    extension: ClassVar[str] = ".pdf"

    def bind(self, pack: ResourcePack, path: str):
        super().bind(pack, path)
        poppler_path: dict[str, Any] = {"poppler_path": state.opts.pdf.poppler_path} if state.opts.pdf.poppler_path is not None else {}

        # Variables -----------

        namespace, _, path = path.partition(":")
        pdf_path = Path(self.ensure_source_path())

        # ---------------------

        # Start to build the file
        logger.debug(f"Building: {pdf_path}")

        # Cache the original PDF
        state.ctx.cache[PDF_NAMESPACE].download(pdf_path.as_uri())
        logger.debug("Cached pdf %s (%s)", f"{namespace}:{path}", pdf_path)
        
        # Cache the plugin options
        opts_dict = state.opts.model_dump()
        with state.ctx.cache[PDF_NAMESPACE] as cache:
            if cache.json.get("options") != opts_dict:
                logger.debug("Invalidating cache due to plugin options change")
                cache.clear()
                logger.debug("Cached plugin options")
                cache.json["options"] = opts_dict

        # Cache the images if we didn't hit the cache
        if state.ctx.cache[PDF_NAMESPACE].has_changed(pdf_path):
            logger.debug("Recaching image files...")
            with TemporaryDirectory() as temp_dir:
                # Convert the PDF to a list of Images

                uncached_images: list[str] = pdf2image.convert_from_path(
                    pdf_path=pdf_path,
                    fmt="png",
                    output_folder=temp_dir,
                    dpi=state.opts.pdf.dpi,
                    thread_count=4,
                    paths_only=True,
                    **poppler_path
                ) # type: ignore

                # Cache the images
                with state.ctx.cache[PDF_NAMESPACE] as cache:
                    cache.timeout(hours=state.opts.cache_timeout_hours)
                    
                    for i in range(0, len(uncached_images)):
                        image_path = uncached_images[i]

                        cache_path = cache.get_path(f"{namespace}:{path}/{i}.png")
                        
                        shutil.copyfile(image_path, cache_path)

                        logger.debug("Cached %s (%s)", f"{namespace}:{path}/{i}.png", cache_path)

            logger.debug("Done caching!")
        
        # Get PDF debug
        # NOTE: oh my god why is pdf2image typed so horribly
        pdf_info = pdf2image.pdfinfo_from_path(
            pdf_path=str(pdf_path),
            **poppler_path
        )

        # Put the cached images into a list
        images: list[Image.Image] = []

        with state.ctx.cache[PDF_NAMESPACE] as cache:
            logger.debug("Loading images from cache...")
            for i in range(0, pdf_info["Pages"]):
                cache_path = cache.get_path(f"{namespace}:{path}/{i}.png")
                
                with Image.open(cache_path) as img:
                    images.append(img.copy())
                    logger.debug("Copied %s (%s)", f"{namespace}:{path}/{i}.png", cache_path)

        # Generate the resource pack assets
        match = re.match(r"([\d.]+) x ([\d.]+) pts", pdf_info["Page size"])
        
        if not match:
            raise ValueError(f'Could not parse page size from: "{pdf_info['Page size']}" ({namespace}:{path})')
        
        page_size = (float(match.group(1)), float(match.group(2)))
        self.generate_assets(pack, namespace, path, images, page_size)
        
        # Prevent the PDF itself from getting put into the resource pack
        raise Drop()

    def generate_assets(
        self, 
        pack: ResourcePack, 
        namespace: str, 
        path: str, 
        images: list[Image.Image],
        page_size: tuple[float, float]
    ) -> None:
        resource_location_path = f"reef/mini/{path}"

        # Calculate the transformation matrix
        offset = (
            0.5 - page_size[0] / 16,
            0.5 - page_size[1] / 16
        )
        transformation_matrix = [
            page_size[0], 0,            0, offset[0], 
            0,            page_size[1], 0, offset[1], 
            0,            0,            1,       0.5, 
            0,            0,            0,       1
        ]

        # File generation
        logger.debug("Building resource pack files...")

        item_model_entries = []

        for i in range(0, len(images)):
            logger.debug("Bulding asset %s", f"{namespace}:{resource_location_path}/{i}")
            image = images[i]
            
            # Texture at `assets/<ns>/textures/item/reef/mini/<pdf_name>/<page>`
            pack[namespace].textures[f"item/{resource_location_path}/{i}"] = Texture(image)

            # Model at `assets/<ns>/models/item/reef/mini/<pdf_name>/<page>`
            pack[namespace].models[f"item/{resource_location_path}/{i}"] = Model({
                "credit": "Generated with Reef",
                "parent": "reef:item/element_base",
                "textures": {
                    "image": f"{namespace}:item/{resource_location_path}/{i}",
                }
            })

            # Build the item model entries
            tints_field = {
                "tints": [{
                    "type": "minecraft:constant",
                    "value": state.opts.tint
                }]
            } if state.opts.tint is not None else {}
            item_model_entries.append({
                "threshold": i,
                "model": {
                    "type": "minecraft:model",
                    "model": f"{namespace}:item/{resource_location_path}/{i}",
                    **tints_field
                }
            })

        # Item Model at `assets/<ns>/items/reef/mini/<pdf_name>`
        pack[namespace].item_models[f"{resource_location_path}"] = ItemModel({
            "model": {
                "type": "minecraft:range_dispatch",
                "property": "minecraft:custom_model_data",
                "index": 0,
                "entries": item_model_entries,
                "transformation": transformation_matrix
            }
        })

        logger.debug("Done building resource pack files!")

@configurable("reef", validator=ReefPluginOptions)
def pdf(ctx: Context, opts: ReefPluginOptions):
    """Adds support for Reef PDF files to generate Reef Mini compatible files."""

    ctx.assets.extend_namespace.append(ReefPdfAsset)