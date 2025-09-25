"""
Based on a list of fruits, you want a new list, 
containing only the fruits with the letter "a" in the name.
Without list comprehension you will have 
to write a for statement with a conditional test inside:
"""
fruits = ["apple", "banana", "cherry", "kiwi", "mango"]
newlist = []

for x in fruits:
  if "a" in x:
    newlist.append(x)

print(newlist)



#With list comprehension you can do all that with only one line of code:
fruits = ["apple", "banana", "cherry", "kiwi", "mango"]

newlist = [x for x in fruits if "a" in x]

print(newlist)


#Syntax
#newlist = [expression for item in iterable if condition == True]


#Only accept items that are not "apple":
newlist = [x for x in fruits if x != "apple"]
#With no if statement:
#newlist = [x for x in fruits]


#You can use the range() function to create an iterable:
newlist = [x for x in range(10)]


#Set the values in the new list to upper case:
newlist = [x.upper() for x in fruits]


#Return "orange" instead of "banana":
newlist = [x if x != "banana" else "orange" for x in fruits]
#The expression in the example above says:
#"Return the item if it is not banana, if it is banana return orange".