import os
print(dir(os))
folder = r"C:\Users\poorn\Downloads"
filename = "IDS_ALLCountries_Data - IDS_ALLCountries_Data.csv"
fullpath = os.path.join(folder, filename)
print(fullpath)
print(os.path.exists(fullpath))     # path existance
print(os.path.basename(fullpath))    # just the filename
print(os.path.dirname(fullpath))     #jst the folder
print(os.path.splitext(fullpath))    # (name, extension) tuple
# output --> ('C:\\Users\\poorn\\Downloads\\IDS_ALLCountries_Data - IDS_ALLCountries_Data', '.csv')
#\\ --> thats how python displays a single string when printed inside a tuple.4
items = os.listdir(folder) #gives list of everything in the folder
print(len(items))   # ['file1.csv', 'file2.pdf', 'SomeFolder', ...]
print(os.path.isfile(fullpath))   # True, since your CSV is a file
print(os.path.isdir(folder))      # True, since Downloads is a folder
for item in items: 
    full_item_path = os.path.join(folder, item)
    if os.path.isfile(full_item_path):
        print(item)

groups = {}
for item in items:
    full_item_path = os.path.join(folder, item)
    if os.path.isfile(full_item_path):
        name, ext = os.path.splitext(item)
        if ext not in groups:
            groups[ext] = []
        groups[ext].append(item)
print(groups)
print(os.getcwd()) # --> prints the current working directory
# prints --> PS C:\Users\poorn\Learning\Project\internation_debt_analysis> 
os.chdir(r'C:\Users\poorn\Learning')
print(os.getcwd())
print(os.listdir()) # --> list the folders in the current working directory
groups = {}
for item in items:
    full_item_path = os.path.join(folder, item)
    if os.path.isfile(full_item_path):
        name, ext = os.path.splitext(item)
        if ext not in groups:
            groups[ext] = []
        groups[ext].append(item)
print(groups)

