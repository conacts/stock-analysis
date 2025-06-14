# 🚀 Stock Research System

**Professional, modular stock analysis platform with automated research pipeline**

## 🎯 Overview

This is a **complete rewrite** of our stock analysis system, transforming scattered scripts into a **professional, modular architecture** that can:

-   **🔄 Automated Daily Research** - Trigger → Screen → Analyze → Decide
-   **🤖 AI-Powered Analysis** - Deep insights with LLM integration
-   **📊 Historical Decision Tracking** - Store daily reasoning and performance
-   **⚡ Dynamic Research** - Real-time screening and analysis
-   **🎨 Clean Architecture** - Modular, maintainable, scalable

## 🏗️ Architecture

```
src/
├── core/
│   └── analyzer.py          # Core stock analysis engine
├── data/
│   └── storage.py           # Data management & SQLite storage
├── pipeline/
│   └── research_engine.py   # Automated research pipeline
└── __init__.py

main_app.py                  # Main application interface
cleanup_old_files.py         # Cleanup script for old files
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install yfinance pandas numpy sqlite3
```

### 2. Run the System

```bash
# Start the main application
uv run main_app.py

# Or directly with Python
python main_app.py
```

### 3. Choose Your Strategy

-   **Growth Strategy** - High-growth stocks with strong fundamentals
-   **Value Strategy** - Undervalued stocks with solid metrics
-   **AI Stocks** - AI-focused companies and enablers

## 🎮 Features

### 📈 Daily Research Pipeline

```python
# Automated research flow:
1. Get stock universe (S&P 500, NASDAQ 100, Growth, Value, AI)
2. Apply screening filters (market cap, P/E, ROE, growth)
3. Analyze stocks (50+ metrics, sentiment, risk)
4. Rank and select top picks (composite scoring)
5. Generate reasoning and decision summary
6. Store results in SQLite database
7. Create LLM prompt for deeper analysis
```

### 🧠 Analysis Engine

-   **Fundamental Analysis** - 25+ financial metrics with sector benchmarking
-   **Technical Analysis** - Price momentum, moving averages, volume
-   **Sentiment Analysis** - News sentiment, analyst recommendations
-   **Risk Assessment** - Multi-factor risk scoring
-   **Composite Scoring** - Weighted 0-100 scoring system

### 💾 Data Management

-   **SQLite Database** - Structured storage for all analysis data
-   **Daily Decisions** - Track reasoning and selected stocks
-   **Performance Tracking** - Monitor recommendation outcomes
-   **Market Context** - Store daily market conditions
-   **Historical Analysis** - Retrieve past decisions and performance

### 🤖 LLM Integration

-   **Automated Prompt Generation** - Rich context for language models
-   **Research Report Format** - Structured data for AI analysis
-   **Decision Reasoning** - Comprehensive investment thesis
-   **Market Insights** - Sector rotation and trend analysis

## 📊 Sample Output

```
🔍 Running Daily Research - Strategy: GROWTH
--------------------------------------------------
🚀 Starting daily research pipeline - Strategy: growth
📊 Stock universe: 32 symbols
🔍 After filtering: 28 symbols
⚡ Limited to 25 stocks for performance
✅ Analyzed 23 stocks successfully
🏆 Selected 5 top picks

📊 RESEARCH REPORT - 2024-01-15
============================================================
Strategy: GROWTH
Total Picks: 5
Average Score: 72.4/100
Sectors: Technology, Healthcare, Consumer Discretionary

🏆 TOP STOCK PICKS
--------------------------------------------------

1. NVDA - NVIDIA Corporation
   Score: 78.5/100 | Rating: Buy | Confidence: High
   Sector: Technology
   Price: $142.94 → Target: $172.00 (+20.3%)
   Allocation: 5-7% | Time Horizon: 6-18 months
   Metrics: PE 65.8 | ROE 115.5% | Growth 69.2%
   Strengths: Excellent ROE, Strong revenue growth, Positive price momentum

💡 MARKET INSIGHTS
------------------------------
Dominant Sectors: {'Technology': 3, 'Healthcare': 1, 'Consumer Discretionary': 1}
Overall Risk Level: Moderate
Growth Focused: Yes
Market Sentiment: Positive

📋 RECOMMENDED ACTIONS
------------------------------
• Consider immediate positions in 2 Strong Buy stocks
• Set price alerts for target prices
• Monitor upcoming earnings dates

💾 LLM prompt saved to: output/llm_prompt_2024-01-15.txt
```

## 🔧 Configuration

### Stock Universes

-   **S&P 500** - Large-cap US stocks
-   **NASDAQ 100** - Tech-heavy growth stocks
-   **Growth** - High-growth companies
-   **Value** - Undervalued opportunities
-   **Mega Cap** - >$500B market cap
-   **AI Stocks** - AI-focused companies

### Screening Filters

```python
filters = {
    'growth': {
        'min_revenue_growth': 0.10,
        'min_market_cap': 1e9
    },
    'value': {
        'max_pe': 20,
        'min_roe': 0.10,
        'min_market_cap': 5e9
    }
}
```

### Scoring Weights

-   **Fundamentals**: 50% (valuation, profitability, growth, health)
-   **Technical**: 25% (momentum, moving averages, volume)
-   **Sentiment**: 15% (news, analyst recommendations)
-   **Risk**: 10% (inverted risk score)

## 📁 Data Storage

### SQLite Tables

-   **daily_analysis** - Individual stock analyses
-   **daily_decisions** - Investment decisions and reasoning
-   **performance_tracking** - Recommendation outcomes
-   **market_context** - Daily market conditions

### Data Retention

-   **Analysis Data** - 1 year (configurable)
-   **Decision History** - Permanent
-   **Performance Tracking** - Permanent
-   **Export Options** - CSV export available

## 🔮 Future Enhancements

### Phase 2 - Real-time Data

-   [ ] Live market data integration
-   [ ] Earnings calendar integration
-   [ ] Real-time news sentiment
-   [ ] Intraday technical analysis

### Phase 3 - Advanced Analytics

-   [ ] Machine learning predictions
-   [ ] Alternative data sources
-   [ ] Options flow analysis
-   [ ] Insider trading data

### Phase 4 - Platform Features

-   [ ] Web dashboard
-   [ ] Mobile alerts
-   [ ] Portfolio optimization
-   [ ] API endpoints

## 🛠️ Development

### Adding New Strategies

```python
# In research_engine.py
def _get_custom_symbols(self) -> List[str]:
    return ['SYMBOL1', 'SYMBOL2', ...]

# Add to get_stock_universe()
universes['custom'] = self._get_custom_symbols()
```

### Custom Filters

```python
# In _get_strategy_filters()
'custom_strategy': {
    'min_market_cap': 10e9,
    'max_pe': 15,
    'min_roe': 0.20
}
```

### Database Queries

```python
# Access storage directly
from src.data.storage import AnalysisStorage
storage = AnalysisStorage()

# Get analysis history
history = storage.get_analysis_history('NVDA', days=30)

# Get performance summary
performance = storage.get_performance_summary()
```

## 📈 Performance

-   **Analysis Speed** - ~2-3 seconds per stock
-   **Batch Processing** - 25 stocks in ~60 seconds
-   **Memory Usage** - <100MB for typical runs
-   **Storage** - ~1MB per day of analysis data

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit changes** (`git commit -m 'Add amazing feature'`)
4. **Push to branch** (`git push origin feature/amazing-feature`)
5. **Open Pull Request**

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

-   **Yahoo Finance** - Financial data API
-   **Pandas** - Data manipulation
-   **SQLite** - Embedded database
-   **asyncio** - Asynchronous processing

---

**Built with ❤️ for intelligent investing**
