import re
txt=input()
word=re.findall(r'ab{2,3}', txt)
print(word)
