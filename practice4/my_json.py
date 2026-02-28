import json

# Python dictionary
data = {
    "name": "Alina",
    "age": 18,
    "city": "Almaty"
}

# Convert to JSON string
json_data = json.dumps(data)
print("JSON string:", json_data)

# Convert back to Python dictionary
python_data = json.loads(json_data)
print("Python dictionary:", python_data)