# Maintain Changelog

## TBD

### Enhancements

- GitHub release will now replace environment variables such as `$VERSION` into
  artefact file names.

## 0.4.0 (2024-12-21)

### Breaking

- Drop support for Python < 3.7.

- Changelog releaser now uses the unreleased name "TBD" instead of "Master".
  `CHANGELOG.md` files must use "TBD" as the upcoming release name going
  forward.

### Enhancements

- Support using branches named `main` as a default branch (previously default
  branches had to be named `master`).

- Repo commands now sort the list of repositories to provide a consistent
  experience across macOS and Linux platforms.

## 0.3.0 (2018-09-11)

### Breaking

- Drop support for Python 3.3.

### Enhancements

- Releasing no longer requires a git remote. Release can be used for local
  repositories.
- Release now offers a `--verbose` flag to log what is happening during
  release.
- GitHub releaser now allows you to upload artefacts to the GitHub release.
- GitHub releaser will now upload changelog release from `CHANGELOG.md` files.
- Hooks are now passed the VERSION as an environment variable.
- Hooks can now be placed in files inside `.maintain/hooks` such as
  `.maintain/hooks/pre_release`.
- Changelog releaser allows you to specify custom sections.

    ```yaml
    release:
      changelog:
        sections:
          'Breaking': major
          'Enhancements': minor
          'Bug Fixes': patch
    ```
- Configuration file can now be passed via the `--config` option.


## 0.2.0 (2016-05-10)

Initial release.
