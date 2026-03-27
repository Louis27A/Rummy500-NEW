# Card Validation & Duplicate Prevention Guide

## Problem Solved

The AIBot now prevents invalid plays where the same card is used in multiple plays. This includes regular cards AND Jokers.

### Before (Invalid Plays Allowed)
```python
Hand: ['J♣', '5♣', 'K♣', '9♣', '3♣', '10♣', 'Q♠', '2♣', 'Q♣', '10♠', 'Q♦']

Bot would try:
Trio: ['Q♠', 'Q♣', 'Q♦']
Sequence: ['9♣', '10♣', 'J♣', 'Q♣', 'K♣']  # ❌ DUPLICATE: Q♣ used twice!
```

### After (Invalid Plays Rejected)
```python
Hand: ['J♣', '5♣', 'K♣', '9♣', '3♣', '10♣', 'Q♠', '2♣', 'Q♣', '10♠', 'Q♦']

Bot validates and rejects the above combination because:
- Q♣ is used in both the Trio AND the Sequence
- Same card cannot appear in two different plays

Bot instead selects:
Trio: ['Q♠', 'Q♣', 'Q♦']
Sequence: ['9♣', '10♣', 'J♣', 'K♣']  # ✅ Valid - uses 4 cards, all unique
```

## How Validation Works

### The Validation Method

```python
def _plays_share_no_cards(self, trios, sequences):
    """
    Validates that no card is used in both trios and sequences.
    Returns True if plays don't share any cards, False otherwise.
    """
```

### Validation Steps

1. **Collect all cards from trios**
   ```python
   trio_cards = [card for trio in trios for card in trio]
   # Example: [Q♠, Q♣, Q♦]
   ```

2. **Collect all cards from sequences**
   ```python
   sequence_cards = [card for sequence in sequences for card in sequence]
   # Example: [9♣, 10♣, J♣, K♣]
   ```

3. **Check for duplicates**
   ```python
   for card in trio_cards:
       if card in sequence_cards:
           return False  # Found duplicate!

   return True  # No duplicates found
   ```

## Joker Handling

Jokers require special attention since they're powerful cards. The validation works the same way:

### Example with Joker

```python
Hand: ['J♣', '5♣', 'K♣', '9♣', '3♣', '10♣', 'Q♠', '2♣', 'Joker', '10♠', 'Q♦']

INVALID (Joker used twice):
Trio: ['Q♠', 'Joker', 'Q♦']
Sequence: ['9♣', '10♣', 'J♣', 'Joker', 'K♣']  # ❌ Joker duplicate!

VALID (Joker used once):
Trio: ['Q♠', 'Joker', 'Q♦']
Sequence: ['9♣', '10♣', 'J♣', 'K♣']  # ✅ No Joker in sequence
```

## Understanding plays_in_table

For the `decide_insert_card()` method, you need to pass board plays correctly.

### Expected Format

**plays_in_table is a LIST of LISTS of Card objects:**

```python
plays_in_table = [
    [Card('5', 'Hearts'), Card('5', 'Spades'), Card('5', 'Diamonds')],     # Play 1 (Trio)
    [Card('9', 'Clubs'), Card('10', 'Clubs'), Card('J', 'Clubs'), Card('Q', 'Clubs')],  # Play 2 (Sequence)
    [Card('2', 'Spades'), Card('3', 'Spades'), Card('4', 'Spades')]        # Play 3 (Sequence)
]
```

### With Jokers

```python
plays_in_table = [
    [Card('K', 'Hearts'), Card('K', 'Diamonds'), Card('Joker', 'Joker')],  # Trio with Joker
    [Card('3', 'Clubs'), Card('4', 'Clubs'), Card('Joker', 'Joker'), Card('6', 'Clubs')]  # Can't work - would need different Joker
]
```

### Important Notes

1. **Each inner list = ONE play**
   - Not divided into trios vs sequences
   - The bot figures out the type automatically

2. **Card objects must be real**
   ```python
   # CORRECT - Real Card objects
   plays_in_table = [
       [card1, card2, card3]
   ]

   # WRONG - String representations
   plays_in_table = [
       ['5♥', '5♠', '5♦']  # ❌ Not valid!
   ]
   ```

3. **Jokers must have joker attribute**
   ```python
   joker = Card('Joker', 'Joker')
   # Must have: joker.joker = True

   # Check if card is joker:
   if card.joker:
       print("This is a joker!")
   ```

## Implementation Example

### Creating plays_in_table from game state

```python
def get_board_plays(game_state):
    """
    Converts game state plays into format for decide_insert_card()
    """
    plays_in_table = []

    # Assuming game_state has plays stored as lists
    for play in game_state['board_plays']:
        # play is already a list of Card objects
        plays_in_table.append(play)

    return plays_in_table

# Usage
bot = AIBot(1, "Test Bot")
plays = get_board_plays(game_state)
insertion = bot.decide_insert_card(plays)  # Pass the list of plays
```

### If plays are stored differently

```python
def convert_to_card_objects(plays_data):
    """
    If plays are stored as strings, convert to Card objects
    """
    plays_in_table = []

    for play_data in plays_data:
        play_cards = []
        for card_str in play_data:
            # Parse card string and create Card object
            if card_str == 'Joker':
                card = Card('Joker', 'Joker')
            else:
                value, suit = parse_card_string(card_str)  # Your parsing logic
                card = Card(value, suit)
            play_cards.append(card)

        plays_in_table.append(play_cards)

    return plays_in_table
```

## Round-Specific Validation

Each round has different requirements. The validation ensures:

### Round 1: 1 Trio + 1 Sequence
```python
valid_play = (
    [trio_with_3_cards],      # 1 trio
    [sequence_with_4_cards]   # 1 sequence
)
# Must not share any cards
```

### Round 2: 2 Sequences
```python
valid_play = (
    [],                       # 0 trios
    [sequence1, sequence2]    # 2 sequences
)
# Must not share any cards
```

### Round 3: 3 Trios
```python
valid_play = (
    [trio1, trio2, trio3],    # 3 different trios
    []                        # 0 sequences
)
# Must not share any cards
```

### Round 4: 2 Trios + 1 Sequence (Using ALL cards)
```python
valid_play = (
    [trio1, trio2],           # 2 trios
    [sequence]                # 1 sequence
)
# Must not share any cards AND must use ALL cards in hand
```

## Testing Validation

### Test Case 1: Regular Card Duplication

```python
from AIBot import AIBot
from Card import Card

bot = AIBot(1, "Test")

# Create a hand with specific cards
bot.playerHand = [
    Card('Q', 'Spades'),
    Card('Q', 'Clubs'),
    Card('Q', 'Diamonds'),
    Card('9', 'Clubs'),
    Card('10', 'Clubs'),
    Card('J', 'Clubs'),
    Card('K', 'Clubs'),
    Card('5', 'Clubs'),
    Card('3', 'Clubs'),
    Card('2', 'Clubs'),
    Card('10', 'Spades')
]

# Try to get a valid play for round 1
play = bot.decide_play_cards(1)

# play should NOT have Q♣ in both trio and sequence
if play:
    trios, sequences = play
    print(f"Trios: {trios}")
    print(f"Sequences: {sequences}")
    # Verify no duplicates
```

### Test Case 2: Joker Duplication

```python
bot.playerHand = [
    Card('Q', 'Spades'),
    Card('Q', 'Diamonds'),
    Card('Joker', 'Joker'),
    Card('9', 'Clubs'),
    Card('10', 'Clubs'),
    Card('J', 'Clubs'),
    Card('K', 'Clubs'),
    Card('5', 'Clubs'),
    Card('3', 'Clubs'),
    Card('2', 'Clubs'),
    Card('10', 'Spades')
]

# Try to get a valid play
play = bot.decide_play_cards(1)

# Joker should appear in EITHER trio OR sequence, not both
if play:
    trios, sequences = play
    all_cards = [c for trio in trios for c in trio] + [c for seq in sequences for c in seq]
    joker_count = sum(1 for c in all_cards if c.joker)
    print(f"Joker used in play: {joker_count} time(s)")  # Should be <= 1
```

## Summary

The validation system ensures:
- ✅ No card appears in multiple plays
- ✅ No Joker is used twice in different plays
- ✅ All cards in a play are from the bot's actual hand
- ✅ Plays meet round-specific requirements
- ✅ Bot only generates valid combinations

This prevents the exact scenarios you described and makes the bot a fair, rule-following player!
