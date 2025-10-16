import re
txt=input()
word=re.findall('^a.*b$', txt)
print(word)