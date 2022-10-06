"""
The question we're trying to answer is: 
When playing hot dice, how many points should I score before stopping and taking my score?

This means that we can ignore the first 1000 points needed to get on the board (we don't care about
that, we can calculate the probability separately)

What would be cool is a graph of the points earned over time based on the given strategies, especially
if it were averaged over time. Probably a pandas thing to do once we have the architecture here

What we'll need is:
    a way to evaluate scores
    a way to select between strategies
"""

# CONSTANTS
# ---------
NUMBER_OF_DICE = 6
NUMBER_OF_FACES = 6
MIN_REPEAT_MULTIPLES = 3

import play
import strategy
import numpy as np
import pandas as pd

# make this an autobuilder
class Game():
    """
    Defines our game object, which includes all of our game attributes like number of players, 
    winning_score, etc.
    """
    def __init__(s, winning_score = 10000):
        s.winning_score = winning_score

# should each player carry their stats object, or should that be passed between games...? 
class Player():
    """
    Defines our player object, who will use information to make decisions
    """
    def __init__(s, name, roll_strategy, score_strategy, roll_kwargs = {}, score_kwargs = {}):
        s.score_strategy = score_strategy
        s.roll_strategy = roll_strategy
        s.name = name
        s.roll_kwargs = roll_kwargs
        s.score_kwargs = score_kwargs
        s.turn_score = 0
        s.turn_remaining_dice = NUMBER_OF_DICE
        s.total_score = 0
        s.number_of_turns = 0
        s.number_of_busts = 0
        s.number_of_rolls = 0
        
    def bust(s):
        """
        Reset the turn score to 0
        """
        s.turn_score = 0
        s.turn_remaining_dice = NUMBER_OF_DICE
        s.number_of_turns += 1
        s.number_of_busts += 1
        return s
        
    def save_turn_score(s):
        """
        Add the turn score to the total score and reset turn score to 0 
        """
        s.total_score += s.turn_score
        s.turn_score = 0
        s.turn_remaining_dice = NUMBER_OF_DICE
        s.number_of_turns += 1
        return s
        
    def score_choice(s, game, scores):
        """
        Make a choice as to which of the scores the player wants to take.
        
        Accepts a game object, and a scores dataframe
        
        Uses the score_strategy function to make the choice
        """
        # add a column for ratings that will be applied to each score
        scores['Rating'] = 0
        
        # send the scores to be rated, take the one with the highest rating, if tie, take the first
        selected_score = s.score_strategy(s, scores, game).nlargest(1, 'Rating')
        
        # add the selected score to this turns's score
        s.turn_score += int(selected_score.Score)
        
        # calculate the number of dice remaining for the next roll
        s.turn_remaining_dice = len(selected_score.Remaining)
        
        return selected_score
    
    def roll_again(s, game, **kwargs):
        """
        Make a choice as to whether or not to roll again. 
        
        Return True to roll again
        """
        roll_again = s.roll_strategy(s, game, **kwargs, **s.roll_kwargs)

        if roll_again: s.number_of_rolls += 1

        return roll_again

    def end_turn(s):
        """
        End the player's turn
        """
        s.total_score += s.turn_score
        s.turn_score = 0
        s.turn_remaining_dice = NUMBER_OF_DICE
    
    def reset(s):
        """
        Reset all stats and scores
        """
        s.end_turn()
        s.total_score = 0
        s.number_of_rolls = 0
        s.number_of_busts = 0
        s.number_of_turns = 0
        
        return s

def main(sample=10000):
    """
    Run a loop that plays hotdice with different Players that have various combinations of 
    strategies
    """
    columns = ['Name', 'Target', 'RollStrat', 'ScoreStrat', 'Turns', 'Busts', 'Rolls']
    results = pd.DataFrame(columns=columns)
    
    game = Game()
    num_samples_per_player = sample
    
    # samples = [100, 200, 300, 400, 500, 600]
    # samples = [450, 500, 550, 600, 650, 700]
    # samples = [450, 475, 500, 525, 550]
    # samples = [450, 475, 487, 500, 513, 525, 550]
    # samples = [450, 500, 550]
    samples = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]

    players = [Player(f'{target_score}hardstop-bestper', strategy.roll_stop_at_unless_hotdice, 
                                strategy.score_best_per_dice_exclude_hot_dice, 
                                roll_kwargs={'target_score':target_score}) \
                         for target_score in samples]


    # things to explore: 
    # 1. Do different player mixes at all change player strategies?
    # 2. Have I enumerated all possible player strategies?
    # 3. Have I tested all possible player strategy combinations? 
    # 4. Could play.human_play() be made into a strategy?
    # 5. Does real human play differ from the strategies I've enumerated? 
    # 6. Is it possible to log the data that comes out of these strategies for future comparison?
    # 7. 
    
    for player in players:
        print(f'\n{player.name}', end='')
        for n in range(num_samples_per_player):
            if n % 10 == 0: print('.', end='')
            # pretend as though this is a new player (reset all of this player's score)
            player.reset()
            # play a single game
            player = play.play(game, player)
            # get the results and add it to the massive results dataframe
            results = pd.concat([results, pd.DataFrame([[player.name, player.roll_kwargs['target_score'], 
                                                    player.roll_strategy.__name__, 
                                                    player.score_strategy.__name__, 
                                                    player.number_of_turns, 
                                                    player.number_of_busts, 
                                                    player.number_of_rolls]], columns=columns)
                                ])
            
    results = results.astype({'Target':int, 'Turns':int, 'Busts':int, 'Rolls':int})
    return results
        
    
if __name__ == '__main__':
    main()