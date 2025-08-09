def count_sum(till: int) -> int:
    sum = 0
    for i in range(till):
        sum += i

    return sum


if __name__ == "__main__":
    print("Hello, World! This is a test script.")
    print("Sum of numbers till 5 is:", count_sum(5))
    print("Sum of numbers till 10 is:", count_sum(10))
    print("Sum of numbers till 20 is:", count_sum(20))
