import re

txt =input()
names = re.findall (r'\b[A-Z][a-z]{3,}\b',txt)
print(names)