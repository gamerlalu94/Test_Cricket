# Cricket Scorer

A command-line cricket scorer application specifically designed for Test cricket matches. It handles ball-by-ball scoring, innings management, series tracking, declarations, and continuation chases as per Test cricket rules.

## Features

- **Ball-by-Ball Scoring**: Track runs, wickets, extras (wide, no-ball), and bowler changes.
- **Test Cricket Rules**: Supports declarations, follow-on, and continuation innings when trailing teams chase lead + 30 runs.
- **Series Tracking**: Keeps track of wins in a Test series, with stumps tied leading to series wins.
- **Save/Load**: Persist match state with password protection.
- **Rollback**: Undo the last ball if needed.
- **Automated Testing**: Includes test cases to verify functionality.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/cricket-scorer.git
   cd cricket-scorer
   ```

2. Ensure Python 3.6+ is installed.

3. Run the scorer:
   ```bash
   python cricket_scorer.py
   ```

## Usage

1. Start a new match by entering the number of players per team (e.g., 3 for testing).
2. Enter player names and captains.
3. Select strikers and bowlers.
4. For each ball, choose from options: Run, Dot, Wicket, Wide, No ball, Rollback, Declare.
5. The program handles innings transitions, targets, and series outcomes automatically.

### Test Cases

Run the included test cases to verify functionality:
```bash
python run_test_cases.py
```

## Rules Implemented

- **Declaration**: In first innings with no wickets, set current score as target.
- **Continuation Chase**: Trailing team gets one innings to chase lead + 30; failure ends series.
- **Series Wins**: Team with more wins wins series; tied stumps favor winner.
- **Innings End**: All out or declaration.

## Contributing

Feel free to submit issues or pull requests.

## License

MIT License - see LICENSE file for details.