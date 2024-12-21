# swiftenv Changelog

## TBD

### Bug Fixes

- `swiftenv uninstall` will now uninstall Swift toolchains on OS X.


## 1.0.0 (2015-12-12)

### Enhancements

- Supports installing final Swift releases such as `2.2`.

### Bug Fixes

- Swift toolchains 'latest' version is no longer shown in `swiftenv versions`
  on OS X.
- Fixes a problem where `swiftenv install` on Linux will incorrectly
  determine URL for the Swift binaries.
- Adds a `--verbose` mode to `swiftenv versions` to show where the version was
  installed.
