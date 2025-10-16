import re

text = input()
word = r'(?<!^)(?=[A-Z])'
result = re.sub(word, ' ', text)
print(result)