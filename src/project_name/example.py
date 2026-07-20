"""Example module demonstrating the src/ layout.

Replace this module with your project's own code.
"""


def mean(values: list[float]) -> float:
    """Return the arithmetic mean of a non-empty list of numbers."""
    if not values:
        raise ValueError("values must not be empty")
    return sum(values) / len(values)
