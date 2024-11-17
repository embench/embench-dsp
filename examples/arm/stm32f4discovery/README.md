
## Building the Arm support library

This only need to be done once. It is not ideal, but this library is always built in tree.

```sh
pushd examples/arm/stm32f4discovery
make
popd
```

## Building for speed

If you haven't already done it, build the Arm support library (see above)

Then you can build the benchmarks.  The compilation options here are those used for the baseline Embench 2.0 results.
```sh
cflags="-O2 -ffunction-sections -fdata-sections -mcpu=cortex-m4 \
  -mfloat-abi=hard -mthumb -mfpu=fpv4-sp-d16"
ldflags="-O2 -Wl,--gc-sections -mcpu=cortex-m4 -mfloat-abi=hard \
  -mthumb \
  -T\${CONFIG_DIR}/link.ld -L\${CONFIG_DIR} \
  -static -nostartfiles --specs=nosys.specs"
scons --config-dir=examples/arm/stm32f4discovery/ \
  --build-dir=bd-arm-gcc-14.0.1-speed \
  cc=arm-none-eabi-gcc cflags="${cflags}" \
  ldflags="${ldflags}" user_libs='m c startup' gsf=1
```

## Building for size

If you haven't already done it, build the Arm support library (see above)

Then you can build the benchmarks.  The compilation options here are those used for the baseline Embench 2.0 results.

```sh
cflags="-Os -ffunction-sections -fdata-sections -mcpu=cortex-m4 \
  -mfloat-abi=hard -mthumb -mfpu=fpv4-sp-d16"
ldflags="-Os -Wl,--gc-sections -mcpu=cortex-m4 -mfloat-abi=hard \
  -mthumb \
  -T\${CONFIG_DIR}/link.ld -L\${CONFIG_DIR} \
  -static -nostartfiles --specs=nosys.specs"
scons --config-dir=examples/arm/stm32f4discovery/ \
  --build-dir=bd-arm-gcc-14.0.1-size \
  cc=arm-none-eabi-gcc cflags="${cflags}" \
  ldflags="${ldflags}" user_libs='m c startup' gsf=1
```
Note that a global scale factor of 1 is always used for code size runs.

## Measuring speed

```sh
./benchmark_speed.py --builddir bd-arm-gcc-14.0.1-speed \
  --target-module=run_stm32f4-discovery \
  --gdb-command=gdb-multiarch --gsf=1 --cpu-mhz=16
```

## Measuring size

```sh
./benchmark_size.py --builddir bd-arm-gcc-14.0.1-size
```
