def true(t):
    result=all(t)
    return result
t1=(true, true, true)
t2=(1, 0, 1)
print(true(t1))
print(true(t2))