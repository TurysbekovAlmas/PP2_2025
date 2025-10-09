"""
Write a function that takes a category name and returns just those movies under that category.
"""

movies = [
    {'name': 'Inception', 'category': 'Sci-Fi'},
    {'name': 'The Godfather', 'category': 'Crime'},
    {'name': 'The Dark Knight', 'category': 'Action'},
    {'name': 'Pulp Fiction', 'category': 'Crime'},
    {'name': 'Interstellar', 'category': 'Sci-Fi'}
]

def score_5_5(genre):
    result = []
    for m in movies:
        if m['category'] == genre:
                result.append(m['name'])
    return result

nameofcategory = input("Enter the name of the category:")
print(score_5_5(nameofcategory))