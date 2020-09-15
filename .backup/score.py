"""
This file will calculate the possible earned scores of a particular roll. 
This returns a pandas dataframe with all possible scoring combinations. Combinations, in this case, 
refers to all ways of scoring that use different dice (a powerset). 

E.g. 
Accepted:
5, 5
1, 5
2, 2, 2
1, 1, 5, 5

Redundant with above list and excluded:
5, 1
5, 1, 1, 5

(In other words, if we can rearrange the roll to be the same as a prior roll, then it's redundant)


Throughout this program, 0 is treated as a die that cannot be rolled.

This assumes that when there are multiple rolls with different scores (like 1,1,1,5 can be scored 
as 1050 or as 350) the largest is taken
"""

import math
import utils as ut
import pandas as pd
from hotdice import NUMBER_OF_DICE, NUMBER_OF_FACES, MIN_REPEAT_MULTIPLES 

# silence the SettingWithCopyWarning
pd.options.mode.chained_assignment = None  # default='warn'

# CONSTANTS:
# ---------
ONES_SCORE = 100
FIVES_SCORE = 50
STRAIGHT_SCORE = 1500
MULTIPLES_SCORE = {1:1000, 2:200, 3:300, 4:400, 5:500, 6:600}
DIE_SCORES = {1:100, 5:50}

# the index to be used on all score DataFrames
SCORE_COLUMNS = ['Score', 'Remaining', 'Type', 'Roll']

def score_straights(roll):
    """
    Look for and score a straight.
    
    >>> score_straight([1,2,3,4,5,6])
    
    >>> score_straight([2,3,1,6,5,4])
    
    >>> score_straight([1,2,2,3,4,5])
    
    >>> score_straight([0,1,2,3,4,5])
    
    """
    # what to return in the case of no straight or a straight
    no_straight = pd.DataFrame(data=[[0, roll, 'straight', tuple()]], columns=SCORE_COLUMNS)
    straight = pd.DataFrame(data=[[STRAIGHT_SCORE, tuple(), 'straight', tuple(roll)]], 
                         columns=SCORE_COLUMNS)
    
    # if there are any 0s in the roll we can't have a straight
    if 0 in roll:
        # not a straight
        return no_straight
    
    # another quick check: if the roll contains duplicates it can't be a straight
    if len(set(roll)) != NUMBER_OF_DICE:
        return no_straight
    
    # sort the roll
    sorted_roll = sorted(roll)
    
    previous_die = sorted_roll[0]
    # check all but the first die
    for die in sorted_roll[1:]:
        # check if the difference between the die and the previous_die is exactly 1
        if (die - previous_die) == 1:
            previous_die = die
        else:
            # the difference was more than 1 at least once. Can't be a straight
            return no_straight
        
    # if every die was one away from the previous die then it's a straight
    return straight

def score_multiples(roll):
    """
    Look for a multiples score. Multiple numbers of the same type
    
    >>> score_multiples([1,1,1,2,3,4])
    
    >>> score_multiples([1,3,3,1,3,3])
    
    >>> score_multiples([1,2,1,3,1,0])
    
    >>> score_multiples([1,2,1,3,0,4])
    
    >>> score_multiples([1,1,1,2,2,2])
    
    """
    no_multiple = pd.DataFrame(data=[[0, roll, 'multiple', tuple()]], columns=SCORE_COLUMNS)
    multiples = pd.DataFrame(data=[[0, roll, 'multiple', tuple()]], columns=SCORE_COLUMNS)
    
    # if there isn't a difference of at least 2 between the set size and the list then no multiple
    if len(roll) - len(set(roll)) < MIN_REPEAT_MULTIPLES - 1:
        return no_multiple
    
    # get all the numbers (n) w/ at least the min number of duplicates and the count of duplicates
    multiples_dict = {n: roll.count(n) for n in set(roll) if roll.count(n) >= MIN_REPEAT_MULTIPLES and n != 0}
    
    multiples_list = []
    for num, count in multiples_dict.items():
        # TODO: Now that score combinations works, we can optionally remove this section
        # account for the fact that you could take a score of 300 after rolling 3,3,3,3
        # dice_to_count here just means, "the number that we will count toward the score"
        for dice_to_count in range(MIN_REPEAT_MULTIPLES, count+1):
            # account for the fact that 2,2,2 is 200 (score*1) but 2,2,2,2,2 is 800 (score*2**2)
            score_multiplier = 2**(dice_to_count - MIN_REPEAT_MULTIPLES)
            
            # convert [3,3,3,3,2,4] to [0,0,0,3,2,4] if dice_to_count is 3
            remaining = []
            num_counted = 0
            for die in roll:
                # the die is not the number we care about
                if die != num:
                    remaining.append(die)
                # it is the one we care about and we haven't counted enough yet
                elif num_counted < dice_to_count:
                    num_counted += 1
                # we've counted enough of them, add the die even though it's the num we care about
                else:
                    remaining.append(die)
            
            # add it to the multiples list
            multiples_list.append([MULTIPLES_SCORE[num] * score_multiplier, 
                              tuple(remaining),
                              'multiple',
                              ut.difference(roll, remaining)])
            
    # create a DataFrame from the list
    multiples = multiples.append(pd.DataFrame(multiples_list, columns=SCORE_COLUMNS))
    return multiples

def score_dice(roll):
    """
    Look for individual scoring die and all of the combinations possible
    """
    scores = pd.DataFrame(data=[[0, roll, 'individual', tuple()]], columns=SCORE_COLUMNS)
    dice_that_score = list(DIE_SCORES.keys())
    
    # find the dice in the roll that score points
    scoring_dice = [die for die in roll if die in dice_that_score]
    
    combinations = list(ut.powerset(scoring_dice))
    
    # only include the rolls that couldn't score multiples
    combinations_no_multiples = set(tuple(sorted(combo)) for combo in combinations if max([combo.count(n) for n in set(combo)]) < MIN_REPEAT_MULTIPLES)
    
    scores_list = []
    for combo in combinations_no_multiples:
        remaining = ut.difference(roll, combo)
        score = sum((DIE_SCORES[die] for die in combo))
        scores_list.append([score, remaining, 
                            'individual', combo])
        
    scores = scores.append(pd.DataFrame(scores_list, columns=SCORE_COLUMNS))
        
    return scores

def get_score_and_type(row, scores):
    """
    Find the score for a given row and the type (or types) of scoring used.
    
    E.g. [1,1,1,5,5,6] could have a score of 1100 and a type of ('multiple', 'individual')
    
    return as a tuple
    """
    matches = scores.loc[scores.Roll.isin(row.ScoringRoll)]
    
    score = matches.Score.sum()
    
    score_type_set = set(matches.Type)
    score_type = tuple(score_type_set) if len(score_type_set) > 1 else score_type_set.pop()
    
    return score, score_type

def score_combinations(scores, roll):
    """
    Find all score combinations. This means that you take a given set of scores (e.g. the rolls 
    (1,1,1), (5), (1,5), (1,1), (1,1,5)) for a given roll (1,1,1,4,2,5) and you see if you can make
    any new combinations. E.g. (1,1,1,5) is possible in this example
    
    Arguments:
    scores - a score dataframe (should have all the columns found in SCORE_COLUMNS)
    roll - the roll associated with these scores
    """
    no_new_combinations = pd.DataFrame(columns=SCORE_COLUMNS)
    all_scores = pd.DataFrame()
    
    scoring_rolls = scores[scores.Score > 0].Roll
    
    # all possible sets of rolls that could contain
    all_scores['ScoringRoll'] = pd.Series(data=ut.powerset(scoring_rolls))
    all_scores['CandidateRoll'] = all_scores.ScoringRoll.map(lambda x: tuple(sorted(list(ut.merge_tuple(x))[0])))
    
    all_scores = all_scores.loc[all_scores.CandidateRoll.map(lambda x: len(x) <= NUMBER_OF_DICE)]
    possible_rolls = all_scores.loc[all_scores.CandidateRoll.map(lambda x: ut.intersection(x, roll) == x)]
    new_rolls = possible_rolls.loc[~possible_rolls.CandidateRoll.isin(scoring_rolls)]
    
    if len(new_rolls) == 0:
        return no_new_combinations
    
    new_rolls['Score'], new_rolls['Type'] = zip(*new_rolls.apply(get_score_and_type, args=(scores,), axis=1))
    new_rolls_best_score = new_rolls.loc[~(new_rolls.sort_values('Score', ascending=False).duplicated(['CandidateRoll'], keep='first')) | ~(new_rolls.duplicated(['CandidateRoll'], keep=False))]
    # print(new_rolls_best_score)
    new_rolls_best_score = new_rolls_best_score.drop(columns='ScoringRoll').rename(columns={'CandidateRoll':'Roll'})
    new_rolls_best_score['Remaining'] = new_rolls_best_score.Roll.map(lambda x: ut.difference(roll, x))
    
    # FIXME: type should probably be changed to be a combination of all types used ('individual', 'multiple')
    # new_rolls_best_score['Type'] = 'combination'
    return new_rolls_best_score
    

def scores(roll):
    """
    Accept a roll (a list of dice, e.g. [1,2,3,4,4,6]) and return a pandas DataFrame with the 
    possible scores.
    
    This function uses score* functions. score* functions are expected to accept a roll and return
    a pandas Series or DataFrame that can be concatenated to the possible_scores DataFrame
    """
    scores = pd.concat([score_straights(roll), score_multiples(roll), score_dice(roll)], 
                                axis=0, sort=True).reset_index()
    
    # now we need to find out if we can combine the rolls into larger combos (and higher scores)
    # E.g. [1,1,1,2,2,2] is already scored as (1,1,1) and (2,2,2) but could also be (1,1,1,2,2,2)
    scores = pd.concat([scores, score_combinations(scores, roll)], axis=0, sort=True).sort_values(['Score'], ascending=False).reset_index()
    
    scores = scores.drop(columns=['index', 'level_0']).fillna(0)
    return scores.loc[scores.Score > 0][['Roll', 'Score', 'Remaining', 'Type']]
    
def manual():
    scores([1,2,3,4,5,6])
    
def test():
    """
    A mini testing suite
    """
    from collections import namedtuple
    fn_map = {'all':scores, 
              'straight':score_straights, 
              'multiple':score_multiples, 
              'individual':score_dice}
    
    # in the case where there can be multiple scores, use the max score
    score = namedtuple('score', list(fn_map.keys()))
    tests = {
        (1,1,1,1,1,1): score(8000, 0,    8000, 200),
        (1,2,3,4,5,6): score(1500, 1500, 0,    150),
        (1,3,4,2,6,5): score(1500, 1500, 0,    150),
        (2,1,5,3,6,4): score(1500, 1500, 0,    150),
        (1,1,5,5,6,6): score(300,  0,    0,    300),
        # these next two are great for testing combination scores
        (1,1,1,3,4,5): score(1050, 0,    1000, 250),
        # this one is only 1000 for the multiples because the multiples function doesn't do combos
        (1,1,1,5,5,5): score(1500, 0,    1000, 300),
        #
        (3,3,3,4,6,6): score(300,  0,    300,  0),
        (3,3,3,3,5,1): score(750,  0,    600,  150),
        (0,0,0,0,0,0): score(0,    0,    0,    0),
        (1,2,3,4,5,0): score(150,  0,    0,    150),
        (6,6,6,0,6,6): score(2400, 0,    2400, 0),
        (2,3,3,2,6,6): score(0,    0,    0,    0),
        (0,1,0,0,0,0): score(100,  0,    0,    100),
        # 20 randomly generated rolls follow (with hand set scores)
        (1,1,2,5,4,2): score(250,  0,    0,    250),
        (1,3,1,1,6,4): score(1000, 0,    1000, 200),
        (2,2,5,2,3,6): score(250,  0,    200,  50),
        (2,2,2,2,2,2): score(1600, 0,    1600, 0),
        (3,1,1,2,3,6): score(200,  0,    0,    200),
        (6,4,2,5,6,3): score(50,   0,    0,    50),
        (5,4,2,4,6,3): score(50,   0,    0,    50),
        (3,3,1,5,2,3): score(450,  0,    300,  150),
        (1,3,3,3,6,2): score(400,  0,    300,  100),
        (5,2,3,4,4,3): score(50,   0,    0,    50),
        (6,1,6,3,3,4): score(100,  0,    0,    100),
        (6,1,1,2,4,4): score(200,  0,    0,    200),
        (3,3,4,2,2,4): score(0,    0,    0,    0),
        (3,4,6,1,5,6): score(150,  0,    0,    150),
        (6,2,1,5,1,5): score(300,  0,    0,    300),
        (2,2,6,4,3,5): score(50,   0,    0,    50),
        (5,6,6,6,5,3): score(700,  0,    600,  100),
        (6,5,4,1,6,5): score(200,  0,    0,    200),
        (2,4,2,1,2,3): score(300,  0,    200,  100),
        (4,1,1,2,3,2): score(200,  0,    0,    200),
        (2,5,4,4,1,5): score(200,  0,    0,    200),
        (1,1,1,5):     score(1050, 0,    1000, 250),
    }
    
    # the score types to skip
    skip = [] # to do all the tests
    # skip = ['straight', 'multiple', 'individual']
    # skip = ['all']
    
    for score_type, fn in fn_map.items():
        if score_type in skip:
            # skip certain methods
            continue
        print(f'{score_type}',end='')
        print()
        for roll, score in tests.items():
            # print(roll)
            res = fn(roll)
            # print(res)
            goal_score = score._asdict()[score_type]
            try:
                result_score = res.Score.max()
            except AttributeError:
                result_score = res.Score
            result_score = 0 if len(res.Score) == 0 else result_score
            assert result_score == goal_score, f'result {result_score} != {goal_score} for roll {roll}   {tuple(sorted(roll))}\n{res}'
            print('.', end='')
        print()
    print("All tests passed")
    
if __name__ == '__main__':
    test()
    # manual()