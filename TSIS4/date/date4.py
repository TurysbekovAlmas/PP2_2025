from datetime import datetime


date_str1 = input("Enter the first date (YYYY-MM-DD HH:MM:SS): ")
date_str2 = input("Enter the second date (YYYY-MM-DD HH:MM:SS): ")


date1 = datetime.strptime(date_str1, '%Y-%m-%d %H:%M:%S')
date2 = datetime.strptime(date_str2, '%Y-%m-%d %H:%M:%S')


dif = date2 - date1


seconds_difference = dif.total_seconds()


print(f"The difference between the two dates is {seconds_difference} seconds.")
