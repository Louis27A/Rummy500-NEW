#!/usr/bin/env python3

"""
Example script showing how to use the AI Bot in your Rummy500 game.
This demonstrates all the key decision-making methods in a realistic context.
"""

from AIBot import AIBot
from Player import Player
from Card import Card
from Deck import Deck


def example_basic_ai_creation():
    """Example 1: Creating and loading an AI bot"""
    print("=" * 60)
    print("Example 1: Creating and Loading AI Bot")
    print("=" * 60)

    bot = AIBot(1, "Expert AI")
    bot.load_model('aibot_model.json')

    print(f"Bot created: {bot.playerName}")
    print(f"Bot win rate: {bot.win_rate:.2%}")
    print(f"Bot experience: {bot.games_played} games")
    print(f"Strategy weights: {bot.strategy_weights}")
    print()


def example_draw_decision():
    """Example 2: Deciding whether to draw from discard or deck"""
    print("=" * 60)
    print("Example 2: Draw Source Decision")
    print("=" * 60)

    bot = AIBot(1, "Smart Bot")
    bot.load_model('aibot_model.json')

    deck = Deck()
    deck.initDeck()

    bot.playerHand = [deck.deck.pop() for _ in range(10)]

    discard_top_card = Card('A', 'Hearts')

    players_info = [
        {'name': 'Player2', 'hand_size': 8},
        {'name': 'Player3', 'hand_size': 5},
        {'name': 'Player4', 'hand_size': 10}
    ]

    decision = bot.decide_draw_source(discard_top_card, len(deck.deck), players_info)

    print(f"Discard card: {discard_top_card}")
    print(f"Deck size: {len(deck.deck)}")
    print(f"Bot decision: {'Draw from DISCARD' if decision else 'Draw from DECK'}")
    print()


def example_play_decision():
    """Example 3: Deciding which cards to play based on round"""
    print("=" * 60)
    print("Example 3: Play Decision by Round")
    print("=" * 60)

    bot = AIBot(1, "Smart Bot")
    bot.load_model('aibot_model.json')

    deck = Deck()
    deck.initDeck()

    bot.playerHand = [deck.deck.pop() for _ in range(15)]

    for round_num in range(1, 5):
        print(f"\nRound {round_num}:")

        play = bot.decide_play_cards(round_num)

        if play:
            print(f"  Bot can play: {len(play[0])} trios and {len(play[1])} sequences")
        else:
            print(f"  Bot cannot play this round")


def example_discard_decision():
    """Example 4: Deciding which card to discard"""
    print("=" * 60)
    print("Example 4: Discard Decision")
    print("=" * 60)

    bot = AIBot(1, "Smart Bot")

    deck = Deck()
    deck.initDeck()

    bot.playerHand = [deck.deck.pop() for _ in range(8)]

    card_to_discard = bot.decide_discard()

    print(f"Bot's hand: {[str(c) for c in bot.playerHand]}")
    print(f"Card to discard: {card_to_discard}")
    print()


def example_insert_card_decision():
    """Example 5: Deciding where to insert cards (CRITICAL MECHANIC)"""
    print("=" * 60)
    print("Example 5: Insert Card Decision")
    print("=" * 60)

    bot = AIBot(1, "Smart Bot")
    bot.load_model('aibot_model.json')

    deck = Deck()
    deck.initDeck()

    bot.playerHand = [
        Card('5', 'Hearts'),
        Card('6', 'Hearts'),
        Card('7', 'Hearts'),
        Card('10', 'Diamonds'),
        Card('10', 'Clubs'),
        Card('K', 'Spades')
    ]

    bot.downHand = True

    plays_on_table = [
        [Card('2', 'Hearts'), Card('3', 'Hearts'), Card('4', 'Hearts')],
        [Card('10', 'Hearts'), Card('10', 'Spades'), Card('10', 'Clubs')]
    ]

    insertion = bot.decide_insert_card(plays_on_table)

    if insertion:
        play_idx, card, position = insertion
        print(f"Bot can insert: {card} into play #{play_idx} at position {position}")
        print(f"This would be a great move to reduce hand size!")
    else:
        print("No beneficial insertions available right now")

    print()


def example_joker_decisions():
    """Example 6: Deciding about Joker movements and substitutions"""
    print("=" * 60)
    print("Example 6: Joker Movement and Substitution")
    print("=" * 60)

    bot = AIBot(1, "Smart Bot")

    deck = Deck()
    deck.initDeck()

    bot.playerHand = [
        Card('3', 'Hearts'),
        Card('4', 'Hearts'),
        Card('5', 'Hearts'),
        Card('6', 'Hearts'),
    ]

    bot.downHand = True

    joker_card = Card('Joker', 'Joker')

    plays_with_joker = [
        [Card('2', 'Hearts'), joker_card, Card('4', 'Hearts'), Card('5', 'Hearts')]
    ]

    move_decision = bot.decide_move_joker(plays_with_joker)

    if move_decision:
        play_idx, new_pos = move_decision
        print(f"Joker can be moved to position {new_pos}")
    else:
        print("Joker cannot be moved (would break sequence)")

    substitute_decision = bot.decide_substitute_joker(plays_with_joker)

    if substitute_decision:
        print(f"Joker can be substituted with: {substitute_decision[1]}")
    else:
        print("No joker substitution available")

    print()


def example_learning_from_game():
    """Example 7: Bot learning from game results"""
    print("=" * 60)
    print("Example 7: Bot Learning from Game Results")
    print("=" * 60)

    bot = AIBot(1, "Learning Bot")
    bot.load_model('aibot_model.json')

    print(f"Before: Win rate = {bot.win_rate:.2%}")
    print(f"Before: Weights = {bot.strategy_weights}")

    game_result = {
        'win': True,
        'points_gained': 0,
        'plays_made': 5
    }

    bot.learn_from_game(game_result)

    print(f"After winning: Win rate = {bot.win_rate:.2%}")
    print(f"After winning: Weights = {bot.strategy_weights}")

    bot.save_model('aibot_model.json')
    print("Model saved!")
    print()


def example_full_turn_simulation():
    """Example 8: Complete turn simulation"""
    print("=" * 60)
    print("Example 8: Full Turn Simulation")
    print("=" * 60)

    bot = AIBot(1, "Simulation Bot")
    bot.load_model('aibot_model.json')

    deck = Deck()
    deck.initDeck()

    bot.playerHand = [deck.deck.pop() for _ in range(12)]

    game_state = {
        'discard_top': Card('7', 'Clubs'),
        'deck_size': len(deck.deck),
        'players_info': [
            {'name': 'P2', 'hand_size': 9},
            {'name': 'P3', 'hand_size': 7},
        ],
        'round_number': 1,
        'plays_in_table': [
            [Card('5', 'Spades'), Card('5', 'Hearts'), Card('5', 'Diamonds')],
            [Card('8', 'Clubs'), Card('9', 'Clubs'), Card('10', 'Clubs'), Card('J', 'Clubs')]
        ]
    }

    print("Simulating Bot Turn:")
    print(f"Initial hand size: {len(bot.playerHand)}")

    draw_decision = bot.decide_draw_source(
        game_state['discard_top'],
        game_state['deck_size'],
        game_state['players_info']
    )
    print(f"1. Draw from {'DISCARD' if draw_decision else 'DECK'}")

    if not bot.downHand:
        play = bot.decide_play_cards(game_state['round_number'])
        if play:
            print(f"2. Make initial play")
            bot.downHand = True

    if bot.downHand:
        insertion = bot.decide_insert_card(game_state['plays_in_table'])
        if insertion:
            print(f"3. Insert card: {insertion[1]}")

    discard = bot.decide_discard()
    print(f"4. Discard: {discard}")
    print()


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "   Rummy500 AI Bot - Usage Examples".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    try:
        example_basic_ai_creation()
        example_draw_decision()
        example_play_decision()
        example_discard_decision()
        example_insert_card_decision()
        example_joker_decisions()
        example_learning_from_game()
        example_full_turn_simulation()

        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)
        print("\nTo train the bot: python train_bot.py --games 500")
        print("To use in your game: See AI_INTEGRATION_GUIDE.md")
        print()

    except Exception as e:
        print(f"\nError in example: {e}")
        print("Make sure aibot_model.json exists by running: python train_bot.py")
