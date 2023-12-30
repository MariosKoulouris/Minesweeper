# Import necessary modules
import pygame
import random
from minesweeper_module import Squares
from minesweeper_module import Lines
from minesweeper_module import Numbers
from collections import deque

# Initialize Pygame
pygame.init()
pygame.font.init()

def checkForWin(): # Function to check for a win condition
    # Check if all marked squares are bombs or if all safe squares are revealed
    if set(marked) == set(bombs) or len(safe_squares) == len(revealed_squares):
        # Display the "YOU WIN" message
        win_text = font.render(win, True, WHITE)
        text_win_rect = win_text.get_rect(center=(WIDTH // 2, LENGTH // 2))
        screen.fill(BLACK)
        screen.blit(win_text, text_win_rect)
        pygame.display.update()
        pygame.time.wait(1000)
        pygame.quit()

def display(): # Function to display the game board
    screen.fill(BLACK)
    # Display each square on the board
    for square in squares:
        square.display(screen)
    # Display lines and numbers on the squares
    for line in lines:
        line.display(screen)
    for number in numbers:
        number.display(screen, SQUARE_SIZE)
    pygame.display.update()
    clock.tick(60)

def initialReveal(pos, bombs): # Function to reveal a set of squares at the start of the game
    # Randomly choose the number of squares to reveal
    reveal_size = random.randint(10, min(25, len(squares)))

    # Find the starting square based on the mouse click position
    start_square = None
    for square in squares:
        if square.x // SQUARE_SIZE == pos[0] // SQUARE_SIZE and square.y // SQUARE_SIZE == pos[1] // SQUARE_SIZE:
            start_square = square
            break
    if start_square is None:
        print("No starting square")
        return

    # Remove the start square from the bombs list if it was accidentally selected as a bomb
    if start_square in bombs:
        bombs.remove(start_square)

    # Use a BFS algorithm to reveal connected squares up to the reveal size
    reveal_squares = set()
    queue = deque([start_square])

    while len(reveal_squares) < reveal_size and queue:
        current_square = queue.popleft()
        reveal_squares.add(current_square)

        # Find neighboring squares that are not revealed or bombs
        neighbors = [
            square
            for square in squares
            if (
                abs(square.x - current_square.x) <= SQUARE_SIZE and square.y == current_square.y
            )
            or (
                square.x == current_square.x and abs(
                    square.y - current_square.y) <= SQUARE_SIZE
            )
        ]
        unrevealed_neighbors = [
            neighbor
            for neighbor in neighbors
            if neighbor not in reveal_squares and neighbor not in bombs
        ]

        # Add unrevealed neighbors to the queue for further exploration
        queue.extend(unrevealed_neighbors)

    # Color the revealed squares silver and add them to the revealed_squares list
    for square in reveal_squares:
        square.color = SILVER
    for square in squares:
        if square.color == SILVER:
            revealed_squares.append(square)
    # Check for neighboring bombs on the revealed squares
    checkForMines(revealed_squares)

def placeBombs(): # Function to randomly place bombs on the board
    # Select a random sample of squares to place the bombs
    bombs = random.sample(squares, min(68, len(squares)))
    # Make the bombs red (just for testing)
    #for square in bombs:
       # square.color = RED
    # Return the list of bomb squares
    return bombs

def reveal(pos):  # Function to reveal a square when left-clicked
    # Calculate the row and column of the clicked square
    Scol = pos[0] // SQUARE_SIZE
    Srow = pos[1] // SQUARE_SIZE

    # Get the clicked square object
    clicked_square = squares[Srow * cols + Scol]

    # Return if the square is marked or already revealed
    if clicked_square in marked or clicked_square in revealed_squares:
        return

    # If the clicked square is a bomb, end the game with a "YOU LOST" message
    if clicked_square in bombs:
        clicked_square.color = RED
        clicked_square.display(screen)
        pygame.display.update()
        end_text = font.render(end, True, WHITE)
        text_end_rect = end_text.get_rect(center=(WIDTH // 2, LENGTH // 2))
        pygame.time.wait(500)
        screen.fill(BLACK)
        screen.blit(end_text, text_end_rect)
        pygame.display.update()
        pygame.time.wait(1000)
        pygame.quit()
    else:
        # Reveal the clicked square and its neighbors if it's a zero
        clicked_square.color = SILVER
        revealed_squares.append(clicked_square)
        checkForMines([clicked_square])

        # If the clicked square is a zero, reveal all connected zeros
        if getNumberOfMinesAround(clicked_square) == 0:
            revealConnectedZeros(clicked_square)

def getNumberOfMinesAround(square): # Function to get the number of neighboring bombs around a square

    # Calculate the row and column of the square
    scol = square.x // SQUARE_SIZE
    srow = square.y // SQUARE_SIZE
    count = 0

    # Check the 8 neighboring squares and count the bombs
    for col in range(-1, 2):
        for row in range(-1, 2):
            nscol = scol + col
            nsrow = srow + row
            if 0 <= nscol < cols and 0 <= nsrow < rows:
                neighbor = squares[nsrow * cols + nscol]
                if neighbor in bombs:
                    count += 1

    return count

def revealConnectedZeros(square): # Function to reveal all connected zeros recursively
    radius = 1
    reveal_stack = [square]  # Stack for DFS algorithm

    while reveal_stack:
        current_square = reveal_stack.pop()
        current_square_b_number = getNumberOfMinesAround(current_square)

        # If the current square is a zero, reveal its neighbors and add them to the stack
        if current_square_b_number == 0:
            current_square.color = SILVER
            for neighbor in getNeighbors(current_square):
                if neighbor.color != SILVER:
                    reveal_stack.append(neighbor)
        else:
            # If the current square has neighboring bombs, display the number
            color = [BLUE, GREEN, RED, DARK_BLUE, MAROON, TURQUOISE,
                     BLACK, ORANGE][current_square_b_number - 1]
            current_square.color = SILVER
            number = Numbers(str(current_square_b_number), current_square.x,
                             current_square.y, color, SILVER, numbersFont)
            numbers.append(number)

def checkForZeros(pos): # Function to check for connected zeros and reveal them
    startcol = pos[0] // SQUARE_SIZE
    startrow = pos[1] // SQUARE_SIZE
    radius = 1
    reveal_stack = [(startcol, startrow)]  # Stack for DFS algorithm
    reveal_squares = set()

    while reveal_stack:
        col, row = reveal_stack.pop()
        square = squares[row * cols + col]
        if square in reveal_squares:
            continue

        reveal_squares.add(square)
        square_b_number = 0

        for n_square in getNeighbors(square):
            if n_square in bombs:
                square_b_number += 1

        if square_b_number == 0:
            for neighbor in getNeighbors(square):
                nscol = neighbor.x // SQUARE_SIZE
                nsrow = neighbor.y // SQUARE_SIZE
                if abs(nscol - col) <= radius and abs(nsrow - row) <= radius:
                    reveal_stack.append((nscol, nsrow))

        # If the square has neighboring bombs, display the number
        if square_b_number > 0:
            color = [BLUE, GREEN, RED, DARK_BLUE, MAROON,
                     TURQUOISE, BLACK, ORANGE][square_b_number - 1]
            square.color = SILVER
            number = Numbers(str(square_b_number), square.x,
                             square.y, color, SILVER, numbersFont)
            numbers.append(number)

    # Color all revealed squares as silver
    for square in reveal_squares:
        square.color = SILVER
        if square not in revealed_squares:
            revealed_squares.append(square)

def getNeighbors(square): # Function to get the neighboring squares of a given square
    scol = square.x // SQUARE_SIZE
    srow = square.y // SQUARE_SIZE
    neighbors = []
    for col in range(-1, 2):
        for row in range(-1, 2):
            nscol = scol + col
            nsrow = srow + row
            for n_square in squares:
                ncol = n_square.x // SQUARE_SIZE
                nrow = n_square.y // SQUARE_SIZE
                if nscol == ncol and nsrow == nrow:
                    neighbors.append(n_square)
    return neighbors

def markAsBomb(pos): # Function to mark a square as a bomb with the right mouse button
    Scol = pos[0] // SQUARE_SIZE
    Srow = pos[1] // SQUARE_SIZE
    for square in squares:
        if square.x // SQUARE_SIZE == Scol and square.y // SQUARE_SIZE == Srow:
            # Return if the square is already revealed
            if square in revealed_squares:
                return
            # Add or remove the square from the marked list and display a black line on the marked square
            if square in marked:
                marked.remove(square)
                for line in lines:
                    if line.x // SQUARE_SIZE == pos[0] // SQUARE_SIZE and line.y // SQUARE_SIZE == pos[1] // SQUARE_SIZE:
                        lines.remove(line)
                        return
            marked.append(square)
            line = Lines(BLACK, square.x, square.y,
                         LINE_THICKNESS, SQUARE_SIZE)
            lines.append(line)

def checkForMines(revealed_squares): # Function to check for neighboring bombs on revealed squares and display numbers
    for square in revealed_squares:
        if square in bombs:
            continue  # Skip the square if it's already a bomb
        square_b_number = 0
        scol = square.x // SQUARE_SIZE
        srow = square.y // SQUARE_SIZE
        for col in range(-1, 2):
            for row in range(-1, 2):
                nscol = scol + col
                nsrow = srow + row
                if 0 <= nscol < cols and 0 <= nsrow < rows:
                    n_square = squares[nsrow * cols + nscol]
                    if n_square in revealed_squares:
                        continue  # Skip the square if it's already revealed
                    if n_square in bombs:
                        square_b_number += 1

        # If the square has neighboring bombs, display the number
        if square_b_number == 0:
            color = SILVER
            pos = pygame.mouse.get_pos()
            checkForZeros(pos)
        elif square_b_number == 1:
            color = BLUE
        elif square_b_number == 2:
            color = GREEN
        elif square_b_number == 3:
            color = RED
        elif square_b_number == 4:
            color = DARK_BLUE
        elif square_b_number == 5:
            color = MAROON
        elif square_b_number == 6:
            color = TURQUOISE
        elif square_b_number == 7:
            color = BLACK
        elif square_b_number == 8:
            color = ORANGE

        number = Numbers(str(square_b_number), square.x,
                         square.y, color, SILVER, numbersFont)
        numbers.append(number)

# Load fonts for displaying text
font = pygame.font.Font("MinecraftTen-VGORe.ttf", 80)
numbersFont = pygame.font.Font("MinecraftTen-VGORe.ttf", 15)
end = "YOU LOST"
win = "YOU WIN"

# Set the dimensions of the game window
LENGTH = 600
WIDTH = 600

# Define the size of each square and line thickness
SQUARE_SIZE = 30
LINE_THICKNESS = 5

# Define color constants
BLACK = (0, 0, 0)
TURQUOISE = (48, 213, 200)
WHITE = (255, 255, 255)
MAROON = (0, 153, 0)
DARK_BLUE = (0, 0, 150)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
PINK = (255, 192, 203)
BROWN = (165, 42, 42)
GRAY = (128, 128, 128)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
SKY_BLUE = (135, 206, 235)
LIME_GREEN = (50, 205, 50)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)
DARK_RED = (139, 0, 0)
DARK_GREEN = (0, 200, 0)

# Define the number of rows and columns on the board
rows = 20
cols = 20

# Initialize lists to hold squares, lines, marked squares, revealed squares, safe squares, and numbers
numbers = []
squares = []
lines = []
marked = []
revealed_squares = []
safe_squares = []

# Create the grid of squares for the game board
for i in range(rows):
    for x in range(cols):
        square = Squares(GREEN, x * SQUARE_SIZE, i * SQUARE_SIZE, SQUARE_SIZE)
        squares.append(square)

# Create the game window
screen = pygame.display.set_mode((LENGTH, WIDTH))
pygame.display.set_caption("Minesweeper")
clock = pygame.time.Clock()

# Initialize variables for game state
done = True
square_clicked = False

# Main loop to wait for the initial mouse click to start the game
while not square_clicked:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                posi = pygame.mouse.get_pos()
                bombs = placeBombs()
                initialReveal(posi, bombs)
                for square in squares:
                    if square not in bombs:
                        safe_squares.append(square)
                square_clicked = True
    display()

# Main game loop
while done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # LEFT BUTTON
                pos = pygame.mouse.get_pos()
                reveal(pos)
                checkForWin()
            elif event.button == 3:  # RIGHT BUTTON
                pos = pygame.mouse.get_pos()
                markAsBomb(pos)
                checkForWin()
                event = None
    display()

# Quit the game when the main loop is exited
pygame.quit()