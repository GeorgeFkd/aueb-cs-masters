# state = [
#     [206, 243, 61, 34],
#     [171, 11, 93, 31],
#     [16, 200, 91, 108],
#     [150, 3, 194, 51],
# ]
#
# round_key = [
#     [173, 129, 68, 82],
#     [223, 100, 38, 109],
#     [32, 189, 53, 8],
#     [253, 48, 187, 78],
# ]
#
# def add_round_key(s, k):
#     # XOR each byte in the state with the corresponding byte in the round key
#     return [[s[row][col] ^ k[row][col] for col in range(4)] for row in range(4)]
#
# def matrix2bytes(matrix):
#     # Flatten the matrix row by row into a bytes object
#     return bytes(sum(matrix, []))
#
# # Perform AddRoundKey
# result_state = add_round_key(state, round_key)
#
# # Convert to bytes and print as string
# print(matrix2bytes(result_state).decode())

# crypto{r0undk3y}



