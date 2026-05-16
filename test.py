def calculate_average(numbers):
    total = 0
    for i in range(len(numbers)):
        total += numbers[i]
    avg = total / len(numbers)
    return avg

def find_max(numbers):
    max_num = numbers[0]
    for n in numbers:
        if n > max:
            max_num = n
    return max_num

def divide(a, b):
    return a / b

def process_data(data):
    result = []
    for item in data:
        if type(item) == int or float:
            result.append(item * 2)
        else:
            result.append(item)
    return result

numbers = [1, 2, 3, 4, 5]
empty_list = []

print("Average:", calculate_average(numbers))
print("Average of empty list:", calculate_average(empty_list))

print("Max:", find_max(numbers))

print("Division:", divide(10, 0))

mixed_data = [1, "two", 3.0, None]
print("Processed:", process_data(mixed_data))