"""
Write a function that takes a category and computes the average IMDB score.
"""

movies = [
    {'name': 'Movie1', 'category': 'Action', 'imdb': 7.5},
    {'name': 'Movie2', 'category': 'Drama', 'imdb': 8.2},
    {'name': 'Movie3', 'category': 'Action', 'imdb': 6.8},
    {'name': 'Movie4', 'category': 'Comedy', 'imdb': 7.0}
]

def category_computes_average(category):
    sum_category_movie = 0
    result = []
    for m in movies:
        if m['category'] == category:
            result.append(m['name'])
            sum_category_movie += m['imdb']
    return sum_category_movie/len(result)
    
category = input("Enter the name of the category:")
print(category_computes_average(category))