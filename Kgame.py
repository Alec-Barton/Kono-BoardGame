#-------------------------
#Alec Barton
#Kgame.py
#-------------------------

import pygame
import Kboard
import Kplayers
import constants
import numpy
import os
import glob
import random

#-------------------------
#GAME CLASS
#represents a single game round, a new one is created each round
#holds the board and the players
#-------------------------
class GAME:
    #-------------------------
    #CONSTRUCTOR
    #PARAMETERS:
    #screen (pygame display object) - screen to be drawn on
    #c (pygame clock object) - clock
    #temp_player_num (int) - number of human players in the game
    #temp_teams ((string, string)) - tuple containing player1's team and player2's team in that order
    #temp_size (int) - size of game board (number of tiles)
    #temp_first (int) - the player that moves first (1 for player1, 2 for player2)
    #temp_load (list of strings) - list of strings containing all the pieces on the board if the board is being loaded
    #(if the board is not being loaded this defaults to None)
    #name (string) - name of the game (for the save file), only assigned if the game is loaded, otherwise a name is given later
    #-------------------------
    def __init__ (self, screen, c,temp_player_num, temp_teams, temp_size, temp_first, temp_load = None, name = None):
        self.name = name
        self.screen = screen
        self.c = c
        self.turn_number=temp_first


        self.text_log = []
        self.end_turn_btn = 0
        self.two_clicks = [None, None]
        self.prev_piece = None

        self.player_number = temp_player_num

        if int(temp_player_num) == 1:
            self.player1 = Kplayers.HUMAN(temp_teams[0])
            # self.player1.set_score(0)
            self.player2 = Kplayers.COMPUTER(temp_teams[1])
            # self.player2.set_score(0)
        if int(temp_player_num) == 2:
            self.player1 = Kplayers.HUMAN(temp_teams[0])
            # self.player1.set_score(temp_score[0])
            self.player2 = Kplayers.HUMAN(temp_teams[1])
            # self.player2.set_score(temp_score[1])

        if temp_load == None:
            self.board = Kboard.BOARD(temp_size)
        else:
            self.board = Kboard.BOARD(temp_size)
            self.board.load_board(temp_load, temp_size)

        # self.render_game(0)

    #-------------------------
    #LOG MOVE
    #adds a human player's move to the text log
    #PARAMETERS:
    #move_coords((int, int)) - x,y coords of the move
    #-------------------------
    def log_move(self, move_coords):
        log = "Player " + str(self.get_players_turn()) + " moved a piece (" + str(self.board.pos_to_grid(move_coords[0])) + " to " + str(self.board.pos_to_grid(move_coords[1])) + ")"
        self.text_log.append(log)

    #-------------------------
    #GET PLAYERS TURN
    #gets which player's turn it is
    #RETURNS: integer denoting the player who's turn it is (1 or 2)
    #-------------------------
    def get_players_turn(self):
        if self.turn_number % 2 == 1:
            return 1
        else:
            return 2

    #-------------------------
    #CLICK ONBOARD
    #checks if a set of pixel coordinates falls on the game board or on the UI
    #PARAMETERS:
    #coord ((int, int)) - pixel coords of a click
    #RETURNS: true if the click is on the board, false if it is on the UI
    #-------------------------
    def click_onboard(self, coord):
        if coord[0] <= constants.BOARD_DIMENSION and coord[1] <= constants.BOARD_DIMENSION:
            return 1
        else:
            return 0

    #-------------------------
    #CURRENT SCORES
    #gets the current scores of the game
    #PARAMETERS:
    #quit (int) - integer reffering to the player that quit the game (None if no one has quit)
    #RETURNS: tuple (int, int) containing player1 and 2's current scores
    #-------------------------
    def current_scores(self, quit = None):
        scores = self.board.score_board()
        if self.player1.get_team() == "B":
            scores = ((scores[0], scores[1]))
        elif self.player1.get_team() == "W":
            scores = ((scores[1], scores[0]))
        if quit:
            if quit == 1:
                scores = ((scores[0] - 5, scores[1]))
            elif quit == 2:
                scores = ((scores[0], scores[1] - 5))
        self.player1.set_score(scores[0])
        self.player2.set_score(scores[1])
        return scores

    #-------------------------
    #CLICK VALID
    #checks if a valid piece has been clicked considering the current player's turn
    #PARAMETERS:
    #coord ((int, int)) - pixel coords of the click
    #RETURNS: true if valid, false if not
    #-------------------------
    def click_valid(self, coord):
        pos = self.board.coord_to_pos(coord)
        piece = self.board.get_piece(pos)

        if self.get_players_turn() == 1:
            team = self.player1.get_team()
        else:
            team = self.player2.get_team()
        if piece == team or piece == (team+team):
            return 1
        else:
            return 0
