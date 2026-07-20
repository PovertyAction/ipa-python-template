"""Tests for project_name.example."""

import pytest

from project_name.example import mean


def test_mean():
    assert mean([1.0, 2.0, 3.0]) == 2.0


def test_mean_empty_raises():
    with pytest.raises(ValueError, match="must not be empty"):
        mean([])
