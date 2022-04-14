#!/usr/bin/env python3

import angr
import claripy
import logging
import struct

def solve_phase_1():

    proj = angr.Project("binary_water_balloon_x86_64", auto_load_libs = False,
                        use_sim_procedures=True)

    # We'll let CLE load at whatever base address it wants, and determine
    # determine function starts from the signature.
    # Note that the base address that CLE chooses is different than the
    # base address that Ghidra chooses by default.

    start = proj.loader.main_object.get_symbol("phase_1").rebased_addr
    bad = proj.loader.main_object.get_symbol("balloon_splat").rebased_addr
    end  = start + 0x18 # Return instruction offset

    # Initialize state at beginning of function
    state = proj.factory.blank_state(addr=start)

    # Create a input_string symbol up to 0x40 bytes in length
    arg = state.solver.BVS("input_string", 8 * 0x40)

    # Create a dummy memory address where the input is stored
    bind_addr = 0x600000
    state.memory.store(bind_addr, arg)

    # The address of the input string is the only function argument
    state.add_constraints(state.regs.rdi == bind_addr)

    simgr = proj.factory.simulation_manager(state)
    simgr.explore(find=end, avoid=bad)

    if simgr.found:
        found = simgr.found[0]
        flag = found.solver.eval(arg, cast_to=bytes)
        return flag[:flag.index(b'\x00')].decode()
    else:
        raise Exception("Failed to find a path to the solution of phase_1")

def solve_phase_2():

    proj = angr.Project("binary_water_balloon_x86_64", auto_load_libs = False,
                        use_sim_procedures=True)

    # We'll let CLE load at whatever base address it wants, and determine
    # determine function starts from the signature.
    # Note that the base address that CLE chooses is different than the
    # base address that Ghidra chooses by default.

    fun_start = proj.loader.main_object.get_symbol("phase_2").rebased_addr
    # Start after sscanf
    start = fun_start + 0x13
    bad = proj.loader.main_object.get_symbol("balloon_splat").rebased_addr
    end  = fun_start + 0x50 # Return instruction offset

    # Initialize state at beginning of function
    state = proj.factory.blank_state(addr=start)

    # Store six symbolic 4-byte integers on the stack
    constraints = []
    for i in range(6):
        constraints.append(state.solver.BVS('int{}'.format(i), 4*8))
        state.memory.store(state.regs.rsp + i*4, constraints[-1])

    simgr = proj.factory.simulation_manager(state)
    simgr.explore(find=end, avoid=bad)

    if simgr.found:
        found = simgr.found[0]
        nums = []
        for c in constraints:
            # eval() is returning big-endian ints, so unpack this myself...
            nums.append(struct.unpack("<I", 
                found.solver.eval(c, cast_to=bytes))[0])
        return "%i %i %i %i %i %i" % tuple(nums)
    else:
        raise Exception("Failed to find a path to the solution of phase_2")

def solve_phase_3():

    proj = angr.Project("binary_water_balloon_x86_64", auto_load_libs = False,
                        use_sim_procedures=True)

    # We'll let CLE load at whatever base address it wants, and determine
    # determine function starts from the signature.
    # Note that the base address that CLE chooses is different than the
    # base address that Ghidra chooses by default.

    fun_start = proj.loader.main_object.get_symbol("phase_3").rebased_addr
    # Start after sscanf
    start = fun_start + 0x24
    bad = proj.loader.main_object.get_symbol("balloon_splat").rebased_addr
    end  = fun_start + 0xca # Return instruction offset

    # Initialize state at beginning of function
    state = proj.factory.blank_state(addr=start)

    # Store two symbolic 4-byte integers on the stack
    arg0 = state.solver.BVS('arg0', 4*8)
    arg1 = state.solver.BVS('arg1', 4*8)
    # Note order of storage
    state.memory.store(state.regs.rsp + 0xc, arg0)
    state.memory.store(state.regs.rsp + 0x8, arg1)

    simgr = proj.factory.simulation_manager(state)
    simgr.explore(find=end, avoid=bad)

    answers = []
    if simgr.found:
        for found in simgr.found:
            f_arg0 = struct.unpack("<I",
                    found.solver.eval(arg0, cast_to=bytes))[0]
            f_arg1 = struct.unpack("<I",
                    found.solver.eval(arg1, cast_to=bytes))[0]
            answers.append("{} {}".format(f_arg0, f_arg1))
    else:
        raise Exception("Failed to find a path to the solution of phase_3")

    answers.sort(key = lambda x: int(x.split(' ')[0]))
    return answers

def solve_phase_4():

    proj = angr.Project("binary_water_balloon_x86_64", auto_load_libs = False,
                        use_sim_procedures=True)

    # We'll let CLE load at whatever base address it wants, and determine
    # determine function starts from the signature.
    # Note that the base address that CLE chooses is different than the
    # base address that Ghidra chooses by default.

    fun_start = proj.loader.main_object.get_symbol("phase_4").rebased_addr
    # Start after sscanf
    start = fun_start + 0x24
    bad = proj.loader.main_object.get_symbol("balloon_splat").rebased_addr
    end  = fun_start + 0x43 # Return instruction offset

    # Initialize state at beginning of function
    state = proj.factory.blank_state(addr=start)

    # Store two symbolic 4-byte integers on the stack
    arg0 = state.solver.BVS('arg0', 4*8)
    arg1 = state.solver.BVS('arg1', 4*8)
    # Note order of storage
    state.memory.store(state.regs.rsp + 0xc, arg0)
    state.memory.store(state.regs.rsp + 0x8, arg1)

    # The recursion will lead to multiple active states even as one is 'found'.
    # A queue allows us to continue execution on those active states to find
    # all possible solutions.

    state_queue = [state]

    answers = []
    while len(state_queue) > 0:
        state = state_queue.pop()

        simgr = proj.factory.simulation_manager(state)
        simgr.explore(find=end, avoid=bad)

        for s in simgr.active:
            state_queue.append(s)

        if simgr.found:
            for found in simgr.found:
                # Handle multiple solutions if needed, although it
                # appears that all of these only have 1.
                for c in found.solver.eval_atmost(arg0, 10):
                    f_arg0 = struct.unpack("<I", found.solver.eval(arg0,
                        cast_to=bytes, extra_constraints=(arg0==c,)))[0]
                    f_arg1 = struct.unpack("<I", found.solver.eval(arg1,
                        cast_to=bytes, extra_constraints=(arg0==c,)))[0]
                    answers.append("{} {}".format(f_arg0, f_arg1))

    answers.sort(key = lambda x: int(x.split(' ')[0]))
    return answers

def solve_phase_5():

    proj = angr.Project("binary_water_balloon_x86_64", auto_load_libs = False,
                        use_sim_procedures=True)

    # We'll let CLE load at whatever base address it wants, and determine
    # determine function starts from the signature.
    # Note that the base address that CLE chooses is different than the
    # base address that Ghidra chooses by default.

    fun_start = proj.loader.main_object.get_symbol("phase_5").rebased_addr
    # Start after sscanf
    start = fun_start + 0x24
    bad = proj.loader.main_object.get_symbol("balloon_splat").rebased_addr
    end  = fun_start + 0x5b # Return instruction offset

    # Initialize state at beginning of function
    state = proj.factory.blank_state(addr=start)

    # Store two symbolic 4-byte integers on the stack
    arg0 = state.solver.BVS('arg0', 4*8)
    arg1 = state.solver.BVS('arg1', 4*8)
    # Note order of storage
    state.memory.store(state.regs.rsp + 0xc, arg0)
    state.memory.store(state.regs.rsp + 0x8, arg1)

    answers = []
    state_queue = [state]
    while len(state_queue) > 0:
        state = state_queue.pop()
        simgr = proj.factory.simulation_manager(state)
        simgr.explore(find=end, avoid=bad)

        for s in simgr.active:
            state_queue.append(s)

        if simgr.found:
            for found in simgr.found:
                f_arg0 = struct.unpack("<I",
                        found.solver.eval(arg0, cast_to=bytes))[0]
                f_arg1 = struct.unpack("<I",
                        found.solver.eval(arg1, cast_to=bytes))[0]
                answers.append("{} {}".format(f_arg0, f_arg1))

    answers.sort(key = lambda x: int(x.split(' ')[0]))
    return answers

def solve_phase_6():

    proj = angr.Project("binary_water_balloon_x86_64", auto_load_libs = False,
                        use_sim_procedures=True)

    # We'll let CLE load at whatever base address it wants, and determine
    # determine function starts from the signature.
    # Note that the base address that CLE chooses is different than the
    # base address that Ghidra chooses by default.

    start = proj.loader.main_object.get_symbol("phase_6").rebased_addr
    bad = proj.loader.main_object.get_symbol("balloon_splat").rebased_addr
    end  = start + 0xa9 # Return instruction offset

    # Initialize state at beginning of function
    state = proj.factory.blank_state(addr=start)

    # Create a input_string symbol up to 0x40 bytes in length
    arg = state.solver.BVS("input_string", 8 * 0x40)

    # Create a dummy memory address where the input is stored
    bind_addr = 0x600000
    state.memory.store(bind_addr, arg)

    # The address of the input string is the only function argument
    state.add_constraints(state.regs.rdi == bind_addr)

    simgr = proj.factory.simulation_manager(state)
    simgr.explore(find=end, avoid=bad)

    if simgr.found:
        found = simgr.found[0]
        flag = found.solver.eval(arg, cast_to=bytes)
        return flag[:flag.index(b'\x00')].decode()
    else:
        raise Exception("Failed to find a path to the solution of phase_6")

print("\x1b[1;33mSolving phase 1...\x1b[0;0m")
phase_1_soln = solve_phase_1()
print("\x1b[1;33mSolving phase 2...\x1b[0;0m")
phase_2_soln = solve_phase_2()
print("\x1b[1;33mSolving phase 3...\x1b[0;0m")
phase_3_solns = solve_phase_3()
print("\x1b[1;33mSolving phase 4...\x1b[0;0m")
phase_4_solns = solve_phase_4()
print("\x1b[1;33mSolving phase 5...\x1b[0;0m")
phase_5_solns = solve_phase_5()
print("\x1b[1;33mSolving phase 6...\x1b[0;0m")
phase_6_soln = solve_phase_6()

print("Phase 1 solution:", phase_1_soln)
print("Phase 2 solution:", phase_2_soln)
for s in phase_3_solns:
    print("Phase 3 solution:", s)
for s in phase_4_solns:
    print("Phase 4 solution:", s)
# Note that the '6' solution is invalid due to a NULL pointer dereference, but
# this analysis didn't catch that since it's unaware of the segmentation.
for s in phase_5_solns[:-1]:
    print("Phase 5 solution:", s)
print("Phase 6 solution:", phase_6_soln)

