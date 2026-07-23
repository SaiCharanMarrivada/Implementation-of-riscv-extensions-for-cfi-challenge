## Submission for [Implementation of RISC-V extensions for Control Flow Integrity](https://mentorship.lfx.linuxfoundation.org/project/846490b5-2092-4645-895a-83c147ba5b68) challenge.

### Challenge
Implement a 3-state FSM in SystemVerilog that accepts a 32-bit packet every cycle: bits [31:24] represent a command (SET=0x01, JUMP=0x02, LPAD=0x03); bits [23:0] are data. If the FSM is in IDLE state, on SET, store data into the internal “label” register. On JUMP, move to the CHECK state. Otherwise, stay IDLE. If the FSM is in CHECK state, LPAD is received, and the data matches “label”, return to IDLE. Otherwise, move to ERROR. If the FSM reaches the ERROR state, it stays there forever.

### State machine
```mermaid
stateDiagram-v2
    direction LR
    [*] --> IDLE

    IDLE --> CHECK: JUMP
    IDLE --> IDLE: SET/invalid command
    CHECK --> IDLE: match
    CHECK --> ERROR: mismatch
    ERROR --> ERROR: any
```

Packets other than `JUMP` leave the FSM in `IDLE`, including `SET`, which
updates the internal label. In `CHECK`, a matching `LPAD` returns to `IDLE`;
all other packets enter `ERROR`. The `ERROR` state is permanent until reset.

### Dependencies
The following dependencies are needed to run the tests.
- `verilator`
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
