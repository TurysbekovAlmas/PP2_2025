import time
import math

def func(num, times):
    timem=times/1000
    time.sleep(timem)
    result=math.sqrt(num)
    return result
num=int(input())
times=int(input())
r=func(num, times)
print(f"Square root of {num} after {times} miliseconds is {r}")