# Voyager CPU

Voyager is a (very) experimental Python emulator of a 32-bit RISC-V core. It's built for research and education with simplicity in mind.

## Features

+ Supports the RV32I ISA using a non-pipelined CPU with a single-cycle instruction fetch, decode, and execution stage.
+ A simple virtual RAM into which test programs (ELF binaries) are loaded.
  -  The [official RISC-V ISA tests](https://github.com/riscv-software-src/riscv-tests/) can be used for this purpose. Some test binaries are redistributed separately under `tests/official-test-binaries/`, which are covered under a separate [LICENSE](./tests/official-test-binaries/LICENSE.md).
+ A basic REPL for viewing register and RAM contents, and executing the next N cycles.
+ MIT license.

## Build and Run

1. (Optional) Clone the pre-built RV32UI tests using:
```
git submodule init
git submodule update
```
The binaries will be placed under `tests/riscv-tests-prebuilt-binaries/`. Alternatively, you can build the [test suites from the official repo](https://github.com/riscv-software-src/riscv-tests/).

2. See the example in `src/voyagercpu/example.py`. You may run this directly using `python src/voyagercpu/example.py`.

3. Enjoy!

4. (Optional) Run the Voyager unit tests using `pytest`

## Todo

+ Add more tests, particularly at the execution stage.
+ Implement some ISA extensions, e.g. the M and C specifications.
+ Add pipelining and privileged mode.
+ Improve pretty printing.
+ Etc.

Please contribute!