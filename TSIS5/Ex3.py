import re 
 
txt=input()
word=re.findall(r'\b[A-Za-z]+(?:_[A-Za-z]+)+\b', txt)
print(word)