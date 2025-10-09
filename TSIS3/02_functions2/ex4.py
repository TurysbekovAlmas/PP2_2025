"""
Write a function that takes a list of movies and computes the average IMDB score.
"""

def func(movies):
    sum = 0
    for i in movies:
        sum+=i['imdb']
    return round(sum/len(movies),2)


movies = [
    {"name": "Movie1", "imdb": 7.5},
    {"name": "Movie2", "imdb": 8.0},
    {"name": "Movie3", "imdb": 6.5}
]

print(func(movies))