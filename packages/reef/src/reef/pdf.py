import logging
import json
import shutil
from pathlib import Path
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

from .options import ReefPluginOptions

__all__ = ["pdf"]

PDF_NAMESPACE = "reef/pdf"
logger = logging.getLogger(PDF_NAMESPACE)

def create_reef_pdf_asset_namespace(ctx: Context, opts: ReefPluginOptions):
    class ReefPdf(File):
        """Class representing a Reef PDF file."""

        scope: ClassVar[NamespaceFileScope] = ("reef",)
        extension: ClassVar[str] = ".pdf"
        poppler_path: dict[str, Any] = {"poppler_path": opts.pdf.poppler_path} if opts.pdf.poppler_path is not None else {}

        def bind(self, pack: ResourcePack, path: str):
            super().bind(pack, path)

            # Variables -----------

            namespace, _, path = path.partition(":")
            pdf_path = Path(self.ensure_source_path())

            # ---------------------

            # Start to build the file
            logger.debug(f"Building: {pdf_path}")

            # Cache the original PDF
            ctx.cache[PDF_NAMESPACE].download(pdf_path.as_uri())
            logger.debug("Cached pdf %s (%s)", f"{namespace}:{path}", pdf_path)

            # Cache the images if we didn't hit the cache
            if ctx.cache[PDF_NAMESPACE].has_changed(pdf_path):
                logger.debug("Recaching image files...")
                with TemporaryDirectory() as temp_dir:
                    # Convert the PDF to a list of Images

                    uncached_images: list[str] = pdf2image.convert_from_path(
                        pdf_path=pdf_path,
                        fmt="png",
                        output_folder=temp_dir,
                        dpi=opts.pdf.dpi,
                        thread_count=4,
                        paths_only=True,
                        **self.poppler_path
                    ) # type: ignore

                    # Cache the images
                    with ctx.cache[PDF_NAMESPACE] as cache:
                        cache.timeout(hours=opts.cache_timeout_hours)
                        
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
                **self.poppler_path
            )

            # Put the cached images into a list
            images: list[Image.Image] = []

            with ctx.cache[PDF_NAMESPACE] as cache:
                logger.debug("Loading images from cache...")
                for i in range(0, pdf_info["Pages"]):
                    cache_path = cache.get_path(f"{namespace}:{path}/{i}.png")
                    
                    with Image.open(cache_path) as img:
                        images.append(img.copy())
                        logger.debug("Copied %s (%s)", f"{namespace}:{path}/{i}.png", cache_path)

            # Generate the resource pack assets
            self.generate_assets(pack, namespace, path, images)
            self.generate_data(ctx.data, namespace, path, pdf_info)

            # Prevent the PDF itself from getting put into the resource pack
            raise Drop()

        def generate_assets(
            self, 
            pack: ResourcePack, 
            namespace: str, 
            path: str, 
            images: list[Image.Image]
        ) -> None:
            resource_location_path = f"reef/mini/{path}"

            # Calculate the transformation matrix
            image_size = images[0].size
            offset = (
                0.5 - image_size[0] / 16,
                0.5 - image_size[1] / 16
            )
            transformation_matrix = [
                image_size[0], 0,            0, offset[0], 
                0,            image_size[1], 0, offset[1], 
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
                        "value": opts.tint
                    }]
                } if opts.tint is not None else {}
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

        def generate_data(
            self, 
            pack: DataPack,
            namespace: str, 
            path: str, 
            pdf_info: dict[str, Any]
        ):
            identifier = f"{namespace}:{path}"
            storage = f"{namespace}:reef"
            nbt_path = f'register.mini."{identifier}"'
            
            logger.debug("Building data %s", f"{namespace}:reef/{path}")
            
            log_prefix = ["", {"text": "[", "color": "#6e3787"}, {"text": "reef", "color": "#ed2de3"}, {"text": "] ", "color": "#6e3787"}]
            register_main = pack[namespace].functions.setdefault("reef/register_namespace", Function([
                f"tellraw @a[tag=reef.permissions.see_debug] {json.dumps([*log_prefix, {"text": f"Registering data for namespace '{namespace}'", "color": "#77d6ff"}])}",
            ]))
            
            
            pack[namespace].functions[f"reef/{path}/register_mini"] = Function([
                f'data modify storage {storage} {nbt_path} set value {{model: "{namespace}:reef/mini/{path}", page_count: {pdf_info["Pages"]}}}',
                f'function reef:api/register/mini {{identifier: "{identifier}", storage_path: \'{storage} {nbt_path}\'}}'
            ])
            
            register_main.append([
                f"function {namespace}:reef/{path}/register_mini"
            ])

    return ReefPdf

# TODO: make ReefDataDefiniton(File)
"""
{
  "type": "pdf",
  "pdf": "ns:pdf_file", // points to assets/ns/reef/pdf/pdf_file
  "size": [100, 100], // [x, y] | optional | default = image size
  "transition": "ns:my_transition" // optional
}

{
  "type": "slideshow", "page", "transition", "mini", "pdf", "gslide"
}
"""


@configurable("reef", validator=ReefPluginOptions)
def pdf(ctx: Context, opts: ReefPluginOptions):
    """Adds support for Reef PDF files to generate Reef Mini compatible files."""

    ctx.assets.extend_namespace.append(create_reef_pdf_asset_namespace(ctx, opts))