from __future__ import print_function
from collections import DefaultDict


class VirtualMachine:
    def __init__(self, fname):
        self.pc = 0
        self.inst = []
        self.data = DefaultDict(int)
        self.registers = DefaultDict(int)
        with open(fname, 'rb') as f:
            lo, hi = map(ord, f.read(2))
            while lo or hi:
                byte = (hi << 8) | lo
                self.data.append(byte)
                lo, hi = map(ord, f.read(2))

    def next_byte(self):
        self.pc += 1
        return self.inst[self.pc]

    def load_val(self, loc):
        if 0 <= loc <= 32767:
            return loc
        elif loc <= 32775:
            return self.registers[loc]
        else:
            raise ValueError("Invalid memory location: %s" % loc)

    def store_reg(self, loc, val):
        if 32768 <= loc <= 32775:
            self.registers[loc] = val

    def read_mem(self, loc):
        return self.data[loc]

    def write_mem(self, loc, val):
        self.data[loc] = val


def noop(vm):
    pass


def op_out(vm):
    c = vm.next_byte()
    print(chr(c), end="")


def op_in(vm):
    i = raw_input()
    print(i)

ops = {
    # 0: halt,
    # 1: op_set,
    # 2: op_push,
    # 3: op_pop,
    # 4: op_eq,
    # 5: op_gt,
    # 6: op_jmp,
    # 7: op_jt,
    # 8: op_jf,
    # 9: op_add,
    # 10: op_mult,
    # 11: op_mod,
    19: op_out,
    20: op_in,
    21: noop,
}

if __name__ == '__main__':
    data_mem = VirtualMachine('challenge.bin')
    # while True:
    #     op = next(i)
    #     if op in ops:
    #         ops[op](i)
    #     else:
    #         print("Don't have operation for opcode: %s" % op)
    #         print("")
    #         break
