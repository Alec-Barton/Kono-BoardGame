#-------------------------
#Alec Barton
#Ktournament.py
#-------------------------

import pygame
import Kgame
import Kplayers
import Kboard
import Kdice
import Kfile
import constants
import numpy
import os
import glob
import random

#-------------------------
#TOURNAMENT CLASS
#creates and manages the game class
#handles a lot of the game logic
#handles most of the graphics
#-------------------------
class TOURNAMENT:
    #-------------------------
    #CONSTRUCTOR
    #-------------------------
    def __init__(self):
        #variables to hold the ongoing tournament score from game to game
        self.player1_score = 0
        self.player2_score = 0
        #tells which part of the game you are currently in
        self.state = constants.game_state.START
        #game object representing a single round
        self.game = None
        #reason a round was ended
        self.end_reason = None

        #variables to hold various settings for the game as they are input by the user
        #eventually they are used to start a new game once they have been filled
        self.temp_player_num = None
        self.temp_teams = [None, None]
        self.temp_size = None
        self.temp_first = None
        self.temp_load = None

        #pygame variables
        #clock
        self.c = pygame.time.Clock()
        #display screen
        self.screen = pygame.display.set_mode(((constants.BOARD_DIMENSION + constants.TEXT_WIDTH), (constants.BOARD_DIMENSION+constants.TURN_HEIGHT+constants.BUTTONS_AREA_HEIGHT)))

        #holds all the valid save files that are found
        self.save_files = []
        #holds the coordinates of buttons on a screen
        self.btn_coords = []

    #-------------------------
    #SETUP
    #sets up the entire game
    #RETURNS: nothing
    #-------------------------
    def setup(self):
        #start pygame
        pygame.init()
        os.chdir(os.getcwd()+"/assets")
        #set task bar icon
        pygame.display.set_icon(pygame.image.load("BB.png"))
        os.chdir(os.path.normpath(os.getcwd() + os.sep + os.pardir))
        #set title bar caption
        pygame.display.set_caption("Kono")
        #set cursor
        pygame.mouse.set_cursor(*pygame.cursors.arrow)

    #-------------------------
    #NEW TOURNAMENT
    #resets all the variables in the tournament to start a new tournament
    #RETURNS: nothing
    #-------------------------
    def new_tournament(self):
        #all important variables are reset to their initial values
        self.player1_score = 0
        self.player2_score = 0
        self.state = constants.game_state.START
        self.game = None
        self.temp_player_num = None
        self.temp_teams = [None, None]
        self.temp_size = None
        self.temp_first = None
        self.temp_load = None
        self.btn_coords = []

    #-------------------------
    #START GAME
    #starts a new game using the temporary variables
    #PARAMETERS:
    #name (string) - the name of the game
    #RETURNS: nothing
    #-------------------------
    def start_game(self, name = None):
        #create a new game object using the temporary variables
        self.game = Kgame.GAME(self.screen, self.c, self.temp_player_num, self.temp_teams, self.temp_size, self.temp_first, self.temp_load, name)

    #-------------------------
    #LOAD GAME
    #loads a game from a text file
    #PARAMETERS:
    #file (string) - name of textfile to load
    #RETURNS: nothing
    #-------------------------
    def load_game(self, file):
        #change directory to where saves are stored
        Kfile.change_dir("saves")
        #save files are tested with the check_load function before they are loaded in this function
        #therefor this function doesnt have to worry about bad inputs

        f = open(file)
        words = []
        #read entire file into list of individual "words"
        for word in f.read().split():
            words.append(word)

        #see if there is a "Players" attribute in the save file
        try:
            i = words.index('Players:')
            #get number of human players
            self.temp_player_num = int(words[i+1])

        except:
            #if there isnt a player attribute then default to a single player game
            self.temp_player_num = 1


        self.temp_teams = ["B", "W"]
        #computer player refers to player2 regardless of if player2 is human or computer
        #load in team for player 2
        i = words.index("Computer:")
        self.player2_score = words[i+2]
        if words[i+4] == "Black":
            self.temp_teams[1] = "B"
        elif words[i+4] == "White":
            self.temp_teams[1] = "W"
        #load in team for player 1
        i = words.index("Human:")
        self.player1_score = words[i+2]
        if words[i+4] == "Black":
            self.temp_teams[0] = "B"
        elif words[i+4] == "White":
            self.temp_teams[0] = "W"

        #find which player moves next
        i = words.index("Next")
        Lnext = words[i+2]
        if (Lnext == "Human"):
            self.temp_first = 1
        elif(Lnext == "Computer"):
            self.temp_first = 2

        #load board
        i = words.index("Board:") + 1
        self.temp_load =[]
        #pieces are put into a list of all pieces that will load the board later
        while (words[i] == "B" or words[i] == "BB" or words[i] == "W" or words[i] == "WW" or words[i] == "O"):
            self.temp_load.append(words[i])
            i+=1
        #find and set the size of the board based on how many pieces were counted
        if len(self.temp_load) == 25:
            self.temp_size = 5
        elif len(self.temp_load) == 49:
            self.temp_size = 7
        elif len(self.temp_load) == 81:
            self.temp_size = 9


        #start the round
        self.start_game(file)
        #set the game_state to playing the game
        self.state = constants.game_state.GAME
        self.render()
        #if the computer moves next, execute it's turn before anything else
        if self.game.player_number == 1 and self.game.turn_number == 2:
            self.end_reason = self.computer_turn()
        pygame.display.update()
        #make sure the file is closed at the end
        f.close()

    #-------------------------
    #CHECK LOAD
    #checks a text file to see if it can be loaded as a valid save file
    #PARAMETERS:
    #file (string) - the name of the text file to be checked
    #RETURNS:
    #True - if the save file is valid
    #False - if the save file is invalid
    #-------------------------
    def check_load(self, file):
        #looks for key words in the file, if any of them are not found it will throw an exception and return false
        try:
            f = open(file)
            words = []
            #read entire file into list of individual "words"
            for word in f.read().split():
                words.append(word)
            #make sure there is a computer keyword
            i = words.index("Computer:")
            LcScore = words[i+2]
            #make sure the team is either black or white
            if words[i+4] == "Black":
                LcTeam = "B"

            elif words[i+4] == "White":
                LcTeam = "W"
            else:
                return False
            #make sure there is a human keyword
            i = words.index("Human:")
            LhScore = words[i+2]
            #make sure the team is either black or white
            if words[i+4] == "Black":
                LhTeam = "B"
            elif words[i+4] == "White":
                LhTeam = "W"
            else:
                return False
                #make sure there is a next keyword
            i = words.index("Next")
            Lnext = words[i+2]
            #make sure next is either human or computer
            if(Lnext == "Human"):
                self.turn_count=1
            elif(Lnext == "Computer"):
                self.turn_count=2
            else:
                return False
             #make sure there is a board keyword
            i = words.index("Board:") + 1
            Lboard =[]
            #make sure there are no invalid pieces on the board
            while (words[i] == "B" or words[i] == "BB" or words[i] == "W" or words[i] == "WW" or words[i] == "O"):
                Lboard.append(words[i])
                i+=1
            #makes sure the board is of a valid size
            if len(Lboard) != 25 and len(Lboard) != 49 and len(Lboard) != 81:
                return False
            return True
        #if any exceptions are thrown the save file is invalid so return false
        except:
            return False


    #-------------------------
    #SAVE GAME
    #saves a game to a textfile
    #RETURNS: nothing
    #-------------------------
    def save_game(self):
        Kfile.change_dir("saves")

        #if the game already had a name (was loaded from a textfile before), open that text file
        if self.game.name:
            f = open(self.game.name, 'w')
        #if the game doesnt have a name create a new textfile to hold the save
        else:
            #count how many current saves there are and give the new file a unique name based on that
            f = open("Save " + str(len(glob.glob("*.txt"))+1) + ".txt", 'w')

        #write the game attributes to the text file
        f.write("Players: " + str(self.game.player_number) + '\n'+ '\n')
        if str(self.game.player2.get_team()) == "B":
            team = "Black"
        elif str(self.game.player2.get_team()) == "W":
            team = "White"

        f.write("Computer: "+ '\n')
        f.write('\t' + "Score: " + str(self.player2_score)+ '\n')
        f.write('\t' + "Color: " + team + '\n' + '\n')

        if str(self.game.player1.get_team()) == "B":
            team = "Black"
        elif str(self.game.player1.get_team()) == "W":
            team = "White"

        f.write("Human: "+ '\n')
        f.write('\t' + "Score: " + str(self.player1_score)+ '\n')
        f.write('\t' + "Color: " + team + '\n' + '\n')
        f.write("Board: "+ '\n')

        b = self.game.board.save_board()
        line = "\t"
        count = 0
        for i in b:
            if i == "O" or i == "B" or i == "W":
                line += (i + "  ")
                count +=1
            elif i == "BB" or i == "WW":
                line += (i + " ")
                count +=1
            if count % self.game.board.dimension == 0 and count > 0:
                f.write(line + '\n')
                line = "\t"
        f.write("\n")
        if self.game.get_players_turn() == 1:
            if self.game.end_turn_btn:
                next = "Computer"
            else:
                next = "Human"
        elif self.game.get_players_turn() == 2:
            if self.game.end_turn_btn:
                next = "Human"
            else:
                next = "Computer"
        f.write("Next Player: " + next + '\n')
        f.close()

    #-------------------------
    #PLAY
    #runs the entire game
    #RETURNS: nothing
    #-------------------------
    def play(self):
        self.render()
        #game loop
        while 1:
            #sets the framerate at 30
            self.c.tick(30)
            #event listner
            for event in pygame.event.get():
                #if the "x" button is clicked
                if event.type == pygame.QUIT:
                    #close the game
                    pygame.quit()
                #if theres a click anywhere in the window
                if event.type == pygame.MOUSEBUTTONDOWN:
                    #get the position of the click
                    mouse_pos = pygame.mouse.get_pos()
                    #decide what the click does
                    self.process_button_click(mouse_pos)

                    mouse_pos = None
                    #wait briefly
                    pygame.time.delay(100)

    #-------------------------
    #RENDER
    #renders different screens of the game depending on the game state
    #RETURNS: nothing
    #-------------------------
    def render(self):
        #change directory to assets so images can be loaded
        Kfile.change_dir("assets")
        
        #what window to render depends on the game state
        #for each screen, button coordinates are calculated and appended to a List when the screen is rendered
        #these coordinates are used by process_button_click function to handle button clicks
        #-------------------------
        #START - Start Game
        #-------------------------
        if self.state == constants.game_state.START:
            #most of the code in rendering function is just to draw text and images to specific positions in the window
            #the individual cases are largely the same so comments for cases after this one will only point out the unique logical parts

            #make sure gamestate is set correctly
            self.state = constants.game_state.START
            #reset button coords
            self.btn_coords = []
            #create a font object for drawing text
            basicfont = pygame.font.Font("Kfont.ttf", 75)
            #make it bold
            basicfont.set_bold(1)
            #get the dimensions of the screen
            s_width, s_height = pygame.display.get_surface().get_size()
            #fill the screen with a single color (basically wipping the screen)
            self.screen.fill(constants.GREY)
            #create a text object
            text = basicfont.render("KONO", False, constants.BLACK)
            #blit is called whenever something is drawn to the screen
            #draw the text to the screen
            self.screen.blit(text , (s_width/2- (text.get_rect().size[0]/2), .2*s_height))

            #process to draw a button
            #load button image
            button = pygame.image.load("button.png")
            #scale button image
            button = pygame.transform.scale(button, (constants.BUTTON_WIDTH, constants.BUTTON_HEIGHT))
            button.convert()
            #create new font object, fonts cannot change their size, they must be re-intialized each time they change size
            basicfont = pygame.font.Font("Kfont.ttf", 20)
            #draw button image to screen
            self.screen.blit(button, (s_width/2- (button.get_rect().size[0]/2), .45*s_height))
            #button coordinates are a tuple containing the coordinates of the top left corner and buttom right corner of the button
            #therefor if a click is between those two corner values then it is on the button
            self.btn_coords.append(((s_width/2- (button.get_rect().size[0]/2), .45*s_height),(s_width/2- (button.get_rect().size[0]/2) + constants.BUTTON_WIDTH, .45*s_height+constants.BUTTON_HEIGHT)))
            #draw text for the button centered on the button
            text = basicfont.render("New Game", False, constants.BLACK)
            self.screen.blit(text , (s_width/2- (button.get_rect().size[0]/2) +constants.BUTTON_WIDTH/2- (text.get_rect().size[0]/2) , (.45*s_height) + constants.BUTTON_HEIGHT/2 - (text.get_rect().size[1]/2)))
            self.screen.blit(button, (s_width/2- (button.get_rect().size[0]/2), .65*s_height))
            self.btn_coords.append(((s_width/2- (button.get_rect().size[0]/2), .65*s_height),(s_width/2- (button.get_rect().size[0]/2) + constants.BUTTON_WIDTH, .65*s_height+constants.BUTTON_HEIGHT)))
            text = basicfont.render("Load Game", False, constants.BLACK)
            self.screen.blit(text , (s_width/2- (button.get_rect().size[0]/2) +constants.BUTTON_WIDTH/2- (text.get_rect().size[0]/2) , (.65*s_height) + constants.BUTTON_HEIGHT/2 - (text.get_rect().size[1]/2)))
            pygame.display.update()

        #-------------------------
        #LOAD - Load Game
        #-------------------------
        elif self.state == constants.game_state.LOAD:
            #basic rendering of text and buttons
            self.save_files = []
            self.state = constants.game_state.LOAD
            self.screen.fill(constants.GREY)
            self.btn_coords = []
            s_width, s_height = pygame.display.get_surface().get_size()
            basicfont = pygame.font.Font("Kfont.ttf", 60)
            basicfont.set_bold(1)
            text = basicfont.render("Choose Save File", False, constants.BLACK)
            self.screen.blit(text , (s_width/2- (text.get_rect().size[0]/2), 20))
            basicfont.set_bold(0)
            basicfont = pygame.font.Font("Kfont.ttf", 30)
            button = pygame.image.load("button.png")
            button = pygame.transform.scale(button, (constants.BUTTON_WIDTH, constants.BUTTON_HEIGHT))
            button.convert()
            self.screen.blit(button, (s_width/2- (button.get_rect().size[0]/2), s_height - 75))
            self.btn_coords.append(((s_width/2- (button.get_rect().size[0]/2), s_height - 75),(s_width/2- (button.get_rect().size[0]/2)+constants.BUTTON_WIDTH, s_height - 75+constants.BUTTON_HEIGHT)))
            text = basicfont.render("Back", False, constants.BLACK)
            self.screen.blit(text , (s_width/2- (button.get_rect().size[0]/2) +constants.BUTTON_WIDTH/2- (text.get_rect().size[0]/2) , (s_height-75) + constants.BUTTON_HEIGHT/2 - (text.get_rect().size[1]/2)))
            s_button = pygame.image.load("O.png")
            basicfont = pygame.font.Font("Kfont.ttf", 25)

            #find all valid save files
            Kfile.change_dir("saves")
            i = 0
            #search directory for any text files
            for file in glob.glob("*.txt"):
                #check if the textfile will work as a save file
                if self.check_load(file):
                    #can load up to 10 different save files
                    if i < 10:
                        #if a valid save file is found draw its name to the screen
                        self.save_files.append(file)
                        text = basicfont.render(os.path.splitext(file)[0], False, constants.BLACK)
                        s_button = pygame.transform.scale(s_button, (text.get_rect().size[1],text.get_rect().size[1]))
                        s_button.convert()
                        self.screen.blit(text , (150 ,110  + 40 * i))
                        #the name of the save file counts as a button in this case
                        self.btn_coords.append(((150 - 1.5* text.get_rect().size[1],110+40*i),(150 - 1.5* text.get_rect().size[1]+text.get_rect().size[1] + text.get_rect().size[0],110+40*i+text.get_rect().size[1])))
                        self.screen.blit(s_button, (150 - 1.5* text.get_rect().size[1],110+40*i))
                        i += 1
            Kfile.change_dir("assets")
            pygame.display.update()

        #-------------------------
        #PLAYERS - Choose Number of Players
        #-------------------------
        elif self.state == constants.game_state.PLAYERS:
            #basic rendering of text and buttons
            self.btn_coords = []
            self.state = constants.game_state.PLAYERS
            self.screen.fill(constants.GREY)
            s_width, s_height = pygame.display.get_surface().get_size()
            basicfont = pygame.font.Font("Kfont.ttf", 60)
            basicfont.set_bold(1)
            text = basicfont.render("Choose Human Players", False, constants.BLACK)
            self.screen.blit(text , (s_width/2- (text.get_rect().size[0]/2), 20))
            basicfont.set_bold(0)
            basicfont = pygame.font.Font("Kfont.ttf", 25)
            button = pygame.image.load("button.png")
            button = pygame.transform.scale(button, (constants.BUTTON_WIDTH, constants.BUTTON_HEIGHT))
            button.convert()
            self.screen.blit(button, (s_width/3- (constants.BUTTON_WIDTH/2), s_height/2 - constants.BUTTON_HEIGHT/2))
            self.btn_coords.append(((s_width/3- (constants.BUTTON_WIDTH/2), s_height/2 - constants.BUTTON_HEIGHT/2),(s_width/3- (constants.BUTTON_WIDTH/2)+constants.BUTTON_WIDTH, s_height/2 - constants.BUTTON_HEIGHT/2+constants.BUTTON_HEIGHT)))
            text = basicfont.render("1 Player", False, constants.BLACK)
            self.screen.blit(text , (s_width/3 - text.get_rect().size[0]/2, s_height/2 - text.get_rect().size[1]/2))
            self.screen.blit(button, (2*s_width/3- (constants.BUTTON_WIDTH/2), s_height/2 - constants.BUTTON_HEIGHT/2))
            self.btn_coords.append(((2*s_width/3- (constants.BUTTON_WIDTH/2), s_height/2 - constants.BUTTON_HEIGHT/2),(2*s_width/3- (constants.BUTTON_WIDTH/2)+constants.BUTTON_WIDTH, s_height/2 - constants.BUTTON_HEIGHT/2+constants.BUTTON_HEIGHT)))
            text = basicfont.render("2 Players", False, constants.BLACK)
            self.screen.blit(text , (2*s_width/3 - text.get_rect().size[0]/2, s_height/2 - text.get_rect().size[1]/2))
            pygame.display.update()

        #-------------------------
        #DICE1 - Choose Dice Roll
        #-------------------------
        elif self.state == constants.game_state.DICE1:
            #basic rendering of text and buttons
            self.btn_coords = []
            self.state = constants.game_state.DICE1
            self.screen.fill(constants.GREY)
            s_width, s_height = pygame.display.get_surface().get_size()
            basicfont = pygame.font.Font("Kfont.ttf", 50)
            basicfont.set_bold(1)
            text = basicfont.render("Dice Rolls", False, constants.BLACK)
            self.screen.blit(text , (s_width/2 - text.get_rect().size[0]/2, 20))
            basicfont.set_bold(0)
            basicfont = pygame.font.Font("Kfont.ttf", 25)
            button = pygame.image.load("button.png")
            button = pygame.transform.scale(button, (constants.BUTTON_WIDTH, constants.BUTTON_HEIGHT))
            button.convert()
            self.screen.blit(button, (s_width/3- (constants.BUTTON_WIDTH/2), s_height/2 - constants.BUTTON_HEIGHT/2))
            self.btn_coords.append(((s_width/3- (constants.BUTTON_WIDTH/2), s_height/2 - constants.BUTTON_HEIGHT/2),(s_width/3- (constants.BUTTON_WIDTH/2)+constants.BUTTON_WIDTH, s_height/2 - constants.BUTTON_HEIGHT/2+constants.BUTTON_HEIGHT)))
            text = basicfont.render("Roll Dice", False, constants.BLACK)
            self.screen.blit(text , (s_width/3 - text.get_rect().size[0]/2, s_height/2 - text.get_rect().size[1]/2))
            self.screen.blit(button, (2*s_width/3- (constants.BUTTON_WIDTH/2), s_height/2 - constants.BUTTON_HEIGHT/2))
            self.btn_coords.append(((2*s_width/3- (constants.BUTTON_WIDTH/2), s_height/2 - constants.BUTTON_HEIGHT/2),(2*s_width/3- (constants.BUTTON_WIDTH/2)+constants.BUTTON_WIDTH, s_height/2 - constants.BUTTON_HEIGHT/2+constants.BUTTON_HEIGHT)))
            text = basicfont.render("Load Dice", False, constants.BLACK)
            self.screen.blit(text , (2*s_width/3 - text.get_rect().size[0]/2, s_height/2 - text.get_rect().size[1]/2))

            pygame.display.update()


        #-------------------------
        #DICE2 - Roll Dice
        #-------------------------
        elif self.state == constants.game_state.DICE2:
            #basic rendering of text and buttons
            self.btn_coords = []
            self.screen.fill(constants.GREY)
            basicfont = pygame.font.Font("Kfont.ttf", 50)

            s_width, s_height = pygame.display.get_surface().get_size()
            basicfont.set_bold(1)
            text = basicfont.render("Dice Rolls", False, constants.BLACK)
            self.screen.blit(text , (s_width/2 - text.get_rect().size[0]/2, 20))
            basicfont.set_bold(0)
            basicfont = pygame.font.Font("Kfont.ttf", 25)
            text = basicfont.render("Player 1", False, constants.BLACK)
            self.screen.blit(text , (s_width/3 - text.get_rect().size[0]/2, 90))
            if self.temp_player_num == 1:
                text = basicfont.render("Computer", False, constants.BLACK)
            else:
                text = basicfont.render("Player 2", False, constants.BLACK)
            self.screen.blit(text , (2*s_width/3 - text.get_rect().size[0]/2, 90))
            basicfont = pygame.font.Font("Kfont.ttf", 20)

            #calculate the dice rolls and draw them to the screen
            roll1 = self.rolls[0]
            roll2 = self.rolls[1]
            i2 = 1
            for i in range(len(roll2)):
                if i2 % 2 == 1:
                    s1 = roll1[i]
                    s2 = roll2[i]
                    i2 += 1
                else:
                    s1 = str(s1) + "          " + str(roll1[i])
                    s2 = str(s2) + "          " + str(roll2[i])
                    text = basicfont.render(str(s1), False, constants.BLACK)
                    self.screen.blit(text , (s_width/3 - text.get_rect().size[0]/2, i*20+ 120))
                    text = basicfont.render(str(s2), False, constants.BLACK)
                    self.screen.blit(text , (2*s_width/3 - text.get_rect().size[0]/2, i*20+ 120))
                    i2 += 1
                    s1 = ""
                    s2 = ""

            #draw the winner of the dice roll
            basicfont = pygame.font.Font("Kfont.ttf", 25)
            if self.rolls[2] == 1:
                text = basicfont.render("Player 1 wins the Dice Roll", False, constants.BLACK)
                #set who moves first
                self.temp_first = 1
            if self.rolls[2] == 2:
                #set who moves first
                self.temp_first = 2
                if self.temp_player_num == 2:
                    text = basicfont.render("Player 2 wins the Dice Roll", False, constants.BLACK)
                if self.temp_player_num == 1:
                    text = basicfont.render("Computer wins the Dice Roll", False, constants.BLACK)

            #basic rendering of text and buttons
            self.screen.blit(text , (s_width/2 - text.get_rect().size[0]/2, .70*s_height))
            button = pygame.image.load("button.png")
            button = pygame.transform.scale(button, (constants.BUTTON_WIDTH, constants.BUTTON_HEIGHT))
            button.convert()
            self.screen.blit(button, (s_width/2- (constants.BUTTON_WIDTH/2), s_height - constants.BUTTON_HEIGHT*2))
            self.btn_coords.append(((s_width/2- (constants.BUTTON_WIDTH/2), s_height - constants.BUTTON_HEIGHT*2),(s_width/2- (constants.BUTTON_WIDTH/2)+constants.BUTTON_WIDTH, s_height - 2*constants.BUTTON_HEIGHT+ constants.BUTTON_HEIGHT)))
            text = basicfont.render("Continue", False, constants.BLACK)
            self.screen.blit(text , (s_width/2 - text.get_rect().size[0]/2, s_height - constants.BUTTON_HEIGHT*2 + text.get_rect().size[1]/2))
            pygame.display.update()


        #-------------------------
        #TEAMS - Human Chooses a Team
        #-------------------------
        elif self.state == constants.game_state.TEAMS:
            #basic rendering of text and buttons
            self.btn_coords = []
            self.state = constants.game_state.TEAMS
            self.screen.fill(constants.GREY)
            s_width, s_height = pygame.display.get_surface().get_size()
            basicfont = pygame.font.Font("Kfont.ttf", 60)
            basicfont.set_bold(1)
            text = basicfont.render("Choose Player " + str(self.temp_first) + " Color", False, constants.BLACK)
            basicfont.set_bold(0)
            self.screen.blit(text , (s_width/2- (text.get_rect().size[0]/2), 20))
            basicfont = pygame.font.Font("Kfont.ttf", 25)
            button = pygame.image.load("button.png")
            button = pygame.transform.scale(button, (constants.BUTTON_WIDTH, constants.BUTTON_HEIGHT))
            button.convert()
            self.screen.blit(button, (s_width/3- (constants.BUTTON_WIDTH/2), s_height/2 - constants.BUTTON_HEIGHT/2))
            self.btn_coords.append(((s_width/3- (constants.BUTTON_WIDTH/2), s_height/2 - constants.BUTTON_HEIGHT/2),(s_width/3- (constants.BUTTON_WIDTH/2)+constants.BUTTON_WIDTH, s_height/2 - constants.BUTTON_HEIGHT/2+constants.BUTTON_HEIGHT)))
            text = basicfont.render("Black", False, constants.BLACK)
            self.screen.blit(text , (s_width/3 - text.get_rect().size[0]/2, s_height/2 - text.get_rect().size[1]/2))
            self.screen.blit(button, (2*s_width/3- (constants.BUTTON_WIDTH/2), s_height/2 - constants.BUTTON_HEIGHT/2))
            self.btn_coords.append(((2*s_width/3- (constants.BUTTON_WIDTH/2), s_height/2 - constants.BUTTON_HEIGHT/2),(2*s_width/3- (constants.BUTTON_WIDTH/2)+constants.BUTTON_WIDTH, s_height/2 - constants.BUTTON_HEIGHT/2+constants.BUTTON_HEIGHT)))
            text = basicfont.render("White", False, constants.WHITE)
            self.screen.blit(text , (2*s_width/3 - text.get_rect().size[0]/2, s_height/2 - text.get_rect().size[1]/2))
            pygame.display.update()

        #-------------------------
        #TEAMS2 - Computer Chooses a Team
        #-------------------------
        elif self.state == constants.game_state.TEAMS2:
            #computer choose's a team so the team should be randomly chosen
            self.screen.fill(constants.GREY)
            s_width, s_height = pygame.display.get_surface().get_size()
            basicfont = pygame.font.Font("Kfont.ttf", 50)
            basicfont.set_bold(1)
            self.btn_coords = []
            #randomly generate 1 or 2
            rand = random.randint(1,2)
            #assign teams based on that random int
            if rand ==1:
                self.temp_teams = ["W", "B"]
                text = basicfont.render("Computer choses Black Team", False, constants.BLACK)
            else:

                text = basicfont.render("Computer choses White Team", False, constants.BLACK)
                self.temp_teams = ["B", "W"]

            #the rest is normal drawing
            self.screen.blit(text , (s_width/2 - text.get_rect().size[0]/2, .25*s_height))
            basicfont.set_bold(0)
            basicfont = pygame.font.Font("Kfont.ttf", 25)
            button = pygame.image.load("button.png")
            button = pygame.transform.scale(button, (constants.BUTTON_WIDTH, constants.BUTTON_HEIGHT))
            button.convert()
            self.screen.blit(button, (s_width/2- (constants.BUTTON_WIDTH/2), .6* s_height))
            self.btn_coords.append(((s_width/2- (constants.BUTTON_WIDTH/2), .6* s_height), (s_width/2- (constants.BUTTON_WIDTH/2) + constants.BUTTON_WIDTH, .6* s_height+ constants.BUTTON_HEIGHT)))
            text = basicfont.render("Continue", False, constants.BLACK)
            self.screen.blit(text , (s_width/2 - text.get_rect().size[0]/2, .6*s_height + text.get_rect().size[1]/2))
            pygame.display.update()
        #-------------------------
        #SIZE - Choose a Size
        #-------------------------
        elif self.state == constants.game_state.SIZE:
            #basic rendering of text and buttons
            self.state = constants.game_state.SIZE
            self.btn_coords = []
            basicfont = pygame.font.Font("Kfont.ttf", 50)
            basicfont.set_bold(1)
            s_width, s_height = pygame.display.get_surface().get_size()
            self.screen.fill(constants.GREY)
            text = basicfont.render("Choose Game Board Size", False, constants.BLACK)
            self.screen.blit(text , (s_width/2- (text.get_rect().size[0]/2), .15*s_height))
            basicfont.set_bold(0)
            basicfont = pygame.font.Font("Kfont.ttf", 30)
            button = pygame.image.load("button.png")
            button = pygame.transform.scale(button, (constants.BUTTON_WIDTH, constants.BUTTON_HEIGHT))
            button.convert()
            self.screen.blit(button, (s_width/2- (button.get_rect().size[0]/2), .35*s_height))
            self.btn_coords.append(((s_width/2- (button.get_rect().size[0]/2), .35*s_height),(s_width/2- (button.get_rect().size[0]/2) + constants.BUTTON_WIDTH, .45*s_height+constants.BUTTON_HEIGHT)))
            text = basicfont.render("5 x 5", False, constants.BLACK)
            self.screen.blit(text , (s_width/2- (button.get_rect().size[0]/2) +constants.BUTTON_WIDTH/2- (text.get_rect().size[0]/2) , (.35*s_height) + constants.BUTTON_HEIGHT/2 - (text.get_rect().size[1]/2)))
            self.screen.blit(button, (s_width/2- (button.get_rect().size[0]/2), .55*s_height))
            self.btn_coords.append(((s_width/2- (button.get_rect().size[0]/2), .55*s_height),(s_width/2- (button.get_rect().size[0]/2) + constants.BUTTON_WIDTH, .65*s_height+constants.BUTTON_HEIGHT)))
            text = basicfont.render("7 x 7", False, constants.BLACK)
            self.screen.blit(text , (s_width/2- (button.get_rect().size[0]/2) +constants.BUTTON_WIDTH/2- (text.get_rect().size[0]/2) , (.55*s_height) + constants.BUTTON_HEIGHT/2 - (text.get_rect().size[1]/2)))
            self.screen.blit(button, (s_width/2- (button.get_rect().size[0]/2), .75*s_height))
            self.btn_coords.append(((s_width/2- (button.get_rect().size[0]/2), .75*s_height),(s_width/2- (button.get_rect().size[0]/2) + constants.BUTTON_WIDTH, .85*s_height+constants.BUTTON_HEIGHT)))
            text = basicfont.render("9 x 9", False, constants.BLACK)
            self.screen.blit(text , (s_width/2- (button.get_rect().size[0]/2) +constants.BUTTON_WIDTH/2- (text.get_rect().size[0]/2) , (.75*s_height) + constants.BUTTON_HEIGHT/2 - (text.get_rect().size[1]/2)))
            pygame.display.update()

        #-------------------------
        #GAME - Play the Game
        #-------------------------
        elif self.state == constants.game_state.GAME:
            self.screen.fill(constants.GREY)
            self.game.board.draw(self.screen)
            basicfont = pygame.font.Font("Kfont.ttf", 30)
            #print who's turn it currently is
            if self.game.get_players_turn() == 1:
                type = "Player"
                if self.game.player1.get_team() == "B":
                    team = "Black"
                else:
                    team = "White"
            else:
                if self.game.player2.get_type() == "Human":
                    type = "Player"
                else:
                    type = "Computer"
                if self.game.player2.get_team() == "B":
                    team = "Black"
                else:
                    team = "White"
            turn_string = type + "'s Turn ("  + team +")"
            text = basicfont.render(turn_string, False, constants.BLACK)
            y = constants.BOARD_DIMENSION + ((constants.TURN_HEIGHT/2) - (text.get_rect().size[1]/2))
            x = int((constants.BOARD_DIMENSION/2)-(text.get_rect().size[0]/2))
            self.screen.blit(text , (x,  y))

            #print the current scores of the game
            basicfont = pygame.font.Font("Kfont.ttf", 18)
            text1 = basicfont.render("Player 1", False, constants.BLACK)
            if self.temp_player_num == 1:
                text2 = basicfont.render("Computer", False, constants.BLACK)
            else:
                text2 = basicfont.render("Player 2", False, constants.BLACK)
            constants.TEXT_WIDTH
            self.screen.blit(text1, (constants.BOARD_DIMENSION + 1.5*constants.TEXT_WIDTH/6 - text1.get_rect().size[0]/2, 10))
            self.screen.blit(text2, (constants.BOARD_DIMENSION + 4.5*constants.TEXT_WIDTH/6 - text2.get_rect().size[0]/2, 10))
            text = basicfont.render("Round", False, constants.BLACK)
            self.screen.blit(text, (constants.BOARD_DIMENSION + constants.TEXT_WIDTH/2 - text.get_rect().size[0]/2, 1.3*text.get_rect().size[1]+10))
            text = basicfont.render("Tournament", False, constants.BLACK)
            self.screen.blit(text, (constants.BOARD_DIMENSION + constants.TEXT_WIDTH/2 - text.get_rect().size[0]/2, 2.5*text.get_rect().size[1]+10))
            self.game.current_scores()
            #get the scores for the current game
            round1 = self.game.player1.get_score()
            round2 = self.game.player2.get_score()

            #color of the score is the same as the team color
            if self.game.player1.get_team() == "B":
                color1 = constants.DARK_GREY
                color2 = constants.WHITE
            else:
                color1 = constants.WHITE
                color2 = constants.DARK_GREY

            #tournament score updates dynamically
            if (round1 > round2):
                awarded =(round1 - round2, 0)
            elif (round2 > round1):
                awarded =(0, round2-round1)
            else:
                awarded = (0,0)
            total1 = str(int(self.player1_score) + int(awarded[0]))
            total2 = str(int(self.player2_score) + int(awarded[1]))
            text1 = basicfont.render(str(round1), False, color1)
            text2 = basicfont.render(str(round2), False, color2)
            self.screen.blit(text1, (constants.BOARD_DIMENSION + 1.5*constants.TEXT_WIDTH/6 - text1.get_rect().size[0]/2, 1.3*text.get_rect().size[1]+10))
            self.screen.blit(text2, (constants.BOARD_DIMENSION + 4.5*constants.TEXT_WIDTH/6 - text2.get_rect().size[0]/2, 1.3*text.get_rect().size[1]+10))
            text1 = basicfont.render(str(total1), False, color1)
            text2 = basicfont.render(str(total2), False, color2)
            self.screen.blit(text1, (constants.BOARD_DIMENSION + 1.5*constants.TEXT_WIDTH/6 - text1.get_rect().size[0]/2, 2.5*text.get_rect().size[1]+10))
            self.screen.blit(text2, (constants.BOARD_DIMENSION + 4.5*constants.TEXT_WIDTH/6 - text2.get_rect().size[0]/2, 2.5*text.get_rect().size[1]+10))
            basicfont = pygame.font.Font("Kfont.ttf", 15)

            #print out the text log
            for i in range(len(self.game.text_log)):
                #only print the move recent 30 entries
                if i >= 30:
                    break
                #color of text gets lighter as it moves further down
                color = tuple(numpy.add(constants.BLACK, (i*3, i*3, i*3)))

                #bold the first entry
                if i == 0:
                    basicfont.set_bold(1)
                else:
                    basicfont.set_bold(0)
                text = basicfont.render(self.game.text_log[len(self.game.text_log) - (i+1)], False, color)
                self.screen.blit(text , (constants.BOARD_DIMENSION + 20, (i*15+95) ))

            x_gap = (constants.BOARD_DIMENSION - (constants.BUTTON_WIDTH*2))/3
            y_gap = (constants.BUTTONS_AREA_HEIGHT - (constants.BUTTON_HEIGHT*2))/3

            screen_size = pygame.display.get_surface().get_size()

            #draw the buttons
            button = pygame.image.load("button.png")
            button = pygame.transform.scale(button, (constants.BUTTON_WIDTH, constants.BUTTON_HEIGHT))
            button.convert()

            basicfont = pygame.font.Font("Kfont.ttf", 30)
            self.btn_coords = []

            self.screen.blit(button, (x_gap ,screen_size[1]- 2*(y_gap+constants.BUTTON_HEIGHT)))
            self.btn_coords.append(((x_gap ,screen_size[1]- 2*(y_gap+constants.BUTTON_HEIGHT)), (x_gap+constants.BUTTON_WIDTH ,screen_size[1]- 2*(y_gap+constants.BUTTON_HEIGHT) + constants.BUTTON_HEIGHT)))
            text = basicfont.render("Save", False, constants.BLACK)
            self.screen.blit(text , (x_gap + constants.BUTTON_WIDTH/2 - (text.get_rect().size[0]/2) ,screen_size[1]- 2*(y_gap+constants.BUTTON_HEIGHT) + constants.BUTTON_HEIGHT/2 - (text.get_rect().size[1]/2)))

            self.screen.blit(button, (2 * x_gap + constants.BUTTON_WIDTH ,screen_size[1]- 2*(y_gap+constants.BUTTON_HEIGHT)))
            self.btn_coords.append(((2 * x_gap + constants.BUTTON_WIDTH ,screen_size[1]- 2*(y_gap+constants.BUTTON_HEIGHT)), (2 * x_gap + 2*constants.BUTTON_WIDTH ,screen_size[1]- 2*(y_gap+constants.BUTTON_HEIGHT)+ constants.BUTTON_HEIGHT)))
            text = basicfont.render("Help", False, constants.BLACK)
            self.screen.blit(text , (2 * x_gap + constants.BUTTON_WIDTH + constants.BUTTON_WIDTH/2 - (text.get_rect().size[0]/2) ,screen_size[1]- 2*(y_gap+constants.BUTTON_HEIGHT)+ constants.BUTTON_HEIGHT/2 - (text.get_rect().size[1]/2)))

            self.screen.blit(button, (x_gap ,screen_size[1]-(y_gap+constants.BUTTON_HEIGHT)))
            self.btn_coords.append((((x_gap ,screen_size[1]-(y_gap+constants.BUTTON_HEIGHT))),(x_gap+constants.BUTTON_WIDTH ,(screen_size[1]-(y_gap+constants.BUTTON_HEIGHT))+constants.BUTTON_HEIGHT)))
            text = basicfont.render("Quit", False, constants.BLACK)
            self.screen.blit(text , (x_gap + constants.BUTTON_WIDTH/2 - (text.get_rect().size[0]/2),screen_size[1]-(y_gap+constants.BUTTON_HEIGHT)+ constants.BUTTON_HEIGHT/2 - (text.get_rect().size[1]/2)))

            #only draw end turn button if its the 2nd move of the turn
            if self.game.end_turn_btn:
                self.screen.blit(button, (2 * x_gap + constants.BUTTON_WIDTH ,screen_size[1]- (y_gap+constants.BUTTON_HEIGHT)))
                self.btn_coords.append(((2 * x_gap + constants.BUTTON_WIDTH ,screen_size[1]- (y_gap+constants.BUTTON_HEIGHT)), (2 * x_gap + 2*constants.BUTTON_WIDTH ,screen_size[1]- (y_gap+constants.BUTTON_HEIGHT)+constants.BUTTON_HEIGHT)))
                text = basicfont.render("End Turn", False, constants.BLACK)
                self.screen.blit(text , (2 * x_gap + constants.BUTTON_WIDTH + constants.BUTTON_WIDTH/2 - (text.get_rect().size[0]/2), screen_size[1]- (y_gap+constants.BUTTON_HEIGHT)+ constants.BUTTON_HEIGHT/2 - (text.get_rect().size[1]/2)))

            pygame.display.update()

        #-------------------------
        #END1 - End the Round
        #-------------------------
        elif self.state == constants.game_state.END1:
            self.btn_coords = []
            self.screen.fill(constants.GREY)
            pygame.display.update()
            basicfont = pygame.font.Font("Kfont.ttf", 35)
            s_width, s_height = pygame.display.get_surface().get_size()
            text = basicfont.render(str(self.end_reason), False, constants.BLACK)
            self.screen.blit(text, (int(s_width/2 - text.get_rect().size[0]/2), int(.025 * s_height)))
            basicfont = pygame.font.Font("Kfont.ttf", 25)
            text1 = basicfont.render("Player 1", False, constants.BLACK)
            if self.temp_player_num == 1:
                text2 = basicfont.render("Computer", False, constants.BLACK)
            else:
                text2 = basicfont.render("Player 2", False, constants.BLACK)
            self.screen.blit(text1, (2.5*s_width/10-text1.get_rect().size[0]/2, .55*s_height))
            self.screen.blit(text2, (7.5*s_width/10-text2.get_rect().size[0]/2, .55*s_height))
            text = basicfont.render("Round", False, constants.BLACK)
            self.screen.blit(text, (s_width/2 - text.get_rect().size[0]/2, .625*s_height))
            text = basicfont.render("Tournament", False, constants.BLACK)
            self.screen.blit(text, (s_width/2 - text.get_rect().size[0]/2, .7*s_height))

            #get the scores for the round
            round1 = self.game.player1.get_score()
            round2 = self.game.player2.get_score()

            #determine the winner of the game create a string announcing it
            #also determine how many points should be given
            if (round1 > round2):
                #how many points the winner gets
                awarded =(round1 - round2, 0)
                award_string1 = "Player 1 wins the Round"
                award_string2 = "Player 1 is awarded " + str(round1 - round2) + " points"
            elif (round2 > round1):
                awarded =(0, round2-round1)
                if self.temp_player_num == 1:
                    award_string1 = "Computer wins the Round"
                    award_string2 = "Computer is awarded " + str(round2 - round1) + " points"
                else:
                    award_string1 = "Player 2 wins the Round"
                    award_string2 = "Player 2 is awarded " + str(round2 - round1) + " points"
            else:
                awarded = (0,0)
                award_string1 = "Tie"
                award_string2 = "no points awarded"

            #caluculate the score of the tournament
            self.player1_score = int(awarded[0]) + int(self.player1_score)
            self.player2_score = int(awarded[1]) + int(self.player2_score)

            #draw the scores to the screen
            text1 = basicfont.render(str(round1), False, constants.BLACK)
            text2 = basicfont.render(str(round2), False, constants.BLACK)
            self.screen.blit(text1, (2.5*s_width/10-text1.get_rect().size[0]/2, .625*s_height))
            self.screen.blit(text2, (7.5*s_width/10-text2.get_rect().size[0]/2, .625*s_height))
            text1 = basicfont.render(str(self.player1_score), False, constants.BLACK)
            text2 = basicfont.render(str(self.player2_score), False, constants.BLACK)
            self.screen.blit(text1, (2.5*s_width/10-text1.get_rect().size[0]/2, .7*s_height))
            self.screen.blit(text2, (7.5*s_width/10-text2.get_rect().size[0]/2, .7*s_height))
            basicfont = pygame.font.Font("Kfont.ttf", 35)
            text = basicfont.render(award_string1, False, constants.BLACK)
            self.screen.blit(text, (int(s_width/2 - text.get_rect().size[0]/2), int(.1 * s_height)))
            text = basicfont.render(award_string2, False, constants.BLACK)
            self.screen.blit(text, (int(s_width/2 - text.get_rect().size[0]/2), int(.175 * s_height)))

            button = pygame.image.load("button.png")
            button = pygame.transform.scale(button, (constants.BUTTON_WIDTH, constants.BUTTON_HEIGHT))
            button.convert()
            basicfont = pygame.font.Font("Kfont.ttf", 25)
            self.screen.blit(button, (2.5*s_width/10- (constants.BUTTON_WIDTH/2), .8*s_height))
            self.btn_coords.append(((2.5*s_width/10- (constants.BUTTON_WIDTH/2), .8*s_height),(2.5*s_width/10- (constants.BUTTON_WIDTH/2) + constants.BUTTON_WIDTH, .8*s_height+constants.BUTTON_HEIGHT)))
            text = basicfont.render("Play Again", False, constants.BLACK)
            self.screen.blit(text , (2.5*s_width/10- (text.get_rect().size[0]/2), .8*s_height+ (text.get_rect().size[1]/2)))
            self.screen.blit(button, (7.5*s_width/10- (constants.BUTTON_WIDTH/2), .8*s_height))
            self.btn_coords.append(((7.5*s_width/10- (constants.BUTTON_WIDTH/2), .8*s_height),(7.5*s_width/10- (constants.BUTTON_WIDTH/2) + constants.BUTTON_WIDTH, .8*s_height+constants.BUTTON_HEIGHT)))
            text = basicfont.render("End", False, constants.BLACK)
            self.screen.blit(text , (7.5*s_width/10- (text.get_rect().size[0]/2), .8*s_height + (text.get_rect().size[1]/2)))

            #draw a small version of the final board
            self.game.board.draw_mini(self.screen, (s_width/2 - 150/2 ,200), 150)
            basicfont = pygame.font.Font("Kfont.ttf", 20)
            text = basicfont.render("Final Board", False, constants.BLACK)
            self.screen.blit(text , (s_width/2 - text.get_rect().size[0]/2, 170))
            pygame.display.update()

        #-------------------------
        #END2 - End the Tournament
        #-------------------------
        elif self.state == constants.game_state.END2:
            self.btn_coords = []
            self.screen.fill(constants.GREY)
            pygame.display.update()
            basicfont = pygame.font.Font("Kfont.ttf", 40)
            s_width, s_height = pygame.display.get_surface().get_size()
            text = basicfont.render("Tournament Over", False, constants.BLACK)
            self.screen.blit(text, (int(s_width/2 - text.get_rect().size[0]/2), int(.05 * s_height)))
            basicfont = pygame.font.Font("Kfont.ttf", 30)

            #determine who won the tournament
            if self.player1_score > self.player2_score:
                text = basicfont.render("Player 1 wins the Tournament", False, constants.BLACK)
            elif self.player2_score > self.player1_score:
                if self.game.player2.get_type() == "Human":
                    text = basicfont.render("Player 2 wins the Tournament", False, constants.BLACK)
                else:
                    text = basicfont.render("Computer wins the Tournament", False, constants.BLACK)
            else:
                text = basicfont.render("Tournament is a Tie", False, constants.BLACK)
            self.screen.blit(text, (s_width/2 - text.get_rect().size[0]/2, .2*s_height))

            basicfont = pygame.font.Font("Kfont.ttf", 25)
            text1 = basicfont.render("Player 1", False, constants.BLACK)
            text2 = basicfont.render("Player 2", False, constants.BLACK)
            self.screen.blit(text1, (2.5*s_width/10-text1.get_rect().size[0]/2, .35*s_height))
            self.screen.blit(text2, (7.5*s_width/10-text2.get_rect().size[0]/2, .35*s_height))
            #print the player's score
            text1 = basicfont.render(str(self.player1_score), False, constants.BLACK)
            text2 = basicfont.render(str(self.player2_score), False, constants.BLACK)
            self.screen.blit(text1, (2.5*s_width/10-text1.get_rect().size[0]/2, .45*s_height))
            self.screen.blit(text2, (7.5*s_width/10-text2.get_rect().size[0]/2, .45*s_height))
            button = pygame.image.load("button.png")
            button = pygame.transform.scale(button, (constants.BUTTON_WIDTH, constants.BUTTON_HEIGHT))
            button.convert()
            basicfont = pygame.font.Font("Kfont.ttf", 25)
            self.screen.blit(button, (2.5*s_width/10- (constants.BUTTON_WIDTH/2), .7*s_height))
            self.btn_coords.append(((2.5*s_width/10- (constants.BUTTON_WIDTH/2), .7*s_height),(2.5*s_width/10- (constants.BUTTON_WIDTH/2) + constants.BUTTON_WIDTH, .7*s_height+constants.BUTTON_HEIGHT)))
            text = basicfont.render("Restart", False, constants.BLACK)
            self.screen.blit(text , (2.5*s_width/10- (text.get_rect().size[0]/2), .7*s_height+ (text.get_rect().size[1]/2)))
            self.screen.blit(button, (7.5*s_width/10- (constants.BUTTON_WIDTH/2), .7*s_height))
            self.btn_coords.append(((7.5*s_width/10- (constants.BUTTON_WIDTH/2), .7*s_height),(7.5*s_width/10- (constants.BUTTON_WIDTH/2) + constants.BUTTON_WIDTH, .7*s_height+constants.BUTTON_HEIGHT)))
            text = basicfont.render("Quit", False, constants.BLACK)
            self.screen.blit(text , (7.5*s_width/10- (text.get_rect().size[0]/2), .7*s_height + (text.get_rect().size[1]/2)))
            pygame.display.update()

    #-------------------------
    #PROCESS BUTTON CLICK
    #takes a button click and decides how to handle it depending on the game state
    #PARAMETERS:
    #click_coord ((int, int)) - the x,y coordinates of the click
    #-------------------------
    def process_button_click(self, click_coord):
        #get the number of the button that was click (None if none were clicked)
        btn_click = self.detect_button_click(click_coord)
        #the number of the button that was clicked will do different things depending on the game state

        #-------------------------
        #START - Start Game
        #-------------------------
        if self.state == constants.game_state.START:
            #new game button
            if btn_click == 1:
                #set game state to choose number of players
                self.state = constants.game_state.PLAYERS
                self.render()
                btn_click = None

            #load a game button
            elif btn_click == 2:
                #set game state to load a game
                self.state = constants.game_state.LOAD
                self.render()
                btn_click = None

        #-------------------------
        #LOAD - Load Game
        #-------------------------
        elif self.state == constants.game_state.LOAD:
            if btn_click:
                #back button
                if btn_click == 1:
                    #go back to first game
                    self.state = constants.game_state.START
                    self.render()
                    btn_click = None
                #determine which save file was chosen
                elif int(btn_click) > 1:
                    #load the game with the proper save file
                    self.load_game(self.save_files[btn_click-2])
                    btn_click = None

        #-------------------------
        #PLAYERS - Choose Number of Players
        #-------------------------
        elif self.state == constants.game_state.PLAYERS:
            #1 human player button
            if btn_click == 1:
                #set number of players to 1
                self.temp_player_num = 1
                #roll dice
                self.state = constants.game_state.DICE1
                self.render()
                btn_click = None
            #2 human players button
            elif btn_click == 2:
                #set number of players to 1
                self.temp_player_num = 2
                #roll dice
                self.state = constants.game_state.DICE1
                self.render()
                btn_click = None

        #-------------------------
        #DICE1 - Choose Dice Roll
        #-------------------------
        elif self.state == constants.game_state.DICE1:
            #roll random dice button
            if btn_click == 1:
                self.state = constants.game_state.DICE2
                #roll dice without loading
                self.rolls = Kdice.roll_dice(False)
                self.render()
                btn_click = None
            #load dice button
            elif btn_click == 2:
                self.state = constants.game_state.DICE2
                #roll dice with loading
                self.rolls = Kdice.roll_dice(True)
                self.render()
                btn_click = None

        #-------------------------
        #DICE2 - Roll Dice
        #-------------------------
        elif self.state == constants.game_state.DICE2:
            #continue button
            if btn_click == 1:
                #first player (winner of the dice roll) was set during the dice roll
                #player 1 chooses the teams
                if self.temp_first == 1:
                    self.state = constants.game_state.TEAMS
                #player 2 choose the teams
                elif self.temp_first == 2:
                    #player 2 is a human
                    if self.temp_player_num == 2:
                        self.state = constants.game_state.TEAMS
                    #player 2 is a computer and must randomly choose a team
                    else:
                        self.state = constants.game_state.TEAMS2
                self.render()
                btn_click = None

        #-------------------------
        #TEAMS - Human Chooses a Team
        #-------------------------
        elif self.state == constants.game_state.TEAMS:
            #player chooses black team button
            if btn_click == 1:
                #player 1 did the choosing
                if self.temp_first == 1:
                    self.temp_teams = ("B", "W")
                #player 2 did the choosing
                else:
                    self.temp_teams = ("W", "B")
                self.state = constants.game_state.SIZE
                self.render()
                btn_click = None

            #player chooses white team button
            elif btn_click == 2:
                #player 1 did the choosing
                if self.temp_first == 1:
                    self.temp_teams = ("W", "B")
                #player 2 did the choosing
                else:
                    self.temp_teams = ("B", "W")
                self.state = constants.game_state.SIZE
                self.render()
                btn_click = None

        #-------------------------
        #TEAMS2 - Computer Chooses a Team
        #-------------------------
        #continue button
        elif self.state == constants.game_state.TEAMS2:
            if btn_click == 1:
                self.state = constants.game_state.SIZE
                self.render()

        #-------------------------
        #SIZE - Choose a Size
        #-------------------------
        elif self.state == constants.game_state.SIZE:
            #board size 5 button
            if btn_click == 1:
                self.state = constants.game_state.GAME
                #set board size to 5
                self.temp_size = 5
                #start the game
                self.start_game()
                self.render()
                #if the computer player moves first do their turn
                if self.game.player_number == 1 and self.game.turn_number == 2:
                    self.end_reason = self.computer_turn()
                btn_click = None
            #board size 7 button
            elif btn_click == 2:
                self.state = constants.game_state.GAME
                #set board size to 7
                self.temp_size = 7
                #start the game
                self.start_game()
                self.render()
                #if the computer player moves first do their turn
                if self.game.player_number == 1 and self.game.turn_number == 2:
                    self.end_reason = self.computer_turn()
                btn_click = None
            #board size 9 button
            if btn_click == 3:
                self.state = constants.game_state.GAME
                #set board size to 9
                self.temp_size = 9
                #start the game
                self.start_game()
                self.render()
                #if the computer player moves first do their turn
                if self.game.player_number == 1 and self.game.turn_number == 2:
                    self.end_reason = self.computer_turn()
                btn_click = None

        #-------------------------
        #GAME - Play the Game
        #-------------------------
        elif self.state == constants.game_state.GAME:
            #if the click is on the gameboard handle it differently
            if self.game.click_onboard(click_coord):
                #first move of the turn
                if not self.game.prev_piece:
                    #if there wasnt a previously selected piece (first half of the move)
                    if not self.game.two_clicks[0]:
                        #if the click is on a valid piece
                        if self.game.click_valid(click_coord):
                            #hold the first click
                            self.game.two_clicks[0] = click_coord
                            #select the piece and its valid moves
                            self.game.board.select(self.game.board.coord_to_pos(click_coord), 1)
                            moves = self.game.board.find_valid(self.game.board.coord_to_pos(click_coord))
                            for i in range(len(moves)):
                                if self.game.board.board[moves[i][0]][moves[i][1]][1] != 3:
                                    self.game.board.select(moves[i], 2)
                    #if there is a previously selected piece
                    else:
                        #hold the 2nd click
                        self.game.two_clicks[1] = click_coord
                        #deselect all pieces
                        self.game.board.reset_select()
                        move_coords = (self.game.board.coord_to_pos(self.game.two_clicks[0]),self.game.board.coord_to_pos(self.game.two_clicks[1]))
                        #if the two clicks form a valid move, make the move
                        if self.game.board.check_move (move_coords[0], move_coords[1]):
                            #make the move
                            turn = self.game.board.move_piece(move_coords[0], move_coords[1], self.screen, self.c)
                            #if the move finished the game, end the game
                            if turn:
                                #give the reason the game ended
                                self.end_reason = turn
                                self.state = constants.game_state.END1
                                self.render()
                            #record the move
                            self.game.log_move(move_coords)
                            #redraw only the board
                            self.game.board.draw(self.screen)
                            #set the previous piece (so its now the 2nd move)
                            self.game.prev_piece = move_coords[1]
                            #select the previous piece and its valid moves
                            self.game.board.select(self.game.prev_piece, 1)
                            moves = self.game.board.find_valid(self.game.prev_piece)
                            for i in range(len(moves)):
                                self.game.board.select(moves[i], 2)
                            #draw the button to end the turn
                            self.game.end_turn_btn = 1
                        #reset the two clicks
                        self.game.two_clicks = [None, None]

                #2nd Move of the turn
                else:
                    #the move is the piece that was previously moved and wherever was clicked now
                    move_coords = (self.game.prev_piece ,self.game.board.coord_to_pos(click_coord))
                    #reselect the correct pieces after each click
                    self.game.board.select(self.game.prev_piece, 1)
                    moves = self.game.board.find_valid(self.game.prev_piece)
                    for i in range(len(moves)):
                        #dont select if its already been selected by the help function
                        if self.game.board.board[moves[i][0]][moves[i][1]][1] != 3:
                            self.game.board.select(moves[i], 2)
                    #if move is valid execute it
                    if self.game.board.check_move(move_coords[0], move_coords[1]):
                        #deselect everything
                        self.game.board.reset_select()
                        #make move
                        turn = self.game.board.move_piece(move_coords[0], move_coords[1], self.screen, self.c)
                        #if the move ended the game, end the game
                        if turn:
                            self.end_reason = turn
                            self.state = constants.game_state.END1
                            self.render()
                        #record move
                        self.game.log_move(move_coords)
                        self.game.two_clicks = [None, None]
                        self.game.prev_piece = None
                        self.game.turn_number += 1
                        #remove button to end the turn
                        self.game.end_turn_btn = 0
                        self.render()
                        #if player 2 is a computer (and the board is not completed)
                        if self.temp_player_num == 1 and not self.game.board.complete:
                            turn = self.computer_turn()
                            if turn:
                                self.end_reason = turn
                                self.state = constants.game_state.END1
                                self.render()

            #save button
            elif btn_click == 1:
                #save the game
                self.save_game()
                #go back to the start
                self.state = constants.game_state.START
                self.render()
            #ask for help button
            elif btn_click == 2:
                #reset the two clicks
                self.game.two_clicks = [None, None]
                #if this is the first move of the turn
                #(advice is different depending on if its first or second move)
                if not self.game.end_turn_btn:
                    #if player 1 asked for help
                    if self.game.get_players_turn() == 1:
                        #get help
                        h = self.game.player1.help(self.game.board, (self.game.end_turn_btn+1))
                        self.game.text_log.append(h)
                    #if player 2 asked for help
                    elif self.game.get_players_turn() == 2:
                        #get help
                        h = self.game.player2.help(self.game.board, (self.game.end_turn_btn+1))
                        self.game.text_log.append(h)
                #if this is the 2nd move of the turn
                else:
                    #if player 1 asked for help
                    if self.game.get_players_turn() == 1:
                        #get help
                        h = self.game.player1.help(self.game.board, (self.game.end_turn_btn+1), self.game.prev_piece)
                        self.game.text_log.append(h)
                    #if player 2 asked for help
                    elif self.game.get_players_turn() == 2:
                        #get help
                        h = self.game.player2.help(self.game.board, (self.game.end_turn_btn+1), self.game.prev_piece)
                        self.game.text_log.append(h)

            #quit game button
            elif btn_click == 3:
                #calculate scores based on who quit
                self.game.current_scores(self.game.get_players_turn())

                #get the reason the game ended as whichever player quit the game
                if self.game.get_players_turn() == 1:
                    self.end_reason = "Player 1 Quit"
                elif self.game.get_players_turn() == 2:
                    if self.temp_player_num == 1:
                        self.end_reason = "Computer Quit"
                    else:
                        self.end_reason = "Player 2 Quit"

                #end the game
                self.state = constants.game_state.END1
                self.render()

            #end turn button
            elif btn_click == 4:
                #reset the turn
                moves=[]
                self.game.prev_piece = None
                self.game.turn_number += 1
                self.game.end_turn_btn = 0
                self.game.board.reset_select()
                #if the computer turn is next do the computer turn
                if self.temp_player_num == 1 and not self.game.board.complete:
                    #do computer turn
                    turn = self.computer_turn()
                    #if the turn ended the game, end the game
                    if turn:
                        self.end_reason = turn
                        self.state = constants.game_state.END1
                        self.render()

            #re-render the screen (as long as the game is still ongoing)
            if self.state == constants.game_state.GAME:
                self.render()

        #-------------------------
        #END1 - End the Round
        #-------------------------
        elif self.state == constants.game_state.END1:
            #play another round button
            if btn_click == 1:
                #player 1 won the game
                if self.game.player1.get_score() > self.game.player2.get_score():
                    #player 1 moves first next round
                    self.temp_first = 1
                    #player 1 choses the teams
                    self.state = constants.game_state.TEAMS
                #player 2 won the game
                elif self.game.player2.get_score() > self.game.player1.get_score():
                    #player 2 moves first next round
                    self.temp_first = 2
                    #player 2 is human
                    if self.game.player2.get_type == "Human":
                        #human choses teams
                        self.state = constants.game_state.TEAMS
                    #player 2 is computer
                    else:
                        #computer choses teams
                        self.state = constants.game_state.TEAMS2
                #game was a tie, reroll the dice
                else:
                    self.state = constants.game_state.DICE1

                #reset variables that are used to start a new game
                self.game = None
                self.temp_teams = [None, None]
                self.temp_size = None
                self.temp_load = None
                self.render()
                pygame.display.update()

            #end the tournament button
            elif btn_click == 2:
                #end the tournament
                self.state = constants.game_state.END2
                self.render()


        #-------------------------
        #END2 - End the Tournament
        #-------------------------
        elif self.state == constants.game_state.END2:
            #restart button
            if btn_click == 1:
                #reset the tournament
                self.new_tournament()
                self.render()
            #quit button
            elif btn_click == 2:
                #close the window
                pygame.quit()

    #-------------------------
    #DETECT BUTTON CLICK
    #takes x,y coordinates of a click and see if those coordinates coorespond to a button
    #PARAMETERS:
    #click_coord ((int, int)) - the x,y coordinates of the click
    #RETURNS: the button that was clicked or None
    #-------------------------
    def detect_button_click(self, click_coord):
        #make sure the click coord is in int
        click_coord = (int(click_coord[0]), int(click_coord[1]) )

        #loop through list of buttons and see if the click is on any of those buttons
        for i in range (len(self.btn_coords)):
            btn = self.btn_coords[i]
            #check if the click falls on the button
            if click_coord[0] > btn[0][0] and click_coord[0] < btn[1][0] and click_coord[1] > btn[0][1] and click_coord[1] < btn[1][1]:
                #return the number of the button that was clicked
                return(i+1)
        #if no button click return None
        return(None)

    #-------------------------
    #COMPUTER TURN
    #executes a turn for the computer player
    #RETURNS:
    #True - if the computer finished the game
    #False - if the computer did not finish the game
    #-------------------------
    def computer_turn(self):
        #stores the string that will be added to the game's textlog
        text_entry = None
        self.render()
        #get first move
        move1 = self.game.player2.do_move(self.game.board, self.game.screen, self.game.c, 1)
        #if the first move finishes the game
        if move1[0] == "complete":
            #end the round
            #calculate scores
            self.game.current_scores()
            #get reason the game ended
            self.end_reason = move1[1]
            self.state = constants.game_state.END1
            self.render()
            return
        #if the computer choses to quit
        if move1[0] == "quit":
            #end the round
            #calculate scores given that the computer quit
            self.game.current_scores(2)
            self.end_reason = "Computer Quit"
            self.state = constants.game_state.END1
            self.render()
            return

        #assuming the game didnt end create a text entry for the text log based on the move and the logic
        elif move1[0] == "capture":
            text_entry = "Computer Captured a Piece (" + self.game.board.pos_to_grid(move1[1][0]) + " to " +  self.game.board.pos_to_grid(move1[1][1]) + ")"
        elif move1[0] == "home":
            text_entry = "Computer move to a Home Position (" + self.game.board.pos_to_grid(move1[1][0]) + " to " +  self.game.board.pos_to_grid(move1[1][1]) + ")"
        elif move1[0] == "block":
            text_entry = "Computer moved foward and blocked a Piece (" + self.game.board.pos_to_grid(move1[1][0]) + " to " +  self.game.board.pos_to_grid(move1[1][1]) + ")"
        elif move1[0] == "foward":
            text_entry = "Computer moved foward (" + self.game.board.pos_to_grid(move1[1][0]) + " to " +  self.game.board.pos_to_grid(move1[1][1]) + ")"

        #add text entry to log
        if text_entry:
            self.game.text_log.append(text_entry)

        self.render()


        text_entry = None
        #get 2nd move
        move2 = self.game.player2.do_move(self.game.board, self.game.screen, self.game.c, 2, move1[1][1])

        #if the 2nd move completes the round
        if move2[0] == "complete":
            #end the round
            #calculate scores
            self.game.current_scores()
            #get the reason the round ended
            self.end_reason = move2[1]
            self.state = constants.game_state.END1
            self.render()
            return
        #assuming the game didnt end create a text entry for the text log based on the move and the logic
        if move2[0] == "capture":
            text_entry = "Computer Captured a Piece (" + self.game.board.pos_to_grid(move2[1][0]) + " to " +  self.game.board.pos_to_grid(move2[1][1]) + ")"
        elif move2[0] == "home":
            text_entry = "Computer move to a Home Position (" + self.game.board.pos_to_grid(move2[1][0]) + " to " +  self.game.board.pos_to_grid(move2[1][1]) + ")"
        elif move2[0] == "block":
            text_entry = "Computer moved foward and blocked a Piece (" + self.game.board.pos_to_grid(move2[1][0]) + " to " +  self.game.board.pos_to_grid(move2[1][1]) + ")"
        elif move2[0] == "foward":
            text_entry = "Computer moved foward (" + self.game.board.pos_to_grid(move2[1][0]) + " to " +  self.game.board.pos_to_grid(move2[1][1]) + ")"

        #add text entry to log
        if text_entry:
            self.game.text_log.append(text_entry)

        #end the turn
        self.game.turn_number += 1
        self.game.end_turn_btn = 0
        self.game.two_clicks = [None, None]
        self.game.prev_piece = None
        self.render()
        pygame.display.update()

        #check to see if the game should end
        if self.game.board.check_end():
            return self.game.board.check_end()
            return 1
        else:
            return 0
