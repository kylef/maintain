# Hooks Releaser

By creating a `.maintain.yml` file in the root of your repository, you can add
hooks to various stages of the release process.

```yaml
release:
  hooks:
    bump:
      pre:
        - echo 'version will be bumped'
      post:
        - echo 'version was bumped'
    release:
      pre:
        - echo 'version will be released'
      post:
        - echo 'version was released'
```
