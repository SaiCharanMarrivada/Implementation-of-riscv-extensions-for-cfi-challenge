## Submission for [Implementation of RISC-V extensions for Control Flow Integrity](https://mentorship.lfx.linuxfoundation.org/project/846490b5-2092-4645-895a-83c147ba5b68) challenge.

### Challenge
Implement a 3-state FSM in SystemVerilog that accepts a 32-bit packet every cycle: bits [31:24] represent a command (SET=0x01, JUMP=0x02, LPAD=0x03); bits [23:0] are data. If the FSM is in IDLE state, on SET, store data into the internal “label” register. On JUMP, move to the CHECK state. Otherwise, stay IDLE. If the FSM is in CHECK state, LPAD is received, and the data matches “label”, return to IDLE. Otherwise, move to ERROR. If the FSM reaches the ERROR state, it stays there forever.

### State machine
<picture>
  <source
    media="(prefers-color-scheme: dark)"
    srcset="fsm_diagram_white.svg">
  <img
    src="fsm_diagram_dark.svg"
    alt="Packet FSM state transitions">
</picture>

Packets other than `JUMP` leave the FSM in `IDLE`, including `SET`, which
updates the internal label. In `CHECK`, a matching `LPAD` returns to `IDLE`;
all other packets enter `ERROR`. The `ERROR` state is permanent until reset.

### Dependencies
The following dependencies are needed to run the tests.
- `verilator` or any cocotb supported simulator
- `cocotb`
- `python3`

### How to run the tests
```bash
make
```
If you want to run the tests with Icarus verilog change the command to
```bash
make SIM=icarus
```
The Makefile was adapted from the [cocotb first steps](https://docs.cocotb.org/en/development/first_steps.html#building-your-design-and-running-simulations).
