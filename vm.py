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

        self.opcodes = {
            0: 'halt',
            1: 'set',
            2: 'push',
            3: 'pop',
            4: 'eq',
            5: 'gt',
            6: 'jmp',
            7: 'jt',
            8: 'jf',
            9: 'add',
            10: 'mul',
            11: 'mod',
            12: 'and',
            13: 'or',
            14: 'not',
            15: 'rmem',
            16: 'wmem',
            17: 'call',
            18: 'ret',
            19: 'out',
            20: 'in',
            21: 'noop',
        }
        self.input_buf = ''

    def next_values(self, i):
        return map(self.vm.load_val, self.vm.next_bytes(i))

    def next_value(self):
        return self.vm.load_val(self.vm.next_byte())

    def noop(self):
        pass

    def op_out(self, a):
        a = self.vm.load_val(a)
        print(chr(a), end="")

    def op_in(self, a):
        if not self.input_buf:
            raw, done = raw_input('>>'), False
            while not done:
                if raw == 'pc':
                    print("PC: " + str(self.vm.pc))
                if raw == 'cd':
                    self.vm.core_dump()
                else:
                    done = True
                    self.input_buf = raw + '\n'
                raw = raw_input('>>')
        self.vm.store_reg(a, ord(self.input_buf[0]))
        self.input_buf = self.input_buf[1:]

    def op_operator(self, operation, a, b, c):
        b, c = map(self.vm.load_val, (b, c))
        res = int(operation(b, c)) % 32768
        self.vm.store_reg(a, res)

    def op_not(self, a, b):
        b = self.vm.load_val(b)
        res = ~b & 0x7FFF
        self.vm.store_reg(a, res)

    def op_jmp(self, a):
        a = self.vm.load_val(a)
        self.vm.pc = a

    def op_jt(self, a, b):
        a, b = map(self.vm.load_val, (a, b))
        if a != 0:
            self.vm.pc = b

    def op_jf(self, a, b):
        a, b = map(self.vm.load_val, (a, b))
        if a == 0:
            self.vm.pc = b

    def op_call(self, a):
        a = self.vm.load_val(a)
        self.vm.stack_push(self.vm.pc)
        self.vm.pc = a

    def op_ret(self):
        new_pc = self.vm.stack_pop()
        self.vm.pc = new_pc

    def op_set(self, a, b):
        b = self.vm.load_val(b)
        self.vm.store_reg(a, b)

    def op_halt(self):
        print("Halting")
        self.vm.core_dump()
        sys.exit()

    def op_push(self, a):
        a = self.vm.load_val(a)
        self.vm.stack_push(a)

    def op_pop(self, a):
        res = self.vm.stack_pop()
        self.vm.store_reg(a, res)

    def op_wmem(self, a, b):
        a, b = map(self.vm.load_val, (a, b))
        self.vm.write_mem(a, b)

    def op_rmem(self, a, b):
        b = self.vm.load_val(b)
        val = self.vm.read_mem(b)
        self.vm.store_reg(a, val)


def num_args(func):
    if type(func) == partial:
        return len(inspect.getargspec(func.func).args) - len(func.args)
    else:
        return len(inspect.getargspec(func).args)


def format_val(val):
    if val <= 32767:
        return str(val)
    else:
        return '$%s' % (val - 32768)

if __name__ == '__main__':
    virtual_machine = VirtualMachine('challenge.bin')
    op_unit = OperatorUnit(virtual_machine)
    cycle_count = 0

    def on_close():
        print("Cycle count: %s" % cycle_count)

    atexit.register(on_close)
    with open('bytecode.asm', 'w+') as f:
        while True:
            cycle_count += 1
            op = virtual_machine.next_byte()
            if op in op_unit.op_functions:
                func = op_unit.op_functions[op]
                args = [virtual_machine.next_byte()
                        for _ in range(num_args(func) - 1)]
                args_out = map(format_val, args)
                if op == 19 and not args_out[0][0] == '$':
                    args_out[0] = "'%s'" % chr(int(args_out[0])).encode('string-escape')
                out = op_unit.opcodes[op] + '\t'
                out += ', '.join(args_out)
                out += '\n'
                f.write(out)
                func(*args)
            else:
                print("Don't have operation for opcode: %s" % op)
                virtual_machine.core_dump()
                break
