#Create a Tuple:
thistuple = ("apple", "banana", "cherry")
print(thistuple)
#Tuples allow duplicate values:


#Print the number of items in the tuple:
thistuple = ("apple", "banana", "cherry")
print(len(thistuple))


#One item tuple, remember the comma:
thistuple = ("apple",)
print(type(thistuple))

#NOT a tuple
thistuple = ("apple")
print(type(thistuple))

#Tuple items can be of any data type:


mytuple = ("apple", "banana", "cherry")
print(type(mytuple))


#Using the tuple() method to make a tuple:
thistuple = tuple(("apple", "banana", "cherry")) # note the double round-brackets
print(thistuple)