#Remove "banana":
thislist = ["apple", "banana", "cherry"]
thislist.remove("banana")
print(thislist)
#If there are more than one item with the specified
#value, the remove() method removes the first occurance:


#Remove the second item:
thislist = ["apple", "banana", "cherry"]
thislist.pop(1)
print(thislist)
#If you do not specify the index, the pop() method removes the last item.


#Remove the first item:
thislist = ["apple", "banana", "cherry"]
del thislist[0]
print(thislist)


#Delete the entire list:
thislist = ["apple", "banana", "cherry"]
del thislist


#Clear the list content:
thislist = ["apple", "banana", "cherry"]
thislist.clear()
print(thislist)