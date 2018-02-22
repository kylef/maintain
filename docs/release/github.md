# GitHub Releaser

## Configuration

```yaml
release:
  github:
    artefacts:
      - main.js
      - main.min.js
```

## Detect

Detects Git repository with an origin of a GitHub repository.

## Bump

There is no bump steps for the GitHub releaser.

## Release

Creates a GitHub release. You can provide artefacts to be uploaded to the
release in the configuration.

GitHub Releaser will detect `CHANGELOG.md` files and pull out the changelog for
the current release to be uploaded to the release.
