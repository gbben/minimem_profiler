import functools
import time
from typing import Callable, Any
import psutil
import logging

from memory_profiler import memory_usage


class MemoryProfiler:
    def __init__(self, log_level: int = logging.INFO):
        """Initialize the memory profiler with custom logging."""
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def profile_function(self, interval: float = 0.1) -> Callable:
        """
        Decorator to profile memory usage of a function.

        Args:
            interval (float): Time interval between memory measurements in seconds
        """

        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> tuple:
                # Get initial memory state
                initial_mem = psutil.Process().memory_info().rss / 1024 / 1024  # MB

                # Profile the function
                start_time = time.time()

                def profile_target():
                    return func(*args, **kwargs)

                # Run the profiling
                result = memory_usage(
                    (profile_target, (), {}),
                    interval=interval,
                    timestamps=True,
                    retval=True,
                )

                # Unpack results
                mem_measurements, timestamps, return_value = (
                    result[:-1],
                    result[0],
                    result[-1],
                )

                # Calculate statistics
                max_mem = max(mem_measurements)
                avg_mem = sum(mem_measurements) / len(mem_measurements)
                mem_diff = max_mem - initial_mem
                duration = time.time() - start_time

                # Log results
                self.logger.info(f"\nMemory Profile for {func.__name__}:")
                self.logger.info(f"{'='*50}")
                self.logger.info(f"Initial memory: {initial_mem:.2f} MB")
                self.logger.info(f"Peak memory: {max_mem:.2f} MB")
                self.logger.info(f"Average memory: {avg_mem:.2f} MB")
                self.logger.info(f"Memory increase: {mem_diff:.2f} MB")
                self.logger.info(f"Duration: {duration:.2f} seconds")

                profile_data = {
                    "initial_mem": initial_mem,
                    "peak_mem": max_mem,
                    "avg_mem": avg_mem,
                    "mem_diff": mem_diff,
                    "duration": duration,
                    "timestamps": timestamps,
                    "measurements": mem_measurements,
                }

                return return_value, profile_data

            return wrapper

        return decorator

    def memory_snapshot(self) -> dict[str, float]:
        """Take a snapshot of current memory usage."""
        process = psutil.Process()
        mem_info = process.memory_info()

        return {
            "rss": mem_info.rss / 1024 / 1024,  # MB
            "vms": mem_info.vms / 1024 / 1024,  # MB
            "percent": process.memory_percent(),
        }

    def profile_block(self, interval: float = 0.1) -> dict[str, Any]:
        """
        Context manager for profiling a block of code.

        Args:
            interval (float): Time interval between measurements in seconds
        """

        class BlockProfiler:
            def __init__(self, interval, logger):
                self.interval = interval
                self.logger = logger
                self.start_mem = None
                self.measurements = []
                self.start_time = None

            def __enter__(self):
                self.start_mem = psutil.Process().memory_info().rss / 1024 / 1024
                self.start_time = time.time()
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                end_time = time.time()
                end_mem = psutil.Process().memory_info().rss / 1024 / 1024
                duration = end_time - self.start_time
                mem_diff = end_mem - self.start_mem

                self.logger.info("\nMemory Profile for code block:")
                self.logger.info(f"{'='*50}")
                self.logger.info(f"Initial memory: {self.start_mem:.2f} MB")
                self.logger.info(f"Final memory: {end_mem:.2f} MB")
                self.logger.info(f"Memory increase: {mem_diff:.2f} MB")
                self.logger.info(f"Duration: {duration:.2f} seconds")

                return {
                    "start_mem": self.start_mem,
                    "end_mem": end_mem,
                    "mem_diff": mem_diff,
                    "duration": duration,
                }

        return BlockProfiler(interval, self.logger)
