import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


IDLE = 0
CHECK = 1
ERROR = 2

SET = 0x01
JUMP = 0x02
LPAD = 0x03


def packet(command, data=0):
    return (command << 24) | data


async def send_packet(dut, command, data=0):
    dut.packet.value = packet(command, data)
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")


@cocotb.test()
async def test_idle_packet_sequences(dut):
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    dut.reset.value = 1
    dut.packet.value = 0
    await RisingEdge(dut.clk)
    dut.reset.value = 0
    await Timer(1, unit="ns")

    assert dut.state.value.to_unsigned() == IDLE

    await send_packet(dut, SET, 0x123456)
    assert dut.state.value.to_unsigned() == IDLE

    await send_packet(dut, LPAD, 0x123456)
    assert dut.state.value.to_unsigned() == IDLE

    await send_packet(dut, 0x00, 0xABCDEF)
    assert dut.state.value.to_unsigned() == IDLE

    await send_packet(dut, 0xFF, 0xABCDEF)
    assert dut.state.value.to_unsigned() == IDLE

    await send_packet(dut, JUMP)
    assert dut.state.value.to_unsigned() == CHECK


@cocotb.test()
async def test_jump_then_matching_lpad_returns_to_idle(dut):
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    dut.reset.value = 1
    dut.packet.value = 0
    await RisingEdge(dut.clk)
    dut.reset.value = 0
    await Timer(1, unit="ns")

    await send_packet(dut, SET, 0x00C0DE)
    await send_packet(dut, JUMP)
    assert dut.state.value.to_unsigned() == CHECK

    await send_packet(dut, LPAD, 0x00C0DE)
    assert dut.state.value.to_unsigned() == IDLE


@cocotb.test()
async def test_jump_then_mismatching_lpad_enters_error(dut):
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    dut.reset.value = 1
    dut.packet.value = 0
    await RisingEdge(dut.clk)
    dut.reset.value = 0
    await Timer(1, unit="ns")

    await send_packet(dut, SET, 0x00C0DE)
    await send_packet(dut, JUMP)
    await send_packet(dut, LPAD, 0xBADBAD)
    assert dut.state.value.to_unsigned() == ERROR


@cocotb.test()
async def test_jump_then_other_packets_enter_error(dut):
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    dut.reset.value = 1
    dut.packet.value = 0
    await RisingEdge(dut.clk)
    dut.reset.value = 0
    await Timer(1, unit="ns")

    await send_packet(dut, SET, 0x111111)
    await send_packet(dut, JUMP)
    await send_packet(dut, SET, 0x222222)
    assert dut.state.value.to_unsigned() == ERROR

    dut.reset.value = 1
    await RisingEdge(dut.clk)
    dut.reset.value = 0
    await Timer(1, unit="ns")
    await send_packet(dut, SET, 0x111111)
    await send_packet(dut, JUMP)
    await send_packet(dut, JUMP)
    assert dut.state.value.to_unsigned() == ERROR

    dut.reset.value = 1
    await RisingEdge(dut.clk)
    dut.reset.value = 0
    await Timer(1, unit="ns")
    await send_packet(dut, SET, 0x111111)
    await send_packet(dut, JUMP)
    await send_packet(dut, 0xFF, 0x111111)
    assert dut.state.value.to_unsigned() == ERROR


@cocotb.test()
async def test_latest_set_data_is_used_by_lpad(dut):
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    dut.reset.value = 1
    dut.packet.value = 0
    await RisingEdge(dut.clk)
    dut.reset.value = 0
    await Timer(1, unit="ns")

    await send_packet(dut, SET, 0x111111)
    await send_packet(dut, SET, 0x222222)
    await send_packet(dut, JUMP)
    await send_packet(dut, LPAD, 0x222222)
    assert dut.state.value.to_unsigned() == IDLE


@cocotb.test()
async def test_error_state_absorbs_all_packets(dut):
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    dut.reset.value = 1
    dut.packet.value = 0
    await RisingEdge(dut.clk)
    dut.reset.value = 0
    await Timer(1, unit="ns")

    await send_packet(dut, SET, 0x123456)
    await send_packet(dut, JUMP)
    await send_packet(dut, LPAD, 0x654321)
    assert dut.state.value.to_unsigned() == ERROR

    # the DUT should stay in the error state once it gets into error state
    for command, data in ((SET, 0x123456), (JUMP, 0), (LPAD, 0), (0xFF, 0xABCDEF)):
        await send_packet(dut, command, data)
        assert dut.state.value.to_unsigned() == ERROR


@cocotb.test()
async def test_reset_returns_to_idle(dut):
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    dut.reset.value = 1
    dut.packet.value = 0
    await RisingEdge(dut.clk)
    dut.reset.value = 0
    await Timer(1, unit="ns")

    await send_packet(dut, SET, 0x123456)
    await send_packet(dut, JUMP)
    await send_packet(dut, LPAD, 0x654321)
    assert dut.state.value.to_unsigned() == ERROR

    dut.reset.value = 1
    await RisingEdge(dut.clk)
    dut.reset.value = 0
    await Timer(1, unit="ns")
    assert dut.state.value.to_unsigned() == IDLE
