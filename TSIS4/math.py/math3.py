import math
a = int(input("Input number of sides: "))
b = int(input("Input the length of a side: "))
y = a * b**2
m = 4 * math.tan(math.pi / a)
area = y / m
print("The area of the polygon is:", area)