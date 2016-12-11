from vm import VirtualMachine


def format_val(val):
    if val <= 32767:
        return str(val)
    else:
        return '$%s' % (val - 32768)

if __name__ == '__main__':
    opcodes = {
            0: ('halt', 0),
            1: ('set', 2),
            2: ('push', 1),
            3: ('pop', 1),
            4: ('eq', 3),
            5: ('gt', 3),
            6: ('jmp', 1),
            7: ('jt', 2),
            8: ('jf', 2),
            9: ('add', 3),
            10: ('mul', 3),
            11: ('mod', 3),
            12: ('and', 3),
            13: ('or', 3),
            14: ('not', 2),
            15: ('rmem', 2),
            16: ('wmem', 2),
            17: ('call', 1),
            18: ('ret', 0),
            19: ('out', 1),
            20: ('in', 1),
            21: ('noop', 0),
        }
    vm = VirtualMachine('challenge.bin')
    with open('source.asm', 'w+') as f:
        while True:
            pc = vm.pc
            op = vm.next_byte()
            if op not in opcodes:
                f.write(str(pc) + ':\traw_byte: ' + str(op) + '\n')
                continue

            args = map(format_val, [vm.next_byte() for _ in range(opcodes[op][1])])
            if op == 19:
                try:
                    args[0] = "'%s'" % chr(int(args[0])).encode('string-escape')
                except:
                    pass
            out = str(pc) + ':\t' + opcodes[op][0] + '\t'
            out += ', '.join(args)
            out += '\n'
            f.write(out)