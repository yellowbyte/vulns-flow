from binaryninja import *

import ctypes
import sys


class Callgraph:

    def __init__(self, view, rootfunction=None):
        self.view = view
        self.rootfunction = rootfunction
        self.leafs = set()
        self.not_leafs = set()
        self.calls = {}  # dict containing callee -> set(callers)
        self.collect_calls()

    def collect_calls(self):

        for function in self.view.functions:
            if not self.is_user_defined(function):
                continue
            for ref in self.view.get_code_refs(function.start):
                caller = ref.function
                self.calls[function] = self.calls.get(function, set())
                if function not in self.not_leafs:
                    self.leafs.add(function)
                call_il = caller.get_low_level_il_at(ref.address)
                if isinstance(call_il, Call) and isinstance(call_il.dest, Constant):
                    self.calls[function].add(caller)
                    self.not_leafs.add(caller)
                    if caller in self.leafs:
                        self.leafs.remove(caller)

    @staticmethod
    def is_user_defined(function):
        func_name = function.name
        if func_name in bv.symbols:
            # function name is in imported symbols
            symbols = bv.symbols[func_name]
            for sym in symbols:
                if (
                        sym.type == SymbolType.DataSymbol or
                        sym.type == SymbolType.FunctionSymbol
                ):
                    if sym.address == function.start:
                        return True
        return False


if __name__ == "__main__":
    filepath = sys.argv[1]
    bv = binaryninja.load(filepath)
    cg = Callgraph(bv)
    breakpoint()