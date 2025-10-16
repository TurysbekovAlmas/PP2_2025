import re

txt=input()
snake = re.sub(r'(?<!^)(?=[A-Z])', '_', txt).lower()
print(snake)