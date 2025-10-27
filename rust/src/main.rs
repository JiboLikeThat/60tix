mod notifier;
mod scraper;
mod state;

use anyhow::Result;
use chrono::{DateTime, Local};
use dotenv::dotenv;
use log::{error, info};
use std::env;
use std::sync::Arc;
use tokio::sync::Mutex;
use tokio::time::{sleep, Duration};
use tokio_cron_scheduler::{Job, JobScheduler};

/// Bot statistics
#[derive(Debug, Clone)]
struct BotStats {
    start_time: DateTime<Local>,
    check_counter: u64,
    last_check_time: Option<DateTime<Local>>,
}

impl BotStats {
    fn new() -> Self {
        Self {
            start_time: Local::now(),
            check_counter: 0,
            last_check_time: None,
        }
    }

    fn increment_check(&mut self) {
        self.check_counter += 1;
        self.last_check_time = Some(Local::now());
    }

    fn uptime(&self) -> String {
        let duration = Local::now().signed_duration_since(self.start_time);
        let days = duration.num_days();
        let hours = duration.num_hours() % 24;
        let minutes = duration.num_minutes() % 60;

        if days > 0 {
            format!("{}d {}h {}m", days, hours, minutes)
        } else if hours > 0 {
            format!("{}h {}m", hours, minutes)
        } else {
            format!("{}m", minutes)
        }
    }
}

/// Perform a scheduled check for new games
async fn scheduled_check(
    stats: Arc<Mutex<BotStats>>,
    notifier: Arc<notifier::TelegramNotifier>,
) -> Result<()> {
    // Update stats
    {
        let mut stats = stats.lock().await;
        stats.increment_check();
        info!("Check #{} - {}", stats.check_counter, Local::now().format("%Y-%m-%d %H:%M:%S"));
    }

    // Fetch games from website
    let games = scraper::get_games().await?;

    if games.is_empty() {
        info!("⚠️  No games found on website");
        return Ok(());
    }

    // Check for new games
    let new_games = state::check_for_new_games(&games).await?;

    if !new_games.is_empty() {
        info!("🎉 Found {} NEW game(s)!", new_games.len());
        for game in &new_games {
            info!("  NEW: {}", game);
        }

        // Send Telegram notification
        match notifier.notify_new_games(&new_games).await {
            Ok(_) => info!("✅ Telegram notification sent successfully"),
            Err(e) => error!("❌ Failed to send Telegram notification: {}", e),
        }
    } else {
        info!("✅ No new games found");
    }

    // Save current state
    state::save_state(&games).await?;

    Ok(())
}

/// Send daily health check message
async fn health_check(
    stats: Arc<Mutex<BotStats>>,
    notifier: Arc<notifier::TelegramNotifier>,
) -> Result<()> {
    info!("Performing health check...");

    let stats = stats.lock().await;
    let uptime = stats.uptime();
    let last_check = stats
        .last_check_time
        .map(|t| t.format("%Y-%m-%d %H:%M:%S").to_string())
        .unwrap_or_else(|| "No checks yet".to_string());

    match notifier
        .send_health_check(
            stats.start_time,
            &uptime,
            stats.check_counter,
            &last_check,
        )
        .await
    {
        Ok(_) => info!("✅ Health check sent to Telegram"),
        Err(e) => error!("❌ Health check failed: {}", e),
    }

    Ok(())
}

#[tokio::main]
async fn main() -> Result<()> {
    // Initialize environment and logging
    dotenv().ok();
    env_logger::Builder::from_env(env_logger::Env::default().default_filter_or("info")).init();

    // Load configuration
    let check_interval_minutes: u64 = env::var("CHECK_INTERVAL_MINUTES")
        .unwrap_or_else(|_| "10".to_string())
        .parse()
        .unwrap_or(10);

    let health_check_hour: u32 = env::var("HEALTH_CHECK_HOUR")
        .unwrap_or_else(|_| "9".to_string())
        .parse()
        .unwrap_or(9);

    // Initialize components
    let stats = Arc::new(Mutex::new(BotStats::new()));
    let notifier = Arc::new(notifier::TelegramNotifier::new()?);

    info!("Starting TSV 1860 München Ticket Monitor (Rust)");
    info!("Started at: {}", Local::now().format("%Y-%m-%d %H:%M:%S"));
    info!("============================================================");

    // Run first check immediately
    info!("Running initial check...");
    if let Err(e) = scheduled_check(Arc::clone(&stats), Arc::clone(&notifier)).await {
        error!("Initial check failed: {}", e);
    }

    info!("============================================================");
    info!("Continuing with scheduled checks every {} minutes", check_interval_minutes);
    info!("============================================================");

    // Setup scheduler
    let mut scheduler = JobScheduler::new().await?;

    // Add periodic check job
    {
        let stats_clone = Arc::clone(&stats);
        let notifier_clone = Arc::clone(&notifier);
        let check_interval = check_interval_minutes;

        scheduler.add(
            Job::new_async(format!("0 */{} * * * *", check_interval).as_str(), move |_uuid, _l| {
                let stats = Arc::clone(&stats_clone);
                let notifier = Arc::clone(&notifier_clone);
                Box::pin(async move {
                    if let Err(e) = scheduled_check(stats, notifier).await {
                        error!("Scheduled check failed: {}", e);
                    }
                })
            })?,
        ).await?;
    }

    // Add daily health check job
    {
        let stats_clone = Arc::clone(&stats);
        let notifier_clone = Arc::clone(&notifier);

        scheduler.add(
            Job::new_async(format!("0 0 {} * * *", health_check_hour).as_str(), move |_uuid, _l| {
                let stats = Arc::clone(&stats_clone);
                let notifier = Arc::clone(&notifier_clone);
                Box::pin(async move {
                    if let Err(e) = health_check(stats, notifier).await {
                        error!("Health check failed: {}", e);
                    }
                })
            })?,
        ).await?;
    }

    scheduler.start().await?;

    info!("✅ Scheduler started. Press Ctrl+C to stop");

    // Wait for Ctrl+C
    tokio::signal::ctrl_c().await?;

    info!("\n🛑 Shutting down ticket monitor...");

    // Send shutdown notification
    let stats = stats.lock().await;
    let uptime = stats.uptime();

    info!("Total checks performed: {}", stats.check_counter);
    info!("Total uptime: {}", uptime);

    if let Err(e) = notifier
        .send_shutdown_notification(stats.start_time, &uptime, stats.check_counter)
        .await
    {
        error!("Failed to send shutdown notification: {}", e);
    } else {
        info!("✅ Shutdown notification sent to Telegram");
    }

    scheduler.shutdown().await?;

    Ok(())
}

