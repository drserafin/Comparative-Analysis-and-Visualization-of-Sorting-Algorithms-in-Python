# TEAM NOTE: This file contains the raw sorting logic for Performance Analysis.
# It does NOT contain the visualization 'yield' steps.

# ==========================================
# 1. BUBBLE SORT
# ==========================================
def bubble_sort(arr):
    """
    Repeatedly swaps adjacent elements if they are in the wrong order.
    
    Complexity:
    - Best Case: O(n) (If array is already sorted)
    - Average/Worst Case: O(n^2) (Nested loops)
    """
    n = len(arr)
    for i in range(n - 1):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr


# ==========================================
# 2. MERGE SORT
# ==========================================
def merge_sort(arr):
    """
    Divide and Conquer: Splits array in half, sorts halves, merges them.
    
    Complexity:
    - All Cases: O(n log n)
    - Space: O(n) (Creates temporary arrays)
    """
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left_half = arr[:mid]
    right_half = arr[mid:]

    merge_sort(left_half)
    merge_sort(right_half)

    i = j = k = 0

    while i < len(left_half) and j < len(right_half):
        if left_half[i] < right_half[j]:
            arr[k] = left_half[i]
            i += 1
        else:
            arr[k] = right_half[j]
            j += 1
        k += 1
    
    while i < len(left_half):
        arr[k] = left_half[i]
        i += 1
        k += 1

    while j < len(right_half):
        arr[k] = right_half[j]
        j += 1
        k += 1

    return arr


# ==========================================
# 3. QUICK SORT (The Pivot Strategy)
# ==========================================
def quick_sort(arr, low, high):
    """
    Selects a 'pivot' element and partitions the array so that
    elements < pivot are on the left, and > pivot are on the right.
    
    Complexity:
    - Best/Average Case: O(n log n)
    - Worst Case: O(n^2) (If pivot is always the smallest/largest element)
    """
    if low < high:
        pi = partition(arr, low, high)

        quick_sort(arr, low, pi - 1)
        quick_sort(arr, pi + 1, high)
    return arr


def partition(arr, low, high):
    pivot = arr[high]  # Choosing the last element as pivot
    i = low - 1        # Pointer for the smaller element

    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]  # Swap

    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


# ==========================================
# 4. RADIX SORT (The Non-Comparative Sort)
# ==========================================
def radix_sort(arr):
    """
    Sorts numbers digit by digit starting from the Least Significant Digit (LSD).
    Uses Counting Sort as a subroutine.
    
    Complexity:
    - Time: O(nk) (where n is array size, k is number of digits)
    - Space: O(n + k)
    """
    max_val = max(arr)
    exp = 1
    
    while max_val // exp > 0:
        counting_sort_by_digit(arr, exp)
        exp *= 10
    return arr


def counting_sort_by_digit(arr, exp):
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


# ==========================================
# TEST RUNNER
# ==========================================
if __name__ == "__main__":
    test_arr = [170, 45, 75, 90, 802, 24, 2, 66]
    
    print("Original Array:", test_arr)

    # 1. Bubble
    arr_bubble = test_arr[:]
    print("Bubble Sort:   ", bubble_sort(arr_bubble))

    # 2. Merge
    arr_merge = test_arr[:]
    print("Merge Sort:    ", merge_sort(arr_merge))

    # 3. Quick
    arr_quick = test_arr[:]
    quick_sort(arr_quick, 0, len(arr_quick) - 1)
    print("Quick Sort:    ", arr_quick)

    # 4. Radix
    arr_radix = test_arr[:]
    print("Radix Sort:    ", radix_sort(arr_radix))
