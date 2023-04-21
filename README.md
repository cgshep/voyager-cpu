# Sphinx CPU

An experimental Python emulator of a RISC-V core built with simplicity in mind for research and educational purposes.

## Features

+ Supports the RV32I ISA using a non-pipelined CPU with a single `cycle` for instruction fetch, decode, and execution.
+ A simple virtual RAM into which test programs (ELF binaries) are loaded. This makes use of the [official RISC-V ISA tests](https://github.com/riscv-software-src/riscv-tests/) (covered under a separate [LICENSE](./tests/official-test-binaries/LICENSE.md)).
  - Some example binaries are redistributed separately under `tests/official-test-binaries/`.
+ A basic REPL for viewing register and RAM contents, and executing the next or N cycle(s).
+ MIT license.

## Usage

1. (Optional) Build the [official RISC-V test binaries](https://github.com/riscv-software-src/riscv-tests/).
2. Run `python src/sphinxcpu/core.py`
3. (Optional) Run tests using `pytest`
4. Enjoy!

## Todo

+ Add more tests, particularly at the execution stage.
+ Implement some ISA extensions, e.g. the M and C specifications.
+ Add pipelining and privileged mode.
+ Etc.

Please contribute!