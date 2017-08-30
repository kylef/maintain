# Hooks Releaser

By creating a `.maintain.yml` file in the root of your repository, you can add
hooks to various stages of the release process.

```yaml
release:
  hooks:
    bump:
      pre:
        - echo '$VERSION will be bumped'
      post:
        - echo '$VERSION was bumped'
    release:
      pre:
        - echo '$VERSION will be released'
      post:
        - echo '$VERSION was released'
```

## Environment Variables

### `VERSION`

VERSION environment variable includes the new version.
