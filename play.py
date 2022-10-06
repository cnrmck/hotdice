"""
"""
import time
import score
import click
import numpy as np
import itertools as it

from hotdice import NUMBER_OF_DICE, NUMBER_OF_FACES, MIN_REPEAT_MULTIPLES

def roll_dice(n=NUMBER_OF_DICE, face=NUMBER_OF_FACES):
    "Roll n dice"
    return tuple(np.random.randint(1, face+1, n))

def human_roll(n=NUMBER_OF_DICE, face=NUMBER_OF_FACES):
    print(f"Rolling {n} die...", end='')
    time.sleep(1)
    return roll_dice(n=n, face=face)

def play(game, player):
    """
    A main loop that plays a single turn of hotdice with a single player
    """
    
    # roll get the first roll
    roll = roll_dice()
    
    while player.total_score < game.winning_score:
        # get the players scores for this roll
        scores = score.scores(roll)
        
        if len(scores) == 0:
            player.bust()
            roll = roll_dice()
            continue
        
        # ask the player to select their score
        score_selection = player.score_choice(game, scores)
        
        hotdice = player.turn_remaining_dice == 0

        # the player chooses whether to roll again
        if player.roll_again(game, hotdice = hotdice):
            # the player has hot dice
            if hotdice:
                # roll _all_ the dice!
                roll = roll_dice()
            else:
                roll = roll_dice(player.turn_remaining_dice)
                
        else:
            # the player has decided to stop, so they get to keep their turn score
            player.save_turn_score()
            
    return player

def human_play():
    """
    A main loop that can be run for a single human player to play a single turn
    """
    total_score = 0
    turn_score = 0
    roll = human_roll()
    remaining_die = NUMBER_OF_DICE

    while True:
        scores = score.scores(roll)
        
        if len(scores) == 0:
            print("Bust!")
            time.sleep(2)
            print(f"Turn Score: {turn}\nTotal Score: {total_score}")
            print("Next turn\n")
            time.sleep(1)
            turn_score = 0
            roll = human_roll()
            continue
        
        # makes it nicer to read for humans
        scores['Remaining'] = scores.apply(lambda x: len(x.Remaining), axis=1)
        scores.drop(columns=['Type'], inplace=True)
        
        print()
        print(scores)
        score_index = int(click.prompt('Which score do you want to take?', 
                                   type=click.Choice(scores.index.astype(str)), default='0'))
        
        selected_roll = scores.loc[scores.index == score_index]
        selected_score = int(selected_roll.Score)
        turn_score += int(selected_roll.Score)
        remaining_die = int(selected_roll.Remaining)
        
        print(f"Added {selected_score} points.\nScore: {turn_score}")
        roll_again = click.prompt(f'Do you want to roll again? ({remaining_die if remaining_die != 0 else NUMBER_OF_DICE} dice)', 
                             type=click.Choice(['Y', 'n']), default='Y')
        
        if roll_again == 'Y':
            if remaining_die == 0:

                roll = human_roll()
            else:
                roll = human_roll(remaining_die)
        else:
            total_score += turn_score 
            print(f"Adding {turn_score} to your total score.\nTotal now: {total_score}")
            print("Next turn\n")
            turn_score = 0
            roll = human_roll()
    
    print(f"Total Score: {total_score}")
    
if __name__ == '__main__':
    human_play()