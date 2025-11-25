# Copyright (c) 2025. Battelle Energy Alliance, LLC
# ALL RIGHTS RESERVED

import binaryninja as bn

from . import switch


class SideEffectThread(bn.BackgroundTaskThread):
    def __init__(self, bv: bn.BinaryView, msg: str, func):
        bn.BackgroundTaskThread.__init__(self, msg, True)
        self.bv = bv
        self.func = func

    def run(self):
        self.func(self.bv)


def fix_all_tables(bv: bn.BinaryView):
    s = SideEffectThread(
        bv, "Attempting to fix all switch statements globally", switch.fix_jump_tables
    )
    s.start()


bn.PluginCommand.register(
    "(Global) Fix V850 jump tables",
    "Fix all switch statements in all functions",
    fix_all_tables,
)
bn.PluginCommand.register_for_address(
    "(Address) Fix V850 jump table",
    "Parses jump table destinations",
    switch.fix_jump_table,
)
