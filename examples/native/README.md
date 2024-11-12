# Configuration

## Building Speed

```sh
scons --config-dir=examples/native/ cflags="-O2 -fdata-sections -ffunction-sections" ldflags="-O2 -Wl,-gc-sections" user_libs=-lm
```

## Building Size

```sh
scons --config-dir=examples/native/ cflags="-Os -fdata-sections -ffunction-sections" ldflags="-Os -rdynamic -Wl,-gc-sections" user_libs=-lm
```