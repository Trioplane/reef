# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/2.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0-beta6] - 2026-06-28

## Added
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
