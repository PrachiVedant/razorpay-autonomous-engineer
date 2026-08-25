import sys
import os

# Ensure the current directory containing calculator.py is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from calculator import add


def test_addition():
    assert add(1, 2) == 3
