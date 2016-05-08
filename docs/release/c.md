# C/C++ Releaser

## Detect

Detects a header file named `version.h` in either `include/<library>/`
or `src/`.

## Bump

The releaser will update the values of the following `#define`s.

- `VERSION_MAJOR`
- `VERSION_MINOR`
- `VERSION_PATCH`

For example:

```c
#define VERSION_MAJOR 1
#define VERSION_MINOR 0
#define VERSION_PATCH 0
```

## Release

There is no release steps for this releaser.
