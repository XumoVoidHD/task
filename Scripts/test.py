def solve(t, cases):
    results = []
    for n, m in cases:
        if m == 0:
            results.append(n)
        else:
            highest_bit = n
            # Calculate the smallest power of 2 that is greater than or equal to n+1
            while highest_bit & (highest_bit + 1) != 0:
                highest_bit |= highest_bit >> 1
            highest_bit += 1
            if m >= 32:  # Since we're working with integers <= 10^9
                results.append(highest_bit - 1)
            else:
                value = n
                for _ in range(m):
                    value |= (value >> 1)
                    value |= (value >> 2)
                    value |= (value >> 4)
                    value |= (value >> 8)
                    value |= (value >> 16)
                results.append(value)
    return results

# Input reading
import sys
input = sys.stdin.read
data = input().split()
t = int(data[0])
cases = [(int(data[i * 2 + 1]), int(data[i * 2 + 2])) for i in range(t)]

# Solve the cases
results = solve(t, cases)

# Output the results
for result in results:
    print(result)
