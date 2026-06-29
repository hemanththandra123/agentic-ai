import pytest
from utils import (divide_numbers, read_file,
                   calculate_average, get_first_element,
                   convert_to_int)

def test_divide_numbers():
    assert divide_numbers(10, 2) == 5

def test_divide_by_zero():
    with pytest.raises((ValueError, ZeroDivisionError)):
        divide_numbers(10, 0)

def test_read_file_not_found():
    with pytest.raises((ValueError, FileNotFoundError)):
        read_file("nonexistent.txt")

def test_calculate_average():
    assert calculate_average([1, 2, 3, 4, 5]) == 3.0

def test_calculate_average_empty():
    with pytest.raises((ValueError, ZeroDivisionError)):
        calculate_average([])

def test_get_first_element():
    assert get_first_element([1, 2, 3]) == 1

def test_get_first_element_empty():
    with pytest.raises((ValueError, IndexError)):
        get_first_element([])

def test_convert_to_int():
    assert convert_to_int("42") == 42

def test_convert_to_int_invalid():
    with pytest.raises((ValueError, TypeError)):
        convert_to_int("abc")