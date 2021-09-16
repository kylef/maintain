# Maintain

A unified interface to maintaining projects of any language.

## Installation

### PIP

```
$ pip install maintain
```

## Usage

### Release automation

Maintain offers a command to automate bumping version numbers and releasing your project.

```shell
$ maintain release patch
```

This release command will figured out the type of package, whether it be a
Python package, Ruby Gem, NPM package etc and then perform the steps necessary
to release it. It will bump the version number, create a release commit, tag
the release and push it to the respective package manager.

Maintain allows you to specify the `major`, `minor` or `patch` to
automatically bump the respective version number, or you can explicitly
specify a version.

#### Pull-request

You can configure Maintain to create a pull request and perform the
release in two steps. This is useful if you use code-review for the release
process:

```shell
$ maintain release 1.2.0-beta.1 --pull-request
```

Once the pull request is merged, you can perform the actual release:

```shell
$ maintain release --no-bump
```

**NOTE:** *This step could be done during continuous integration.*

#### Custom Hooks

By creating a `.maintain.yml` file in the root of your repository, you can add
hooks to various stages of the release process.
