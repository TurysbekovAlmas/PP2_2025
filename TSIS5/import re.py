import re
txt=input()
word=re.findall(r'qp{2,3}', txt)
print(word)