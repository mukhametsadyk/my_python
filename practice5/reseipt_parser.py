import re

text = "Менде 2 алма, 3 банан бар."


result = re.search(r"\d+", text)
print("search:", result.group()) 


all_numbers = re.findall(r"\d+", text)
print("findall:", all_numbers)  


split_text = re.split(r"\d+", text)
print("split:", split_text) 

sub_text = re.sub(r"\d+", "*", text)
print("sub:", sub_text)  


text = "abc 123 xyz"
print(re.findall(r".bc", text))
print(re.findall(r"\d+", text))
print(re.findall(r"\w{3}", text))