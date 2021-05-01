import vk_api
import psycopg2
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import matplotlib.pyplot as plt
import sys
import pandas as pd

removing_characters = ["(", ")", "[", "]", "«", "»", "&", "!", "\""]
forbidden_substrings = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "/", "club", "\\", ";", "#", "@", "https"]


def clear_word(word):
    for character in removing_characters:
        word = word.replace(character, '')
    return word


def check_word(word):
    if len(word) == 0 or not word.isalpha():
        return False
    for substring in forbidden_substrings:
        if substring in word:
            return False
    return True


def get_words(text):
    text = text.replace("\n", " ").replace(",", "").replace(".", "").replace("?", "").replace("!", "").lower()
    nltk.download('stopwords')
    nltk.download('punkt')
    eng_stop_words = set(stopwords.words('english'))
    ru_stop_words = set(stopwords.words('russian'))
    word_tokens = word_tokenize(text)
    words = []
    for w in word_tokens:
        if w not in eng_stop_words and w not in ru_stop_words:
            words.append(w)
    # words = text.split()
    words.sort()
    return words


def count_number_of_words(words):
    key_words = []
    words_dict = dict()
    for word in words:
        if check_word(word):
            key_words.append(clear_word(word))
    for word in key_words:
        if word in words_dict:
            words_dict[word] += 1
        else:
            words_dict[word] = 1
    return words_dict


vk_session = vk_api.VkApi(token='e7f3bb958665e4bc3475554f09bea284e4aea68176eac663326f5daa54bfcdf984542f99bf7f6ade44e65')
api = vk_session.get_api()
tools = vk_api.VkTools(vk_session)
# wall = tools.get_all('wall.get', 100, {'owner_id': })
# walls = api.wall.get(domain='itis_kfu', count=100)
# print(walls['items'][0]['text'])
walls = []
for i in range(100):
    walls.append(api.wall.get(domain='itis_kfu', count=100, offset=i))
resultText = ""
for wall in walls:
    for item in wall['items']:
        if 'title' in item:
            resultText += item['title']
            resultText += ' '
        resultText += item['text']
words_dictionary = count_number_of_words(get_words(resultText))
words_dictionary = dict(sorted(words_dictionary.items(), key=lambda dict_item: dict_item[1]))

plt.rcParams["figure.figsize"] = 15, 10
plt.title('Words statistics')
words_top = 100
bars = list(words_dictionary.values())[len(words_dictionary) - words_top:]
xticks = list(words_dictionary.keys())[len(words_dictionary) - words_top:]
plt.bar(range(words_top), bars, align='center')
plt.xticks(range(words_top), xticks, rotation='vertical')
plt.tight_layout()
plt.savefig('Top-100 words.png')
# plt.show()

connection = psycopg2.connect(
    database='',
    user='postgres',
    password='aws48916011',
    host='dm-rg-database.cvjyc3nfgos9.us-east-1.rds.amazonaws.com',
    port='5432',
)
create_table_query = """
CREATE TABLE IF NOT EXISTS vk_words (
  word TEXT PRIMARY KEY ,
  count BIGINT
);
"""
connection.autocommit = True
cursor = connection.cursor()
cursor.execute(create_table_query)
w = []
for dict_word in words_dictionary:
    w.append((dict_word.ljust(20).strip(), words_dictionary[dict_word]))
words_records = ", ".join(["%s"] * len(w))
insert_query = (
    f"INSERT INTO vk_words (word, count) VALUES {words_records}"
)
connection.autocommit = True
cursor = connection.cursor()
cursor.execute(insert_query, w)
connection.commit()
connection.close()
