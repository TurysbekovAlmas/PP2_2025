thisset = {"apple", "banana", "cherry"}
print(thisset)
"""
Set Items
Set items are unordered, unchangeable, and do not allow duplicate values.

Unordered
Unordered means that the items in a set do not have a defined order.

Set items can appear in a different order every time you use them, 
and cannot be referred to by index or key.

Unchangeable
Set items are unchangeable, meaning that we cannot change the items 
after the set has been created.
"""


#Duplicate values will be ignored:
thisset = {"apple", "banana", "cherry", "apple"}

print(thisset)


#True and 1 is considered the same value:
thisset = {"apple", "banana", "cherry", True, 1, 2}

print(thisset)
#False and 0 is considered the same value:


#Get the number of items in a set:
thisset = {"apple", "banana", "cherry"}

print(len(thisset))