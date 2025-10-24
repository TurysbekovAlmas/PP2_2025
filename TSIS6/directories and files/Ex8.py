import os

file = 'file3.txt'
location = "C:/Users/Almas/Desktop/PP2_2025/TSIS6/directories and files"
path = os.path.join(location, file)
if os.path.exists(path):
    try:
        os.remove(path)
        print("% s removed successfully" % {path})
    except PermissionError:
        print(f"You do not have permission to delete '{path}'")
    except OSError as error:
        print(error)
        print("File path can not be removed")
else:
     print(f"The file '{path}' does not exist")
