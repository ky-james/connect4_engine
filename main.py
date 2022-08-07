# import statements
import pygame as pg
import numpy as np
import math 
import random

# game constants
BG_COLOUR = (0,0,255)
BG_HIGHLIGHT = (93,173,235)
MENU_COLOUR = (19,19,19)
MENU_HIGHLIGHT = (51,51,51)
BLACK = (0,0,0)
RED = (194,59,33)
YELLOW = (255,211,1)
NUM_ROWS = 6
NUM_COLS = 7
PLAYER = 0
AI = 1
EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2
LINE_LENGTH = 4
MENU = True

# graphics constants
SQUARESIZE = 100
RADIUS = int(SQUARESIZE/2 - 5)

# globals 
diff = ["Easy", "Hard"]
sel_diff = 0
diff_colours =  ((0,255,0), (255,0,0))

# game functions 
def gen_board():
    return np.zeros((NUM_ROWS, NUM_COLS))

def play_piece(board, row, col, piece):
    board[row][col] = piece

def valid_spot(board, col):
    return board[NUM_ROWS - 1][col] == 0

def find_valid_row(board, col):
    for row in range(NUM_ROWS):
        if board[row][col] == 0:
            return row

def winning_move(board, piece):
    # horizontal check
    for col in range(NUM_COLS - 3):
        for row in range(NUM_ROWS):
            if board[row][col] == piece and board[row][col + 1] == piece and board[row][col + 2] == piece and board[row][col + 3] == piece:
                return True
    
    # vertical check
    for col in range(NUM_COLS):
        for row in range(NUM_ROWS - 3):
            if board[row][col] == piece and board[row + 1][col] == piece and board[row + 2][col] == piece and board[row + 3][col] == piece:
                return True
    
    # positively sloped diagonal check
    for col in range(NUM_COLS - 3):
        for row in range(NUM_ROWS - 3):
            if board[row][col] == piece and board[row + 1][col + 1] == piece and board[row + 2][col + 2] == piece and board[row + 3][col + 3] == piece:
                return True

    # negatively sloped diagonal check
    for col in range(NUM_COLS - 3):
        for row in range(3, NUM_ROWS):
            if board[row][col] == piece and board[row - 1][col + 1] == piece and board[row - 2][col + 2] == piece and board[row - 3][col + 3] == piece:
                return True

def eval(screen, piece):
    eval = 0
    opponent_piece = PLAYER_PIECE
    if piece == PLAYER_PIECE:
        opponent_piece = AI_PIECE
    
    if screen.count(piece) == 4:
        eval += 100
    
    elif screen.count(piece) == 3 and screen.count(EMPTY) == 1:
        eval += 5
    
    elif screen.count(piece) == 2 and screen.count(EMPTY) == 2:
        eval += 2

    if screen.count(opponent_piece) ==  3 and screen.count(EMPTY) == 1:
        eval -= 4

    return eval

def eval_board(board, piece):
    board_eval = 0

    # center row 
    center_col = [int(i) for i in list(board[:, NUM_COLS//2])]
    num_center = center_col.count(piece)
    board_eval += num_center * 3

    # cols 
    for col in range(NUM_COLS):
        col_array = [int(i) for i in list(board[:,col])]
        for row in range(NUM_ROWS - 3):
            line = col_array[row: row + LINE_LENGTH]
            board_eval += eval(line, piece)

    # rows
    for row in range(NUM_ROWS):
        row_array = [int(i) for i in list(board[row,:])]
        for col in range(NUM_COLS - 3):
            line = row_array[col: col + LINE_LENGTH]
            board_eval += eval(line, piece)

    # positively slopped diagonal
    for row in range(NUM_ROWS - 3):
        for col in range(NUM_COLS - 3):
            line = [board[row + i][col + i] for i in range(LINE_LENGTH)]
            board_eval += eval(line, piece)
    
    # negatively slopped diagonal
    for row in range(NUM_ROWS - 3):
        for col in range(NUM_COLS - 3):
            line = [board[row + 3 - i][col + i] for i in range(LINE_LENGTH)]
            board_eval += eval(line, piece)
    
    return board_eval

def get_valid_spots(board):
    valid_spots = []
    for col in range(NUM_COLS):
        if valid_spot(board, col):
            valid_spots.append(col)

    return valid_spots

# algorithm functions
def is_node_terminal(board):
    return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_spots(board)) == 0

def minmax(board, depth, alpha, beta, player):
    valid_spots = get_valid_spots(board)
    is_terminal = is_node_terminal(board)

    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE):
                return (None, 1000000)
            elif winning_move(board,PLAYER_PIECE):
                return (None, -100000)
            else:
                return (None, 0)
        
        else:
            return (None, eval_board(board, AI_PIECE))
    
    if player:
        value = -100000000
        column = random.choice(valid_spots)
        for col in valid_spots:
            row = find_valid_row(board, col)
            board_copy = board.copy()
            play_piece(board_copy, row, col, AI_PIECE)
            new_score = minmax(board_copy, depth-1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value

    else:
        value = 100000000
        column = random.choice(valid_spots)
        for col in valid_spots:
            row = find_valid_row(board, col)
            board_copy = board.copy()
            play_piece(board_copy, row, col, PLAYER_PIECE)
            new_score = minmax(board_copy, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        
        return column, value

def best_move(board, piece):
    valid_spots = get_valid_spots(board)
    best_score = -100000
    best_col = random.choice(valid_spots)
    for col in valid_spots:
        row = find_valid_row(board, col)
        b_copy = board.copy()
        play_piece(b_copy, row, col, piece)
        score = eval_board(b_copy, piece)
        if score > best_score:
            best_score = score
            best_col = col
    return best_col

# graphics functions 
def draw_board(board):
	for c in range(NUM_COLS):
		for r in range(NUM_ROWS):
			pg.draw.rect(screen, BG_COLOUR, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
			pg.draw.circle(screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)
	
	for c in range(NUM_COLS):
		for r in range(NUM_ROWS):		
			if board[r][c] == PLAYER_PIECE:
				pg.draw.circle(screen, RED, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
			elif board[r][c] == AI_PIECE: 
				pg.draw.circle(screen, YELLOW, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
	pg.display.update()

def draw_menu(window, font):
    title_text = font.render('Connect 4!' , True, MENU_COLOUR)
    window.blit(title_text, (160, 50))

def draw_menu_buttons(window, font):
    pg.draw.rect(window, BG_HIGHLIGHT, [50, 225, 600, 175])
    pg.draw.rect(window, BG_HIGHLIGHT, [50, 500, 600, 175])

    b1_coors = (50, 225, 650, 400)
    b2_coors = (50, 500, 650, 675)

    pg.draw.line(window, (MENU_HIGHLIGHT), (b1_coors[0], b1_coors[1]), (b1_coors[2], b1_coors[1]), 5)
    pg.draw.line(window, (MENU_HIGHLIGHT), (b1_coors[0], b1_coors[3]), (b1_coors[2], b1_coors[3]), 5)
    pg.draw.line(window, (MENU_HIGHLIGHT), (b1_coors[0], b1_coors[1]), (b1_coors[0], b1_coors[3]), 5)
    pg.draw.line(window, (MENU_HIGHLIGHT), (b1_coors[2], b1_coors[1]), (b1_coors[2], b1_coors[3]), 5)

    pg.draw.line(window, (MENU_HIGHLIGHT), (b2_coors[0], b2_coors[1]), (b2_coors[2], b2_coors[1]), 5)
    pg.draw.line(window, (MENU_HIGHLIGHT), (b2_coors[0], b2_coors[3]), (b2_coors[2], b2_coors[3]), 5)
    pg.draw.line(window, (MENU_HIGHLIGHT), (b2_coors[0], b2_coors[1]), (b2_coors[0], b2_coors[3]), 5)
    pg.draw.line(window, (MENU_HIGHLIGHT), (b2_coors[2], b2_coors[1]), (b2_coors[2], b2_coors[3]), 5)

    button1_sel_text = font.render('Click to Select Difficulty', True, MENU_COLOUR)
    button1_diff_text = font.render(diff[sel_diff], True, diff_colours[sel_diff])

    button2_text = font.render('Start Game!', True, MENU_COLOUR)

    window.blit(button1_sel_text, (115, 235))
    window.blit(button1_diff_text, (300, 320))
    window.blit(button2_text, (235, 560))

# setting up graphics
board = gen_board()
game_over = False
pg.init()
width = NUM_COLS * SQUARESIZE
height = (NUM_ROWS+1) * SQUARESIZE
size = (width, height)
screen = pg.display.set_mode(size)
screen.fill(BG_COLOUR)
pg.display.set_caption('Programmed with <3 by Ky James')
myfont = pg.font.SysFont("Comic Sans Ms", 40)
menu_font = pg.font.SysFont('Comic Sans Ms', 80)
button_font = pg.font.SysFont('Comic Sans Ms', 40)
turn = random.randint(PLAYER, AI)

# main line 
while True:

    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
        
        if MENU:
            draw_menu(screen, menu_font)
            draw_menu_buttons(screen, button_font)
            pg.display.update()

            if event.type == pg.MOUSEBUTTONDOWN:
                coordinates = pg.mouse.get_pos()
                x, y = coordinates[0], coordinates[1]

                if x < 800 and x > 50:

                    # clicks difficulty selector
                    if y < 400 and y > 225 and x < 650 and x > 50:
                        sel_diff += 1
                        if sel_diff > 1:
                            sel_diff = 0
                                                
                    elif y < 675 and y > 500 and x < 650 and x > 50:
                        screen.fill(BLACK)
                        game_over = False
                        MENU = False
                        break

        else:
            draw_board(board)
            pg.display.update()

            if event.type == pg.MOUSEMOTION and not game_over:
                pg.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
                posx = event.pos[0]
                if turn == PLAYER:
                    pg.draw.circle(screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)

            if event.type == pg.MOUSEBUTTONDOWN:
                posx = event.pos[0]
                posy = event.pos[1]

                if not game_over:
                    pg.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
                    # Ask for Player 1 Input
                    if turn == PLAYER:
                        col = int(math.floor(posx/SQUARESIZE))

                        if valid_spot(board, col):
                            row = find_valid_row(board, col)
                            play_piece(board, row, col, PLAYER_PIECE)

                            if winning_move(board, PLAYER_PIECE):
                                label = myfont.render("You Won!!", 1, RED)
                                play_again = myfont.render('Return to Menu', 1, diff_colours[0])
                                screen.blit(label, (40,20))
                                screen.blit(play_again, (375, 20))
                                game_over = True

                            turn += 1
                            turn = turn % 2
                            draw_board(board)

            # # Ask for Player 2 Input
            if turn == AI and not game_over:				

                if sel_diff == 0:
                    col, minimax_score = minmax(board, 3, -math.inf, math.inf, True)

                    if valid_spot(board, col):
                        row = find_valid_row(board, col)
                        play_piece(board, row, col, AI_PIECE)

                        if winning_move(board, AI_PIECE):
                            label = myfont.render("You Suck loll!!", 1, YELLOW)
                            play_again = myfont.render('Back to Menu', 1, diff_colours[0])
                            screen.blit(label, (40,18))
                            screen.blit(play_again, (410, 18))
                            game_over = True

                        draw_board(board)
                        turn += 1
                        turn = turn % 2

                elif sel_diff == 1:
                    col, minimax_score = minmax(board, 5, -math.inf, math.inf, True)

                    if valid_spot(board, col):
                        row = find_valid_row(board, col)
                        play_piece(board, row, col, AI_PIECE)

                        if winning_move(board, AI_PIECE):
                            label = myfont.render("You Suck loll!!", 1, YELLOW)
                            play_again = myfont.render('Back to Menu', 1, diff_colours[0])
                            screen.blit(label, (40,18))
                            screen.blit(play_again, (410, 18))
                            game_over = True

                        draw_board(board)

                        turn += 1
                        turn = turn % 2
            
            if game_over:
                if event.type == pg.MOUSEBUTTONDOWN:
                    posx = event.pos[0]
                    posy = event.pos[1]
                    if posx > 412 and posy < 98:
                        screen.fill(BG_COLOUR)
                        MENU = True
                        board = np.zeros((6,7))