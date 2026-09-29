# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/2.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0-beta13]

## Added

- `dpi` field in `.pdf.mcmeta` files that override the DPI to render the PDF with. If not present, uses the `default_dpi` in plugin options.

## Changed

- `dpi` field in plugin options renamed to `default_dpi`

## [1.0.0-beta12]

## Changed

- The first index of the override sequence now appends its elements to the first index of the page sequence.
  * This means that override sequences can now use the first index to spawn elements or other stuff right when the screen switches pages.

## [1.0.0-beta11]

### Fixed

- odfdo missing in main dependencies.

## [1.0.0-beta10]

### Added

- MCMeta file for PDFs to override the size of the generated assets.
  * This won't change the resolution of the image. It only changes the scale of the image inside the world.
  * Currently a `.pdf.mcmeta` file containing a `size` field which accepts a tuple of two floats.

### Changed
- The `overrides` field is now available for both Reef special data types.

## [1.0.0-beta9] - 2026-08-03

### Fixed
- ACTUALLY fixed the fatal bug in PDF overrides generation for real this time.

### Removed
- Herobrine

## [1.0.0-beta8] - 2026-08-03

### Fixed
- Fatal bug in PDF overrides generation using `.append` instead of `.extend`.

## [1.0.0-beta7] - 2026-07-29

### Added
- Reef Special Data PDF type now accepts an `overrides` fields which lets you append normal Reef data into a PDF type.

## [1.0.0-beta6] - 2026-06-28

### Added
- Reef Element asset namespace (`assets/ns/reef/element`) that generates models and item model definitions to use in Reef slideshows.
  * `reef:graphic` Reef Element type.
  * `reef:animated_element` Reef Element type.

## [1.0.0-beta5] - 2026-06-27

## Changed
- README.md

## [1.0.0-beta4] - 2026-06-27

### Added
- Reef Slideshow namespace (`data/ns/reef/slideshow`) that generates registry functions.
- Reef Page namespace (`data/ns/reef/page`) that generates registry functions.
- Reef Transition namespace (`data/ns/reef/transition`) that generates registry functions.
- `compress_functions` plugin option to put all registry code for a namespace into one file.

### Changed
- Updated beet to 0.166.0

## [1.0.0-beta3] - 2026-06-07

### Added
- Reef Special namespace (`data/ns/reef/special`) that handles data pack code-gen.
    * `reef:pdf` reef special type.
    * `reef:item_model` reef special type.
    * Reef Special types can use `transition` to specify a transition to play for the entire slideshow.
- CHANGELOG.md

### Changed
- Reef PDF asset namespace no longer handles data pack code-gen. It now purely handles resource pack code-gen.
- In-game slideshow size now uses the PDF `Page size` data.
- Cache now invalidates when the Reef plugin options changes.

## [1.0.0-beta2] - 2026-06-06

### Changed
- README.md

## [1.0.0-beta1] - 2026-06-06

### Added
- PDF data and asset generation support.
- PDF namespace.
