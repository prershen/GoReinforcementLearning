import copy
import random
from read import readInput
from write import writeOutput
from host import helper

BOARD_SIZE = 5

def calculate_euler(board, cur_player):
    euler_number=0
    for i in range(0, BOARD_SIZE-1):
        for j in range(0, BOARD_SIZE-1):
            window = [
                board[i][j], board[i][j + 1],
                board[i + 1][j], board[i + 1][j + 1]
            ]
            ones = window.count(cur_player)
            if ones == 1:
                euler_number += 1
            elif ones == 3:
                euler_number -= 1
            elif ones == 2 and window[0] == window[3] and window[1] == window[2]:
                euler_number += 2
    # print("Euler number ", euler_number)
    return euler_number

def heuristic_evaluation(board, cur_player, next_player_of_evaluation):
    no_of_player_pieces = 0
    no_of_opp_pieces = 0
    heuristic_player = 0
    heuristic_opp = 0
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] == player:
                no_of_player_pieces += 1
                heuristic_player += (no_of_player_pieces + helper_obj.find_liberty(board, i, j))
            elif board[i][j] == 3 - player:
                no_of_opp_pieces += 1
                heuristic_opp += (no_of_opp_pieces + helper_obj.find_liberty(board, i, j))
    if cur_player == next_player_of_evaluation:
        return heuristic_player - heuristic_opp
    return heuristic_opp - heuristic_player

def minimizer(alpha, beta, cur_player, next_player, curr_state, prev_state, max_depth):
    best_score = heuristic_evaluation(curr_state, cur_player, next_player)
    if max_depth == 0:
        return best_score
    curr_state2 = copy.deepcopy(curr_state)

    for move in helper_obj.valid_place_check(prev_state, curr_state, next_player):
        next_state = helper_obj.make_move(curr_state, move, next_player)
        curr_score = -1 * maximizer(alpha, beta, cur_player, 3-next_player, next_state, curr_state2, max_depth-1)
        if curr_score > best_score:
            best_score = curr_score
        player = -1 * best_score
        if player < alpha:
            return best_score
        if best_score > beta:
            beta = best_score

    return best_score
    
def maximizer(alpha, beta, cur_player, next_player, curr_state, prev_state, max_depth):
    best_score = heuristic_evaluation(curr_state, cur_player, next_player)
    if max_depth == 0:
        return best_score
    curr_state2 = copy.deepcopy(curr_state)

    for move in helper_obj.valid_place_check(prev_state, curr_state, next_player):
        next_state = helper_obj.make_move(curr_state, move, next_player)
        curr_score = -1 * minimizer(alpha, beta, cur_player, 3-next_player, next_state, curr_state2, max_depth-1)
        if curr_score > best_score:
            best_score = curr_score
        player = -1 * best_score
        if player < beta:
            return best_score
        if best_score > alpha:
            alpha = best_score
    
    return best_score


def minimax(alpha, beta, player, curr_state, prev_state, max_depth):
    moves = list()
    best_score = 0
    curr_state2 = copy.deepcopy(curr_state)

    for move in helper_obj.valid_place_check(prev_state, curr_state, player):
        next_state = helper_obj.make_move(curr_state, move, player)
        score = -1 * minimizer(alpha, beta, player, 3-player, next_state, curr_state2, max_depth)
        if score > best_score or not moves:
            best_score = score
            alpha = best_score
            moves = [move]
        elif score == best_score:
            moves.append(move)
    return moves

if __name__ == "__main__":
    player, previous_board, current_board = readInput(BOARD_SIZE)
    helper_obj = helper()
    filled=0
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if current_board[i][j] != 0:
                filled += 1
    if (filled==0 and player==1) or (filled==1 and player==2 and current_board[2][2]==0):
        possible_actions = [(2,2)]
    else:
        possible_actions = minimax(-1000, -1000, player, current_board, previous_board, 2)

    if possible_actions == []:
        action = ['PASS']
    else:
        # if multiple actions with same score, then pick any one
        action = random.choice(possible_actions)
    print(action)
    writeOutput(action)