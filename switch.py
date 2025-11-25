# Copyright (c) 2025. Battelle Energy Alliance, LLC
# ALL RIGHTS RESERVED

import binaryninja as bn


def sign_extend(value, bits):
    """Sign extend a 'bits' size value."""
    sign_bit = 1 << (bits - 1)
    return (value & (sign_bit - 1)) - (value & sign_bit)


def find_table_size(bv: bn.BinaryView, block: bn.BasicBlock) -> int:
    """Determine table size from preceding cmp instruction."""
    size = 0
    addr = block.start
    while addr <= block.end:
        tokens, length = block.function.arch.get_instruction_text(
            bv.read(addr, 4), addr
        )
        if str(tokens[0]).rstrip() == "cmp":
            size = int(str(tokens[2]), 16) + 1
        elif str(tokens[0]).rstrip() == "bh":
            info: bn.InstructionInfo = block.function.arch.get_instruction_info(
                bv.read(addr, 4), addr
            )
            branches: [bn.InstructionBranch] = info.branches
            target: int = next(
                filter(lambda x: x.type is bn.BranchType.TrueBranch, branches)
            ).target
            bv.define_user_symbol(
                bn.Symbol(bn.SymbolType.DataSymbol, target, "case_default")
            )
            block.function.set_comment_at(target, "Default case")
        elif str(tokens[0]).rstrip() == "jr":
            info: bn.InstructionInfo = block.function.arch.get_instruction_info(
                bv.read(addr, 4), addr
            )
            bv.define_user_symbol(
                bn.Symbol(
                    bn.SymbolType.DataSymbol, info.branches[0].target, "case_default"
                )
            )
            block.function.set_comment_at(info.branches[0].target, "Default case")
        addr += length
    return size


def fix_jump_table(bv: bn.BinaryView, address: int, update=True):
    if len(bv.get_basic_blocks_at(address)) == 0:
        return False

    bv.begin_undo_actions()
    block: bn.BasicBlock = bv.get_basic_blocks_at(address)[0]
    tokens, length = block.function.arch.get_instruction_text(
        bv.read(address, 4), address
    )
    if str(tokens[0]).rstrip() != "switch":
        bn.log_error("Instruction != switch")
        return False

    dom = block.immediate_dominator
    if not dom:
        bn.log_error(
            "No dominator block available -- is this function valid? \
                   If invalid: (1) Undefine function --> (2) search above for real switch statement"
        )
        return False
    tsize = find_table_size(bv, block.immediate_dominator)
    block.function.set_comment_at(address, "Switch table of size {}".format(tsize))
    bn.log_debug("Found switch table of size {}".format(str(tsize)))

    branches = []
    cursor = address + length  # PC + 2
    br = bn.BinaryReader(bv, bn.Endianness.LittleEndian)
    br.seek(cursor)
    for i in range(tsize):
        offset = sign_extend(br.read16(), 16) << 1
        branches.append((block.function.arch, cursor + offset))
        bv.define_user_data_var(cursor + i * 2, bn.Type.int(2, False))
        bv.define_user_symbol(
            bn.Symbol(bn.SymbolType.DataSymbol, cursor + i * 2, "case_" + str(i))
        )

    block.function.set_user_indirect_branches(address, branches, block.function.arch)
    block.function.reanalyze()

    bv.commit_undo_actions()
    if update:
        bv.update_analysis()
    return True


def eliminate_invalid_switches(bv: bn.BinaryView):
    bv.begin_undo_actions()
    switches = []
    collisions = {}
    for fxn in bv.functions:
        for instr in fxn.instructions:
            if instr[0][0].text.rstrip() == "switch":
                switches.append(instr[1])
                blocks: [bn.BasicBlock] = bv.get_basic_blocks_at(instr[1])
                if len(blocks) > 1:
                    bn.log_info("Collision at 0x{:x}: {}".format(instr[1], blocks))
                    if instr[1] in collisions:
                        collisions[instr[1]].append(fxn.start)
                    else:
                        collisions[instr[1]] = [fxn.start]
    bn.log_debug("{}".format(collisions))
    for addr in collisions:
        highest = max(collisions[addr])
        bn.log_info("Eliminating function at 0x{:x}".format(highest))
        bv.remove_function(bv.get_function_at(highest))
    bv.commit_undo_actions()
    return switches


def fix_jump_tables(bv: bn.BinaryView):
    bv.store_metadata(
        "v850jump_analysis_changed", False
    )  # set this to True if our sweep finds new functions
    bv.store_metadata(
        "v850jump_active", True
    )  # makeshift mutex (if caller cares about waiting for results)
    while True:
        switches = eliminate_invalid_switches(bv)
        bn.log_info("Fixing switch statements at...")
        for addr in switches:
            bn.log_info("0x{:x}".format(addr))
            fix_jump_table(bv, addr, update=False)
        switches2 = eliminate_invalid_switches(bv)
        num_fixed = len(switches) - len(switches2)
        bn.log_info(
            "Fixed {} switch {}".format(
                num_fixed, "statement" if num_fixed == 1 else "statements"
            )
        )
        if num_fixed > 0:
            bv.store_metadata("v850jump_analysis_changed", True)
            bv.update_analysis_and_wait()
        else:
            break
    bv.store_metadata("v850jump_active", False)
    return
