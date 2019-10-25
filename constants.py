import enum

class game_state(enum.Enum):
    START = 1
    LOAD = 2
    PLAYERS = 3
    DICE1 = 4
    DICE2 = 5
    TEAMS = 6
    TEAMS2 = 7
    SIZE = 8
    GAME = 9
    END1 = 10
    END2 = 11
#Constants

#Window Dimension Constants
BOARD_DIMENSION = 400
BUTTONS_AREA_HEIGHT = 150
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 60
TURN_HEIGHT = 50
TEXT_WIDTH = 450

#Color Constants
BLACK = (0,0,0)
WHITE = (255,255,255)
GREY = (170,170,170)
DARK_GREY = (75,75,75)
# YELLOW = (255, 200, 0)


#scoring constants
SCORE_BLACK_5 = (
3,1,5,1,3,
1,0,0,0,1,
0,0,0,0,0,
0,0,0,0,0,
0,0,0,0,0
)

SCORE_WHITE_5 = (
0,0,0,0,0,
0,0,0,0,0,
0,0,0,0,0,
1,0,0,0,1,
3,1,5,1,3
)
SCORE_BLACK_7 = (
3,1,5,7,5,1,3,
1,0,0,0,0,0,1,
0,0,0,0,0,0,0,
0,0,0,0,0,0,0,
0,0,0,0,0,0,0,
0,0,0,0,0,0,0,
0,0,0,0,0,0,0
)

SCORE_WHITE_7 = (
0,0,0,0,0,0,0,
0,0,0,0,0,0,0,
0,0,0,0,0,0,0,
0,0,0,0,0,0,0,
0,0,0,0,0,0,0,
1,0,0,0,0,0,1,
3,1,5,7,5,1,3,
)
SCORE_BLACK_9 = (
3,1,5,7,9,7,5,1,3,
1,0,0,0,0,0,0,0,1,
0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,
)
SCORE_WHITE_9 = (
0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,
1,0,0,0,0,0,0,0,1,
3,1,5,7,9,7,5,1,3,
)

#Test Constants
# TText = [
# "Test1",
# "Test2",
# "Test3",
# "Test4",
# "Test5",
# "Test6",
# "Test7",
# "Test8",
# "Test9",
# "Test10",
# "Test11",
# "Test12",
# "Test13",
# "Test14",
# "Test15",
# "Test16",
# "Test17",
# "Test18",
# "Test19",
# "Test20",
# "Test21",
# "Test22",
# "Test23",
# "Test24",
# "Test25",
# "Test26",
# "Test27",
# "Test28",
# "Test29",
# "Test30",
# "Test31",
# "Test32",
# "Test33",
# "Test22",
# "Test23",
# "Test24",
# "Test25",
# "Test26",
# "Test27",
# "Test28",
# "Test29",
# "Test30",
# "Test31",
# "Test32",
# "Test33",
# "Try moving foward and blocking a piece (A4 to B5)",
# ]
