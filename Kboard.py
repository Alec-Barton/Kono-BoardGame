#-------------------------
#Alec Barton
#Kboard.py
#-------------------------

import math
import random
import os
import pygame
import constants

#-------------------------
#BOARD CLASS
#represents the game board
#includes the logic for the board
#-------------------------
class BOARD:

    #-------------------------
    #CONSTRUCTOR
    #PARAMETERS:
    #dimension (int) - size of the board (number of tiles)
    #-------------------------
    def __init__(self, dimension):
        #set the dimension of the board
        self.dimension = dimension
        #fill the board with blank spaces
        self.board = [[["O", 0] for x in range(self.dimension)] for x in range(self.dimension)]
        #populates the board with the appropriate pieces
        for i in (range(self.dimension)):
            self.board[0][i][0] = "W"
            self.board[self.dimension -1][i][0] = "B"
        self.board[1][0][0] = "W"
        self.board[1][self.dimension-1][0] = "W"
        self.board[self.dimension-2][0][0] = "B"
        self.board[self.dimension-2][self.dimension-1][0] = "B"
        #sets complete to false
        self.complete = 0

    #-------------------------
    #LOAD BOARD
    #loads the game board
    #PARAMETERS:
    #board_list (list) - list of strings containing all of the pieces on the board
    #dimension (int) - size of the board
    #RETURNS: nothing
    #-------------------------
    def load_board(self, board_list, dimension):
        #sets the dimension
        self.dimension = dimension
        index = 0
        #iterates through list of pieces and loads them onto the board
        for i in range(self.dimension):
            for j in range(self.dimension):
                p = board_list[index]
                self.board[i][j][0] = board_list[index]
                index+=1

    #-------------------------
    #SAVE BOARD
    #creates a list of the pieces on the board
    #RETURNS: the list of the pieces on the board
    #-------------------------
    def save_board(self):
        pieces = []
        #collects pieces into a list
        for i in range(self.dimension):
            for j in range(self.dimension):
                pieces.append(self.board[i][j][0])
        return pieces

    #-------------------------
    #DRAW BOARD
    #draws the game board onto the screen
    #PARAMETERS:
    #screen - pygame display object to draw on
    #RETURNS: nothing
    #-------------------------
    def draw (self, screen):
        #resets board area to a blank screen
        screen.fill(constants.GREY, (0,0,constants.BOARD_DIMENSION, constants.BOARD_DIMENSION))
        #loops throught board, drawing each piece
        for i in range(self.dimension):
            for j in range(self.dimension):
                #calculates the pixel size each piece should be
                image_size = int((constants.BOARD_DIMENSION/self.dimension))

                #if the piece is selected, draw the selection color
                if self.board[i][j][1]:
                    #the file name is directly related to the interger stored for the selection type
                    select_name = ("S" + str(self.board[i][j][1]) + ".png")
                    #loads image, scales it and draws it to the board
                    select = pygame.image.load(select_name)
                    select = pygame.transform.scale(select, (image_size, image_size))
                    select.convert()
                    screen.blit(select, ((j*(constants.BOARD_DIMENSION/self.dimension)), (i*(constants.BOARD_DIMENSION/self.dimension))))

                #draws piece to board
                #the file name is directly related to the string stored for the piece
                image_name = self.board[i][j][0] + ".png"
                piece = pygame.image.load(image_name)
                scale = (image_size/(piece.get_rect().size[0]))
                piece = pygame.transform.rotozoom(piece, 0, scale)
                piece.convert()
                screen.blit(piece, ((j*(constants.BOARD_DIMENSION/self.dimension)), (i*(constants.BOARD_DIMENSION/self.dimension))))

        #draws the alphanumeric grid
        tile_size = constants.BOARD_DIMENSION/self.dimension
        basicfont = pygame.font.Font("Kfont.ttf", 10)
        for i in range(self.dimension):
            x_text = basicfont.render(str(i+1), False, constants.BLACK)
            y_text = basicfont.render(chr(65+i), False, constants.BLACK)
            screen.blit(x_text , ((i*tile_size + tile_size/2) - (x_text.get_rect().size[0]/2),  0))
            screen.blit(y_text , (2,  (i*tile_size + tile_size/2)- (x_text.get_rect().size[1]/2)))

    #-------------------------
    #DRAW MINI
    #draws a smaller verson of the board onto the screen
    #PARAMETERS:
    #screen - pygame display object to draw on
    #position ((int, int)) - tuple with the x,y coords to draw the board to
    #size (int) - size in pixels to draw the board
    #RETURNS: nothing
    #-------------------------
    def draw_mini(self, screen, position = (0,0), size = 100):
        #draws the board in the same way as the draw() function but without the alphanumeric grid or selections
        for i in range(self.dimension):
            for j in range(self.dimension):
                image_size = int((size/self.dimension))
                image_name = self.board[i][j][0] + ".png"
                piece = pygame.image.load(image_name)
                scale = (image_size/(piece.get_rect().size[0]))
                piece = pygame.transform.rotozoom(piece, 0, scale)
                piece.convert()
                screen.blit(piece, ((j*(size/self.dimension) + position[0]), (i*(size/self.dimension) + position[1])))

    #-------------------------
    #MOVE PIECE
    #moves a piece to a new location if it is a valid move
    #PARAMETERS:
    #position1 ((int, int)) - board position of the piece
    #position1 ((int, int)) - board position of where the piece will be moved to
    #screen - pygame display object to draw on
    #clock - pygame clock object
    #RETURNS: true and reason the game ended if the game is over, false if the game is not over
    #-------------------------
    def move_piece(self, position1, position2, screen, clock):
        #finds valid moves for the starting piece
        valid_moves=self.find_valid(position1)
        #makes sure the attempted move is a valid move
        if position2 in valid_moves:
            #get starting piece
            piece1 = self.get_piece(position1)
            #set original position to empty
            self.set_piece(position1, "O")
            #run the animation of moving a piece
            self.move_animate(position1, position2, screen, piece1, clock)
            #set the new position to the piece
            self.set_piece(position2, piece1)
            #check for super pieces and the end of the game
            self.check_super()
            if self.check_end():
                return(self.check_end())
            else:
                return (0)

    #-------------------------
    #MOVE ANIMATE
    #draws an animation of the piece moving
    #PARAMETERS:
    #position1 ((int, int)) - board position of the piece
    #position1 ((int, int)) - board position of where the piece will be moved to
    #screen - pygame display object to draw on
    #piece1 (string) - piece that is being moved
    #clock - pygame clock object
    #RETURNS: the reason the game ended if the game is over, false if the game is not over
    #-------------------------
    def move_animate(self, position1, position2, screen, piece1, clock):
        coord1 = self.pos_to_coord(position1)
        coord2 = self.pos_to_coord(position2)
        #determines how many pixels the piece moves per frame
        speed_const = 5
        #calculates the total pixel distance the piece must travel
        distance = math.sqrt(2*((constants.BOARD_DIMENSION/self.dimension)**2))

        #calculates the x and y direction the piece will move
        x_sign = 1 if ((coord2[0]-coord1[0]) > 0) else -1
        y_sign = 1 if ((coord2[1]-coord1[1]) > 0) else -1

        #distance the piece has traveled so far
        traveled = 0
        position = coord1
        #run the animation loop
        while traveled < distance :
            clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                     pygame.quit();
            image_size = int((constants.BOARD_DIMENSION/self.dimension))
            file_name = str(piece1) + ".png"
            piece = pygame.image.load(file_name)
            piece = pygame.transform.scale(piece, (image_size, image_size))
            piece.convert()
            position = ((position[0]+(x_sign * speed_const)), (position[1]+(y_sign * speed_const)))
            self.draw(screen)
            #draw the piece at its intermediate position
            screen.blit(piece, position)
            pygame.display.update()
            pygame.time.delay(100)
            #updates the piece to a new intermediate position
            traveled += math.sqrt(2*((speed_const)**2))
        pygame.time.delay(100)

    #-------------------------
    #CHECK MOVE
    #checks if a given move is valid
    #PARAMETERS:
    #position1 ((int, int)) - board position of the piece
    #position1 ((int, int)) - board position of where the piece will be moved to
    #RETURNS: true if the move is valid, false if not
    #-------------------------
    def check_move(self, position1, position2):
        #checks if the move is valid
        moves = self.find_valid(position1)
        if position2 in moves:
            #the move is valid
            return 1
        else:
            #the move is invalid
            return 0

    #-------------------------
    #CHECK VALID (Private Function)
    #used by the find_valid function, checks if piece can be moved to its destination
    #PARAMETERS:
    #position1 ((int, int)) - board position of the piece
    #position1 ((int, int)) - board position of where the piece will be moved to
    #RETURNS: true if the piece can be moved, false if it cannot
    #-------------------------
    def __check_valid(self, position1, position2):
        piece1 = self.get_piece(position1)
        piece2 = self.get_piece(position2)
        #checks if the piece can move to its new position based on what piece is at the new position
        #does not check if the 2nd position is within the moveable range of the starting position
        if piece1 == "B" or piece1 == "BB":
            team = "B"
        else:
            team = "W"
        if piece2 == "O":
            return 1
        else:
            if piece2 == team or piece2 == (team+team):
                return 0
            elif piece1 == (team+team):
                return 1
            else:
                return 0

    #-------------------------
    #FIND VALID
    #finds all valid moves for a piece
    #PARAMETERS:
    #position ((int, int)) - board position of the piece
    #RETURNS: list of all valid moves for the piece
    #-------------------------
    def find_valid(self, position):
        valid_moves = []
        #checks the four diagonal positions that a piece could move to and see which (if any) are valid
        #if the move is valid add it to the list of valid moves
        if(position[0] > 0 and position[1] > 0):
            position2 = (position[0]-1, position[1]-1)
            if(self.__check_valid(position, position2)):
                valid_moves.append(position2)
        if(position[0] < (self.dimension-1) and position[1] >0):
            position2 = (position[0]+1, position[1]-1)
            if(self.__check_valid(position, position2)):
                valid_moves.append(position2)
        if(position[0] > 0 and position[1] < (self.dimension-1)):
            position2 = (position[0]-1, position[1]+1)
            if(self.__check_valid(position, position2)):
                valid_moves.append(position2)
        if(position[0] < (self.dimension-1) and position[1] <(self.dimension-1)):
            position2 = (position[0]+1, position[1]+1)
            if(self.__check_valid(position, position2)):
                valid_moves.append(position2)
        #return all the valid moves
        return (valid_moves)

    #-------------------------
    #SELECT
    #highlights a piece on the board
    #PARAMETERS:
    #position ((int, int)) - board position of the piece to highlighted
    #type (int) - number cooresponding to the color of the selection
    #(green - for piece, yellow - for valid moves, blue - for help)
    #RETURNS: nothing
    #-------------------------
    def select(self, position, type):
        #assigns an interger cooresponding to the selection type to the board at the proper position
        self.board[position[0]][position[1]][1]=type

    #-------------------------
    #RESET SELECT
    #de-selects every piece on the board
    #RETURNS: nothing
    #-------------------------
    def reset_select(self):
        #loops through board deselecting each piece
        for i in range (self.dimension):
            for j in range (self.dimension):
                self.board[i][j][1] = 0

    #-------------------------
    #CHECK SUPER
    #checks board and upgrades any eligible pieces to super pieces
    #RETURNS: nothing
    #-------------------------
    def check_super(self):
        #checks each home position, if the proper piece is in a move position upgrade it to a super piece
        for i in (range(self.dimension)):
            if self.board[0][i][0] == "B":
                self.set_piece((0,i), "BB")
            if self.board[self.dimension -1][i][0] == "W":
                self.set_piece((self.dimension -1,i), "WW")

        if self.board[1][0][0] == "B":
            self.set_piece((1,0), "BB")
        if self.board[1][self.dimension-1][0] == "B":
            self.set_piece((1,self.dimension-1), "BB")
        if self.board[self.dimension-2][0][0] == "W":
            self.set_piece((self.dimension-2,0), "WW")
        if self.board[self.dimension-2][self.dimension-1][0] == "W":
            self.set_piece((self.dimension-2,self.dimension-1), "WW")

    #-------------------------
    #CHECK END
    #checks the board to see if the game should end
    #RETURNS: string of reason game ended or false if the game is not over
    #-------------------------
    def check_end(self):
        #number of black and white pieces in a home position
        bpieces = 0
        wpieces = 0
        #total number of black and white pieces, the number each team is trying to reach
        bgoal = 0
        wgoal = 0

        #count number of pieces of each team on the board
        for i in range(self.dimension):
            for j in range(self.dimension):
                if self.board[i][j][0] == "B" or self.board[i][j][0] == "BB":
                    bgoal += 1
                elif self.board[i][j][0] == "W" or  self.board[i][j][0] == "WW":
                    wgoal += 1

        #count all pieces in home postions
        for i in (range(self.dimension)):
            if self.board[0][i][0] == "BB":
                bpieces+=1
            if self.board[self.dimension -1][i][0] == "WW":
                wpieces+=1
        if self.board[1][0][0] == "BB":
            bpieces+=1
        if self.board[1][self.dimension-1][0] == "BB":
            bpieces+=1
        if self.board[self.dimension-2][0][0] == "WW":
            wpieces+=1
        if self.board[self.dimension-2][self.dimension-1][0] == "WW":
            wpieces+=1

        #if there are no black pieces left then white cleared the board
        if bgoal == 0:
            self.complete=1
            return "White cleared the Board"
        #if there are no white pieces left then white cleared the board
        elif wgoal == 0:
            self.complete=1
            return "Black cleared the Board"
        #if the number of black pieces in home positions is equal to the total number of black pieces then black completed the board
        if bpieces >= bgoal:
            self.complete=1
            return "Black completed the Board"
        #if the number of white pieces in home positions is equal to the total number of white pieces then white completed the board
        elif wpieces >= wgoal:
            self.complete=1
            return "White completed the Board"
        #board isnt complete
        else:
            return 0

    #-------------------------
    #GET SCORING
    #get the scoring constants for the given board size
    #RETURNS: tuple containing (black scoring list, white scoring list)
    #-------------------------
    def get_scoring(self):
        #returns the proper constants
        if self.dimension == 5:
            return (constants.SCORE_BLACK_5, constants.SCORE_WHITE_5)
        elif self.dimension == 7:
            return (constants.SCORE_BLACK_7, constants.SCORE_WHITE_7)
        elif self.dimension == 9:
            return (constants.SCORE_BLACK_9, constants.SCORE_WHITE_9)

    #-------------------------
    #SCORE BOARD
    #scores the board
    #RETURNS: tuple containing (black score, white score)
    #-------------------------
    def score_board(self):
        board_pieces = []
        blackscore = 0
        whitescore = 0
        #number of black and white pieces
        B = 0
        W = 0
        #gets lists with the score values of each position for each team
        scores = self.get_scoring()
        bvalues = scores[0]
        wvalues = scores[1]

        #put all pieces on the board into a list
        for i in range(self.dimension):
            for j in range(self.dimension):
                board_pieces.append(self.board[i][j][0])

        #award the point value of each position to correct team
        for i in range (len(board_pieces)):
            if board_pieces[i] == "B" or board_pieces[i] =="BB":
                blackscore += bvalues[i]
                B += 1
            if board_pieces[i] == "W" or board_pieces[i] =="WW":
                whitescore += wvalues[i]
                W += 1

        #award points for each captured piece
        blackscore += ((self.dimension+2-W) * 5)
        whitescore += ((self.dimension+2-B) * 5)

        return(blackscore, whitescore)

    #-------------------------
    #COORD TO POS
    #converts pixel coordinate to board position
    #PARAMETERS:
    #coord ((int, int)) - pixel coordinates
    #RETURNS: tuple containing board position
    #-------------------------
    def coord_to_pos(self, coord):
        return ((int(coord[1]/(constants.BOARD_DIMENSION/self.dimension))), (int(coord[0]/(constants.BOARD_DIMENSION/self.dimension))))

    #-------------------------
    #POS TO COORD
    #converts board position to pixel coordinate
    #PARAMETERS:
    #pos ((int, int)) - board position
    #RETURNS: tuple containing pixel coordinates
    #-------------------------
    def pos_to_coord(self, pos):
        return(((pos[1]*(constants.BOARD_DIMENSION/self.dimension)),(pos[0]*(constants.BOARD_DIMENSION/self.dimension))))

    #-------------------------
    #POS TO GRID
    #converts board postion to alphanumeric postion (such as 0,0 to A1)
    #PARAMETERS:
    #pos ((int, int)) - board position
    #RETURNS: string containing alphanumeric postion
    #-------------------------
    def pos_to_grid(self, pos):
        x = str(pos[1] + 1)
        y = chr(pos[0] + 65)
        return str(x+y)

    #-------------------------
    #GET PIECE
    #gets piece at certain board position
    #PARAMETERS:
    #position ((int, int)) - board position of piece
    #RETURNS: string containing the piece
    #-------------------------
    def get_piece(self, position):
        return self.board[position[0]][position[1]][0]

    #-------------------------
    #SET PIECE
    #sets a board postion to a different piece
    #PARAMETERS:
    #position ((int, int)) - board position to be set
    #piece (string) - the piece to assigned to the position
    #RETURNS: nothing
    #-------------------------
    def set_piece(self, position, piece):
        self.board[position[0]][position[1]][0] = piece

    #-------------------------
    #GET DIMENSION
    #gets the size of the board (in tiles)
    #RETURNS: board dimension
    #-------------------------
    def get_dimension(self):
        return self.dimension

    #-------------------------
    #PRINT BOARD
    #prints the board to the console as strings, useful for testing
    #RETURNS: nothing
    #-------------------------
    def print_board(self):
        for i in (range(self.dimension)):
            for j in (range(self.dimension)):
                print (self.board[i][j], end='')
            print("\n")
