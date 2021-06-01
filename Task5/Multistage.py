import pandas as pd
import collections
from collections import Counter
import itertools

data_set = pd.read_csv("market_basket.csv")
data_set.head(len(data_set))

test_data_set = data_set['shrimp']

test_data_set.append(data_set['almonds'])
test_data_set.append(data_set['avocado'])
test_data_set.append(data_set['vegetables mix'])
unique_data = data_set['shrimp'].append(data_set['almonds']).append(data_set['avocado']).append(
    data_set['vegetables mix']).append(
    data_set['green grapes']).append(data_set['whole weat flour']).append(data_set['yams']).append(
    data_set['cottage cheese']).append(
    data_set['energy drink']).append(data_set['tomato juice']).append(data_set['low fat yogurt']).append(
    data_set['green tea']).append(
    data_set['honey']).append(data_set['salad']).append(data_set['mineral water']).append(data_set['salmon']).append(
    data_set['antioxydant juice']).append(data_set['frozen smoothie']).append(data_set['spinach']).append(
    data_set['olive oil']).unique()

list_data_with_nan = data_set.values.tolist()

list_data_no_nan = []
for partData in list_data_with_nan:
    temp = [x for x in partData if str(x) != 'nan']
    list_data_no_nan.append(temp)

prepared_data = list_data_no_nan[:]
for i in range(len(prepared_data)):
    for j in range(len(prepared_data[i])):
        for k in range(len(unique_data)):
            if prepared_data[i][j] == unique_data[k]:
                prepared_data[i][j] = k

unpacked_list = [item for sublist in prepared_data for item in sublist]

first_len_count = Counter(unpacked_list).most_common()

bad_numbers = []
for i in first_len_count:
    if i[1] < 30:
        bad_numbers.append(i[0])

list_doubletones = []


def find_subsets(S, m):
    return set(itertools.combinations(S, m))


for i in prepared_data:
    if len(i) > 1:
        temp = list(find_subsets(i, 2))
        list_doubletones.append(temp)
    else:
        list_doubletones.append(i)

bit_map = Counter()


def first_hash(n1, n2=0):
    bit_map[(n1 + n2) % 100] = bit_map[(n1 + n2) % 100] + 1


def second_hash(n1, n2=0):
    if (n1 + n2) % 100 not in bit_map.values():
        bit_map2[(n1 + n2 * 2) % 100] += 1


for i in list_doubletones:
    if len(i) > 1:
        for j in i:
            if len(j) > 1:
                first_hash(j[0], j[1])
            else:
                first_hash(j[0])

temp = bit_map.most_common(44)
bit_map.subtract(temp)

bit_map2 = collections.Counter()

for i in list_doubletones:
    if len(i) > 1:
        for j in i:
            if len(j) > 1:
                second_hash(j[0], j[1])
            else:
                second_hash(j[0])

dispair_answer = []


def clean_bitmap():
    for i in list_doubletones:
        if len(i) > 1:
            for j in i:
                if len(j) > 1:
                    if (j[0] + j[1]) % 100 in bit_map.keys() and (j[0] + j[1] * 2) % 100 in bit_map2.keys() and j[0] \
                            not in bad_numbers and j[1] not in bad_numbers:
                        dispair_answer.append(j)
                else:
                    if (j[0]) % 100 in bit_map.keys() and (j[0]) % 100 in bit_map2.keys() and j[0] not in bad_numbers:
                        dispair_answer.append(j)


clean_bitmap()
result = set(dispair_answer)

for i in result:
    print(unique_data[i[0]] + ", " + unique_data[i[1]])
