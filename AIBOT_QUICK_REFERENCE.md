# AI Bot Quick Reference

## Quick Setup (3 Steps)

```bash
# Step 1: Train the bot
python train_bot.py --games 500

# Step 2: In your ui2.py, add:
from AIBot import AIBot
bot = AIBot(1, "AI Opponent")
bot.load_model('aibot_model.json')

# Step 3: During bot's turn:
if hasattr(player, 'is_ai') and player.is_ai:
    # Bot makes all decisions automatically!
    draw = player.decide_draw_source(discard, deck_size, players_info)
    play = player.decide_play_cards(round_number)
    insert = player.decide_insert_card(plays_in_table)  # CRITICAL!
    discard = player.decide_discard()
```

## Key Methods (In Order of Use)

| Method | Purpose | Returns |
|--------|---------|---------|
| `decide_draw_source()` | Draw from discard or deck? | `bool` |
| `decide_play_cards()` | Which cards to play? | `(trios, sequences)` |
| `decide_insert_card()` | Insert into existing plays? | `(index, card, pos)` |
| `decide_move_joker()` | Move joker in sequence? | `(index, position)` |
| `decide_discard()` | Which card to discard? | `Card` |

## Critical: Card Insertion

**This is the most important mechanic!** Without `decide_insert_card()`, the bot will lose.

```python
# After bot bajada (downHand == True)
insertion = bot.decide_insert_card(board_plays)
if insertion:
    play_idx, card, position = insertion
    board_plays[play_idx].insert(position, card)
    bot.playerHand.remove(card)
```

## Learning & Saving

```python
# Record game result
bot.learn_from_game({
    'win': True,
    'points_gained': 50,
    'plays_made': 4
})

# Save progress
bot.save_model('aibot_model.json')

# Continue training later
python train_bot.py --load aibot_model.json --games 200
```

## Bot Attributes

```python
bot.is_ai                    # True (identifies as AI)
bot.win_rate                 # 0.0 to 1.0
bot.games_played             # Total games
bot.games_won                # Wins
bot.strategy_weights         # {'aggressive': 0.5, ...}
bot.playerHand               # List of Card objects
bot.playerPoints             # Accumulated points
bot.downHand                 # Has made initial play?
bot.playMade                 # List of plays made
```

## Decision Flow (Per Turn)

```
1. Draw Phase
   └─ decide_draw_source() → Take discard? Yes/No

2. Playing Phase (if not yet bajado)
   └─ decide_play_cards() → What to play?

3. Insertion Phase (if bajado)
   └─ decide_insert_card() → Where to insert?
   └─ decide_move_joker() → Move joker?

4. Discard Phase
   └─ decide_discard() → What card to remove?
```

## Training Parameters

```bash
python train_bot.py \
    --games 500            # Number of games to train
    --output my_bot.json   # Save location
    --load my_bot.json     # Continue from checkpoint
    --bots 1               # Number of bots to train
```

## Testing the Bot

```bash
# Run examples
python example_ai_usage.py

# This shows:
- Creating & loading bots
- All decision methods in action
- Learning from games
- Full turn simulation
```

## Performance Metrics

After training, check:
```python
bot.load_model('aibot_model.json')
print(f"Win Rate: {bot.win_rate:.2%}")
print(f"Games: {bot.games_played}")
print(f"Experience: {bot.games_won} victories")
```

## Common Issues

| Issue | Solution |
|-------|----------|
| Bot makes invalid plays | Check Card.values order |
| Model not found | Run `python train_bot.py` first |
| Bot always loses | Train with more games (500-1000) |
| No insertions happening | Verify `downHand` is True before `decide_insert_card()` |

## Integration Checklist

- [ ] Train bot: `python train_bot.py --games 500`
- [ ] Import AIBot in ui2.py
- [ ] Create bot instance with load_model()
- [ ] Call `decide_draw_source()` for draw phase
- [ ] Call `decide_play_cards()` for play phase
- [ ] Call `decide_insert_card()` for insertion phase ⭐ CRITICAL
- [ ] Call `decide_discard()` for discard phase
- [ ] Call `learn_from_game()` at round end
- [ ] Call `save_model()` to persist learning

## File Structure

```
AIBot.py                    # Main bot class
AITrainer.py               # Training system
train_bot.py               # Training CLI tool
example_ai_usage.py        # Usage examples
aibot_model.json           # Trained model (generated)
AI_INTEGRATION_GUIDE.md    # Full documentation
AIBOT_QUICK_REFERENCE.md   # This file
```

---

**Remember**: The bot inherits from `Player`, so it works like a regular player but makes decisions automatically!
