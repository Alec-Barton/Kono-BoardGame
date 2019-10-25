#-------------------------
#Alec Barton
#Kplayers.py
#-------------------------

import random

#-------------------------
#PLAYER CLASS
#base class for the Human and Computer player classes
#has some functions that are used by both child classes
#-------------------------
class PLAYER:
    #-------------------------
    #CONSTRUCTOR
    #PARAMETERS:
    #team (string) - "B" for black team, "W" for white team
    #-------------------------
    def __init__(self, team = None):
        if team == "B" or team == "W":
            self.team = team
        self.score = 0

    #-------------------------
    #AI
    #the "AI" for the computer player (and help function)
    #determines the best move to do next
    #PARAMETERS:
    #board (board object) - the game board
    #move_num (int) - 1 if this is the first move of the turn, 2 if this is the second move
    #piece ((int, int)) - tuple containing the ending position of the previous move of the player during this turn
    #(this defaults to None if this is the first move of the turn)
    #RETURNS: tuple containing the best move
    #[0] - the calculated weight of the move (this is mostly useful for debugging)
    #[1] - the move itself, stored as ((x and y of original position)(x and y of new postion))
    #[2] - the "logic", a string containin the reason this move was chosen
    #-------------------------
    def AI(self, board, move_num, piece = None):
        #list to contain all potential moves
        moves = []
        #list to contain the moves after they have been weighted
        weighted_move = []

        team = self.get_team()
        logic = None

        #set the "home side" for the team, the side the player is trying to reach
        if team == "B":
            opponent ="W"
            home_side = 0
        elif team == "W":
            opponent = "B"
            home_side = board.dimension - 1

        #if the previous piece moved is None then the list of moves is all valid moves of all pieces on the player's team
        if piece == None:
            for i in range (board.get_dimension()):
                for j in range (board.get_dimension()):
                    #loop through board finding each piece
                    pos1 = (i, j)
                    piece1 = board.get_piece(pos1)
                    #check if the piece belongs to the player
                    if piece1 == team or piece1 == (team + team):
                        pos2 = board.find_valid(pos1)
                        #if that piece has at least one valid move add all its valid moves to the list
                        if len(pos2) > 0:
                            for p in pos2:
                                moves.append((pos1, p))
        #if there was a previous piece moved this turn then potential moves is all valid moves of that one piece
        else:
            pos2 = board.find_valid(piece)
            for p in pos2:
                moves.append((piece, p))


        #cases for if no valid moves are found
        if len(moves) == 0:
            #if the player has not moved yet this turn they cannot end their turn so they must quit
            if move_num == 1:
                return("quit")
            #if the player has the option to end their turn they should do that
            elif move_num == 2:
                return("end")

        #loop through each move, assigning each a weight
        for i in moves:
            #weight starts at 0
            weight = 0
            #assign weights of decreasing values to moves based on what those moves accomplish
            if move_num == 1 and board.get_piece(i[0]) == (team+team) and  (board.get_piece(i[1]) == opponent or board.get_piece(i[1]) == (opponent + opponent)):
                #adds weight if a piece is Captured
                #will only capture a piece if it is the first move
                #this way pieces either stay in their home positions or move back into them on their second move
                weight += 100000
                if logic == None:
                    logic = "capture"
            #add weight if the move moves into a home position
            if self.is_home(i[0],i[1], board) and not abs(home_side - i[1][0]) > abs(home_side - i[0][0]):
                #weight is given dependant on how many points the home position is worth
                weight += (self.is_home(i[0],i[1], board) * 10000)
                if logic == None:
                    logic = "home"
            #add weight if the move moves a piece closer to its "home side"
            if abs(home_side - i[1][0]) < abs(home_side - i[0][0]):
                #additional weight is given the closer to the home side the move is
                weight += (100* (board.dimension-abs(home_side - (i[1][0]))))
                #additional weight is given if the move also blocks an enemy pieces move
                if self.check_block(board, i[1], opponent):
                    weight += 10
                    if logic == None:
                        logic = "block"
                #if a block is not made the piece simply moves foward instead
                else:
                    if logic == None:
                        logic = "foward"
            #doesnt add any weight for backwards moves, only attempts a backwards move if no other options are avaible
            if abs(home_side - i[1][0]) > abs(home_side - i[0][0]):
                #will only move backward if its the first move of the turn
                if move_num == 1:
                    if logic == None:
                        logic = "back"
                #if its the 2nd move end turn instead of moving backward
                elif move_num == 2:
                    if logic == None:
                        logic = "end"
            weighted_move.append((weight, i, logic))
            logic = None
        #sort the list of all moves such that the move with the highest weight(and therefor best) is at the end of the list
        weighted_move.sort()
        #return end if end is the best move
        if weighted_move[len(weighted_move)-1][2] == "end":
            return "end"
        #return the move at the end of the list (the best move)
        return (weighted_move[len(weighted_move)-1])

    #-------------------------
    #IS HOME
    #checks if a move moves a piece into the home position
    #PARAMETERS:
    #position1 ((int, int)) - starting x,y position of the move
    #position2 ((int, int)) - ending x,y position of the move
    #board (board object) - the board
    #RETURNS: score value of the position the move ends on, 0 (false) if it is not a home position
    #-------------------------
    def is_home(self, position1, position2, board):
            #get scoring constants
            scores = board.get_scoring()
            if self.team == "B":
                home = scores[0]
            elif self.team == "W":
                home = scores[1]

            #find score value of position and return it
            index = position2[0] * board.dimension + position2[1]
            if home[index] != 0:
                return home[index]
            else:
                return 0

    #-------------------------
    #CHECK BLOCK
    #checks if a move also blocks an enemy piece
    #PARAMETERS:
    #board (board object) - the board
    #position2 ((int, int)) - ending x,y position of the move
    #opponent (string) - the opponent team
    #RETURNS: true if a block is made, false if not
    #-------------------------
    def check_block(self,board,position2, opponent):
        #find all moves for the opponent
        for i in range (board.get_dimension()):
            for j in range (board.get_dimension()):
                piece1 = board.get_piece((i,j))
                if piece1 == opponent or piece1 == (opponent + opponent):
                    pos2 = board.find_valid((i,j))
                    for p in pos2:
                        #if the moves end position is the same as the end position of an enemy move then a block is made
                        if p == position2:
                            #return true if a block is made
                            return 1
        return 0

    #-------------------------
    #GET SCORE
    #RETURNS: the players score
    #-------------------------
    def get_score(self):
        return self.score
    #-------------------------
    #SET SCORE
    #PARAMETERS:
    #s (int) - value to set score to
    #RETURNS: none
    #-------------------------
    def set_score(self, s):
        self.score = s
    #-------------------------
    #GET TEAM
    #RETURNS: the players team as a string
    #-------------------------
    def get_team(self):
        return self.team
    #-------------------------
    #SET TEAM
    #PARAMETERS:
    #s (string) - string to set team to
    #RETURNS: none
    #-------------------------
    def set_team(self, team):
        self.team = team

#-------------------------
#HUMAN CLASS
#(inheritted from PLAYER class)
#a human controlled player
#-------------------------
class HUMAN(PLAYER):
    #-------------------------
    #HELP
    #gets help for the user using the built in AI function
    #PARAMETERS:
    #board (board object) - game board
    #move_num (int) - 1 if this is the first move of the turn, 2 if this is the second move
    #piece ((int, int)) - tuple containing the ending position of the previous move (defaults to None)
    #RETURNS: a string containing the recommeneded move
    #-------------------------
    def help(self, board, move_num, piece = None):
        #deselect any currently selected pieces
        board.reset_select()
        #gets the best move from the AI
        move = self.AI(board, move_num, piece)

        #convert the move into a string
        if move == "quit":
            text_entry = "You have no moves left, just quit"
        elif move == "end":
            text_entry = "Try ending your turn"
        else:
            logic = move[2]
            position1 = move[1][0]
            position2 = move[1][1]
            if logic == "capture":
                text_entry = "Try capturing a piece (" + str(board.pos_to_grid(position1)) + " to " + str(board.pos_to_grid(position2)) + ")"
            elif logic == "home":
                text_entry = "Try moving to a home position (" + str(board.pos_to_grid(position1)) + " to " + str(board.pos_to_grid(position2)) + ")"
            elif logic == "block":
                text_entry = "Try moving foward and blocking a piece (" + str(board.pos_to_grid(position1)) + " to " + str(board.pos_to_grid(position2)) + ")"
            elif logic == "foward":
                text_entry = "Try moving foward (" + str(board.pos_to_grid(position1)) + " to " + str(board.pos_to_grid(position2)) + ")"
            elif logic == "back":
                text_entry = "Try moving backward (" + str(board.pos_to_grid(position1)) + " to " + str(board.pos_to_grid(position2)) + ")"
            #if a move is suggested, select that move on the board
            if logic != "end":
                board.select(position1, 3)
                board.select(position2, 3)
        #return the text entry
        return text_entry

    #-------------------------
    #GET TYPE
    #RETURNS: a string ("Human") to denote this object is a human player
    #-------------------------
    def get_type(self):
        return "Human"

#-------------------------
#COMPUTER CLASS
#(inheritted from PLAYER class)
#a computer controlled player
#-------------------------
class COMPUTER(PLAYER):
    #-------------------------
    #DO MOVE
    #decides and performs a move for the computer player during it's turn
    #PARAMETERS:
    #board (board object) - the game board
    #screen (pygame display object) - game screen to be drawn on
    #clock (pygame clock object) - clock
    #move_num (int) - 1 if this is the first move of the turn, 2 if this is the second move
    #piece ((int, int)) - tuple containing the ending position of the previous move (defaults to None)
    #RETURNS: none
    #-------------------------
    def do_move(self, board, screen, clock, move_num, piece = None):
        #use AI function to get best move
        turn = self.AI(board, move_num, piece)
        #if the move is quit or end, return that, it will be handled by the function that called do_move
        if turn == "quit" or turn == "end":
            return ((turn, None))
        #otherwise, perform the move
        else:
            move = turn[1]
            logic = turn[2]
            turn = board.move_piece(move[0], move[1], screen, clock)
            #if the move completes the game return "complete" and the reason it was completed
            if turn:
                return("complete", turn)
            #return what the move and the reason so that it can be logged
            return(logic, move)

    #-------------------------
    #GET TYPE
    #RETURNS: a string ("Computer") to denote this object is a computer player
    #-------------------------
    def get_type(self):
        return "Computer"
