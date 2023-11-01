import numpy as np
import json

WIN_REWARD = 1.0
DRAW_REWARD = 0.7
LOSS_REWARD = 0.0

class NpArrayEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

class QLearner:
    GAME_NUM = 10000

    def __init__(self, alpha=0.7, gamma=0.9, initial_value=0.5, side=None):
        self.side = side
        self.alpha = alpha
        self.gamma = gamma
        # self.q_values = {}
        # f = open('qvalues.json')
        # self.q_values = json.load(f)
        self.history_states = []
        self.initial_value = initial_value

    def set_side(self, side):
        self.side = side
        if self.side == 1:
            f = open('qvalues1.json')
            self.q_values = json.load(f)
        else:
            f = open('qvalues2.json')
            self.q_values = json.load(f)

    # returns Q value of the state
    def Q(self, state):
        if state not in self.q_values:
            # q_val = np.array([[0.05, 0.1, 0.1, 0.1, 0.05],
            #                   [0.1, 0.3, 0.3, 0.3, 0.1],
            #                   [0.1, 0.3, 0.3, 0.3, 0.1],
            #                   [0.1, 0.3, 0.3, 0.3, 0.1],
            #                   [0.05, 0.1, 0.1, 0.1, 0.05]])
            q_val = np.array([[0.1, 0.2, 0.2, 0.2, 0.1],
                              [0.2, 0.4, 0.4, 0.4, 0.2],
                              [0.2, 0.4, 0.6, 0.4, 0.2],
                              [0.2, 0.4, 0.4, 0.4, 0.2],
                              [0.1, 0.2, 0.2, 0.2, 0.1]])
            self.q_values[state] = q_val
        return self.q_values[state]

    def _select_best_move(self, board):
        state = board.encode_state()
        q_values = self.Q(state)
        return self._find_max(q_values, board)

    def _find_max(self, q_values, board):
        # finding the possible moves with the current board state
        possible_moves = []
        for i in range(0, 5):
            for j in range(0, 5):
                if board.is_valid_move(i, j, self.side):
                    possible_moves.append([i, j])
                else:
                    q_values[i][j] = -1.0 #it is already occupied
        if not possible_moves:
            return "PASS"
        else:
            curr_max = -np.inf
            row, col = 0, 0
            for move in possible_moves:
                if q_values[move[0]][move[1]] > curr_max:
                    curr_max = q_values[move[0]][move[1]]
                    row, col = move[0], move[1]
            return row, col

    def move(self, board):
        result = self._select_best_move(board)
        # print(f"Player move: {result}")
        if result == "PASS":
            return "PASS"
        else:
            row, col = result[0], result[1]
            self.history_states.append((board.encode_state(), (row, col)))
            board.move(row, col, self.side)
            return row, col

    def learn(self, board):
        if board.game_result == 0:
            reward = DRAW_REWARD
        elif board.game_result == self.side:
            reward = WIN_REWARD
        else:
            reward = LOSS_REWARD
        self.history_states.reverse()
        max_q_value = -1.0
        for state, move in self.history_states:
            # state, move = hist_state
            q = self.Q(state)
            if max_q_value < 0:
                q[move[0]][move[1]] = reward
            else:
                q[move[0]][move[1]] = q[move[0]][move[1]] * (1 - self.alpha) + self.alpha * self.gamma * max_q_value
            max_q_value = np.max(q)
        self.history_states = []

    def save_QValues(self):
        print(len(self.q_values))
        json_obj = json.dumps(self.q_values, cls=NpArrayEncoder)
        if self.side==1:
            with open("qvalues1.json", "w") as outfile:
                outfile.write(json_obj)
        else:
            with open("qvalues2.json", "w") as outfile:
                outfile.write(json_obj)