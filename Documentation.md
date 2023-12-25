# Documentation for Forex Trading Bot

## Overview
The Forex Trading Bot is an automated trading system designed for the Forex market, with a focus on the EUR/USD currency pair. It uses algorithmic strategies to execute trades based on technical analysis.

## Broker: OANDA
- **OANDA API**: The bot uses the OANDA API for market data access and trade execution.
- **Account Requirement**: Users must have an OANDA account and obtain API keys for bot operation.

## Trading Strategy
The bot's strategy involves analyzing candlestick patterns in the EUR/USD currency pair.

### Strategy Details
- **Signal Generation**:
  - **Bearish Pattern**: A sell signal is generated when the current candle closes lower than its opening, and the previous candle closed higher than its opening.
  - **Bullish Pattern**: A buy signal is generated when the current candle closes higher than its opening, and the previous candle closed lower than its opening.
  - **No Clear Pattern**: No action is taken if the patterns do not match these criteria.

### Risk Management
- **Stop Loss and Take Profit**: The bot sets stop loss and take profit orders based on the previous candlestick's price range.

## Components
1. **Data Fetching (`get_candles`)**:
   - Retrieves real-time candle data from OANDA.
2. **Signal Processing (`signal_generator`)**:
   - Analyzes candle data to generate trading signals.
3. **Order Execution (`trading_job`)**:
   - Executes trades based on the generated signals.
4. **Scheduling**:
   - Uses APScheduler to automate trading at specific times.

## Installation and Usage
For detailed instructions on setting up and using the Forex Trading Bot, please refer to the README file included in this repository.

## Monitoring and Performance
- Regular monitoring of the bot's performance is recommended.
- Track performance metrics like win rate and risk-reward ratio.

## Future Enhancements
- Plans to add support for more currency pairs.
- Ongoing optimization of the trading strategy.

## Disclaimer
The Forex Trading Bot is for educational purposes and should be used with caution. Trading involves risk, and users should be fully aware of these risks before using the bot.

---
