use crate::scraper::Game;
use anyhow::{Context, Result};
use chrono::{DateTime, Local};
use log::{info, warn};
use serde::Serialize;
use std::env;

const TELEGRAM_API_BASE: &str = "https://api.telegram.org";

#[derive(Debug, Serialize)]
struct SendMessageRequest {
    chat_id: String,
    text: String,
    parse_mode: String,
}

/// Telegram bot notifier
pub struct TelegramNotifier {
    bot_token: String,
    chat_id: String,
    client: reqwest::Client,
}

impl TelegramNotifier {
    /// Create a new Telegram notifier from environment variables
    pub fn new() -> Result<Self> {
        let bot_token = env::var("TELEGRAM_BOT_TOKEN")
            .context("TELEGRAM_BOT_TOKEN not set in environment")?;
        
        let chat_id = env::var("TELEGRAM_CHAT_ID")
            .context("TELEGRAM_CHAT_ID not set in environment")?;

        if bot_token.is_empty() || bot_token == "your_bot_token_here" {
            anyhow::bail!("Invalid TELEGRAM_BOT_TOKEN");
        }

        if chat_id.is_empty() || chat_id == "your_chat_id_here" {
            anyhow::bail!("Invalid TELEGRAM_CHAT_ID");
        }

        Ok(Self {
            bot_token,
            chat_id,
            client: reqwest::Client::new(),
        })
    }

    /// Send a message to Telegram
    async fn send_message(&self, text: &str) -> Result<()> {
        let url = format!("{}/bot{}/sendMessage", TELEGRAM_API_BASE, self.bot_token);

        let request = SendMessageRequest {
            chat_id: self.chat_id.clone(),
            text: text.to_string(),
            parse_mode: "HTML".to_string(),
        };

        let response = self
            .client
            .post(&url)
            .json(&request)
            .send()
            .await
            .context("Failed to send Telegram message")?;

        if !response.status().is_success() {
            let status = response.status();
            let body = response.text().await.unwrap_or_default();
            anyhow::bail!("Telegram API error {}: {}", status, body);
        }

        Ok(())
    }

    /// Send notification about new games
    pub async fn notify_new_games(&self, games: &[Game]) -> Result<()> {
        if games.is_empty() {
            return Ok(());
        }

        let mut message = String::from("🎟️ <b>New Game(s) Available!</b>\n\n");

        for game in games {
            message.push_str(&format!(
                "⚽ <b>{}</b>\n📅 {} {}\n🏟️ {}\n🔗 <a href=\"{}\">Buy Tickets</a>\n\n",
                game.teams,
                game.date,
                game.time,
                game.matchday,
                game.url()
            ));
        }

        self.send_message(&message).await?;
        info!("✅ Sent notification for {} new game(s)", games.len());
        Ok(())
    }

    /// Send daily health check message
    pub async fn send_health_check(
        &self,
        start_time: DateTime<Local>,
        uptime: &str,
        check_count: u64,
        last_check: &str,
    ) -> Result<()> {
        let message = format!(
            "💚 <b>Health Check</b>\n\n\
             ✅ <b>Status:</b> Running\n\
             🕐 <b>Started:</b> {}\n\
             ⏱️ <b>Uptime:</b> {}\n\
             🔄 <b>Checks:</b> {}\n\
             📅 <b>Last check:</b> {}",
            start_time.format("%Y-%m-%d %H:%M:%S"),
            uptime,
            check_count,
            last_check
        );

        self.send_message(&message).await?;
        Ok(())
    }

    /// Send shutdown notification
    pub async fn send_shutdown_notification(
        &self,
        start_time: DateTime<Local>,
        uptime: &str,
        check_count: u64,
    ) -> Result<()> {
        let message = format!(
            "🛑 <b>Bot Shutting Down</b>\n\n\
             🕐 <b>Started:</b> {}\n\
             🕑 <b>Stopped:</b> {}\n\
             ⏱️ <b>Total uptime:</b> {}\n\
             🔄 <b>Total checks:</b> {}",
            start_time.format("%Y-%m-%d %H:%M:%S"),
            Local::now().format("%Y-%m-%d %H:%M:%S"),
            uptime,
            check_count
        );

        self.send_message(&message).await?;
        Ok(())
    }
}

