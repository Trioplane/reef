from beet import PluginOptions
from pydantic import Field

class PdfPluginOptions(PluginOptions):
    poppler_path: str | None = None
    dpi: int = 200
    
class ReefPluginOptions(PluginOptions):
    tint: int | None = None
    compress_functions: bool = False
    cache_timeout_hours: int = 24

    pdf: PdfPluginOptions = PdfPluginOptions()