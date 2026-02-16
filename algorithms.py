import random

# -----------------------------------------------------------------------------
# BUBBLE SORT IMPLEMENTATION
# -----------------------------------------------------------------------------
def bubble_sort(arr):
    n = len(arr)
    for i in range(n - 1):
        for j in range(0, n - i - 1):
            yield arr, [j, j + 1]
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j+ 1], arr[j]
                yield arr, [j, j+1] 
            else:
                 yield arr, [j, j+1]

# -----------------------------------------------------------------------------
# MERGE SORT IMPLEMENTATION
# -----------------------------------------------------------------------------
def merge_sort(arr):
    """Starts the recursive merge sort."""
    yield from merge_sort_recursive(arr, 0, len(arr) - 1)

def merge_sort_recursive(arr, start, end):
    """Recursive helper function."""
    if start < end:
        mid = (start + end) // 2
        yield from merge_sort_recursive(arr, start, mid)
        yield from merge_sort_recursive(arr, mid + 1, end)
        yield from merge(arr, start, mid, end)

def merge(arr, start, mid, end):
    left_part = arr[start:mid + 1]
    right_part = arr[mid + 1:end + 1]

    i = 0
    j = 0
    k = start

    while i < len(left_part) and j < len(right_part):
        yield arr, [start + i, mid + 1 + j]

        if left_part[i] <= right_part[j]:
            arr[k] = left_part[i]
            i += 1
        else:
            arr[k] = right_part[j]
            j += 1
        
        yield arr, [k]
        k += 1

    while i < len(left_part):
        arr[k] = left_part[i]
        yield arr, [k]
        i += 1
        k += 1

    while j < len(right_part):
        arr[k] = right_part[j]
        yield arr, [k]
        j += 1
        k += 1

# -----------------------------------------------------------------------------
# QUICK SORT IMPLEMENTATION
# -----------------------------------------------------------------------------
def quick_sort(arr):
    """Starts the recursive quick sort."""
    yield from quick_sort_recursive(arr, 0, len(arr) - 1)

def quick_sort_recursive(arr, low, high):
    """Recursive helper function."""
    if low < high:
        pivot_index = yield from partition(arr, low, high)
        yield from quick_sort_recursive(arr, low, pivot_index - 1)
        yield from quick_sort_recursive(arr, pivot_index + 1, high)

def partition(arr, low, high):
    """Partitions the array around a pivot."""
    pivot = arr[high]
    i = low - 1

    for j in range(low, high):
        yield arr, [j, high]
        if arr[j] < pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
            yield arr, [i, j]

    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    yield arr, [i + 1, high]
    return i + 1

# -----------------------------------------------------------------------------
# RADIX SORT IMPLEMENTATION
# -----------------------------------------------------------------------------
def radix_sort(arr):
    """Main entry point for Radix Sort."""
    if not arr:
        return

    max_val = max(arr)
    exp = 1
    while max_val // exp > 0:
        yield from counting_sort_on_digit(arr, exp)
        exp *= 10

def counting_sort_on_digit(arr, exp):
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
        yield arr, [i]

# -----------------------------------------------------------------------------
# LINEAR SEARCH IMPLEMENTATION
# -----------------------------------------------------------------------------
def linear_search_wrapper(arr):
    """Wrapper to pick a random target and start the search."""
    if not arr:
        return
        
    target = random.choice(arr)
    yield from linear_search(arr, target)

def linear_search(arr, target):
    """Iterates through the list until the target is found."""
    for i in range(len(arr)):
        yield arr, [i]
        if arr[i] == target:
            yield arr, [i]
            return