"""
Write a function that takes a single movie and returns True if its IMDB score is above 5.5
"""

movies = [
    {'name': 'Inception', 'imdb': 8.8},
    {'name': 'The Room', 'imdb': 3.7},
    {'name': 'Interstellar', 'imdb': 8.6},
    {'name': 'The Godfather', 'imdb': 9.2},
    {'name': 'Frozen', 'imdb': 7.5}
]

def score_5_5(movie_name):
    for m in movies:
        if m['name'] == movie_name:
            if m['imdb'] > 5.5:
                return True
    return False

film = input("Enter the name of the movie:")
print(score_5_5(film))