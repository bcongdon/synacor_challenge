from __future__ import print_function
from collections import defaultdict
from functools import partial
import operator
import inspect
import sys
import atexit


class VirtualMachine:
    def __init__(self, fname):
        self.pc = 0
        self.data = []
        self.registers = defaultdict(int)
        self.stack = []
        with open(fname, 'rb') as f:
            lo, hi = map(ord, f.read(2))
            while True:
                self.data.append((hi << 8) | lo)
                try:
                    lo, hi = map(ord, f.read(2))
                except ValueError:
                    break
            print("Loaded %s bytes of program binary. " % len(self.data))
            while len(self.data) < 32769:
                self.data.append(0)

    def core_dump(self):
        print("*** Core Dump ***")
        print("PC: %s" % self.pc)
        print("Registers:")
        print(self.registers)

    def next_byte(self):
        res = self.data[self.pc]
        self.pc += 1
        return res

    def next_bytes(self, num_bytes):
        return [self.next_byte() for _ in range(num_bytes)]

    def load_val(self, loc):
        if 0 <= loc <= 32767:
            return loc
        elif 32768 <= loc <= 32775:
            return self.registers[loc]
        else:
            self.core_dump()
            raise ValueError("Invalid memory location: %s" % loc)

    def store_reg(self, loc, val):
        if val >= 32768:
            val = self.load_val(val)
        if 32768 <= loc <= 32775:
            self.registers[loc] = val
        elif 0 <= loc <= 7:
            self.registers[loc + 32768] = val
        else:
            raise ValueError("Invalid register: %s" % loc)

    def read_mem(self, loc):
        return self.data[loc]

    def write_mem(self, loc, val):
        self.data[loc] = val

    def stack_push(self, i):
        self.stack.append(i)

    def stack_pop(self):
        if not self.stack:
            raise "Tried to pop an empty stack!"
        return self.stack.pop()


class OperatorUnit:
    def __init__(self, vm):
        self.vm = vm
        self.op_functions = {
            0: self.op_halt,
            1: self.op_set,
            2: self.op_push,
            3: self.op_pop,
            4: partial(self.op_operator, operator.eq),
            5: partial(self.op_operator, operator.gt),
            6: self.op_jmp,
            7: self.op_jt,
            8: self.op_jf,
            9: partial(self.op_operator, operator.add),
            10: partial(self.op_operator, operator.mul),
            11: partial(self.op_operator, operator.mod),
            12: partial(self.op_operator, operator.__and__),
            13: partial(self.op_operator, operator.__or__),
            14: self.op_not,
            15: self.op_rmem,
            16: self.op_wmem,
            17: self.op_call,
            18: self.op_ret,
            19: self.op_out,
            20: self.op_in,
            21: self.noop,
        }
        self.input_buf = ''

    def next_values(self, i):
        return map(self.vm.load_val, self.vm.next_bytes(i))

    def next_value(self):
        return self.vm.load_val(self.vm.next_byte())

    def noop(self):
        pass

    def op_out(self):
        a = self.next_value()
        print(chr(a), end="")

    def op_in(self):
        a = self.vm.next_byte()
        if not self.input_buf:
            self.input_buf = raw_input('>>') + '\n'
        self.vm.store_reg(a, ord(self.input_buf[0]))
        self.input_buf = self.input_buf[1:]

    def op_operator(self, operation):
        a = self.vm.next_byte()
        b, c = self.next_values(2)
        res = int(operation(b, c)) % 32768
        self.vm.store_reg(a, res)

    def op_not(self):
        a = self.vm.next_byte()
        b = self.next_value()
        res = ~b & 0x7FFF
        self.vm.store_reg(a, res)

    def op_jmp(self):
        a = self.next_value()
        self.vm.pc = a

    def op_jt(self):
        a, b = self.next_values(2)
        if a != 0:
            self.vm.pc = b

    def op_jf(self):
        a, b = self.next_values(2)
        if a == 0:
            self.vm.pc = b

    def op_call(self):
        self.vm.stack_push(self.vm.pc + 1)
        a = self.next_value()
        self.vm.pc = a

    def op_ret(self):
        new_pc = self.vm.stack_pop()
        self.vm.pc = new_pc

    def op_set(self):
        a = self.vm.next_byte()
        b = self.next_value()
        self.vm.store_reg(a, b)

    def op_halt(self):
        print("Halting")
        self.vm.core_dump()
        sys.exit()

    def op_push(self):
        a = self.next_value()
        self.vm.stack_push(a)

    def op_pop(self):
        a = self.vm.next_byte()
        res = self.vm.stack_pop()
        self.vm.store_reg(a, res)

    def op_wmem(self):
        a = self.next_value()
        b = self.next_value()
        self.vm.write_mem(a, b)

    def op_rmem(self):
        a = self.vm.next_byte()
        b = self.next_value()
        val = self.vm.read_mem(b)
        self.vm.store_reg(a, val)


def num_args(func):
    if type(func) == partial:
        return len(inspect.getargspec(func.func).args) - len(func.args)
    else:
        return len(inspect.getargspec(func).args)

if __name__ == '__main__':
    virtual_machine = VirtualMachine('challenge.bin')
    op_unit = OperatorUnit(virtual_machine)
    cycle_count = 0


    def on_close():
        print("Cycle count: %s" % cycle_count)

    atexit.register(on_close)
    while True:
        cycle_count += 1
        op = virtual_machine.next_byte()
        if op in op_unit.op_functions:
            op_unit.op_functions[op]()
        else:
            print("Don't have operation for opcode: %s" % op)
            virtual_machine.core_dump()
            break
