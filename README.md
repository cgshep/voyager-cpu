# Sphinx CPU

Sphinx CPU is an experimental Python emulator of a 32-bit RISC-V core. It's built with simplicity in mind for research and educational purposes.

## Features

+ Supports the RV32I ISA using a non-pipelined CPU with a single-cycle instruction fetch, decode, and execution stage.
+ A simple virtual RAM into which test programs (ELF binaries) are loaded. The [official RISC-V ISA tests](https://github.com/riscv-software-src/riscv-tests/), covered under a separate [LICENSE](./tests/official-test-binaries/LICENSE.md), can be used for this purpose.
  - Some test binaries are redistributed separately under `tests/official-test-binaries/`.
+ A basic REPL for viewing register and RAM contents, and executing the next or N cycle(s).
+ MIT license.

## Usage

1. (Optional) If you don't want to use the [pre-built test binaries](tests/official-test-binaries/), then build the [official RV32UI RISC-V test suites](https://github.com/riscv-software-src/riscv-tests/) from the official repo.
2. Run `python src/sphinxcpu/core.py`
3. Enjoy!
4. (Optional) Run tests using `pytest`

## Todo

+ Add more tests, particularly at the execution stage.
+ Implement some ISA extensions, e.g. the M and C specifications.
+ Add pipelining and privileged mode.
+ Improve pretty printing.
+ Etc.

Please contribute!