import pygame
import random
from queue import PriorityQueue

# Initialize Pygame
pygame.init()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
PINK = (255, 192, 203)
CYAN = (0, 255, 255)

# Game settings
WIDTH = 600
HEIGHT = 400
CELL_SIZE = 20
GRID_WIDTH = WIDTH // CELL_SIZE
GRID_HEIGHT = HEIGHT // CELL_SIZE
FPS = 15  # Increase Pacman's speed

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pygame Pacman with AI")
clock = pygame.time.Clock()

# Game variables
pacman_x = 1
pacman_y = 1
ghosts = [
    {'x': GRID_WIDTH - 2, 'y': GRID_HEIGHT - 2, 'color': RED},
    {'x': 1, 'y': GRID_HEIGHT - 2, 'color': PINK},
    {'x': GRID_WIDTH - 2, 'y': 1, 'color': CYAN}
]
score = 0
lives = 3
level = 1
power_pellets = [(5, 5), (GRID_WIDTH - 6, 5), (5, GRID_HEIGHT - 6), (GRID_WIDTH - 6, GRID_HEIGHT - 6)]
power_pellet_timer = 0

# Initialize the board
board = []
for y in range(GRID_HEIGHT):
    row = []
    for x in range(GRID_WIDTH):
        if x == 0 or x == GRID_WIDTH - 1 or y == 0 or y == GRID_HEIGHT - 1:
            row.append('#')
        elif (x, y) in power_pellets:
            row.append('O')
        else:
            row.append('.')
    board.append(row)

def draw_board():
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if board[y][x] == '#':
                pygame.draw.rect(screen, BLUE, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            elif board[y][x] == '.':
                pygame.draw.circle(screen, WHITE, (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2), 2)
            elif board[y][x] == 'O':
                pygame.draw.circle(screen, WHITE, (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2), 5)

def draw_pacman():
    color = YELLOW if power_pellet_timer == 0 else WHITE
    pygame.draw.circle(screen, color, (pacman_x * CELL_SIZE + CELL_SIZE // 2, pacman_y * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 2)

def draw_ghosts():
    for ghost in ghosts:
        color = BLUE if power_pellet_timer > 0 else ghost['color']
        pygame.draw.circle(screen, color, (ghost['x'] * CELL_SIZE + CELL_SIZE // 2, ghost['y'] * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 2)

def move_pacman(dx, dy):
    global pacman_x, pacman_y, score, power_pellet_timer
    new_x = pacman_x + dx
    new_y = pacman_y + dy
    if board[new_y][new_x] != '#':
        pacman_x = new_x
        pacman_y = new_y
        if board[new_y][new_x] == '.':
            board[new_y][new_x] = ' '
            score += 10
        elif board[new_y][new_x] == 'O':
            board[new_y][new_x] = ' '
            score += 50
            power_pellet_timer = 100  # 10 seconds at 10 FPS

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star(start, goal, board):
    neighbors = [(0,1), (0,-1), (1,0), (-1,0)]
    close_set = set()
    came_from = {}
    gscore = {start:0}
    fscore = {start:heuristic(start, goal)}
    oheap = PriorityQueue()
    oheap.put((fscore[start], start))
    
    while oheap:
        current = oheap.get()[1]
        
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path

        close_set.add(current)

        for i, j in neighbors:
            neighbor = current[0] + i, current[1] + j
            tentative_g_score = gscore[current] + 1
            if 0 <= neighbor[0] < len(board[0]) and 0 <= neighbor[1] < len(board):
                if board[neighbor[1]][neighbor[0]] == '#':
                    continue
            else:
                continue
                
            if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, 0):
                continue
                
            if  tentative_g_score < gscore.get(neighbor, 0) or neighbor not in [i[1]for i in oheap.queue]:
                came_from[neighbor] = current
                gscore[neighbor] = tentative_g_score
                fscore[neighbor] = gscore[neighbor] + heuristic(neighbor, goal)
                oheap.put((fscore[neighbor], neighbor))
                
    return None

def move_ghost(ghost):
    global power_pellet_timer
    start = (ghost['x'], ghost['y'])
    if power_pellet_timer > 0:
        # Run away from Pacman
        goal = (GRID_WIDTH - 1 - pacman_x, GRID_HEIGHT - 1 - pacman_y)
    else:
        # Chase Pacman
        goal = (pacman_x, pacman_y)
    
    path = a_star(start, goal, board)
    if path and len(path) > 1:
        ghost['x'], ghost['y'] = path[1]

def smart_pacman_move():
    global pacman_x, pacman_y
    moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    best_move = None
    best_score = float('-inf')

    for dx, dy in moves:
        new_x = pacman_x + dx
        new_y = pacman_y + dy
        if board[new_y][new_x] != '#':
            score = 0
            if board[new_y][new_x] == '.':
                score += 10
            elif board[new_y][new_x] == 'O':
                score += 50
            
            # Check distance to nearest ghost
            min_ghost_dist = min(abs(new_x - g['x']) + abs(new_y - g['y']) for g in ghosts)
            score += min_ghost_dist * 5  # Prioritize staying away from ghosts
            
            if score > best_score:
                best_score = score
                best_move = (dx, dy)

    if best_move:
        move_pacman(*best_move)

def check_collision():
    global lives, power_pellet_timer, score
    for ghost in ghosts:
        if pacman_x == ghost['x'] and pacman_y == ghost['y']:
            if power_pellet_timer > 0:
                ghost['x'], ghost['y'] = GRID_WIDTH - 2, GRID_HEIGHT - 2
                score += 200
            else:
                lives -= 1
                if lives > 0:
                    return True
                else:
                    return False
    return True

def next_level():
    global level, ghosts, pacman_x, pacman_y, board, power_pellets
    level += 1
    pacman_x, pacman_y = 1, 1
    for ghost in ghosts:
        ghost['x'], ghost['y'] = GRID_WIDTH - 2, GRID_HEIGHT - 2
    if level % 2 == 0 and len(ghosts) < 4:
        ghosts.append({'x': GRID_WIDTH // 2, 'y': GRID_HEIGHT // 2, 'color': (255, 165, 0)})  # Orange ghost
    
    # Reset the board
    board = []
    for y in range(GRID_HEIGHT):
        row = []
        for x in range(GRID_WIDTH):
            if x == 0 or x == GRID_WIDTH - 1 or y == 0 or y == GRID_HEIGHT - 1:
                row.append('#')
            elif (x, y) in power_pellets:
                row.append('O')
            else:
                row.append('.')
        board.append(row)

# Game loop
running = True
ai_control = False
ghost_move_counter = 0  # Counter to reduce ghost speed

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                ai_control = not ai_control

    if ai_control:
        smart_pacman_move()
    else:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            move_pacman(0, -1)
        elif keys[pygame.K_s]:
            move_pacman(0, 1)
        elif keys[pygame.K_a]:
            move_pacman(-1, 0)
        elif keys[pygame.K_d]:
            move_pacman(1, 0)

    ghost_move_counter += 1
    if ghost_move_counter % 2 == 0:  # Ghosts move every other frame
        for ghost in ghosts:
            move_ghost(ghost)

    if not check_collision():
        print("Game Over! You ran out of lives!")
        running = False

    if '.' not in str(board) and 'O' not in str(board):
        print(f"Level {level} completed!")
        next_level()

    screen.fill(BLACK)
    draw_board()
    draw_pacman()
    draw_ghosts()

    # Draw score, lives, and level
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, WHITE)
    ai_text = font.render("AI: " + ("ON" if ai_control else "OFF"), True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (WIDTH - 100, 10))
    screen.blit(level_text, (WIDTH // 2 - 40, 10))
    screen.blit(ai_text, (WIDTH // 2 - 40, HEIGHT - 30))

    pygame.display.flip()

    if power_pellet_timer > 0:
        power_pellet_timer -= 1

    clock.tick(FPS)

pygame.quit()
