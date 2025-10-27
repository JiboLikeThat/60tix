#!/usr/bin/env python3
"""
Test script to demonstrate the new first-run behavior.

This shows that:
1. First run (no state file) saves games without notifying
2. Subsequent runs detect new games normally
"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.scraper import Game, check_for_new_games, STATE_FILE

def test_first_run_behavior():
    """Test that first run doesn't notify about existing games."""
    
    print("=" * 60)
    print("Testing First Run Behavior")
    print("=" * 60)
    
    # Clean state for test
    if STATE_FILE.exists():
        print(f"\n⚠️  Found existing state file: {STATE_FILE}")
        print("Please delete it to test first run behavior:")
        print(f"  rm {STATE_FILE}")
        return
    
    # Simulate first run with some games
    print("\n1️⃣  First Run - No state file exists")
    print("-" * 60)
    
    games = [
        Game("game-1", "TSV 1860 vs Team A", "1. Heimspiel", "Sa. 01.12.2025", "14:00"),
        Game("game-2", "TSV 1860 vs Team B", "2. Heimspiel", "Sa. 08.12.2025", "14:00"),
    ]
    
    print(f"Current games on website:")
    for game in games:
        print(f"  - {game}")
    
    new_games = check_for_new_games(games)
    
    print(f"\n✓ New games detected: {len(new_games)}")
    print("✓ State file created: Yes" if STATE_FILE.exists() else "✗ State file created: No")
    print(f"✓ Expected behavior: 0 new games (baseline saved)")
    print(f"✓ Actual result: {len(new_games)} new games")
    
    if len(new_games) == 0:
        print("\n✅ SUCCESS: First run behaved correctly!")
    else:
        print("\n❌ FAILED: Should not notify on first run")
        return
    
    # Simulate second run with a new game
    print("\n2️⃣  Second Run - State file exists, new game added")
    print("-" * 60)
    
    games_with_new = [
        Game("game-1", "TSV 1860 vs Team A", "1. Heimspiel", "Sa. 01.12.2025", "14:00"),
        Game("game-2", "TSV 1860 vs Team B", "2. Heimspiel", "Sa. 08.12.2025", "14:00"),
        Game("game-3", "TSV 1860 vs Team C", "3. Heimspiel", "Sa. 15.12.2025", "14:00"),  # NEW
    ]
    
    print(f"Current games on website:")
    for game in games_with_new:
        marker = " 🆕 NEW!" if game.game_id == "game-3" else ""
        print(f"  - {game}{marker}")
    
    new_games = check_for_new_games(games_with_new)
    
    print(f"\n✓ New games detected: {len(new_games)}")
    if new_games:
        print("New games:")
        for game in new_games:
            print(f"  - {game}")
    
    print(f"✓ Expected behavior: 1 new game (game-3)")
    print(f"✓ Actual result: {len(new_games)} new games")
    
    if len(new_games) == 1 and new_games[0].game_id == "game-3":
        print("\n✅ SUCCESS: New game detection works!")
    else:
        print("\n❌ FAILED: Should detect exactly 1 new game")
        return
    
    # Show state file contents
    print("\n3️⃣  Final State")
    print("-" * 60)
    
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
        print(f"State file: {STATE_FILE}")
        print(f"Games tracked: {len(state.get('games', []))}")
        print(f"Started: {state.get('started', 'Unknown')}")
        print(f"Last updated: {state.get('last_updated', 'Unknown')}")
    
    print("\n" + "=" * 60)
    print("✅ All tests passed! The new behavior works correctly.")
    print("=" * 60)
    print("\nTo clean up:")
    print(f"  rm {STATE_FILE}")


if __name__ == "__main__":
    test_first_run_behavior()

