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
        s.round_score = 0
        s.round_remaining_dice = NUMBER_OF_DICE
        s.total_score = 0
        s.number_of_rounds = 0
        s.number_of_busts = 0
        s.number_of_rolls = 0
        
    def bust(s):
        """
        Reset the round score to 0
        """
        s.round_score = 0
        s.round_remaining_dice = NUMBER_OF_DICE
        s.number_of_rounds += 1
        s.number_of_busts += 1
        return s
        
    def save_round_score(s):
        """
        Add the round score to the total score and reset round score to 0 
        """
        s.total_score += s.round_score
        s.round_score = 0
        s.round_remaining_dice = NUMBER_OF_DICE
        s.number_of_rounds += 1
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
        
        # add the selected score to this round's score
        s.round_score += int(selected_score.Score)
        
        # calculate the number of dice remaining for the next roll
        s.round_remaining_dice = len(selected_score.Remaining)
        
        return selected_score
    
    def roll_again(s, game):
        """
        Make a choice as to whether or not to roll again. 
        
        Return True to roll again
        """
        s.number_of_rolls += 1
        return s.roll_strategy(s, game, **s.roll_kwargs)
    
    def reset(s):
        """
        Reset all stats and scores
        """
        s.round_score = 0
        s.round_remaining_dice = NUMBER_OF_DICE
        s.total_score = 0
        s.number_of_rounds = 0
        s.number_of_busts = 0
        s.number_of_rolls = 0
        
        return s

def main():
    """
    Run a loop that plays hotdice with different Players that have various combinations of 
    strategies
    """
    # the list of players to use
    # players = []
    columns = ['Name', 'Target', 'RollStrat', 'ScoreStrat', 'Rounds', 'Busts', 'Rolls']
    results = pd.DataFrame(columns=columns)
    
    game = Game()
    num_samples_per_player = 10000
    # [250, 300, 350, 400, 450, 500, 550, 600, 650, 700]
    
    players = [Player(f'{target_score}softstop-bestper', strategy.roll_stop_at_unless_hotdice, 
                                strategy.score_best_per_dice_exclude_hot_dice, 
                                roll_kwargs={'target_score':target_score}) \
                         for target_score in [650]]
    
    for player in players:
        print(f'\n{player.name}', end='')
        for _ in range(num_samples_per_player):
            print('.', end='')
            # pretend as though this is a new player (reset all of this player's score)
            player.reset()
            # play a single game
            player = play.play(game, player)
            # get the results and add it to the massive results dataframe
            results = results.append(pd.DataFrame([[player.name, player.roll_kwargs['target_score'], 
                                                    player.roll_strategy.__name__, 
                                                    player.score_strategy.__name__, 
                                                    player.number_of_rounds, 
                                                    player.number_of_busts, 
                                                    player.number_of_rolls]], columns=columns))
            
    results = results.astype({'Target':int, 'Rounds':int, 'Busts':int, 'Rolls':int})
    return results
        
    
if __name__ == '__main__':
    main()