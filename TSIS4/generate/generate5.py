n = int(input("print num: "))
def countdown_generator(n):
    for i in range(n, -1, -1):
        yield i

for num in countdown_generator(n):
    print(num) 