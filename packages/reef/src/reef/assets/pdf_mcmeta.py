import logging
from typing import ClassVar

from beet import (
    Context,
    JsonFileBase,
    NamespaceFileScope,
    configurable,
)
from pydantic import BaseModel

from ..options import ReefPluginOptions

__all__ = ["ReefPdfMcmeta", "ReefPdfMcmetaModel", "pdf_mcmeta"]

PDF_NAMESPACE = "reef/assets/pdf.mcmeta"
logger = logging.getLogger(PDF_NAMESPACE)

class ReefPdfMcmetaModel(BaseModel):
    size: tuple[float, float] | None = None
    dpi: int | None = None 

class ReefPdfMcmeta(JsonFileBase):

    model = ReefPdfMcmetaModel
    scope: ClassVar[NamespaceFileScope] = ("reef", "pdf")
    extension: ClassVar[str] = ".pdf.mcmeta"

@configurable("reef", validator=ReefPluginOptions)
def pdf_mcmeta(ctx: Context, opts: ReefPluginOptions):
    """Adds support for Reef PDF files to generate Reef Mini compatible files."""

    ctx.assets.extend_namespace.append(ReefPdfMcmeta)
