from random import randint
from statistics import mean, median, mode

n_iterations = 1000
n_players = 8
n_die_converted_to_zero = 0 #if this is two, then it's like you're starting on your second turn every time.
stopping_point = 0
incrementation_of_stopping_point = 50
#setup
ones_score = 100
fives_score = 50
straight_score = 1500
score_multiple = {"1":1000, "2":200, "3":300, "4":400, "5":500, "6":600}

scores = []
score_for_turn = 0
score = 0
n_scoring_hands = 0
n_turns = 0 # not always used, only when seeking an endgame number and counting n_turns to it
#dice should always have 6 die in it
dice = [0,0,0,0,0,0] # NOTE: To manually set starting values, put them in this array, otherwise put 0s (for however many dice you want)

# checks if something is a straight, if so returns the score and zeroed out dice. Otherwise 0
def scoreStraight(dice):
    score = 0
    count = 0
    for num in range(1,7):
        #print(num)
        for die in dice:
            if die == num:
                count += 1
                break #only find one
            else:
                pass

    if (count == 6):
        for i in range(len(dice)):
            dice[i] = 0
        return straight_score, dice
    else:
        return 0, dice

# returns the score gained by having 3 or more of the same die, 0s out used die
def scoreMultiples(dice):
    score = 0
    for num in range(1,7):
        count = 0
        dice_copy = dice.copy()
        for i in range(len(dice_copy)):
            if (dice_copy[i] == num): # add and num != 2 to not count twos
                count += 1
                dice_copy[i] = 0
        if (count > 2):
            score += (count - 2) * score_multiple[str(num)]
            for i in range(len(dice)):
                if(dice[i] == num):
                    dice[i] = 0
    return score, dice



#scores your roll, returns your score and the dice
def scoreRoll(dice):
    round_score = 0
    multiples_score = 0
    straight_score, dice = scoreStraight(dice)
    if(straight_score == 0):
        multiples_score, dice = scoreMultiples(dice)
        #print("test", dice)
        if(True): #or multiples_score == 0 for Max Multiples strategy, True for Standard Strategy
            for i in range(len(dice)):
                if dice[i] == 1:
                    round_score += ones_score
                    dice[i] = 0
                    #break # uncomment break for Max Multiples strat, comment for Standard Strategy,
                elif dice[i] == 5:
                    round_score += fives_score
                    dice[i] = 0
                    #break # uncomment for Max Multiples strat, comment for Standard Strategy
                else:
                    pass

    round_score += straight_score + multiples_score
    return round_score, dice

#this function accepts the total number we want to replaceWithZero, the number we've already replaced, and the remaining indices available
def replaceWithZero(total_n, n_replaced_with_zero, remaining_indices):
    if(remaining_indices < (total_n - n_replaced_with_zero) ):
        return print("Fail!")
    else:
        if(total_n > n_replaced_with_zero and randint(0, (remaining_indices - (total_n - n_replaced_with_zero) ) ) == 0):
            return True
        else:
            return False

# reroll the die, then return it
def rollDie():
    die = randint(1,6)
    return die

# each player has a different strategy
for player in range(n_players):
    stopping_point += incrementation_of_stopping_point
    score = []
    n_turns_taken = []
    n_scoring_hands = 0
    # roll dice and calculate score for that hand. for each hand, keep rolling until bust
    for turn in range(n_iterations):
        n_turns = 0
        score_for_turn = 0
        while(score_for_turn < 10000):
            #print(score_for_turn)
            n_replaced_with_zero = 0
            for i in range(len(dice)):
                if(replaceWithZero(n_die_converted_to_zero, n_replaced_with_zero, (len(dice) - i) ) ):
                    dice[i] = 0
                    n_replaced_with_zero += 1
                else:
                    dice[i] = rollDie()

            bust = False
            stop = False
            while(not(bust) and not(stop)):
                score, dice = scoreRoll(dice)
                if(score == 0):
                    #print("Bust!")
                    bust = True
                #this does hot dice part
                elif(sum(dice) == 0):
                    for i in range(len(dice)):
                        dice[i] = rollDie()
                elif(score_for_turn >= stopping_point):  # uncomment this if statement to test stoppting point strats (on the board is 1000)
                    score_for_turn += score
                    n_scoring_hands += 1
                    #print("Stop")
                    stop = True
                else:
                    for i in range(len(dice)):
                        if(dice[i] != 0):
                            dice[i] = rollDie()
                score_for_turn += score
                n_turns += 1
                score = 0
            n_turns_taken.append(n_turns)
            if(bust):
                scores.append(0)
            else:
                #print("Append scores: %d" % score_for_turn)
                scores.append(score_for_turn)

    print("%d" % stopping_point)
    print("(%.2dk iter) Mean %.2d, Median %.2d, Mode %.2d, Max %.2d" % (n_iterations/1000, mean(scores), median(sorted(scores)), mode(scores), max(scores)) )
    print("Scoring Hands Percentage %.2f%%" % ((n_scoring_hands/n_iterations)*100 ) )
    print("Expected Score for 10 Turns: %d \nExpected Median Score for 10 Turns: %d" % ((mean(scores) * (n_scoring_hands/n_iterations)*10), (median(scores) * (n_scoring_hands/n_iterations)*10)) )
    print("Number of Turns to 10,000: %.2f" % (mean(n_turns_taken)) )




    #print(scores)
