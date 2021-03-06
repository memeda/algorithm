#coding=utf8
import copy
import logging
import functools
import config

@functools.total_ordering
class Puzzle8State(object) :
    EXPAND_UP = 0
    EXPAND_DOWN = 1
    EXPAND_LEFT = 2
    EXPAND_RIGHT = 3
    
    @classmethod
    def is_2puzzle_same(cls , state1 , state2) :
        return state1._predict_score2target_state(state2) == 0

    def __init__(self) :
        self.puzzle_data = None
        self.blank_row = 0 # it count from 1 , not 0 ! because it is an interface to outer .
        self.blank_col = 0
        self.history_states = []
        self.history_expand_actions = []
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

    def _parsing_1d_puzzle_data(self , puzzle_data_1d , blank_row , blank_col) :
        '''
        1-d puzzle data to 2-d puzzle data , make it more clearly 
        Note : the return data is independent with the input puzzle_data in the memory .(slice operation has copy the data)
        '''
        assert(len(puzzle_data_1d) == 8)
        row_idx = ( blank_row - 1 ) * 3 + blank_col - 1 
        complete_puzzle = copy.copy(puzzle_data_1d)
        complete_puzzle.insert(row_idx , config.BLANK)
        return [ complete_puzzle[row * 3 : (row + 1)* 3] for row in range(3) ]
    
    def is_same2other_state(self , target) :
        return self._predict_score2target_state(target) == 0

    def _predict_score2target_state(self , target) :
        '''
        h*(x)
        target : Puzzle8State , target puzzle state 
        '''
        equals_rst = [ 1 if self.puzzle_data[row][col] != target.puzzle_data[row][col] else 0 
                       for row in range(3) for col in range(3) ]
        return sum(equals_rst)

    def set_cost4a_star(self , target) :
        '''
        f(x) = g(x) + h*(x)
        '''
        #self.total_cost = self.having_cost +  self.having_cost << self._predict_score2target_state(target)
        #self.total_cost = self._predict_score2target_state(target)
        self.total_cost = self.having_cost +  self._predict_score2target_state(target)
    
    def add_previous_state2history(self , pre_state) :
        self.history_states.append(pre_state)

    def _build_expand_state(self , expand_type) :
        '''
        According to the expand type to build a puzzle state
        '''
        state = Puzzle8State()
        state.having_cost = self.having_cost + 1 # update root to new state cost 
        state.puzzle_data = copy.deepcopy(self.puzzle_data) 
        if expand_type == Puzzle8State.EXPAND_UP :
            state.blank_row = self.blank_row - 1
            state.blank_col = self.blank_col 
        elif expand_type == Puzzle8State.EXPAND_DOWN :
            state.blank_row = self.blank_row + 1
            state.blank_col = self.blank_col 
        elif expand_type == Puzzle8State.EXPAND_LEFT :
            state.blank_row = self.blank_row
            state.blank_col = self.blank_col - 1
        elif expand_type == Puzzle8State.EXPAND_RIGHT :
            state.blank_row = self.blank_row
            state.blank_col = self.blank_col + 1
        else :
            logging.error("invlaid expand type")
        # swap original blank element and new blank element
        state.puzzle_data[state.blank_row-1][state.blank_col-1] , state.puzzle_data[self.blank_row-1][self.blank_col-1] = (
                state.puzzle_data[self.blank_row-1][self.blank_col-1] , state.puzzle_data[state.blank_row-1][state.blank_col-1] )
        state.history_states = copy.copy(self.history_states)
        state.history_expand_actions = copy.copy(self.history_expand_actions)
        state.add_previous_state2history(self)
        state.history_expand_actions.append(expand_type)
        return state
    
    def _clear_redundant_state(self , states) :
        no_redundant_states_lst = []
        for state in states :
            is_redundant = False 
            for history_state in state.history_states :
                if state._predict_score2target_state(history_state) == 0 :
                    is_redundant = True
                    break
            if not is_redundant :
                no_redundant_states_lst.append(state)
        return no_redundant_states_lst
    
    def expand_states(self) :
        states_lst = []
        ## clearly ! blank_row , blank_col count from 1 ! 
        # to up
        if self.blank_row > 1  :
            states_lst.append(self._build_expand_state(Puzzle8State.EXPAND_UP))
        # to down
        if self.blank_row < 3 :
            states_lst.append(self._build_expand_state(Puzzle8State.EXPAND_DOWN))
        # to left
        if self.blank_col > 1 :
            states_lst.append(self._build_expand_state(Puzzle8State.EXPAND_LEFT))
        # to right
        if self.blank_col < 3 :
            states_lst.append(self._build_expand_state(Puzzle8State.EXPAND_RIGHT))
        no_redundant_states = self._clear_redundant_state(states_lst)
        return no_redundant_states
    
    def print_history(self) :
        ## history_states and history_expand_actions has some different !
        ## history_states[0] is the init state ! but history_expand_actions[0] is the first action !
        ## history_states didn't including the current state , but history_expand_actions has the last action .
        ## so actions have been done to fix it ! 
        cnt = 0
        split_line = "-"*10
        act2words = {Puzzle8State.EXPAND_UP : "空格向上" , Puzzle8State.EXPAND_DOWN : "空格向下" , 
                     Puzzle8State.EXPAND_LEFT : "空格向左" , Puzzle8State.EXPAND_RIGHT : "空格向右"}
        print "{split_line}{cnt}{split_line}".format(**locals())
        print "初始状态"
        print self.history_states[0]
        for his_act , his_state in zip(self.history_expand_actions , self.history_states[1:] + [ self ,]) :
            cnt += 1
            print "{split_line}{cnt}{split_line}".format(**locals())
            print act2words.get(his_act , "未知")
            print his_state.__str__()


    def __str__(self) :
        node_str_lst = [ str(node) if node != config.BLANK else " " 
                         for row in self.puzzle_data for node in row ]
        lines = [ "{0:^3}{1:^3}{2:^3}".format(*node_str_lst[3*row_id : 3*(row_id+1) ]) for row_id in range(3) ]
        cost_info = "g(n) = {0} , f(n) = {1}".format(self.having_cost , self.total_cost)
        return "\n".join(lines + [ cost_info , ] )

    def __cmp__(self , other_state) :
        '''
        According to the total state ( that is , f(n) ) to rank the state . 
        Smaller is in front 
        '''
        return cmp(self.total_cost , other_state.total_cost)
    
    def __lt__(self , other_state) :
        '''
        in outer , we use heapq to keep the search ordering desc by f(n)
        In heapq , using `__lt__` to compare the elements , so `__lt__` is needed .
        we using `functools.total_ordering` , so just define `__lt__`  and `__eq__` , all rich comparing is defined !
        '''
        return self.total_cost < other_state.total_cost
    
    def __eq__(self , other_state) :
        return self.total_cost == other_state.total_cost
