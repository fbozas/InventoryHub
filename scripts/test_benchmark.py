"""Offline tests for performance report utilities (not performance measurements)."""
import unittest

from benchmark_api import percentile
from compare_benchmarks import reduction_percentage


class BenchmarkMathTests(unittest.TestCase):
    def test_percentile(self):
        self.assertEqual(percentile([1, 2, 3, 4, 5], 50), 3)
        self.assertEqual(percentile([1, 2, 3, 4, 5], 95), 4.8)

    def test_single_sample(self):
        self.assertEqual(percentile([8], 95), 8)

    def test_empty_samples(self):
        with self.assertRaises(ValueError):
            percentile([], 95)

    def test_reduction(self):
        self.assertEqual(reduction_percentage(20, 15), 25)
        self.assertEqual(reduction_percentage(20, 25), -25)

    def test_zero_baseline(self):
        with self.assertRaises(ValueError):
            reduction_percentage(0, 2)


if __name__ == "__main__":
    unittest.main()
