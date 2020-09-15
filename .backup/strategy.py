"""
Players can have different strategies when it comes to playing hot dice.

Essentially, they can have either roll strategies, or score selection strategies

All scores must have ratings by the time they are passed in
"""

from hotdice import NUMBER_OF_DICE, NUMBER_OF_FACES, MIN_REPEAT_MULTIPLES 
# 
# def roll_(s, n_dice, other_player_scores, my_current_score, winning_score, last_roll_boolean, am_I_on_the_board, ):
#     """
#     A class method
# 
#     Rolls again if 
#     """
#     pass

def roll_stop_at(s, game, target_score):
    """
    Roll again unless target score is reached / passed
    """
    if s.round_score >= target_score:
        return False
    else:
        return True

def roll_stop_at_unless_hotdice(s, game, target_score):
    """
    Roll again unless target score is reached / passed or if you have hotdice
    """
    if roll_stop_at(s, game, target_score) or target_score == NUMBER_OF_DICE:
        return True
    else:
        return False

def score_triple_2_bad(s, scores, game):
    """
    Reduce the attractiveness of triple 2s
    """
    scores.loc[scores.Roll.map(lambda x: x.count(2) == 3)]['Rating'] -= 1
    return scores

def score_big_better(s, scores, game):
    """
    Higher scores get better ratings. Simple.
    """
    # should already be sorted, but just in case
    # make the rating more negative for worse scores
    scores['Rating'] = scores.sort_values(['Score']).reset_index().index * -1
    return scores

def score_best_per_dice(s, scores, game, discount_factor=1):
    """
    Higher scores get better ratings, but are made a bit smaller if a score requires many dice

    the discount_factor lets you say how big of an effect you want to see. Bigger number == more 
    discount
    """
    scores = score_big_better(s, scores, game)
    
    # this is just to make the division work (no 0s involved)
    offset = len(scores.index) + 1
    
    scores['Rating'] = scores.Rating + offset
    
    scores['Rating'] = scores.apply(lambda x: x.Rating - (len(x.Roll) + 1), axis=1) - offset
    # alternatively, you could discount by this clever contraption: 
    # / (((len(x.Roll) - 1) * discount_factor) + 1)
    
    return scores

def score_best_per_dice_exclude_hot_dice(s, scores, game, discount_factor=1):
    """
    Same as best scores, but don't discount things that would give us hot dice
    """
    scores = score_big_better(s, scores, game)
    
    scores_weighted = score_best_per_dice(s, scores.loc[scores.Roll.map(lambda x: len(x) < NUMBER_OF_DICE)], 
                                            discount_factor, game)
    
    scores = scores_weighted.join(scores.loc[~scores_weighted], how='outer')
    
    return scores

def score_avoid_fives(s, scores, game, five_cost = 1):
    """
    When possible, don't take single fives
    """
    non_multiples = scores.loc[scores.Type != 'multiple']
    
    fives_cost['Rating'] += non_multiples.apply(lambda x: x.Roll.count(5) * five_cost * -1, axis=1)
    
    non_multiples_discounted =  non_multiples.Rating - fives_cost
    
    scores = non_multiples_discounted.join(scores.loc[~non_multiples_discounted], how='outer')
    
    return scores