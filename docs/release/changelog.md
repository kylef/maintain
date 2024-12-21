# Changelog Releaser

Changelog releaser allows you to update a
[semantic changelog](http://github.com/kylef/changelog).

## Configuration

Changelog Releaser allows you to specify the types of changelog sections and
their underlying semantic meaning.

```yaml
release:
  changelog:
    sections:
      'Breaking': major
      'Enhancements': minor
      'Bug Fixes': patch
```

## Detect

Detects a `CHANGELOG.md` file in the root of your library.

## Bump

Finds a "TBD" release in your CHANGELOG and changes it to the current
version with the current date.

```markdown
## TBD

### Bug Fixes

- Adds support for building Swift 2.2.1 from source, and installing 2.2.1
  development snapshots.
- `swiftenv uninstall` will now uninstall Swift toolchains on OS X.
```

## Release

There is no release steps for the changelog releaser.
