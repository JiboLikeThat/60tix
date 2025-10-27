use anyhow::{Context, Result};
use headless_chrome::{Browser, LaunchOptions};
use log::{debug, info, warn};
use scraper::{Html, Selector};
use serde::{Deserialize, Serialize};
use std::fmt;

const TICKETING_URL: &str = "https://www.tsv1860-ticketing.de/tsv1860/";

/// Represents a game/event
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Game {
    pub game_id: String,
    pub teams: String,
    pub matchday: String,
    pub date: String,
    pub time: String,
}

impl fmt::Display for Game {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "{} - {} {} ({})",
            self.teams, self.date, self.time, self.matchday
        )
    }
}

impl Game {
    pub fn url(&self) -> String {
        format!(
            "https://www.tsv1860-ticketing.de/tsv1860/data/Veranstaltungen2/{}",
            self.game_id
        )
    }
}

/// Fetch the ticketing page HTML using headless browser
async fn fetch_page() -> Result<String> {
    info!("Launching headless browser...");

    let browser = Browser::new(
        LaunchOptions::default_builder()
            .headless(true)
            .build()
            .context("Failed to build launch options")?,
    )
    .context("Failed to launch browser")?;

    let tab = browser
        .new_tab()
        .context("Failed to create new tab")?;

    info!("Navigating to {}", TICKETING_URL);
    tab.navigate_to(TICKETING_URL)
        .context("Failed to navigate to URL")?;

    // Wait for page to load
    tab.wait_for_element("body")
        .context("Failed to wait for body element")?;

    // Check if we're in a waiting room
    let url = tab.get_url();
    if url.contains("waiting-room") || url.contains("Warteraum") {
        info!("⏳ Entered waiting room, waiting for queue to pass...");
        
        // Wait up to 30 minutes for the waiting room to clear
        for _ in 0..180 {
            std::thread::sleep(std::time::Duration::from_secs(10));
            let current_url = tab.get_url();
            if current_url.contains("tsv1860-ticketing.de/tsv1860") && 
               !current_url.contains("waiting-room") {
                info!("✅ Waiting room cleared!");
                break;
            }
        }
    }

    info!("✅ Page loaded successfully");

    let html = tab
        .get_content()
        .context("Failed to get page content")?;

    Ok(html)
}

/// Parse games from HTML
fn parse_games(html: &str) -> Result<Vec<Game>> {
    let document = Html::parse_document(html);
    let mut games = Vec::new();

    // Find the event list container
    let eventlist_selector = Selector::parse("div.row.eventlist")
        .map_err(|e| anyhow::anyhow!("Invalid selector: {:?}", e))?;

    let Some(event_list) = document.select(&eventlist_selector).next() else {
        warn!("EventList div not found on page");
        return Ok(games);
    };

    // Find all game divs (container listitem), excluding empty items
    let listitem_selector = Selector::parse("div.container.listitem, div.container.listitem.item_1, div.container.listitem.item_2")
        .map_err(|e| anyhow::anyhow!("Invalid selector: {:?}", e))?;

    for item in event_list.select(&listitem_selector) {
        // Skip empty items
        if item
            .value()
            .classes()
            .any(|c| c.contains("b-item-empty"))
        {
            continue;
        }

        // Find itemheaderbox
        let headerbox_selector = Selector::parse("div.itemheaderbox")
            .map_err(|e| anyhow::anyhow!("Invalid selector: {:?}", e))?;

        let Some(header_box) = item.select(&headerbox_selector).next() else {
            continue;
        };

        // Get links from header box
        let link_selector = Selector::parse("a.col")
            .map_err(|e| anyhow::anyhow!("Invalid selector: {:?}", e))?;

        let links: Vec<_> = header_box.select(&link_selector).collect();
        if links.len() < 2 {
            continue;
        }

        // Extract game ID from first link's href
        let Some(href) = links[0].value().attr("href") else {
            continue;
        };

        let game_id = href
            .split('/')
            .last()
            .unwrap_or("")
            .to_string();

        if game_id.is_empty() {
            continue;
        }

        // Extract team names from nested spans
        let span_selector = Selector::parse("span.SmallerGrad1")
            .map_err(|e| anyhow::anyhow!("Invalid selector: {:?}", e))?;

        let teams = links[0]
            .select(&span_selector)
            .next()
            .map(|s| s.inner_html())
            .unwrap_or_else(|| "Unknown".to_string());

        // Extract matchday from second link
        let matchday = links[1].inner_html();

        // Extract date
        let date_selector = Selector::parse("span.date")
            .map_err(|e| anyhow::anyhow!("Invalid selector: {:?}", e))?;

        let date = item
            .select(&date_selector)
            .next()
            .map(|s| s.inner_html())
            .unwrap_or_else(|| "Unknown".to_string());

        // Extract time
        let time_selector = Selector::parse("span.time")
            .map_err(|e| anyhow::anyhow!("Invalid selector: {:?}", e))?;

        let time = item
            .select(&time_selector)
            .next()
            .map(|s| s.inner_html().replace("Uhr", "").trim().to_string())
            .unwrap_or_else(|| "".to_string());

        let game = Game {
            game_id,
            teams,
            matchday,
            date,
            time,
        };

        debug!("Parsed game: {:?}", game);
        games.push(game);
    }

    info!("✅ Parsed {} game(s)", games.len());
    Ok(games)
}

/// Fetch and parse games from the ticketing website
pub async fn get_games() -> Result<Vec<Game>> {
    info!("🔍 Checking for games...");
    let html = fetch_page().await?;
    let games = parse_games(&html)?;
    Ok(games)
}

