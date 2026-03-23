# AI Bot - Frequently Asked Questions

## Training & Setup

### Q: How do I train the bot?
**A:** Run this command in your project directory:
```bash
python train_bot.py --games 500
```
This trains the bot through 500 simulated games and saves the model to `aibot_model.json`.

### Q: How long does training take?
**A:** About 1-2 seconds per game, so 500 games takes roughly 10 minutes. You can train while working on other parts of your game.

### Q: Can I continue training a bot?
**A:** Yes! Use the `--load` parameter:
```bash
python train_bot.py --load aibot_model.json --games 200
```
This continues training from where it left off.

### Q: What's the minimum number of games to train?
**A:** Start with 100 games minimum. The bot improves progressively:
- 100 games: Basic competency
- 500 games: Good player
- 1000+ games: Very strong player

## Bot Behavior

### Q: Why does the bot sometimes play badly?
**A:** The bot learns statistically. Early training (first 100 games) has basic strategy. As it plays more, it learns better patterns.

### Q: Will the bot always beat me?
**A:** With 500+ games of training, it should be very competitive. The bot's skill grows progressively.

### Q: Can I have multiple AI bots with different skill levels?
**A:** Yes! Train different models:
```bash
python train_bot.py --games 100 --output easy_bot.json
python train_bot.py --games 500 --output normal_bot.json
python train_bot.py --games 1000 --output hard_bot.json
```

Then load different models:
```python
easy_bot = AIBot(1, "Easy AI")
easy_bot.load_model('easy_bot.json')

hard_bot = AIBot(2, "Hard AI")
hard_bot.load_model('hard_bot.json')
```

## Integration Issues

### Q: The bot doesn't make the initial play (no bajada)
**A:** The bot might not have valid combinations. Check:
1. Is the round number correct?
2. Are the Card values in the correct order?
3. Try training with more games

### Q: The bot is not inserting cards into plays
**A:** Make sure:
1. `decide_insert_card()` is called AFTER bot has bajado (`downHand == True`)
2. The `plays_in_table` parameter contains valid board plays
3. The bot's hand actually has cards that can be inserted

### Q: Game crashes when bot plays
**A:** Check these common issues:
1. **Card removal**: Remove discarded card from `playerHand`
2. **Insertion**: Remove inserted card from `playerHand`
3. **Drawing**: Add drawn card to `playerHand`
4. **Validation**: Ensure all card operations maintain hand consistency

### Q: Bot makes invalid plays
**A:** The bot should validate through its internal checks, but verify:
1. `Card.values` has correct order: A, 1-10, J, Q, K, A
2. Suit names match your Card class
3. Joker card has `joker=True` property

## Decision Methods

### Q: What's the difference between all those decide_* methods?
**A:** Here's the order in a typical turn:

1. **decide_draw_source()** - Pick card source (discard or deck)
2. **decide_play_cards()** - Make initial play (if not bajado)
3. **decide_insert_card()** - Insert into existing plays (after bajada)
4. **decide_move_joker()** - Rearrange joker in sequences (optional)
5. **decide_discard()** - Remove a card

### Q: What does "bajada" mean?
**A:** It's the Spanish term for the initial play. Each round has different requirements:
- Round 1: Must play 1 trio + 1 sequence
- Round 2: Must play 2 sequences
- Round 3: Must play 3 trios
- Round 4: Must play 2 trios + 1 sequence (using ALL cards)

After bajada, the bot can only insert cards or discard.

### Q: How does the bot decide to insert vs discard?
**A:** The bot:
1. Looks at all cards in hand
2. Checks which can be inserted into board plays
3. Calculates best insertion (prioritizes high-point cards)
4. If found, inserts; otherwise discards worst card

## Card Insertion Deep Dive

### Q: Why is card insertion so critical?
**A:** Because:
- **Only way to win**: Emptying your hand wins the round
- **Reduces points**: Prevents accumulating 500+ points
- **Game strategy**: The entire endgame revolves around this
- **Without it**: Bot will always lose eventually

### Q: Can the bot insert into any play?
**A:** Yes, but with rules:
- **Sequences**: Can add consecutive cards at either end
- **Trios**: Can add same-value cards or joker (if < 2 jokers)
- **Validation**: Bot checks rules automatically

### Q: What if the bot can't insert anything?
**A:** It discards its worst card and passes the turn.

## Learning & Improvement

### Q: How does the bot learn?
**A:** Through `learn_from_game()`:
- Records if game was won or lost
- Updates strategy weights based on outcome
- Winning strategy weights increase
- Losing strategy weights decrease

### Q: What are strategy weights?
**A:** The bot has three strategies:
- **Aggressive**: Take more risks, play more cards
- **Conservative**: Play it safe, minimize losses
- **Balanced**: Mix of both approaches

The weights determine which strategy is used. Learning adjusts these proportions.

### Q: Do I have to call learn_from_game()?
**A:** For training, no - `train_bot.py` does it automatically. But for live games, yes:

```python
# After round ends
bot.learn_from_game({
    'win': player == winner,
    'points_gained': player.playerPoints,
    'plays_made': len(player.playMade)
})
```

### Q: When should I save the model?
**A:** After each game, if you want the bot to learn:
```python
bot.learn_from_game(result)
bot.save_model('aibot_model.json')
```

Or after multiple games to batch-save:
```python
for i in range(10):
    play_game(bot)
bot.save_model('aibot_model.json')
```

## Performance & Optimization

### Q: How can I make the bot smarter?
**A:**
1. Train with more games (500 → 1000)
2. Train against multiple opponent types
3. Let it learn from real games
4. Fine-tune strategy weights if needed

### Q: Can I modify strategy weights manually?
**A:** Yes:
```python
bot = AIBot(1, "Custom Bot")
bot.strategy_weights = {
    'aggressive': 0.7,  # More aggressive
    'conservative': 0.1,
    'balanced': 0.2
}
```

### Q: What's the bot's win rate typically?
**A:** After training:
- 100 games: ~40-50% win rate
- 500 games: ~50-65% win rate
- 1000 games: ~60-70% win rate

(Depends on opponent strength)

## Debugging

### Q: How do I see what the bot is thinking?
**A:** Use the example script:
```bash
python example_ai_usage.py
```
This shows decisions for each situation.

### Q: Can I print debug info?
**A:** Modify the code to add prints:
```python
# In AIBot.py, add to any decide_* method:
print(f"Bot considering: {self.playerHand}")
print(f"Decision: {result}")
```

### Q: How do I check bot statistics?
**A:** Load and inspect:
```python
bot = AIBot(1, "Test")
bot.load_model('aibot_model.json')
print(f"Win Rate: {bot.win_rate:.2%}")
print(f"Games: {bot.games_played}")
print(f"Wins: {bot.games_won}")
```

## Advanced Topics

### Q: Can I create custom AI strategies?
**A:** Yes! Extend the AIBot class:
```python
class CustomBot(AIBot):
    def decide_discard(self, must_burn_joker=False):
        # Your custom logic here
        return super().decide_discard(must_burn_joker)
```

### Q: How do I analyze bot decisions?
**A:** Access `game_history`:
```python
bot.load_model('aibot_model.json')
for game in bot.game_history[-10:]:  # Last 10 games
    print(game)
```

### Q: Can bots play against each other offline?
**A:** Yes, use `AITrainer.train_bots()` which simulates games.

## Troubleshooting

### Q: "aibot_model.json not found"
**A:** Train the bot first:
```bash
python train_bot.py --games 100
```

### Q: "Card has no attribute 'joker'"
**A:** Your Card class might not have a `joker` property. Check Card.py and ensure all cards have this attribute.

### Q: Bot keeps losing every game
**A:**
1. Train with more games (at least 500)
2. Check that `decide_insert_card()` is being called
3. Verify game rules are implemented correctly
4. Test with `demo_ai_game.py`

### Q: Bot plays invalid moves despite validation
**A:** Check:
1. Is `Card.values` in the correct order?
2. Are suit names consistent?
3. Are Joker cards properly identified?

## Best Practices

### Q: What's the recommended training schedule?
**A:**
1. Initial: `python train_bot.py --games 500`
2. After integration: `train_bot.py --load aibot_model.json --games 100`
3. Weekly: Train additional games as bot plays more

### Q: Should I train multiple bots?
**A:** Yes! Training 2-3 bots together improves their play against each other.

### Q: How often should the bot be retrained?
**A:**
- For casual play: After every 50-100 real games
- For competitive play: Train periodically (weekly)
- Before major releases: Retrain with 1000+ games

## Still Have Questions?

Check these files for more info:
- **AI_INTEGRATION_GUIDE.md** - Complete technical guide
- **AIBOT_QUICK_REFERENCE.md** - Quick lookup
- **example_ai_usage.py** - Code examples
- **demo_ai_game.py** - Working demonstration

Or look at the inline documentation in:
- **AIBot.py** - Detailed method documentation
- **AITrainer.py** - Training system
