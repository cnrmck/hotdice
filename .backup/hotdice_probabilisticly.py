die_sides = 6

def no(prob):
    '''
    Utility function to invert a given probability. Would have used `not` but it's a reserved token
    >>> no(.35)
    0.65
    
    >>> no(prob_of_set(3))
    0.9722222222222222
    
    The above example can be read as "The probability of no set of length 3"
    '''
    return 1 - prob

def prob_of_straight(num_dice=6, min_dice=6):
    '''
    The probability of a straight given a certain number of dice thrown
    Args:
        num_dice (int): the number of dice thrown
        min_dice (int): the number of dice required to get a straight in this game Default: 6
    '''
    # if you don't have enough dice to make a straight, you cannot get a straight
    if num_dice < min_dice:
        return 0
    
    global die_sides
    
    prob = 1
    for n in range(1, num_dice+1):
        prob *= (n / die_sides)
        
    return prob

def prob_of_set(set_size, acceptable_rolls=6):
    '''
    The probability of getting a set of a certain length given a number of acceptable numbers
    Args:
        set_size (int): the size of the set
        acceptable_rolls (int): the number of rolls that are acceptable for a straight. For example,
                              if a set can only be made of 5s and 6s then acceptable_rolls is 2
    '''
    global die_sides
    return ((1 / die_sides)**(set_size - 1)) * (acceptable_rolls / die_sides)

def prob_of_any_set(num_dice=6, acceptable_rolls=6, min_set_size=3):
    '''
    The probability of getting a set of any length given a certain number of dice
    Args:
        num_dice (int): the number of dice rolled
        acceptable_rolls (int): the number of rolls that are acceptable for a straight. For example,
                              if a set can only be made of 5s, and 6s then acceptable_rolls is 2
        min_set_size (int): the minimum size of a set
        die_sides (int): the number of sides on the rolled die
    '''
    global die_sides
    
    prob_no_set = 1
    for set_size in range(min_set_size, num_dice + 1):
        prob_no_set *= no(prob_of_set(set_size, acceptable_rolls))
        
    return no(prob_no_set)

def prob_of_die_score(num_dice=6, acceptable_rolls=2):
    '''
    The probability of rolling a scoring die (not including the probability of a straight or set).
    Normally, only the rolls 1 and 5 are scoring rolls.
    Args:
        num_dice (int): the number of dice rolled
        acceptable_rolls (int): the number of rolls that are scoring rolls
        die_sides (int): the number of sides on the rolled die
    '''
    global die_sides
    return 1 - (((die_sides - acceptable_rolls) / die_sides)**num_dice)

def prob_of_num_die_score(num_score=1, num_dice=6, acceptable_rolls=2):
    '''
    The probability of exactly num_score dice scoring
    Args:
        num_score (int): the number of dice required to score
        num_dice (int): the number of dice rolled
        acceptable_rolls (int): the number of rolls that are scoring rolls
    '''
    assert num_dice >= num_score, "You can't get more scoring dice than you rolled"
    global die_sides
    score_prob = acceptable_rolls / die_sides
    
    return (score_prob**num_score) * (no(score_prob)**(num_dice-num_score))

def prob_of_bust(num_dice=6, die_score_acceptable_rolls=2):
    '''
    The probability of getting no scoring rolls (i.e. busting)
    Args:
        num_dice (int): the number of dice rolled
        die_score_acceptable_rolls (int): the number of die rolls that score
        die_sides (int): the number of sides on the die in use
    '''
    global die_sides
    # if two die have not been rolled then you can't get a set with them, exclude those rolls
    acceptable_rolls_for_set = die_sides - die_score_acceptable_rolls
    return no(prob_of_die_score(num_dice, die_score_acceptable_rolls)) \
            * no(prob_of_any_set(num_dice, acceptable_rolls_for_set))
            
def score_set(set_size):
    '''
    The average score of rolling a set of a particular length
    Args:
        set_size (int): the size of the set that you rolled
    '''
    # the computational way to solve the problem is below:
    # global die_sides
    # total_score = 0
    # for n in range(1, die_sides + 1):
    #     # 1 gets a score of 1000, all other ones just get scores of 100 * the roll
    #     multiple = n * 100 if n is not 1 else 1000
    #     score = multiple * max(2 * (set_size - 3), 1)
    #     total_score+=score
    # # the average score achieved by scoring on all sides
    # return total_score / die_sides
    
    # However, it turns out that the pattern reduces to this for all set sizes:
    return 500 if set_size is 3 else 1000 * (set_size - 3)

def score_die(roll_scores = {1: 100, 5: 50}):
    '''
    The average score from rolling a scoring die
    Args:
        roll_scores (dict): a dictionary containing the scoring rolls and their associated scores
    '''
    total_score = 0
    for roll, score in roll_scores.items():
        total_score += score
        
    return total_score / len(roll_scores)

def average_num_scoring_dice(num_dice=6, acceptable_rolls=2):
    '''
    The average number of scoring dice you will get, given a certain number of rolled dice
    This is not including the probability of straights or sets
    Args:
        num_dice (int): the number of dice rolled
        die_score_acceptable_rolls (int): the number of die rolls that score
    '''
    global die_sides
    
    num_scoring = 0
    for roll in range(1, num_dice+1):
        num_scoring += acceptable_rolls / die_sides
        
    return num_scoring

