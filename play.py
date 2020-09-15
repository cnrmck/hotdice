"""
"""
import score
import click
import numpy as np
import itertools as it

from hotdice import NUMBER_OF_DICE, NUMBER_OF_FACES, MIN_REPEAT_MULTIPLES

def roll_dice(n=NUMBER_OF_DICE):
    "Roll n dice"
    return tuple(np.random.randint(1, 7, n))

def play(game, player):
    """
    A main loop that plays a single game of hotdice with a single player
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
        
        # the player chooses whether to roll again
        if player.roll_again(game):
            # the player has hot dice
            if player.round_remaining_dice == 0:
                # roll all the dice
                roll = roll_dice()
            else:
                roll = roll_dice(player.round_remaining_dice)
                
        else:
            # the player has decided to stop, so they get to keep their round score
            player.save_round_score()
            
    return player

def human_play():
    """
    A main loop that can be run for a single human player to play a single round
    """
    total_score = 0
    round_score = 0
    roll = roll_dice()
    while True:
        scores = score.scores(roll)
        
        if len(scores) == 0:
            print("\n\nBust!")
            print("Next round\n")
            round_score = 0
            roll = roll_dice()
            continue
        
        # makes it nicer to read for humans
        scores['Remaining'] = scores.apply(lambda x: len(x.Remaining), axis=1)
        scores.drop(columns=['Type'], inplace=True)
        
        print(scores)
        score_index = int(click.prompt('Which score do you want to take?', 
                                   type=click.Choice(scores.index.astype(str)), default=0))
        
        selected_roll = scores.loc[scores.index == score_index]
        selected_score = int(selected_roll.Score)
        round_score += int(selected_roll.Score)
        remaining_die = int(selected_roll.Remaining)
        
        print(f"Added {selected_score} points.\nScore: {round_score}")
        roll_again = click.prompt(f'Do you want to roll again? ({remaining_die if remaining_die != 0 else NUMBER_OF_DICE} dice)', 
                             type=click.Choice(['Y', 'n']), default='Y')
        
        if roll_again is 'Y':
            if remaining_die == 0:
                roll = roll_dice()
            else:
                roll = roll_dice(remaining_die)
        else:
            total_score += round_score 
            print(f"Adding {round_score} to your total score.\nTotal now: {total_score}")
            print("Next round\n")
            round_score = 0
    
    print(f"Total Score: {total_score}")
    
if __name__ == '__main__':
    human_play()