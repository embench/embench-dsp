# Configuration

## Building Speed

```sh
scons --config-dir=examples/native/ cflags="-O2 -fdata-sections -ffunction-sections" ldflags="-O2 -Wl,-gc-sections" user_libs=-lm
```

## Building Size

```sh
scons --config-dir=examples/native/ cflags="-Os -fdata-sections -ffunction-sections" ldflags="-Os -rdynamic -Wl,-gc-sections" user_libs=-lm
```

## Measuring speed

```sh
./benchmark_speed.py --target-module=run_stm32f4-discovery --gsf=1 --cpu-mhz=16
```

## Measuring size

```sh
./benchmark_size.py
```
