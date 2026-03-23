#!/usr/bin/env python3

"""
Demonstration script: AI Bot vs AI Bot game simulation
Shows how the bot makes decisions in a realistic game scenario.
"""

import sys
from AIBot import AIBot
from Deck import Deck
from Card import Card


class SimpleGameSimulation:
    """A simplified game simulation to demonstrate AI bot decisions"""

    def __init__(self, num_bots=2):
        self.bots = []
        self.round_number = 1
        self.board_plays = []
        self.discard_pile = []
        self.deck = None

        for i in range(num_bots):
            bot = AIBot(i, f"AI Bot {i+1}")
            bot.load_model('aibot_model.json')
            self.bots.append(bot)

    def initialize_game(self):
        """Set up initial game state"""
        print("\n" + "=" * 70)
        print("RUMMY500 AI BOT DEMONSTRATION".center(70))
        print("=" * 70)

        self.deck = Deck()
        self.deck.initDeck()

        for bot in self.bots:
            bot.playerHand = [self.deck.deck.pop() for _ in range(10)]
            bot.playerPoints = 0

        self.discard_pile = [self.deck.deck.pop()]

        print(f"\n✓ Game initialized with {len(self.bots)} AI bots")
        print(f"✓ Each bot has 10 cards")
        print(f"✓ Round 1 rules: Must play 1 trio + 1 sequence to bajarse")

    def simulate_turn(self, bot_index):
        """Simulate a single turn for a bot"""
        bot = self.bots[bot_index]

        print(f"\n{'-' * 70}")
        print(f"🎮 Turn: {bot.playerName}")
        print(f"{'-' * 70}")
        print(f"Hand size: {len(bot.playerHand)} cards")
        print(f"Bajado: {'Yes' if bot.downHand else 'No'}")

        players_info = [
            {'name': b.playerName, 'hand_size': len(b.playerHand)}
            for b in self.bots if b != bot
        ]

        decision = bot.decide_draw_source(
            self.discard_pile[-1],
            len(self.deck.deck),
            players_info
        )

        if decision:
            card = self.discard_pile.pop()
            bot.playerHand.append(card)
            print(f"📥 Drew from DISCARD: {card}")
        else:
            if self.deck.deck:
                card = self.deck.deck.pop()
                bot.playerHand.append(card)
                print(f"📥 Drew from DECK: {card}")

        if not bot.downHand:
            play = bot.decide_play_cards(self.round_number)
            if play:
                print(f"✅ Making initial play (bajada)!")
                print(f"   - {len(play[0])} trios")
                print(f"   - {len(play[1])} sequences")
                bot.downHand = True
                self.board_plays.append(play)
            else:
                print(f"❌ Cannot bajarse this turn")
        else:
            insertion = bot.decide_insert_card(self.board_plays)
            if insertion:
                play_idx, card, position = insertion
                print(f"✨ Inserting card into play {play_idx}!")
                print(f"   - Card: {card}")
                print(f"   - Position: {position}")
                bot.playerHand.remove(card)

            joker_move = bot.decide_move_joker(self.board_plays)
            if joker_move:
                play_idx, new_pos = joker_move
                print(f"🃏 Moving joker to position {new_pos}")

        discard_card = bot.decide_discard()
        if discard_card:
            bot.playerHand.remove(discard_card)
            self.discard_pile.append(discard_card)
            print(f"📤 Discarded: {discard_card}")

        hand_points = sum(self._get_points(c) for c in bot.playerHand)
        print(f"📊 Remaining hand points: {hand_points}")

    def get_players_info(self):
        """Get info about all players"""
        info = []
        for bot in self.bots:
            points = sum(self._get_points(c) for c in bot.playerHand)
            info.append({
                'name': bot.playerName,
                'hand_size': len(bot.playerHand),
                'points': points,
                'bajado': bot.downHand
            })
        return info

    def print_game_status(self):
        """Print current game status"""
        print(f"\n{'=' * 70}")
        print(f"📊 GAME STATUS - Round {self.round_number}".ljust(70))
        print(f"{'=' * 70}")

        for info in self.get_players_info():
            status = "✅ Bajado" if info['bajado'] else "⏳ Waiting"
            print(f"{info['name']:20} | Hand: {info['hand_size']:2} | "
                  f"Points: {info['points']:3} | {status}")

        print(f"Board plays: {len(self.board_plays)} active plays")
        print(f"Deck remaining: {len(self.deck.deck)} cards")

    def _get_points(self, card):
        """Get point value of a card"""
        if card.joker:
            return 25
        elif card.value == 'A':
            return 20
        elif card.value in ['10', 'J', 'Q', 'K']:
            return 10
        else:
            return 5

    def run_simulation(self, turns=6):
        """Run a simplified game simulation"""
        self.initialize_game()

        try:
            for turn in range(turns):
                self.print_game_status()

                bot_index = turn % len(self.bots)
                self.simulate_turn(bot_index)

                if turn == turns - 1:
                    print(f"\n{'=' * 70}")
                    print("🏁 Demonstration Complete!".center(70))
                    print(f"{'=' * 70}")

                    print("\nFinal Bot Statistics:")
                    for bot in self.bots:
                        print(f"\n{bot.playerName}:")
                        print(f"  Win Rate: {bot.win_rate:.2%}")
                        print(f"  Games Played: {bot.games_played}")
                        print(f"  Strategy: {bot.strategy_weights}")

                    print("\n" + "=" * 70)
                    print("To train the bot further:")
                    print("  python train_bot.py --games 500")
                    print("\nTo integrate into your game:")
                    print("  See AI_INTEGRATION_GUIDE.md")
                    print("=" * 70 + "\n")

        except FileNotFoundError:
            print("\n❌ Error: aibot_model.json not found!")
            print("\nFirst, train the bot:")
            print("  python train_bot.py --games 500\n")
            sys.exit(1)

        except Exception as e:
            print(f"\n❌ Error during simulation: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


def main():
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + "🤖 Rummy500 AI Bot - Game Demonstration".center(68) + "║")
    print("║" + "Watch the AI bots play against each other".center(68) + "║")
    print("╚" + "=" * 68 + "╝")

    simulation = SimpleGameSimulation(num_bots=2)
    simulation.run_simulation(turns=6)


if __name__ == "__main__":
    main()
