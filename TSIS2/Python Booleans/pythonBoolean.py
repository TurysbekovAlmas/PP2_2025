print(10 > 9)
print(10 == 9)
print(10 < 9)

print("\n")


a = 200
b = 33

if b > a:
  print("b is greater than a")
else:
  print("b is not greater than a")

print("\n")

print(bool("Hello"))
print(bool(15))

print("\n")

x = "Hello"
y = 15

print(bool(x))
print(bool(y))



"""
The following will return False:

bool(False)
bool(None)
bool(0)
bool("")
bool(())
bool([])
bool({})
"""

print("\n")

x = 200
print(isinstance(x, int))