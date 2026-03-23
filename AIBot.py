import json
import os
from datetime import datetime
from Player import Player
from Card import Card
import random
import numpy as np


class AIBot(Player):

    def __init__(self, bot_id, bot_name="AI Bot"):
        super().__init__(bot_id, bot_name)
        self.is_ai = True

        self.strategy_weights = {
            'aggressive': 0.5,
            'conservative': 0.3,
            'balanced': 0.2
        }

        self.learned_patterns = {
            'optimal_plays': {},
            'discard_strategy': {},
            'card_values': {}
        }

        self.game_history = []
        self.decisions_made = []
        self.win_rate = 0.0
        self.games_played = 0
        self.games_won = 0

    def decide_draw_source(self, discard_top_card, deck_size, players_info):
        """
        Decides whether to draw from discard pile or deck.
        Returns True for discard, False for deck.
        """
        if not discard_top_card:
            return False

        card_usefulness = self._evaluate_card_usefulness(discard_top_card)
        hand_completion = self._evaluate_hand_completion()

        risk_factor = self._calculate_risk_factor(players_info)

        if card_usefulness > 0.6 and hand_completion < 0.5:
            return True
        elif random.random() < (0.3 - risk_factor):
            return True

        return False

    def decide_play_cards(self, round_number):
        """
        Decides which cards to play based on current hand and round requirements.
        Returns list of tuples: (cards_to_play, play_type)
        """
        valid_plays = self._find_valid_plays(round_number)

        if not valid_plays:
            return None

        best_play = self._select_best_play(valid_plays, round_number)
        return best_play

    def decide_discard(self, must_burn_joker=False):
        """
        Decides which card to discard.
        Returns the card to discard.
        """
        if must_burn_joker:
            return self._find_joker_burn_pair()

        card_values = self._calculate_card_values()
        worst_card = min(self.playerHand, key=lambda c: card_values.get(c, 0))

        return worst_card

    def decide_buy_card(self, discard_card, hand_value, players_info):
        """
        Decides whether to buy a discarded card.
        Returns True or False.
        """
        if not discard_card:
            return False

        usefulness = self._evaluate_card_usefulness(discard_card)
        current_hand_score = sum(self._get_card_point_value(c) for c in self.playerHand)

        if current_hand_score > 200:
            return usefulness > 0.4

        return usefulness > 0.5

    def decide_move_joker(self, plays_in_table):
        """
        Decides if joker should be moved in a sequence.
        Returns (play_index, new_position) or None
        """
        for i, play in enumerate(plays_in_table):
            if self._has_movable_joker(play):
                new_pos = self._calculate_best_joker_position(play)
                if new_pos is not None:
                    return (i, new_pos)

        return None

    def decide_substitute_joker(self, plays_in_table):
        """
        Decides if a joker should be substituted in a sequence.
        Returns (play_index, card_to_use) or None
        """
        for i, play in enumerate(plays_in_table):
            if self._contains_joker(play):
                joker_card = self._find_substitutable_card(play)
                if joker_card and joker_card in self.playerHand:
                    return (i, joker_card)

        return None

    def decide_insert_card(self, plays_in_table):
        """
        Decides which card to insert into existing plays.
        This is a key strategy: inserting cards reduces hand size without initial play.
        Returns (play_index, card_to_insert, position) or None
        """
        if not self.downHand:
            return None

        best_insertion = None
        best_score = -1

        for play_idx, play in enumerate(plays_in_table):
            for card in self.playerHand:
                insertion_result = self._try_insert_card(card, play)
                if insertion_result:
                    position = insertion_result
                    insertion_score = self._score_insertion(card, play, play_idx)

                    if insertion_score > best_score:
                        best_score = insertion_score
                        best_insertion = (play_idx, card, position)

        return best_insertion

    def _try_insert_card(self, card, play):
        """
        Tries to insert a card into a play.
        Returns the position where it can be inserted, or None if impossible.

        Validates:
        - Card can extend a sequence
        - Card value matches a trio
        - Joker can be substituted for a trio card
        """
        play_type = self._get_play_type(play)

        if play_type == 'sequence':
            return self._can_insert_into_sequence(card, play)
        elif play_type == 'trio':
            return self._can_insert_into_trio(card, play)

        return None

    def _can_insert_into_sequence(self, card, sequence):
        """
        Checks if a card can be inserted into a sequence.
        Sequences can be extended at the ends if the card is consecutive.
        Returns the position (0 for start, len for end) or None.
        """
        if card.joker:
            return None

        card_values = Card.values
        card_idx = card_values.index(card.value) if card.value in card_values else -1

        if card_idx == -1 or card.suit != sequence[0].suit:
            return None

        sequence_indices = []
        for seq_card in sequence:
            if not seq_card.joker:
                idx = card_values.index(seq_card.value) if seq_card.value in card_values else -1
                if idx != -1:
                    sequence_indices.append(idx)

        if not sequence_indices:
            return None

        min_idx = min(sequence_indices)
        max_idx = max(sequence_indices)

        if card_idx == min_idx - 1:
            return 0
        elif card_idx == max_idx + 1:
            return len(sequence)

        return None

    def _can_insert_into_trio(self, card, trio):
        """
        Checks if a card can be inserted into a trio.
        Trios accept cards with the same value (max 1 joker per trio).
        Returns position 0 (always append for trios) or None.
        """
        if not trio or len(trio) < 3:
            return None

        trio_value = trio[0].value

        if card.value == trio_value:
            joker_count = sum(1 for c in trio if c.joker)
            if not card.joker and joker_count <= 1:
                return 0

        if card.joker and not any(c.joker for c in trio):
            return 0

        return None

    def _get_play_type(self, play):
        """
        Determines if a play is a sequence or trio.
        """
        if not play or len(play) < 3:
            return None

        first_card = play[0]

        suits = set(c.suit for c in play if not c.joker)
        if len(suits) == 1:
            return 'sequence'

        values = set(c.value for c in play if not c.joker)
        if len(values) == 1:
            return 'trio'

        return 'mixed'

    def _score_insertion(self, card, play, play_idx):
        """
        Scores how good an insertion would be.
        Higher score = better insertion.
        """
        score = 0.0

        card_points = self._get_card_point_value(card)
        score += (25 - card_points) / 25

        remaining_hand = [c for c in self.playerHand if c != card]
        remaining_points = sum(self._get_card_point_value(c) for c in remaining_hand)

        if remaining_points < 50:
            score += 0.5

        play_type = self._get_play_type(play)
        if play_type == 'sequence':
            score += 0.3
        elif play_type == 'trio':
            score += 0.2

        return score

    def _find_valid_plays(self, round_number):
        """
        Finds all valid plays possible with current hand.
        """
        plays = []

        trios = self._find_all_trios()
        sequences = self._find_all_sequences()

        if round_number == 1:
            combinations = self._combine_plays(trios, sequences, min_trios=1, min_sequences=1)
        elif round_number == 2:
            combinations = self._combine_plays([], sequences, min_sequences=2)
        elif round_number == 3:
            combinations = self._combine_plays(trios, [], min_trios=3)
        elif round_number == 4:
            combinations = self._combine_plays(trios, sequences, min_trios=2, min_sequences=1, use_all=True)
        else:
            combinations = []

        return combinations

    def _find_all_trios(self):
        """
        Finds all valid trios in current hand.
        """
        trios = []
        value_groups = {}

        for card in self.playerHand:
            if card.value not in value_groups:
                value_groups[card.value] = []
            value_groups[card.value].append(card)

        for value, cards in value_groups.items():
            if len(cards) >= 3:
                for combo in self._get_valid_trio_combinations(cards):
                    trios.append(combo)

        return trios

    def _find_all_sequences(self):
        """
        Finds all valid sequences in current hand.
        """
        sequences = []
        suit_groups = {}

        for card in self.playerHand:
            if card.suit not in suit_groups:
                suit_groups[card.suit] = []
            suit_groups[card.suit].append(card)

        for suit, cards in suit_groups.items():
            valid_sequences = self._find_sequences_in_suit(cards)
            sequences.extend(valid_sequences)

        return sequences

    def _get_valid_trio_combinations(self, cards):
        """
        Returns valid trio combinations (3+ cards with same value, max 1 joker).
        """
        if len(cards) < 3:
            return []

        combinations = []
        joker_count = sum(1 for c in cards if c.joker)

        if joker_count > 1:
            cards_no_joker = [c for c in cards if not c.joker]
            if len(cards_no_joker) >= 3:
                combinations.append(cards_no_joker[:3])
            if len(cards_no_joker) >= 2:
                joker = next(c for c in cards if c.joker)
                combinations.append(cards_no_joker + [joker])
        else:
            combinations.append(cards[:3])
            if len(cards) > 3:
                combinations.append(cards[:4])

        return combinations

    def _find_sequences_in_suit(self, cards):
        """
        Finds valid sequences (4+ consecutive cards of same suit).
        """
        if len(cards) < 4:
            return []

        sequences = []
        card_values = Card.values

        sorted_cards = sorted(cards, key=lambda c: card_values.index(c.value) if c.value in card_values else -1)

        for i in range(len(sorted_cards) - 3):
            for j in range(i + 4, len(sorted_cards) + 1):
                potential_sequence = sorted_cards[i:j]
                if self._is_valid_sequence(potential_sequence):
                    sequences.append(potential_sequence)

        return sequences

    def _is_valid_sequence(self, cards):
        """
        Validates if a sequence is valid (consecutive cards, max 2 non-consecutive jokers).
        """
        if len(cards) < 4:
            return False

        card_values = Card.values
        joker_positions = [i for i, c in enumerate(cards) if c.joker]

        if len(joker_positions) > 2:
            return False

        if len(joker_positions) == 2:
            if joker_positions[1] - joker_positions[0] == 1:
                return False

        non_joker_cards = [c for c in cards if not c.joker]
        if len(non_joker_cards) < 2:
            return False

        non_joker_indices = [card_values.index(c.value) for c in non_joker_cards if c.value in card_values]

        if len(non_joker_indices) >= 2:
            min_idx = min(non_joker_indices)
            max_idx = max(non_joker_indices)
            expected_length = max_idx - min_idx + 1

            if expected_length == len(cards):
                return True

        return len(cards) == 4 and len([c for c in cards if not c.joker]) >= 3

    def _combine_plays(self, trios, sequences, min_trios=0, min_sequences=0, use_all=False):
        """
        Combines trios and sequences into valid play combinations.
        """
        valid_combinations = []

        if use_all:
            for trio_combo in trios:
                for seq_combo in sequences:
                    if len([c for trio in trio_combo for c in trio]) + len([c for seq in seq_combo for c in seq]) == len(self.playerHand):
                        valid_combinations.append((trio_combo, seq_combo))
        else:
            for trio_combo in trios:
                for seq_combo in sequences:
                    if len(trio_combo) >= min_trios and len(seq_combo) >= min_sequences:
                        valid_combinations.append((trio_combo, seq_combo))

        return valid_combinations

    def _select_best_play(self, valid_plays, round_number):
        """
        Selects the best play from available options based on strategy.
        """
        if not valid_plays:
            return None

        scored_plays = []
        for play in valid_plays:
            score = self._score_play(play, round_number)
            scored_plays.append((score, play))

        scored_plays.sort(reverse=True, key=lambda x: x[0])
        return scored_plays[0][1]

    def _score_play(self, play, round_number):
        """
        Scores a potential play based on various factors.
        """
        score = 0.0

        used_cards = [c for trio in play[0] for c in trio] + [c for seq in play[1] for c in seq]
        remaining_cards = [c for c in self.playerHand if c not in used_cards]

        remaining_points = sum(self._get_card_point_value(c) for c in remaining_cards)
        score += (500 - remaining_points) / 100

        joker_count = sum(1 for c in used_cards if c.joker)
        score -= joker_count * 0.3

        num_plays = len(play[0]) + len(play[1])
        score += num_plays * 0.2

        return score

    def _evaluate_card_usefulness(self, card):
        """
        Evaluates how useful a card is for current hand (0-1 scale).
        """
        usefulness = 0.0

        card_value = card.value
        card_suit = card.suit

        matching_value = sum(1 for c in self.playerHand if c.value == card_value and c != card)
        usefulness += min(matching_value / 3, 0.4)

        matching_suit = sum(1 for c in self.playerHand if c.suit == card_suit and c != card)
        usefulness += min(matching_suit / 4, 0.35)

        if card.joker:
            usefulness += 0.25

        return min(usefulness, 1.0)

    def _evaluate_hand_completion(self):
        """
        Evaluates how close the hand is to completing a valid play (0-1 scale).
        """
        completion = 0.0

        trios = self._find_all_trios()
        sequences = self._find_all_sequences()

        completion += len(trios) * 0.3
        completion += len(sequences) * 0.4

        return min(completion, 1.0)

    def _calculate_risk_factor(self, players_info):
        """
        Calculates risk factor based on opponent situations (0-1 scale).
        """
        if not players_info:
            return 0.0

        risk = 0.0

        for player_info in players_info:
            if player_info.get('hand_size', 0) <= 2:
                risk += 0.3

        return min(risk, 1.0)

    def _calculate_card_values(self):
        """
        Calculates strategic value of each card in hand.
        """
        card_values = {}

        for card in self.playerHand:
            value = 0.0

            matching_value = sum(1 for c in self.playerHand if c.value == card.value and c != card)
            value += matching_value * 0.5

            matching_suit = sum(1 for c in self.playerHand if c.suit == card.suit and c != card)
            value += matching_suit * 0.3

            point_value = self._get_card_point_value(card)
            value += point_value / 20

            if card.joker:
                value += 2.0

            card_values[card] = value

        return card_values

    def _has_movable_joker(self, play):
        """
        Checks if a play contains a movable joker.
        """
        return any(c.joker for c in play)

    def _calculate_best_joker_position(self, play):
        """
        Calculates the best position for a joker in a sequence.
        """
        joker_pos = next((i for i, c in enumerate(play) if c.joker), None)

        if joker_pos is None:
            return None

        if joker_pos == 0 or joker_pos == len(play) - 1:
            other_pos = len(play) - 1 if joker_pos == 0 else 0
            return other_pos

        return None

    def _contains_joker(self, play):
        """
        Checks if a play contains any jokers.
        """
        return any(c.joker for c in play)

    def _find_substitutable_card(self, play):
        """
        Finds a card that can substitute a joker in a play.
        """
        for card in self.playerHand:
            if not card.joker and card not in play:
                if self._can_substitute_joker(card, play):
                    return card

        return None

    def _can_substitute_joker(self, card, play):
        """
        Checks if a card can substitute a joker in a play.
        """
        joker_positions = [i for i, c in enumerate(play) if c.joker]

        if not joker_positions:
            return False

        card_values = Card.values
        card_idx = card_values.index(card.value) if card.value in card_values else -1

        for pos in joker_positions:
            if pos == 0 or pos == len(play) - 1:
                return True

        return False

    def _find_joker_burn_pair(self):
        """
        Finds the best card to pair with joker for burning.
        """
        non_jokers = [c for c in self.playerHand if not c.joker]

        if not non_jokers:
            return None

        card_values = self._calculate_card_values()
        worst_non_joker = min(non_jokers, key=lambda c: card_values.get(c, 0))

        return worst_non_joker

    def _get_card_point_value(self, card):
        """
        Returns the point value of a card according to game rules.
        """
        if card.joker:
            return 25
        elif card.value == 'A':
            return 20
        elif card.value in ['10', 'J', 'Q', 'K']:
            return 10
        else:
            return 5

    def learn_from_game(self, game_result):
        """
        Updates bot's learning patterns based on game result.
        game_result: dict with 'win', 'points_gained', 'plays_made', etc.
        """
        self.games_played += 1

        if game_result.get('win'):
            self.games_won += 1

        self.win_rate = self.games_won / self.games_played if self.games_played > 0 else 0.0

        self.game_history.append({
            'timestamp': datetime.now().isoformat(),
            'result': game_result,
            'win_rate': self.win_rate
        })

        self._update_strategy_weights(game_result)

    def _update_strategy_weights(self, game_result):
        """
        Updates strategy weights based on game performance.
        """
        if game_result.get('win'):
            self.strategy_weights['aggressive'] *= 1.05
            self.strategy_weights['balanced'] *= 1.02
        else:
            self.strategy_weights['conservative'] *= 1.03

        total = sum(self.strategy_weights.values())
        self.strategy_weights = {k: v/total for k, v in self.strategy_weights.items()}

    def save_model(self, filename='aibot_model.json'):
        """
        Saves bot's learned state to a file.
        """
        model_data = {
            'strategy_weights': self.strategy_weights,
            'learned_patterns': self.learned_patterns,
            'games_played': self.games_played,
            'games_won': self.games_won,
            'win_rate': self.win_rate,
            'game_history': self.game_history[-100:]
        }

        with open(filename, 'w') as f:
            json.dump(model_data, f, indent=2, default=str)

    def load_model(self, filename='aibot_model.json'):
        """
        Loads bot's learned state from a file.
        """
        if not os.path.exists(filename):
            print(f"Model file {filename} not found. Starting with default weights.")
            return

        with open(filename, 'r') as f:
            model_data = json.load(f)

        self.strategy_weights = model_data.get('strategy_weights', self.strategy_weights)
        self.learned_patterns = model_data.get('learned_patterns', self.learned_patterns)
        self.games_played = model_data.get('games_played', 0)
        self.games_won = model_data.get('games_won', 0)
        self.win_rate = model_data.get('win_rate', 0.0)
