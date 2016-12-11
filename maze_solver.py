import operator
from collections import deque

maze = [
    ['*', '8', '-', '1'],
    ['4', '*', '11', '*'],
    ['+', '4', '-', '18'],
    ['22', '-', '9', '*']
]

def result(path):
    res, op = int(path[0]), None
    path = path[1:]
    operators = {
        '+': operator.add,
        '*': operator.mul,
        '-': operator.sub
    }
    for i in path:
        if i in operators:
            op = operators[i]
        else:
            res = op(res, int(i))
    return res


def solved(state):
    x, y, p, s = state
    return x == 3 and y == 0 and result(p) == 30


def hash(state):
    x, y, p, s = state
    return ','.join(map(str, (x, y, result(p))))


def dfs():
    state = (0, 3, ['22'], 0)
    seen = {}
    dfs_s = deque([state])
    sols = []
    while dfs_s:
        curr = dfs_s.popleft()
        print len(dfs_s), curr
        if solved(curr):
            sols.append(curr)
            break
        x, y, p, s = curr
        if hash(curr) in seen and seen[hash(curr)] < s:
            continue
        if x == 3 and y == 0:
            continue
        seen[hash(curr)] = s
        if x == 0 and y == 3 and s != 0:
            continue
        if s > 12:
            continue
        if x > 0:
            dfs_s.append((x - 1, y, p + [maze[y][x - 1]], s + 1))
        if x < 3:
            dfs_s.append((x + 1, y, p + [maze[y][x + 1]], s + 1))
        if y > 0:
            dfs_s.append((x, y - 1, p + [maze[y - 1][x]], s + 1))
        if y < 3:
            dfs_s.append((x, y + 1, p + [maze[y + 1][x]], s + 1))
    print "Solutions"
    print sols

dfs()