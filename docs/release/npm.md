# Node Package Manager Releaser

## Detect

The NPM releaser will detect a `package.json` file in the root of your library.

## Bump

Bumping simply updates the version inside the `package.json` file.

## Release

The release stage of the NPM releaser will `npm publish` your library, which
depends on NPM being installed.
