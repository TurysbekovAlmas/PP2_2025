thisdict = {
  "brand": "Ford",
  "model": "Mustang",
  "year": 1964, #Dictionaries cannot have two items with the same key:
  "year": 2020
}
print(thisdict)

print(thisdict["brand"])

print(len(thisdict))

print("\n")

thisdict = dict(name = "John", age = 36, country = "Norway")
print(thisdict)