# Embench&#x2122; DSP: Open Signal Processing Benchmarks for Embedded Platforms

## Stable benchmark versions

The following git tags may be used to select the version of the repository for
a stable release.

The following git tags may be used to select the version of the repository for a stable release.

- `embench-dsp-1.0`

## Using the benchmarks

The benchmarks can be used to yield a single consistent score for the
performance of a platform and its compiler tool chain.  The mechanism for this
is described in the [user manual](./doc/README.md).

## Structure of the repository

The top level directory contains Python scripts to build and execute the benchmarks. The following are the key top level directories.

- [`examples`](./examples): containing examples for Embench build configurations for different boards.

- [`doc`](./doc): The user manual for Embench-DSP.

- [`golden-ref`](./golden-ref): Scripts to generate the DSP test data (input, output, coefficients, etc.). Parameterized number of samples to support more than one benchmark in some cases.

- [`lib`](./lib): The library source of the DSP functions, modified from the CMSIS DSP Library.

- [`src`](./src): The top-level source for the benchmarks, one directory
  per benchmark.

- [`support`](./support): The generic wrapper code and helper functions for benchmarks.

- [`pylib`](./pylib): Support code for the python scripts.