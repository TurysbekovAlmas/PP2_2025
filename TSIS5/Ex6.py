import re
txt=input()
x=re.sub(" ", ":" , txt)
y=re.sub(" ", ",", txt)
print(x)
print(y)