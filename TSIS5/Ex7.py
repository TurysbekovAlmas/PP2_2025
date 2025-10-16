import re
def camel(txt):
    def capitals(match):
        return match.group(1).upper()
    return re.sub(r"_([a-zA-Z])",capitals,txt)
camls=camel(input())
print(camls)