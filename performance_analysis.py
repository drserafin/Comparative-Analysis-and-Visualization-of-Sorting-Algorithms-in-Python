import time
import random
import os
import sys
import pygal

# Increase recursion limit for Quick Sort on sorted/reversed arrays (worst case)
sys.setrecursionlimit(25000)

# =============================================================================
# Pure sorting algorithm implementations (no generators) for accurate timing
# =============================================================================

def bubble_sort(arr):
    n = len(arr)
    for i in range(n - 1):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]

def merge_sort(arr):
    if len(arr) > 1:
        mid = len(arr) // 2
        left = arr[:mid]
        right = arr[mid:]

        merge_sort(left)
        merge_sort(right)

        i = j = k = 0
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                arr[k] = left[i]
                i += 1
            else:
                arr[k] = right[j]
                j += 1
            k += 1

        while i < len(left):
            arr[k] = left[i]
            i += 1
            k += 1

        while j < len(right):
            arr[k] = right[j]
            j += 1
            k += 1

def quick_sort(arr):
    _quick_sort_helper(arr, 0, len(arr) - 1)

def _quick_sort_helper(arr, low, high):
    if low < high:
        pi = _partition(arr, low, high)
        _quick_sort_helper(arr, low, pi - 1)
        _quick_sort_helper(arr, pi + 1, high)

def _partition(arr, low, high):
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        if arr[j] < pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1

def radix_sort(arr):
    if not arr:
        return
    max_val = max(arr)
    exp = 1
    while max_val // exp > 0:
        _counting_sort(arr, exp)
        exp *= 10

def _counting_sort(arr, exp):
    n = len(arr)
    output = [0] * n
    count = [0] * 10

    for i in range(n):
        index = (arr[i] // exp) % 10
        count[index] += 1

    for i in range(1, 10):
        count[i] += count[i - 1]

    i = n - 1
    while i >= 0:
        index = (arr[i] // exp) % 10
        output[count[index] - 1] = arr[i]
        count[index] -= 1
        i -= 1

    for i in range(n):
        arr[i] = output[i]

def linear_search(arr, target):
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return -1

# =============================================================================
# Array generation helpers
# =============================================================================

def generate_array(size, condition):
    if condition == "Random":
        return [random.randint(1, 10000) for _ in range(size)]
    elif condition == "Sorted":
        return list(range(1, size + 1))
    elif condition == "Reversed":
        return list(range(size, 0, -1))

# =============================================================================
# Benchmarking function
# =============================================================================

def benchmark(algo_func, arr, runs=5):
    """Times the algorithm over multiple runs and returns the average time in seconds."""
    times = []
    for _ in range(runs):
        arr_copy = arr.copy()
        start = time.time()
        algo_func(arr_copy)
        end = time.time()
        times.append(end - start)
    return sum(times) / len(times)

def benchmark_linear_search(arr, runs=5):
    """Special benchmark for linear search - searches for a random existing element."""
    times = []
    for _ in range(runs):
        target = random.choice(arr)
        start = time.time()
        linear_search(arr, target)
        end = time.time()
        times.append(end - start)
    return sum(times) / len(times)

# =============================================================================
# Main analysis
# =============================================================================

def run_analysis():
    sizes = [100, 500, 1000, 2000, 5000, 10000]
    conditions = ["Random", "Sorted", "Reversed"]
    algorithms = {
        "Bubble Sort": bubble_sort,
        "Merge Sort": merge_sort,
        "Quick Sort": quick_sort,
        "Radix Sort": radix_sort,
    }

    # results[condition][algo_name] = list of avg times for each size
    results = {}
    for cond in conditions:
        results[cond] = {}
        for algo_name in list(algorithms.keys()) + ["Linear Search"]:
            results[cond][algo_name] = []

    print("=" * 65)
    print("  SORTING ALGORITHM PERFORMANCE ANALYSIS")
    print("  Averaging over 5 runs per configuration")
    print("=" * 65)

    for cond in conditions:
        print(f"\n--- Condition: {cond} ---")
        print(f"{'Algorithm':<16} ", end="")
        for s in sizes:
            print(f"{'n='+str(s):>10}", end="")
        print()
        print("-" * (16 + 10 * len(sizes)))

        for algo_name, algo_func in algorithms.items():
            print(f"{algo_name:<16} ", end="", flush=True)
            for size in sizes:
                arr = generate_array(size, cond)
                avg_time = benchmark(algo_func, arr)
                results[cond][algo_name].append(avg_time)
                print(f"{avg_time:>9.5f}s", end="", flush=True)
            print()

        # Linear Search
        print(f"{'Linear Search':<16} ", end="", flush=True)
        for size in sizes:
            arr = generate_array(size, "Random")
            avg_time = benchmark_linear_search(arr)
            results[cond]["Linear Search"].append(avg_time)
            print(f"{avg_time:>9.5f}s", end="", flush=True)
        print()

    # Save charts
    os.makedirs("charts", exist_ok=True)
    generate_charts(results, sizes, conditions)
    print("\nDone! Charts saved to charts/ folder.")

# =============================================================================
# Chart generation using pygal (SVG output)
# =============================================================================

def generate_charts(results, sizes, conditions):
    style = pygal.style.CleanStyle

    # Chart 1-3: Line chart for each input condition
    for cond in conditions:
        chart = pygal.Line(
            title=f"Sorting Algorithm Performance - {cond} Input",
            x_title="Array Size (n)",
            y_title="Average Time (seconds)",
            x_labels=[str(s) for s in sizes],
            style=style,
            legend_at_bottom=True,
            dots_size=4,
            width=900,
            height=500
        )

        for algo_name, times in results[cond].items():
            chart.add(algo_name, [round(t, 6) for t in times])

        filename = f"charts/performance_{cond.lower()}.svg"
        chart.render_to_file(filename)
        print(f"  Saved: {filename}")

    # Chart 4: Bar chart comparing algorithms across conditions at n=5000
    target_size = 5000
    size_index = sizes.index(target_size)
    algo_names = list(results["Random"].keys())

    chart = pygal.Bar(
        title=f"Algorithm Comparison Across Input Conditions (n={target_size})",
        x_title="Algorithm",
        y_title="Average Time (seconds)",
        x_labels=algo_names,
        style=style,
        legend_at_bottom=True,
        width=900,
        height=500
    )

    for cond in conditions:
        times = [round(results[cond][algo][size_index], 6) for algo in algo_names]
        chart.add(cond, times)

    chart.render_to_file("charts/comparison_bar_chart.svg")
    print("  Saved: charts/comparison_bar_chart.svg")

    # Chart 5: Bar chart showing scaling of each algorithm (Random input only)
    for algo_name in algo_names:
        chart = pygal.Bar(
            title=f"{algo_name} - Scaling Across Array Sizes (Random Input)",
            x_title="Array Size",
            y_title="Average Time (seconds)",
            x_labels=[str(s) for s in sizes],
            style=style,
            show_legend=False,
            width=700,
            height=400
        )
        times = [round(t, 6) for t in results["Random"][algo_name]]
        chart.add(algo_name, times)

        safe_name = algo_name.lower().replace(" ", "_")
        filename = f"charts/scaling_{safe_name}.svg"
        chart.render_to_file(filename)
        print(f"  Saved: {filename}")


if __name__ == "__main__":
    run_analysis()
