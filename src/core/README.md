# 🧠 Core Analysis Engine

**The heart of the stock research system - handles all fundamental, technical, and sentiment analysis**

## 📁 Module Structure

```
core/
├── __init__.py          # Module initialization
├── analyzer.py          # Main StockAnalyzer class
└── README.md           # This documentation
```

## 🎯 Overview

The `core` module contains the `StockAnalyzer` class, which is the central engine for all stock analysis. It combines multiple analysis methodologies into a single, comprehensive scoring system.

## 📊 StockAnalyzer Class

### Initialization

```python
from src.core.analyzer import StockAnalyzer

analyzer = StockAnalyzer()
```

The analyzer initializes with **sector benchmarks** for 11 major sectors, providing context-aware analysis that compares stocks against their industry peers.

### Sector Benchmarks

```python
sector_benchmarks = {
    'Technology': {'avg_pe': 25, 'avg_roe': 0.20, 'avg_debt_equity': 0.3},
    'Healthcare': {'avg_pe': 20, 'avg_roe': 0.15, 'avg_debt_equity': 0.4},
    'Financial Services': {'avg_pe': 12, 'avg_roe': 0.12, 'avg_debt_equity': 0.8},
    # ... 8 more sectors
}
```

## 🔍 Analysis Methods

### 1. Main Analysis Method

```python
analysis = analyzer.analyze_stock('AAPL')
```

**Returns:** Complete analysis dictionary with:

-   `fundamentals` - Financial metrics and ratios
-   `technical` - Price momentum and indicators
-   `sentiment` - News and analyst sentiment
-   `risk` - Risk assessment and identified risks
-   `score` - Composite scoring breakdown
-   `recommendation` - Investment recommendation

### 2. Fundamental Analysis (`_analyze_fundamentals`)

**Extracts 25+ financial metrics:**

#### Valuation Metrics

-   `pe_ratio` - Price-to-earnings ratio
-   `forward_pe` - Forward P/E ratio
-   `peg_ratio` - Price/earnings to growth ratio
-   `price_to_sales` - Price-to-sales ratio
-   `price_to_book` - Price-to-book ratio
-   `ev_ebitda` - Enterprise value to EBITDA

#### Profitability Metrics

-   `profit_margin` - Net profit margin
-   `operating_margin` - Operating profit margin
-   `gross_margin` - Gross profit margin
-   `roe` - Return on equity
-   `roa` - Return on assets

#### Growth Metrics

-   `revenue_growth` - Year-over-year revenue growth
-   `earnings_growth` - Year-over-year earnings growth

#### Financial Health Metrics

-   `debt_to_equity` - Debt-to-equity ratio
-   `current_ratio` - Current assets / current liabilities
-   `quick_ratio` - Quick assets / current liabilities
-   `cash_per_share` - Cash per share
-   `free_cash_flow` - Free cash flow

#### Market Metrics

-   `market_cap` - Market capitalization
-   `beta` - Stock volatility vs market
-   `dividend_yield` - Annual dividend yield

#### Analyst Data

-   `analyst_target` - Mean analyst price target
-   `num_analysts` - Number of analysts covering
-   `recommendation_mean` - Average analyst recommendation

**Scoring Algorithm:**

-   **Valuation (25 points)** - Compares P/E to sector average
-   **Profitability (25 points)** - ROE vs sector benchmark
-   **Growth (25 points)** - Revenue growth thresholds
-   **Financial Health (25 points)** - Debt levels + liquidity ratios

### 3. Technical Analysis (`_analyze_technical`)

**Calculates technical indicators:**

#### Moving Averages

-   `ma_20` - 20-day moving average
-   `ma_50` - 50-day moving average
-   `price_vs_ma20` - Current price vs 20-day MA
-   `price_vs_ma50` - Current price vs 50-day MA

#### Momentum Indicators

-   `momentum_1m` - 1-month price momentum
-   `momentum_3m` - 3-month price momentum

#### Volume Analysis

-   `volume_ratio` - Recent volume vs average volume

#### Volatility

-   `volatility` - Annualized price volatility

**Scoring Algorithm:**

-   **Base Score:** 50 points
-   **MA Signals:** +15 points for >5% above MA, +5 for positive
-   **Momentum:** +10 for >10% monthly gain, +5 for >5%
-   **Volume:** +5 for high volume, -5 for low volume

### 4. Sentiment Analysis (`_analyze_sentiment`)

**Analyzes market sentiment:**

#### News Sentiment

-   Fetches recent news headlines
-   Keyword-based sentiment scoring
-   Positive words: 'beat', 'strong', 'growth', 'upgrade', 'buy'
-   Negative words: 'miss', 'weak', 'decline', 'downgrade', 'sell'

#### Analyst Sentiment

-   `recommendation_mean` - Average analyst rating
-   `analyst_sentiment` - Buy/Hold/Sell classification

**Sentiment Categories:**

-   **Very Positive** - News score > 2
-   **Positive** - News score > 0
-   **Neutral** - News score = 0
-   **Negative** - News score < 0
-   **Very Negative** - News score < -2

### 5. Risk Assessment (`_assess_risk`)

**Identifies and scores investment risks:**

#### Financial Risks

-   **High Debt** - Debt-to-equity > 1.0 (+2 risk points)
-   **Liquidity Concerns** - Current ratio < 1.0 (+2 risk points)

#### Market Risks

-   **High Volatility** - Beta > 1.5 (+1 risk point)

#### Sentiment Risks

-   **Negative Sentiment** - Poor news sentiment (+1 risk point)

#### Valuation Risks

-   **High Valuation** - P/E ratio > 40 (+1 risk point)

**Risk Levels:**

-   **Low Risk** - 0-3 points
-   **Moderate Risk** - 4-6 points
-   **High Risk** - 7+ points

### 6. Composite Scoring (`_calculate_composite_score`)

**Weighted scoring system:**

```python
weights = {
    'fundamental': 0.50,  # 50% weight
    'technical': 0.25,    # 25% weight
    'sentiment': 0.15,    # 15% weight
    'risk': 0.10          # 10% weight (inverted)
}
```

**Score Calculation:**

```python
composite = (
    fund_score * 0.50 +
    tech_score * 0.25 +
    sent_score * 0.15 +
    risk_score * 0.10
)
```

### 7. Investment Recommendation (`_generate_recommendation`)

**Rating System:**

-   **Strong Buy** - Score ≥ 80 (8-10% allocation)
-   **Buy** - Score ≥ 70 (5-7% allocation)
-   **Moderate Buy** - Score ≥ 60 (3-5% allocation)
-   **Hold** - Score ≥ 50 (1-3% allocation)
-   **Weak Hold** - Score ≥ 40 (0-1% allocation)
-   **Sell** - Score < 40 (0% allocation)

**Time Horizon Logic:**

-   **6-18 months** - Revenue growth > 30%
-   **1-3 years** - Revenue growth > 15%
-   **3-5 years** - Lower growth stocks

**Confidence Levels:**

-   **High** - 10+ analysts covering
-   **Moderate** - <10 analysts covering

## 🔧 Usage Examples

### Basic Analysis

```python
from src.core.analyzer import StockAnalyzer

analyzer = StockAnalyzer()
result = analyzer.analyze_stock('NVDA')

print(f"Score: {result['score']['composite_score']}")
print(f"Rating: {result['recommendation']['rating']}")
```

### Accessing Specific Components

```python
# Fundamental metrics
fundamentals = result['fundamentals']
pe_ratio = fundamentals['pe_ratio']
roe = fundamentals['roe']

# Technical indicators
technical = result['technical']['indicators']
momentum = technical['momentum_1m']

# Risk assessment
risks = result['risk']['identified_risks']
risk_level = result['risk']['risk_level']
```

### Batch Analysis

```python
symbols = ['AAPL', 'GOOGL', 'MSFT']
results = []

for symbol in symbols:
    analysis = analyzer.analyze_stock(symbol)
    if analysis:
        results.append(analysis)

# Sort by score
results.sort(key=lambda x: x['score']['composite_score'], reverse=True)
```

## 🎯 Key Features

### Sector-Aware Analysis

-   Compares stocks against industry peers
-   Adjusts scoring based on sector norms
-   Accounts for sector-specific characteristics

### Multi-Factor Scoring

-   Combines fundamental, technical, sentiment, and risk factors
-   Weighted approach prioritizes fundamentals
-   Normalized 0-100 scoring system

### Comprehensive Risk Assessment

-   Identifies specific risk factors
-   Quantifies overall risk level
-   Integrates risk into final scoring

### Investment-Ready Recommendations

-   Clear buy/hold/sell ratings
-   Portfolio allocation suggestions
-   Time horizon guidance
-   Confidence levels

## 🔍 Data Sources

-   **Yahoo Finance** - Primary data source via `yfinance`
-   **Real-time Data** - Current prices and fundamentals
-   **Historical Data** - 6 months for technical analysis
-   **News Data** - Recent headlines for sentiment
-   **Analyst Data** - Recommendations and targets

## ⚠️ Limitations

-   **Data Dependency** - Relies on Yahoo Finance data quality
-   **News Sentiment** - Simple keyword-based approach
-   **Sector Benchmarks** - Static benchmarks, not dynamic
-   **Technical Analysis** - Limited to basic indicators
-   **Real-time Constraints** - API rate limiting considerations

## 🚀 Future Enhancements

-   **Advanced Technical Analysis** - RSI, MACD, Bollinger Bands
-   **Machine Learning Sentiment** - NLP-based news analysis
-   **Dynamic Benchmarks** - Real-time sector comparisons
-   **Alternative Data** - Social sentiment, insider trading
-   **Options Analysis** - Implied volatility and flow data
