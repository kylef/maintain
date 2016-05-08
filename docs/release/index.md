# Release

Maintain offers a release command to automate bumping version numbers and
releasing your library.

For example, using the release command you can release a version `1.2.0` of
your library.

```shell
$ maintain release 1.2.0
```

Maintain allows you to specify `major`, `minor` or `patch` to
automatically bump the respective version number automatically:

```shell
$ maintain release minor
```

The release command will firstly determine the appropriate releasers for your
library.

This release command will figured out the type of package, whether it be a
Python package, Ruby Gem, NPM package etc and then perform the steps necessary
to release it. It will bump the version number, create a release commit, tag
the release and push it to the respective package manager.


You can also configure Maintain to create a pull request and perform the
release in two steps. This is useful if you use code-review for the release
process:

```shell
$ maintain release 0.3.1 --pull-request
```

Once the pull request is merged, you can perform the actual release:

```shell
$ maintain release 0.3.1 --no-bump
```

**NOTE:** *This step could be done during continuous integration.*

#### Supported Packages

- `VERSION` file
- Python
- [CocoaPods](https://cocoapods.org)
- [NPM](https://www.npmjs.com)
- [RubyGems](https://rubygems.org)

#### Custom Hooks

By creating a `.maintain.yml` file in the root of your repository, you can add
hooks to various stages of the release process.

```yaml
release:
  bump:
    pre:
    - echo 'version will be bumped'
    post:
    - echo 'version was bumped'
  release:
    pre:
    post:
```

You may also disable a releaser from bumping, for example, if your
configuration file reads the version from a `VERSION` file instead of having a
copy.

```yaml
release:
  bump:
    disable:
    - CocoaPods
```

Custom bumping files:

```yaml
release:
  bump:
    file:
    - filenmae.rb
      foo
```
