import random
from collections import Counter

amount = 1000000
counter = 0
sequence = []


# calculating second moment / вычисление второго момента
def calculate_second_moment(seq):
    c = Counter(seq)
    return sum(v ** 2 for v in c.values())


# calculating zero, first moments and estimating second moment (The "Alon-Matias-Szegedy” algorithm)
# вычисление нулевого, первого момента и оценка/приближение второго момента (алгоритм "Алона-Матиаса-Сегеди")
def estimate_second_moment(seq, number_of_variables):
    nums = list(range(len(seq)))
    random.shuffle(nums)
    nums = sorted(nums[:number_of_variables])
    d = {}
    for i, c in enumerate(seq):
        if i in nums and c not in d:
            d[c] = 0
        if c in d:
            d[c] += 1
    moments = [len(d),  # 0th moment
               amount,  # 1st moment
               int(len(seq) / float(len(d)) * sum((2 * v - 1) for v in d.values()))  # 2nd moment estimate
               ]
    return moments


# generating random numbers into a sequence / генерация рандомных чисел в последовательность
for n in range(amount):
    sequence.append(random.randint(1, 1000))
    counter += 1


# calculating results / вычисление результатов

second_moment = calculate_second_moment(sequence)

m = estimate_second_moment(sequence, 100)
print('0th moment: ', m[0])
print('1st moment: ', m[1])
print('2nd moment: ', second_moment)
print('2nd moment by Alon-Matias-Szegedy from 100: ', m[2])
print('Difference: ', abs(second_moment - m[2]))
print('\n')

m = estimate_second_moment(sequence, 500)
print('0th moment: ', m[0])
print('1st moment: ', m[1])
print('2nd moment: ', second_moment)
print('2nd moment by Alon-Matias-Szegedy from 500: ', m[2])
print('Difference: ', abs(second_moment - m[2]))
