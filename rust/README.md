# 60tix - Rust Implementation

High-performance Rust implementation of the TSV 1860 München ticket monitor.

## Status

🚧 **Coming Soon**

This implementation is planned but not yet started. Planned features:

- Async runtime with tokio
- Web scraping with headless_chrome or playwright-rust
- Telegram bot API client
- JSON-based state persistence
- Minimal memory footprint
- Fast startup and low CPU usage

## Planned Architecture

```
rust/
├── src/
│   ├── main.rs          # Entry point & scheduler
│   ├── scraper.rs       # Web scraping logic
│   ├── notifier.rs      # Telegram integration
│   └── state.rs         # State management
├── Cargo.toml           # Dependencies
└── README.md            # This file
```

## Contributing

Interested in implementing this? PRs are welcome! See the Python implementation in `../python/` for reference.

