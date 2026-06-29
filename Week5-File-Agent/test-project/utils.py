def divide_numbers(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def read_file(filename):
    try:
        f = open(filename, 'r')
        content = f.read()
        return content
    except FileNotFoundError:
        raise ValueError(f"File not found: {filename}")

def calculate_average(numbers):
    if len(numbers) == 0:
        raise ValueError("Cannot calculate average of empty list")
    total = 0
    for n in numbers:
        total += n
    return total / len(numbers)

def get_first_element(lst):
    if len(lst) == 0:
        raise IndexError("List is empty")
    return lst[0]

def convert_to_int(value):
    try:
        value = str(value)
        return int(value)
    except ValueError:
        raise ValueError(f"Invalid input: {value}")