from datetime import date
import json
# The original dictionary
data = {
    
    date(2024, 7, 3): {'127.1.1.1', '74.225.252.130', '183.82.108.162'},
    date(2024, 7, 2): {'', '127.0.1.1', '74.225.252.130', '49.205.105.64', '127.0.0.1', '127.1.1.1'},
    date(2024, 7, 1): {'', '183.82.108.162', '49.205.104.0', '74.225.252.130', '74.225.252.131', '127.0.0.1'},
    
}

# Calculate the length of each set and store it in a new dictionary
lengths = {k.strftime('%Y-%m-%d'): len(v) for k, v in data.items() if v}
length = 0
# Print the result
for key, value in lengths.items():
    print(f"{key}: {value}")
    length = length +value
print(length)


# Convert the lengths dictionary to JSON
json_lengths = json.dumps(lengths, indent=4)
print(json_lengths)