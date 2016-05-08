# CocoaPods Releaser

## Detect

The CocoaPods releaser is enabled when any files which have the extension
`.podspec` or `.podspec.json` are found in the root of the library.

## Bump

Bumping is supported for both Ruby podspecs and JSON podspecs. For Ruby
podspecs, the version of the specification is bumped directly.

For JSON podspecs, both the version and the git source `tag` of the
repository is updated.

## Release

The release stage of the CocoaPods releaser depends on the `cocoapods` gem,
which can be installed via RubyGems:

```shell
$ gem install cocoapods
```

You will also need to login to trunk before releasing:

```shell
$ pod trunk register
```
