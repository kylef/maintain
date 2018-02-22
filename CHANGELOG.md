# Maintain Changelog

## Master

### Enhancements

- Releasing no longer requires a git remote. Release can be used for local
  repositories.
- Release now offers a `--verbose` flag to log what is happening during
  release.
- GitHub releaser now allows you to upload artefacts to the GitHub release.
- Hooks are now passed the VERSION as an environment variable.
- Hooks can now be placed in files inside `.maintain/hooks` such as
  `.maintain/hooks/pre_release`.
- Added a Conventional Commits releaser.


## 0.2.0 (2016-05-10)

Initial release.
