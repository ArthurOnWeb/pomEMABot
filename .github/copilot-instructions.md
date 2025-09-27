# pomEMABot Copilot Instructions

## Project Overview
pomEMABot is a Telegram bot for monitoring cryptocurrency price trends using EMA100 crossovers and custom price alerts. It fetches real-time data from the Bitget exchange, stores user-specific watchlists and alerts in a local SQLite database, and sends notifications via Telegram. The bot simplifies trend trading by alerting on price-EMA crosses and threshold hits, without providing financial advice.

Core features:
- Add/remove watched pairs (symbol + timeframe, e.g., BTC/USDT 1h).
- Set/remove price alerts (above/below target).
- On-demand charts (candlesticks + EMA100) and current price/EMA values.
- Automated 1-minute checks for crosses and alerts.

## Architecture
The bot follows a modular structure with clear separation: bot handlers for user interactions, services for business logic (data fetching, analysis, charting), and a database layer for persistence.

- **Entry Point (`main.py`)**: Loads `.env` (requires `TG_TOKEN`), initializes SQLite DB via `Base.metadata.create_all()`, builds `python-telegram-bot` v21+ Application (async polling). In `post_init`, starts APScheduler if `chat_id.txt` exists (saves chat_id on first `/start`). Registers handlers from `bot/handlers.py`.
  
- **Bot Layer (`bot/`)**: 
  - `handlers.py`: Async command handlers (e.g., `/add SYMBOL TF`, `/chart SYMBOL [TF]`). Each uses `SessionLocal()` for scoped DB sessions, calls services for computations, replies with formatted messages (emojis, Markdown). Supports inline callbacks (e.g., "remove:SYMBOL").
  - `messages.py`: Static strings like `HELP_MESSAGE` for consistent responses.
  - `keyboards.py`: Unused in current code (potential for inline buttons).

- **Database (`database/`)**:
  - `connection.py`: SQLite engine (`ema_bot.db`, thread-safe), `SessionLocal` factory.
  - `models.py`: `Pair` (chat_id, symbol, timeframe; unique constraint) and `PriceAlert` (chat_id, symbol, target_price, direction="above/below", active=True; unique on chat_id+symbol+target).
  - `crud.py`: Basic ORM ops (query/add/remove with commit/rollback; handles duplicates via constraints).

- **Services (`services/`)**:
  - `price_fetcher.py`: Singleton CCXT Bitget client (public mode by default; auto-inits). `fetch_ohlcv(symbol, timeframe="1h", limit=100)` returns pandas DataFrame (OHLCV + timestamp as datetime).
  - `technical_analysis.py`: `compute_ema(df, span=100)` adds 'ema' column via ewm. `detect_price_ema_cross(df)` checks last two candles for price crossing EMA (returns 1 bullish, -1 bearish, 0 none).
  - `alert_system.py`: `schedule_alerts(scheduler, app, chat_id)` adds 1-min interval jobs: per-pair `check_pair` (fetches/computes/detects cross, sends if signal changed; tracks via global `_last_signals` dict to avoid spam). Global `check_price_alerts` (fetches 1m close, triggers/removes if hit).
  - `chart_generator.py`: `generate_chart(symbol, timeframe="1h")` fetches ~200 candles, computes EMA, plots mplfinance candlestick + line, returns BytesIO PNG buffer for Telegram photo.

- **Data Flows**:
  - Commands: User input → handler → DB CRUD or service call (e.g., fetch_ohlcv → compute_ema) → formatted Telegram reply.
  - Alerts: Scheduler (UTC, 1-min, misfire_grace=30s) → fetch_ohlcv (limit=102 for EMA) → analysis → conditional message (no duplicates).
  - Why this structure? Simple, stateless services; file-based chat_id enables quick setup without DB user table; public CCXT avoids auth complexity for monitoring.

- **Globals/ State**: Minimal – `_bitget_client` (price_fetcher), `_last_signals` (alert_system for cross tracking).

## Developer Workflows
- **Setup/Run Locally**:
  1. `pip install -r requirements.txt` (includes python-telegram-bot==21.6, ccxt==4.4.85, SQLAlchemy==2.0.41, pandas==2.0.3, mplfinance==0.12.9b7, APScheduler==3.11.0, python-dotenv==1.0.1).
  2. Create `.env`: `TG_TOKEN=your_bot_token_from_botfather`.
  3. `python main.py` – Auto-creates DB, starts polling. Send `/start` to bot to save chat_id.txt and enable alerts.
  - Non-obvious: Alerts/scheduler only activate post-/start; console prints "✅ Chat ID trouvé" on init.

- **Docker Deployment (`docker/`)**:
  - `docker-compose up -d` (or `build` first): Uses `Dockerfile` (assumed Python base), mounts `.env`, persists DB in volume `pomema-data`. Runs `entrypoint.sh` (likely `python main.py`). Restart: `unless-stopped`. TZ=Europe/Paris.
  - Check logs: `docker-compose logs -f pomemabot`.

- **Testing**:
  - `pytest tests/` – Currently only `test_technical_analysis.py` (verifies EMA computation and cross detection on sample DataFrames).
  - Manual: Run bot, test commands; inspect `ema_bot.db` with `sqlite3 ema_bot.db "SELECT * FROM pairs;"`. Simulate fetches by calling services directly.

- **Debugging**:
  - Errors: Handlers catch `Exception`, reply user message (e.g., "❌ Impossible de récupérer {symbol}"), print traceback to console.
  - Scheduler: Monitor APScheduler logs (job IDs like "alert_{chat_id}_{symbol}_{tf}"); stop via KeyboardInterrupt in main.
  - Data: Use `fetch_ohlcv("BTC/USDT", "1h", 5)` in REPL; check crosses with sample DF.
  - Common issues: Rate limits (CCXT enableRateLimit=True); invalid symbols (Bitget-specific, e.g., "BTC/USDT").

- **Adding Features**:
  - New command: Add to `register_handlers(app)` in handlers.py, implement async func with `update.message.reply_text`.
  - New alert type: Extend `schedule_alerts`, add DB model/CRUD.
  - Update help: Edit `HELP_MESSAGE` in messages.py.

## Conventions and Patterns
- **Python Style**: Async handlers (await replies); sync services (CCXT/pandas safe in async). Use typing (e.g., `pd.DataFrame`, `Optional[int]`). Broad excepts for robustness; no explicit logging beyond print.
- **DB Patterns**: Scoped sessions (`with SessionLocal() as db:` not used; manual close). Unique constraints prevent duplicates (e.g., add_pair returns None if exists). No migrations – rely on create_all.
- **Data Handling**: Symbols uppercase (e.g., "BTC/USDT"); timeframes CCXT strings ("1m","1h","4h"). Fetches use minimal limit (e.g., EMA_PERIOD+2=102). Pandas DFs: 'timestamp' as datetime, 'close' for EMA.
- **Messaging**: Emojis for alerts (🔔 for crosses, 📊 for data); Markdown parse_mode; concise (e.g., "/chart BTC/USDT 4h" plots last 200 candles).
- **Differ from Common**: File-based chat_id (simple, no user table); fixed 1-min polling (all pairs/alerts; scales poorly but fits solo use). Public-only CCXT (no trades). No env for DB/scheduler interval (hardcoded).
- **No Tools**: No linters (black/isort), type checkers (mypy), or CI visible. Tests minimal – focus on core analysis.

## Integration Points and Communication
- **Telegram**: ApplicationBuilder().token().post_init(start_scheduler).build().run_polling(). Handlers via CommandHandler; photo replies for charts (reply_photo(photo=buf)).
- **CCXT/Bitget**: Public fetches only; no auth (init_price_fetcher() auto). Supports spot/futures? (code uses default spot).
- **APScheduler**: AsyncIOScheduler(timezone="UTC"); interval jobs with kwargs (bot, chat_id, etc.); replace_existing=True for updates.
- **Pandas/Mplfinance**: OHLCV to plot(type='candle', addplot=EMA line, style='yahoo', savefig='png' to BytesIO).
- **Cross-Component**: Handlers import/call services/DB directly (no dependency injection). Scheduler passes Bot instance for sends.

Example Pattern – EMA Cross Alert in `check_pair`:
```python
df = fetch_ohlcv(symbol, timeframe, limit=EMA_PERIOD + 2)
df = compute_ema(df)
signal = detect_price_ema_cross(df)
if signal != 0 and signal != _last_signals.get(key, 0):
    direction = "🔔 Croisement haussier" if signal == 1 else "🔔 Croisement baissier"
    await bot.send_message(chat_id, f"{direction} {symbol} ...")
    _last_signals[key] = signal
```

## Key Files and Examples
- **Architecture Exemplars**: `main.py` (setup), `alert_system.py` (scheduling logic), `handlers.py` (command flow).
- **Patterns**: `crud.py` (DB ops with constraints, e.g., `add_pair` try-except-rollback), `price_fetcher.py` (singleton client).
- **User-Facing**: `README.md` (commands/setup), `messages.py` (text templates).
- **Deployment**: `docker-compose.yml` (volumes for DB persistence).

When editing, preserve async patterns, public CCXT, 1-min checks, and SQLite simplicity. Reference Bitget symbols/timeframes. For new services, return pandas DFs for consistency.