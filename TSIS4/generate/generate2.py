a = int(input("print number: "))
for i in range(a):
    if i % 2 == 0:
        if (a - 2) == i or (a - 1) == i:
            print(i)
            break
        print(i, end=", ")