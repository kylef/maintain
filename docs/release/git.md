# git Releaser

## Configuration

```yaml
release:
  git:
    commit_format: Release {version}
    tag_format: {version}
```

## Detect

Detects Git repositories.

## Bump

Commits all of the pending changes for the release.

## Release

Tags the commit and pushes the changes.
