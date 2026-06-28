from beet import Context, Model, configurable
import logging

from .options import ReefPluginOptions
from . import assets
from . import data

__all__ = [
	"reef",
	"beet_default"
]

logger = logging.getLogger("reef")

def beet_default(ctx: Context):
	ctx.require(reef)

@configurable(validator=ReefPluginOptions)
def reef(ctx: Context, opts: ReefPluginOptions):
	"""Initializes the Reef plugin system"""
	logger.debug("Creating base assets...")

	ctx.assets["reef"].models["item/element_base"] = Model({
		"credit": "Generated with Reef",
		"ambientocclusion": False,
		"elements": [
			{
				"from": [0, 0, 0],
				"to": [1, 1, 0],
				"shade": False,
				"light_emission": 15,
				"rotation": {"angle": 0, "axis": "y", "origin": [0, 0, 0]},
				"faces": {
					"north": {"uv": [0, 0, 16, 16], "texture": "#image", "tintindex": 0}
				}
			}
		]
	})

	logger.debug("Created reef:item/element_base")

	ctx.require(assets.element)
	ctx.require(assets.pdf)
	ctx.require(data.special)
	ctx.require(data.page)
	ctx.require(data.slideshow)
	ctx.require(data.transition)