def string(str):
    u = l = 0
    for i in str:
        if i.isupper():
            u += 1
        elif i.islower():
            l += 1
    return u, l

input = input()
result = string(input)
print(f"upper case: {result[0]}, lower case: {result[1]}")
