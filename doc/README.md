# Embench&#x2122; DSP User Guide

<!--
Contributor Jeremy Bennett <jeremy.bennett@embecosm.com>
Contributor Roger Shepherd <roger.shepherd@rcjd.net>

SPDX-License-Identifier: GFDL-1.2

Document conventions:
- 80 character lines
- Wikipedia heading conventions (First word only capitalized, unless a proper
  noun)
- US spelling throughout.
- Run "make spell" before committing changes.
- Do not commit the PDF!
- The first line must not be the "comment" which inserts the ToC
-->

Authors: Embench&#x2122; Task Group
Issue:   1.0

## Table of Contents

<!-- ToC can be updated using 'make toc' in a Linux like systems -->
<!-- Insert ToC here -->

- [About Embench](#about-embench)
    - [The Bristol/Embecosm Embedded Benchmark Suite (BEEBS)](#the-bristolembecosm-embedded-benchmark-suite-beebs)
    - [Future work](#future-work)
    - [Feedback and how to contribute](#feedback-and-how-to-contribute)
    - [Contributors](#contributors)
    - [Document history](#document-history)
- [Building and running Embench](#building-and-running-embench)
    - [Prerequisites](#prerequisites)
    - [Preparation](#preparation)
    - [Configuring the benchmarks](#configuring-the-benchmarks)
    - [Building the benchmarks](#building-the-benchmarks)
    - [Running the benchmark of code size](#running-the-benchmark-of-code-size)
    - [Running the benchmark of code speed](#running-the-benchmark-of-code-speed)
- [Recording reliable results](#recording-reliable-results)
- [Statistics of computing benchmarks](#statistics-of-computing-benchmarks)
    - [Computing a benchmark value for speed](#computing-a-benchmark-value-for-speed)
    - [Computing a benchmark value for code size](#computing-a-benchmark-value-for-code-size)
- [Reference platform](#reference-platform)
- [Documentation](#documentation)
    - [Building the documentation](#building-the-documentation)
- [Adding a new board to Embench](#adding-a-new-board-to-embench)
    - [Creating a configuration for the new board](#creating-a-configuration-for-the-new-board)
    - [Configuration variables](#configuration-variables)
- [The GNU Free Documentation License version 1.2, November 2002](#the-gnu-free-documentation-license-version-1.2-november-2002)
    - [Preamble](#preamble)
    - [Applicability and definitions](#applicability-and-definitions)
    - [Verbatim copying](#verbatim-copying)
    - [Copying in quantity](#copying-in-quantity)
    - [Modifications](#modifications)
    - [Combining documents](#combining-documents)
    - [Collections of documents](#collections-of-documents)
    - [Aggregation with independent works](#aggregation-with-independent-works)
    - [Translation](#translation)
    - [Termination](#termination)
    - [Future revisions of this license](#future-revisions-of-this-license)
    - [Addendum: how to use this License for your documents](#addendum-how-to-use-this-license-for-your-documents)

<!-- End of ToC insertion -->

## Building and running Embench DSP

The benchmarks have to be first compiled, then they can then be measured on the target.

### Prerequisites

Embench expects the following version of tools. Update your system accordingly.

| _Components_ | _Version_    |
| -------------| -------------|
| python       | 3.6 or later |
| scons        | 4.5 or later |
| target-specific toolchain (e.g. debugger) | NA |

The following non-standard Python packages are needed.

|  _Package_  | _Comments_                      |
|-------------|---------------------------------|
| pyelftools  |                                 |
| numpy (optional)     | For data generation |
| matplotlib (optional) | - |
| scipy (optional)      | - |


### Preparation

clone this git repository:
```bash
git clone https://github.com/embench/embench-dsp.git
```

### Configuring the benchmarks

The benchmarks are configured using _scons_ in several ways:

- default values in the scons build script; and
- on the command line to the scons build script.

Command line variables take precedence over default values.

In addition, there must be board specific code in a directory specified with
the `--config-dir` option to _scons_.  It should contain the following files.

- a board specific header, `boardsupport.h`:
    - for example for the reference Arm platform
    [`examples/arm/stm32f4discovery/boardsupport.h`](../examples/arm/stm32f4discovery/boardsupport.h).
- board specific code in `boardsupport.c`.
    - for example for the reference Arm platform
    [`examples/arm/stm32f4discovery/boardsupport.c`](../examples/arm/stm32f4discovery/boardsupport.c).

The board specific files are used only to provide code essential to
the functionality. The board support header (`boardsupport.h`) is often
empty. It can be used to set some of the configuration variables, however the
preferred approach is to specify these on the _scons_ command line.

The board support code file (`boardsupport.c`) is used to define three
functions.

- `void initialise_board ()`: Called to set up the board;
- `void start_trigger ()`: Called when we start timing the benchmark, to start
any board specific timing mechanism.
- `void stop_trigger ()`: Called when we stop timing the benchmark, to stop
any board specific timing mechanism.

`scons --help` prints the available configuration variables.

The following variables are the most useful to be specified on the command line when building the benchmarks.

- `cc`: The C compiler to use. Default value `cc`.
- `ld`: The linker to use. Default value is the same as `cc`.
- `cflags`: A list of compiler flags, which are passed to `cc` for the
  compilation of object files. Default value `[]`.
- `ldflags`: A list of linker flags, which are passed to `ld`. Default value
  `[]`.
- `user_libs`: A list of libraries to be linked with all executables.  The
  libraries may be absolute file names or arguments to the linker.  In the
  latter case corresponding arguments in `ldflags` may be needed.  For example
  with GCC or Clang/LLVM if `-l` or `-l:` flags are used in `user_libs`, then
  `-L` flags may be needed in `ldflags`.  Default value is the empty list, `[]`.

Unknown variables are silently ignored.  There is no need to set an unused parameter, and any configuration file may be empty or missing if no flags need to be set.

### Building the benchmarks

Embench is built with _scons_ (see [scons.org](https://scons.org/).  The build script is [`sconstruct.py`](../sconstruct.py). 

See the README files in the [`examples`](../examples/) directory for typical scons invocations.  As well as the variables described above (section
([Configuring the benchmarks](#configuring-the-benchmarks)), _scons_ takes the following options.

- `--build-dir`: The programs are built out of tree, this specifies the
  directory in which to build.  It may be an absolute or relative directory
  name; if the latter, it will be relative to the top level directory of the
  repository. Default value `bd`.
- `--config-dir`: The directory which contains your `boardsupport.c`
  and `boardsupport.h`.  Must be specified.
- `-c`: Clean the build directory and delete all intermediaries and final
  files from any previous runs of the script. Remember to specify
  `--build-dir` if you are not using the default build directory.
- `--help`: Provide help on the arguments.

Within variables, `${CONFIG_DIR}` is substituted with the `--config_dir`
value, and `${BUILD_DIR}` with the value of `--build_dir`.

### Running the benchmark of code size

Benchmarking code size uses the [`benchmark_size.py`](../benchmark_size.py)
script, which takes the following arguments.

- `--builddir`: The programs are build out of tree, this specifies the
  directory in which the programs were built.  It may be an absolute or
  relative directory name; if the latter, it will be relative to the top level
  directory of the repository. Default value `bd`.
- `--logdir`: A log file is created with detailed information about the
  benchmark run. This specifies the directory in which to place the log file.
  It may be an absolute or relative directory name; if the latter, it will be
  relative to the top level directory of the repository. Default value `logs`.
- `--baselinedir <dir>`: Specifies the directory in which reference
  size data can be found. May be an absolute or relative directory
  name. If it is relative then it will be interpreted as relative to the
  top level directory of the repository. The default value is `baseline-data`,
  and size data will be sourced from `baseline-data/size.json`.
- `--relative` or `--absolute`: If `--relative` is specified, present
  benchmark results relative to the baseline architecture.  If `--absolute` is
  specified, present absolute benchmark results.  If neither is specified,
  present relative results, because this is the defined norm for Embench.
- `--metric`. A space separated list of section types to include when
  calculating the benchmark metric.  Permitted values ares `text`, `data`,
  `rodata`, `bss`.  Default value `text`.
- `--text-output`: Output the text in a plain text format. This is the
  default.
- `--json-output`: Output the results in json format, instead of the
  default plain text format.
- `--csv-output`: Output the results as a CSV file (suitable for use in
  spreadsheets).
- `--md-output`: Output the results as a table in MarkDown format.
- `--baseline-output`: Output results in a format suitable for use as
  baseline data instead of the default text format. This can be used
  instead of the reference data in `baseline-data/size.json`.  This
  automatically applies `--absolute`.
- `--dummy-benchmark`: The directory which contains an empty benchmark
  used for library and startup routine size adjustments of other benchmarks.
  **Note.** Primarily intended for use by developers.
- `--file-extension`: An optional extension appended to benchmark names when
  building file-system paths to benchmark binaries. For example, specifying
  `.exe` would change paths of the form `bd/src/benchmark/benchmark` to
  `bd/src/benchmark/benchmark.exe`. Might be required on non-Unix systems.
- `--help`: Provide help on the arguments.

Before calculating relative or absolute benchmark sizes, the size of
`dummy-benchmark` metrics is subtracted from each benchmark's size to account
for tool chain specific size overhead in supporting code.

The size of `text`, `data`, and `rodata` metrics are determined by the flags of
elf sections in each benchmark.

- `text`: allocated and executable.
- `data`: allocated and writable, optionally also executable.
- `rodata`: allocated.
- `bss`: all unallocated writable data.

The official Embench scores use just `text`, however it is also make sense to
use `text` + `data` + `rodata`, which is the size of an image in the ROM of an
embedded system (including the initializing values for the `data` sections).
Note that some linker scripts will allocate explicit sections for stack and/or
heap, and these will be included in `bss`.

### Running the benchmark of code speed

Benchmark code speed uses the [`benchmark_speed.py`](../benchmark_speed.py)
script, which takes the following general arguments.

- `--builddir`: The programs are build out of tree, this specifies the
  directory in which the programs were built.  It may be an absolute or
  relative directory name; if the latter, it will be relative to the top level
  directory of the repository. Default value `bd`.
- `--logdir`: A log file is created with detailed information about the
  build. This specifies the directory in which to place the log file.  It may
  be an absolute or relative directory name; if the latter, it will be
  relative to the top level directory of the repository. Default value `logs`.
- `--baselinedir <dir>`: Specifies the directory in which reference
  speed data can be found. May be an absolute or relative directory
  name. If it is relative then it will be interpreted as relative to the
  top level directory of the repository. The default value is `baseline-data`,
  and speed data will be sourced from `baseline-data/speed.json`.
- `--relative` or `--absolute`: If `--relative` is specified, present
  benchmark results relative to the baseline architecture.  If `--absolute` is
  specified, present absolute benchmark results.  If neither is specified,
  present relative results, because this is the defined norm for Embench.
- `--text-output`: Output the text in a plain text format. This is the
  default.
- `--json-output`: Output the results in json format, instead of the
  default plain text format.
- `--baseline-output`: Output results in a format suitable for use as
  baseline data instead of the default text format. This can be used
  instead of the reference data in `baseline-data/speed.json`.
- `--target-module <target module>`: This mandatory argument specifies a
  python module in the [`pylib`](../pylib) directory with definitions of
  routines to run the benchmark. Note that the argument specifies the name of
  module (e.g. [`run_stm32f4-discovery`](../pylib/run_stm32f4-discovery.py))
  not the name of the file that contains the module
  (e.g. [`run_stm32f4-discovery.py`](../pylib/run_stm32f4-discovery.py)).
- `--timeout`: The maximum time (in seconds) allowed for each benchmark program
  to run. Default value 30.
- `--file-extension`: An optional extension appended to benchmark names when
  building file-system paths to benchmark binaries. For example, specifying
  `.exe` would change paths of the form `bd/src/benchmark/benchmark` to
  `bd/src/benchmark/benchmark.exe`. Might be required on non-Unix systems.
- `--help`: Provide help on the arguments.
- `--gsf`: Provides the gsf used to build the benchmarks.
- `--cpu-mhz`: Provides the mhz the cpu runs at, to get a cpu-normalized result.

There is so much variation in how a benchmark can be run that the detailed implementation is left to a python module specified by `--target-module`. This module may define additional arguments. If this module has been specified when
`--help` has also been specified, help will be provided on the target module's
arguments.

## Recording reliable results

For each benchmark run, you must record:

- details of the platform used, including its clock speed;
- if the platform is simulated or real.  If simulated, an indication of accuracy must be stated (i.e., fully cycle accurate or cycle approximate);
- for a simulated platform, configuration options of the chip should be stated (e.g., branch predictor size, cache sizes, and so on);
- details of the chip on the platform, including its precise architecture variant;
- details of the compiler tool chain used, typically the version of each component and library, or for development tool chains the repository commit ID of each component;
- the compiler and linker flags used for the benchmarks, which should be the same for each benchmark program; and
- the version of Embench DSP used.

For clarification compiler flags, whose effect is to vary the choice and parameters of optimization passes on a per program (or per compilation unit or function) basis are permitted.  For example flags which use machine learning techniques to match source code styles with the a choice of optimization passes.

The philosophy of recorded data should be such that anyone else can take the same platform and tool chain and duplicate the results.

## Statistics of computing benchmarks

These computations are carried out by the benchmark scripts.

### Computing a benchmark value for speed

The benchmarks should be compiled with `cflags` and `ldflags` that optimize for speed, such as `-O2`.

Carry out the following steps.

- For each benchmark record the time take to execute between `start_trigger` and `stop_trigger`.
- This time should be recorded using hardware internal to the device being benchmarked - e.g., CPU cycle counter or other fast timer (i.e., running at a significantly higher rate than the benchmark takes to run).
- For each benchmark, compute its speed relative to the reference platform - see [Reference platform](#reference-platform) - by dividing the normalized time value of the reference benchmark by the time calculated in the previous step.
- Divide the relative score by `cpy_mhz`.
- Calculate the geometric mean, geometric standard deviation and range of one geometric standard deviation of the relative speeds.

The benchmark value is the geometric mean of the relative speeds. A larger value means a faster platform.  The range gives an indication of how much variability there is in this performance.

In addition the geometric mean may then be divided by the value used for CPU_MHZ, to yield an Embench score per MHz. This is an indication of the efficiency of the platform in carrying out computation.

### Computing a benchmark value for code size

The benchmarks should be compiled with `cflags` and `ldflags` that optimize for size, such as `-Os`.  The sections that count towards code size are specified in the `--metric` option when building.  By default just text sections are counted.

There is a fixed overhead to all benchmarks, which we wish to exclude when benchmarking.  This is done by compiling a dummy benchmark, which has no body, and subtracting its size from the size of sections when measured.

- For each benchmark record the size of all sections of the chosen metric.
- Subtract the sum of all chosen metric sections of the `dummy-benchmark` from
- For each benchmark, compute its size relative to the reference platform - see [Reference platform](#reference-platform) - by dividing the size recorded in the previous step by the size of the corresponding reference benchmark.
- Take the set of relative scores for all benchmarks and calculate the geometric mean, geometric standard deviation and range of one geometric standard deviation of the relative size.

The benchmark value is the geometric mean of the relative size. A larger value means code is larger.  The range gives an indication of how much variability there is in this measurement.

**NOTE** The computation of the relative value is inverted compared to the computation for speed.  This means that for size, **small** is good.

**NOTE** Older versions of the GNU _size_ program report the size of `.text` + `.rodata` section.  In measuring the size, the script requires a version of GNU _size_ which supports the `-G` flag, which will yield the size of just `.text` sections.

## Adding a new board to Embench DSP

### Creating a configuration for the new board

The configurations are in the `examples` directory and grouped by processor type.

Thus if we wanted to create a new configuration for the `mynewboard` board which has a 32-bit RISC-V processor, we would create a new directory:
```
mkdir examples/riscv32/mynewboard
```
In here, we create two files, `boardsupport.c` and `boardsupport.h`.

`boardsupport.h` can be empty, but is available if desired to specify default values of some of the _scons_ variables (e.g. `CPU_MHZ`.  Remember you can always override these values from the
command line.

`boardsupport.c` must define three `void` functions:

- `initialize_board` which is called to initialize the board;
- `start_trigger` which is called at the start of the test run; and
- `stop_trigger` which is called at the end of the test run.

It is usual for this file to include `support.h` to pick up any board and chip specific definitions that may prove useful.

Typically the tests are run using GDB and a remote GDB server to load the programs into a remote target.  This can set breakpoint on `start_trigger` and `stop_trigger` to start and stop timing.  In this case, these two function need no actual content, and the following is a sufficient implementation:

```C
void
start_trigger ()
{
  __asm__ volatile ("" : : : "memory");
}

void
stop_trigger ()
{
  __asm__ volatile ("" : : : "memory");
}
```

By marking the inline assembly volatile and clobbering memory, we guarantee a function which will just contain a return statement.

However alternative implementations may invoke an on-chip timer, writing values into global variables which can be read from the debugger.  This is the case for the Arm reference board.

Other files specific to the board may also be in this directory.  For example OpenOCD configuration files and linker scripts for use when building the programs.

### Configuration variables

Custom variables for compiling the benchmarks for your target are
specified as command line arguments to `scons`.