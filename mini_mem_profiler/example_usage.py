from mini_mem_profiler.mini_profiler import MemoryProfiler

profiler = MemoryProfiler()


# * As a function decorator
@profiler.profile_function(interval=0.1)
def memory_intensive_function():
    large_list = [i**2 for i in range(1000000)]
    return sum(large_list)


# Run the function and get results
result, profile_data = memory_intensive_function()

# * As a context manager
with profiler.profile_block() as block:
    large_dict = {i: i**2 for i in range(100000)}

# * taking a snapshot
snapshot = profiler.memory_snapshot()
print(f"Current memory usage: {snapshot['rss']:.2f} MB")
