
import re

def split_at_uppercase(text):
    words = re.findall('[A-Z][^A-Z]*', text)
    return words


text = input()
result = split_at_uppercase(text)
print(result)