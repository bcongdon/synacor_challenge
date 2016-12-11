from itertools import permutations


def check_solution(arr):
    a, b, c, d, e = arr
    return a + b * c ** 2 + d ** 3 - e == 399

if __name__ == '__main__':
    coins = {
        2: 'red',
        3: 'corroded',
        5: 'shiny',
        7: 'concave',
        9: 'blue'
    }

    sol = next(i for i in permutations(coins.keys(), len(coins))
               if check_solution(i))
    print('Correct order: ' + ', '.join([coins[i] for i in sol]))
    print('({} + {}*{}^2 + {}^3 - {} = 399)'.format(*sol))
