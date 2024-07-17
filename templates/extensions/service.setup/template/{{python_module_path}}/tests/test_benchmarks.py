# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import asyncio

from omni.kit.test import AsyncTestCase, BenchmarkTestCase


class TestBenchmarks(BenchmarkTestCase):
    """
    Example Benchmark class with custom metrics.
    * To use custom metrics one has to derive from  `BenchmarkTestCase`.
    * Benchmark methods have to start with the 'benchmark' prefix.
    * The runtime of the benchmark methods and their skip state
      belong to the default metrics which are always reported.
    """

    def setUp(self):
        pass

    async def benchmark_sleepy_with_custom_metrics(self):
        """
        Benchmark method using custom metrics.
        """
        # sample for custom metric 'sleep_time' is set to 0.1s
        self.set_metric_sample(name="sleep_time", value=0.1, unit="s")
        await asyncio.sleep(0.1)
        # sample for custom metric 'runs' is set to 1
        self.set_metric_sample(name="runs", value=1)

    async def benchmark_sleepy_with_custom_metrics_array(self):
        """
        Another benchmark method using custom metrics to demonstrate setting arrays for a metric, and to show that
        there's no crosstalk of metrics between benchmarks.
        """
        # array of samples for custom metric 'my_other_metric' is set to [1.2ms, 0.9ms, 1.1ms]
        self.set_metric_sample_array(name="my_other_metric", values=[1.2, 0.9, 1.1], unit="ms")
        await asyncio.sleep(0.01)


class TestBenchmarksNoCustomMetric(AsyncTestCase):
    """
    Example Benchmark class without custom metrics.
    * If you are not planning to use custom metrics you can derive from `AsyncTestCase`.
    * Benchmark methods have to start with the 'benchmark' prefix.
    * The runtime of the benchmark methods and their skip state
      belong to the default metrics which are always reported.
    """

    def setUp(self):
        pass

    async def benchmark_sleepy_no_custom(self):
        await asyncio.sleep(0.1)
