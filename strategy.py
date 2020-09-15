"""
Players can have different strategies when it comes to playing hot dice.

Essentially, they can have either roll strategies, or score selection strategies

All scores must have ratings by the time they are passed in
The player object generally just selects the roll with the best rating.
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

def score_best_per_dice(s, scores, game, marginal_value_of_die=67):
    """
    Higher scores get better ratings, but are made a bit smaller if a score requires many dice

    the marginal_value_of_die lets you say how big of an effect you want to see. 
    Bigger number == more discount
    
    The default was computed by guessing the expected value (ev) of a single die is roughly 66.66
        However, this could be made smarter by computing the ev given (|) the # of die remaining
        Doing so would require a bunch of additional work, as ev | #die is strategy dependent
    
    """
    # scores = score_big_better(s, scores, game)
    
    # scores = scores.Score - (scores.Remaining.map(len) * marginal_value_of_die)
    
    scores['Rating'] = ((scores.Remaining.map(len) * marginal_value_of_die) + scores.Score).rank()
    
    # norm to make 0 the max
    scores['Rating']= scores.Rating - scores.Rating.max()
    
    scores['Len'] = scores.apply(lambda x: len(x.Roll), axis=1)
    scores = scores.sort_values('Len', ascending=False).sort_values('Rating', ascending=False).drop(columns=['Len'])
    
    return scores

def score_best_per_dice_exclude_hot_dice(s, scores, game, discount_factor=1):
    """
    Same as best scores, but don't discount things that would give us hot dice
    """
    
    scores_weighted = score_best_per_dice(s, 
                                          scores.loc[scores.Roll.map(lambda x: len(x) < NUMBER_OF_DICE)], 
                                          game)
    scores_weighted = scores_weighted.append(scores.loc[~scores.index.isin(scores_weighted.index)]).sort_values(['Rating', 'Score'], ascending=False)
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