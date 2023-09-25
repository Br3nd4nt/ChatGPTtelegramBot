def generateMatrix(n: int):
    c = 0
    top = bottom = left = right = 0
    mat = [[0] * n for _ in range(n)]
    x = y = 0
    state = 0
    while c != n * n:
        # print(c, state, x, y)
        print(x, y)
        c += 1
        if state == 0: # left to right
            mat[y][x + right - left] = c
            x += 1
        elif state == 1: # top to bottom
            mat[y][x + right - left] = c
            y += 1
        elif state == 2: # right to left
            mat[y][x + right - left] = c
            x -= 1
        else:
            mat[y][x + right - left] = c # bottom to top
            y -= 1
        if (c + top + right + bottom + left) % n == 0:
            if state == 0:
                x -= 1
                y += 1
                top += 1
            elif state == 1:
                y -= 1
                x -= 1
                right += 1
            elif state == 2:
                x += 1
                y -= 1
                bottom += 1
            else:
                y += 1
                x += 1
                left += 1
            state = (state + 1) % 4
    return mat

for i in generateMatrix(3):
    print(i)