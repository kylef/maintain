# Maintain

A unified interface to maintaining projects of any language.

## Installation

### Easy Install

```
$ easy_install maintain
```

### PIP

```
$ pip install maintain
```

## Usage

### Release automation

Maintain offers a command to automate bumping version numbers and releasing your project.

```shell
$ maintain release 0.3.1
```

You can also configure Maintain to create a pull request and perform the release in two steps:

```shell
$ maintain release 0.3.1 --pull-request
```

Once the pull request is merged, you can perform the actual release:

```shell
$ maintain release 0.3.1 --no-bump
```

#### Supported Packages

- [CocoaPods](https://cocoapods.org)
- [NPM](https://www.npmjs.com)

