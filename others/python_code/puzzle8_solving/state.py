#coding=utf8
import copy

import config

class Puzzle8State(object) :
    EXPAND_UP = 0
    EXPAND_DOWN = 1
    EXPAND_LEFT = 2
    EXPAND_RIGHT = 3
    def __init__(self) :
        self.puzzle_data = None
        self.blank_row = -1
        self.blank_col = -1
        self.history_states = []
        self.having_cost = 0 # the cost from root to current , g(x)
        self.total_cost = 0 # g(x) + h*(x)

    def init_puzzle_data(self , puzzle_data_1d , blank_row , blank_col) :
        '''
        puzzle_data : list , like [1,2,3,4,5,6,7,8] , fill with the 8 blocks row by row except the blank block in the 3 * 3 check
        blank_x , blank_y : int , the blank block position . count from 1 !
        '''
        self.puzzle_data = self._parsing_1d_puzzle_data(puzzle_data_1d , blank_row , blank_col)
        self.blank_row = blank_row
        self.blank_col = blank_col

    def _parsing_1d_puzzle_data(puzzle_data_1d , blank_row , blank_col) :
        '''
        1-d puzzle data to 2-d puzzle data , make it more clearly 
        Note : the return data is independent with the input puzzle_data in the memory .(slice operation has copy the data)
        '''
        assert(len(puzzle_data_1d) == 8)
        row_idx = ( blank_row - 1 ) * 3 + blank_col - 1 
        complete_puzzle = copy.copy(puzzle_data_1d).insert(row_idx , config.BLANK)
        return [ complete_puzzle[row * 3 : (row + 1)* 3] for row in range(3) ]
    
    def _predict_score2target_state(self , target) :
        '''
        h*(x)
        target : Puzzle2State , target puzzle state 
        '''
        equals_rst = [ 1 if self.puzzle_data[row][col] != target.puzzle_data[row][col] else 0 
                       for row in range(3) for col in range(3) ]
        return sum(equals_rst)

    def set_cost4a_star(self , target) :
        '''
        f(x) = g(x) + h*(x)
        '''
        self.total_cost = self.having_cost + self._predict_score2target_state
    
    def add_previous_state2history(self , pre_state) :
        self.history_states.append(pre_state)

    def _build_expand_state(self , expand_type) :
       '''
       According to the expand type to build a puzzle state
       '''
        state = Puzzle2State()
        state.having_cost = self.having_cost + 1 # update root to new state cost 
        state.puzzle_data = copy.deepcopy(self.puzzle_data) 
        if expand_type = Puzzle2State.EXPAND_UP :
            state.blank_row = self.blank_row - 1
            state.blank_col = self.blank_col 
        elif expand_type == Puzzle2State.EXPAND_DOWN :
            state.blank_row = self.blank_row + 1
            state.blank_col = self.blank_col 
        elif expand_type == Puzzle8State.EXPAND_LEFT :
            state.blank_row = self.blank_row
            state.blank_col = self.blank_col -1
        elif expand_type == Puzzle8State.EXPAND_RIGHT :
            state.blank_row = self.blank_row
            state.blank_col = self.blank_col + 1
        # swap original blank element and new blank element
        state.puzzle_data[state.blank_row][state.blank_col] , state.puzzle_data[self.blank_row][self.blank_col] = (
                state.puzzle_data[self.blank_row][self.blank_col] , state.puzzle_data[state.blank_row][state.blank_col] )
        state.add_previous_state2history(self)
        return state

    def expand_states(self) :
        states_lst = []
        # to up
        if self.blank_row > 0  :
            states_lst.append(self._build_expand_state(Puzzle8State.EXPAND_UP))
        # to down
        if self.blank_row < 2 :
            states_lst.append(self._build_expand_state(Puzzle8State.EXPAND_DOWN))
        # to left
        if self.blank_col > 0 :
            states_lst.append(self._build_expand_state(Puzzle8State.EXPAND_LEFT))
        # to right
        if self.blank_col < 2 :
            states_lst.append(self._build_expand_state(Puzzle8State.EXPAND_RIGHT))
        return states_lst

    def print_state(self) :
        node_str_lst = [ str(node) if node != config.BLANK else " " 
                         for row in self.puzzle_data for node in row ]
        lines = [ "{0:^3}{1:^3}{2:^3}".format(*node_str_lst[3*row_id : 3*(row_id+1) ]) for row_id in range(3) ]

