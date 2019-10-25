#-------------------------
#Alec Barton
#Kdice.py
#-------------------------

import random
import os

#-------------------------
#ROLL DICE
#generates dice rolls
#PARAMETERS:
#load (bool) - true if loading the dice from a file, false if not
#RETURNS: tuple
#[0] - player1's rolls
#[1] - player2's rolls
#[2] - number of player that wins the dice roll
#-------------------------
def roll_dice(load):
    #lists to hold the rolls
    all_rolls = []
    p1_rolls = []
    p2_rolls = []

    #load the dice rolls from a txt file
    if load:
        try:
            #open the txt file
            f = open('dice.txt')
            #split entire file into individual rolls
            for roll in f.read().split():
                all_rolls.append(roll)

            #divides the rolls into player1's and player2's
            i = 0
            while i < len(all_rolls):
                p1_rolls.append(all_rolls[i])
                p1_rolls.append(all_rolls[i+1])
                p2_rolls.append(all_rolls[i+2])
                p2_rolls.append(all_rolls[i+3])
                i+=4
            #if there is an uneven number of rolls for player1 and player 2, shorten one so they are even
            if len(p1_rolls) != len(p2_rolls):
                p1_rolls[:len(p2_rolls)]
        except:
            #if cannot load the dice from file generate dice rolls instead
            return(roll_dice(False))

    #randomly generate the dice rolls
    else:
        #loops as long as the dice rolls are a tie
        while 1:
            #generates the dice rolls
            p1_rolls.append(random.randint(1,6))
            p1_rolls.append(random.randint(1,6))
            p2_rolls.append(random.randint(1,6))
            p2_rolls.append(random.randint(1,6))

            if p1_rolls[len(p1_rolls)-1]+p1_rolls[len(p1_rolls)-2] != p2_rolls[len(p2_rolls)-1]+p2_rolls[len(p2_rolls)-2]:
                #breaks when a winner can be declared
                break

    #holds the total scores of the dice rolls
    p1_total = 0
    p2_total = 0

    #totals up the scores of each player
    for i in p1_rolls:
        p1_total += int(i)
    for i in p2_rolls:
        p2_total += int(i)

    #declares a winner of the dice roll
    if p1_total > p2_total:
        dice_winner = 1
    elif p2_total > p1_total:
        dice_winner = 2

    #returns the rolls and the winner
    return (p1_rolls, p2_rolls, dice_winner)
