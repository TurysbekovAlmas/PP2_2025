def palindrome(str):
    return str==''.join(reversed(str))
str=input()
p=palindrome(str)
if p is True:
    print("Yes") 
else:
    print("No")
