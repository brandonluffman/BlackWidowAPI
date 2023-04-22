text = ""
with open('categories.txt', 'r') as ifile:
    text = ifile.read()

# get all sepearte string split by space
data = text.split("\n")

# add quotes to each one
data = [f"\"{name}\"" for name in data]

# append them together with commas inbetween
updated_text = ", ".join(data)

print(updated_text)