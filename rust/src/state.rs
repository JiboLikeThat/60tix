use crate::scraper::Game;
use anyhow::{Context, Result};
use chrono::{DateTime, Local};
use log::info;
use serde::{Deserialize, Serialize};
use std::collections::HashSet;
use std::path::Path;
use tokio::fs;

const STATE_FILE: &str = "state.json";

#[derive(Debug, Serialize, Deserialize)]
struct StateData {
    started: String,
    last_updated: String,
    games: Vec<Game>,
}

/// Load previous game IDs from state file
async fn load_game_ids() -> Result<HashSet<String>> {
    let path = Path::new(STATE_FILE);

    if !path.exists() {
        info!("📝 No state file found, creating new one");
        return Ok(HashSet::new());
    }

    let contents = fs::read_to_string(path)
        .await
        .context("Failed to read state file")?;

    let data: StateData = serde_json::from_str(&contents)
        .context("Failed to parse state file")?;

    let game_ids: HashSet<String> = data.games.iter().map(|g| g.game_id.clone()).collect();

    info!("📖 Loaded {} game IDs from state", game_ids.len());
    Ok(game_ids)
}

/// Save current games to state file
pub async fn save_state(games: &[Game]) -> Result<()> {
    let path = Path::new(STATE_FILE);

    // Load existing state to preserve 'started' field
    let started = if path.exists() {
        let contents = fs::read_to_string(path).await.ok();
        contents
            .and_then(|c| serde_json::from_str::<StateData>(&c).ok())
            .map(|d| d.started)
    } else {
        None
    };

    let started = started.unwrap_or_else(|| Local::now().to_rfc3339());

    let data = StateData {
        started,
        last_updated: Local::now().to_rfc3339(),
        games: games.to_vec(),
    };

    let json = serde_json::to_string_pretty(&data)
        .context("Failed to serialize state")?;

    fs::write(path, json)
        .await
        .context("Failed to write state file")?;

    info!("💾 Saved state with {} games", games.len());
    Ok(())
}

/// Check for new games compared to saved state
///
/// On first run (no state file), saves current games without marking them as new.
/// On subsequent runs, returns games that weren't in the previous state.
pub async fn check_for_new_games(games: &[Game]) -> Result<Vec<Game>> {
    let previous_game_ids = load_game_ids().await?;

    // First run - no state file exists
    if previous_game_ids.is_empty() {
        info!("🆕 First run detected - saving current games as baseline");
        save_state(games).await?;
        return Ok(Vec::new()); // Don't notify about games on first run
    }

    // Normal operation - check for new games
    let new_games: Vec<Game> = games
        .iter()
        .filter(|game| !previous_game_ids.contains(&game.game_id))
        .cloned()
        .collect();

    Ok(new_games)
}

