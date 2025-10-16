import re 
txt=input()
word=re.findall(r'ab*', txt)
print(word)