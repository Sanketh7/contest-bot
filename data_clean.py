with open('ppe_data.csv', 'r') as file:
    filedata = file.read()

filedata = filedata.replace("’", "'")
filedata = filedata.replace(' ,', ',')

with open('ppe_data.csv', 'w') as file:
    file.write(filedata)