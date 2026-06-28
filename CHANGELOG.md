# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/2.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- *nothing yet...* 

## [1.0.0-beta7] - 2026-06-28

### Fixed

- Environment changed back to production.

## [1.0.0-beta6] - 2026-06-27

### Added

- pack.png

### Changed

- Cleaned up debug messages
  * Most of them now run per player rather than broadcasting globally.
  * Most of them now has a hover text that will show extra info about the log replacing the long debug logs.
- Update to Minecraft 26.2

### Removed

- Demo and testing files for Smithed Summit. It has been moved to a separate data pack and resource pack.

## [1.0.0-beta5] - 2026-06-13

### Added

- Ability to trigger commands on pages on certain events.
    * `commands.on_load` - Triggers when the page data gets loaded. Elements hasn't been displayed on this step.
    * `commands.on_enter` - Triggers after elements display.
    * `commands.on_unload` - Triggers when the page unloads.
- Ability to trigger commands on elements on certain events.
    * `commands.on_enter` - Triggers when the element gets spawned.
    * `commands.on_exit` - Triggers when the element is about to be removed.
- Element entities now store their element data in their `data` NBT rather than being stored temporarily in a temporary internal storage.

### Changed

- All remote API functions now check if the player has the `reef.permissions.use_remote` permission.

## [1.0.0-beta4] - 2026-06-07

### Added

- `components` field on elements to add arbitrary data components to the display entities.
- Reef mini definition
- Reef mini register API (`reef:api/register/mini`)

## [1.0.0-beta3] - 2026-05-16

### Added
- Screens
- Slideshows
- Pages
- Transitions
- Remote item
- Permission system