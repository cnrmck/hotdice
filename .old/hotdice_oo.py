import random
import statistics

"""
Relationship between objects:
Game: can have multiple players and rules that differ between games
Player: can have different strategies and different scores
Strategy: selects a decision based on a game state
Score: the thing a Player is trying to maximize, the game selects the player with the highest score
    once the end of game rule is triggered. (Normally, it's a score above a certain limit)
GameRules: a set of rules that a game uses to say what's allowed and what's not
"""

class Game():
    """
    Defines an instance of a game. 
    
    Interacts with Players and GameRules
    """
    def __init__(s, game_rules, players):
        s.players = players
        s.game_rules = game_rules
        
    def __call__(s):
        s.game_rules(s.players)

class GameRules():
    """
    Defines GameRules that can be called by a Game. 
    
    A Game calls GameRules 
    """