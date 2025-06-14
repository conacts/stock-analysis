# 💾 Data Management System

**Persistent storage and tracking for all analysis data, decisions, and performance metrics**

## 📁 Module Structure

```
data/
├── __init__.py          # Module initialization
├── storage.py           # AnalysisStorage & DecisionTracker classes
└── README.md           # This documentation
```

## 🎯 Overview

The `data` module provides comprehensive data management capabilities using SQLite for persistent storage. It tracks daily analysis results, investment decisions, performance metrics, and market context.

## 🗄️ Database Schema

### SQLite Database: `data/stock_analysis.db`

#### Table: `daily_analysis`

Stores individual stock analysis results.

```sql
CREATE TABLE daily_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,                    -- Analysis date (YYYY-MM-DD)
    symbol TEXT NOT NULL,                  -- Stock ticker symbol
    analysis_data TEXT NOT NULL,           -- Complete analysis JSON
    composite_score REAL,                  -- Overall score (0-100)
    rating TEXT,                          -- Buy/Hold/Sell rating
    confidence TEXT,                      -- High/Moderate confidence
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date, symbol)                  -- One analysis per stock per day
);
```

#### Table: `daily_decisions`

Stores daily investment decisions and reasoning.

```sql
CREATE TABLE daily_decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,                    -- Decision date
    decision_type TEXT NOT NULL,           -- Type of decision
    reasoning TEXT NOT NULL,               -- Investment reasoning
    selected_stocks TEXT,                  -- Selected stocks JSON
    market_context TEXT,                   -- Market context JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date)                          -- One decision per day
);
```

#### Table: `performance_tracking`

Tracks recommendation performance over time.

```sql
CREATE TABLE performance_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,                  -- Stock ticker
    recommendation_date TEXT NOT NULL,     -- When recommended
    entry_price REAL,                     -- Price when recommended
    current_price REAL,                   -- Current/latest price
    target_price REAL,                    -- Analyst target price
    rating TEXT,                          -- Original rating
    days_held INTEGER,                    -- Days since recommendation
    return_pct REAL,                      -- Return percentage
    status TEXT,                          -- active/closed
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Table: `market_context`

Stores daily market conditions and context.

```sql
CREATE TABLE market_context (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,                    -- Market date
    market_sentiment TEXT,                 -- Overall sentiment
    vix_level REAL,                       -- VIX volatility index
    sector_rotation TEXT,                  -- Sector rotation data JSON
    economic_indicators TEXT,              -- Economic data JSON
    news_themes TEXT,                     -- Major news themes JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date)                          -- One context per day
);
```

## 🏗️ AnalysisStorage Class

### Initialization

```python
from src.data.storage import AnalysisStorage

# Default database path
storage = AnalysisStorage()

# Custom database path
storage = AnalysisStorage("custom/path/analysis.db")
```

### Core Methods

#### 1. Store Daily Analysis

```python
def store_daily_analysis(self, analysis_data: Dict) -> bool
```

**Purpose:** Store complete stock analysis results
**Input:** Analysis dictionary from `StockAnalyzer.analyze_stock()`
**Returns:** Success status (True/False)

**Example:**

```python
analysis = analyzer.analyze_stock('AAPL')
success = storage.store_daily_analysis(analysis)
```

**Stored Data:**

-   Complete analysis JSON (all metrics, scores, recommendations)
-   Composite score for quick filtering
-   Rating and confidence for reporting
-   Automatic date stamping

#### 2. Store Daily Decision

```python
def store_daily_decision(self, decision_data: Dict) -> bool
```

**Purpose:** Store investment decisions and reasoning
**Input:** Decision dictionary with reasoning and selected stocks
**Returns:** Success status

**Example:**

```python
decision = {
    'decision_type': 'daily_stock_selection',
    'reasoning': 'Selected 3 growth stocks with strong fundamentals...',
    'selected_stocks': [
        {'symbol': 'NVDA', 'score': 78.5, 'rating': 'Buy'},
        {'symbol': 'GOOGL', 'score': 72.1, 'rating': 'Buy'}
    ],
    'market_context': {
        'analysis_date': '2024-01-15',
        'market_sentiment': 'Positive'
    }
}
storage.store_daily_decision(decision)
```

#### 3. Get Analysis History

```python
def get_analysis_history(self, symbol: str, days: int = 30) -> List[Dict]
```

**Purpose:** Retrieve historical analysis for a specific stock
**Parameters:**

-   `symbol` - Stock ticker symbol
-   `days` - Number of days to look back (default: 30)

**Returns:** List of historical analysis data

**Example:**

```python
# Get NVDA analysis for last 30 days
history = storage.get_analysis_history('NVDA', 30)

for analysis in history:
    print(f"{analysis['date']}: Score {analysis['composite_score']}")
```

#### 4. Get Daily Decisions

```python
def get_daily_decisions(self, days: int = 30) -> List[Dict]
```

**Purpose:** Retrieve recent daily decisions
**Returns:** List of decision records with reasoning and selected stocks

#### 5. Performance Tracking

```python
def update_performance(self, symbol: str, current_price: float) -> bool
def get_performance_summary(self) -> Dict
```

**Performance Updates:**

-   Calculates return percentages
-   Tracks days held
-   Updates current prices
-   Maintains active/closed status

**Performance Summary:**

```python
summary = storage.get_performance_summary()
# Returns:
{
    'active_positions': [...],
    'total_positions': 5,
    'average_return': 12.5,
    'total_return': 62.5
}
```

#### 6. Market Context Storage

```python
def store_market_context(self, context_data: Dict) -> bool
```

**Purpose:** Store daily market conditions
**Example:**

```python
context = {
    'market_sentiment': 'Bullish',
    'vix_level': 18.5,
    'sector_rotation': {'Technology': 'Outperforming'},
    'economic_indicators': {'GDP_growth': 2.1},
    'news_themes': ['AI Revolution', 'Fed Policy']
}
storage.store_market_context(context)
```

#### 7. Data Export

```python
def export_to_csv(self, table_name: str, output_path: str) -> bool
```

**Purpose:** Export any table to CSV format
**Example:**

```python
# Export all daily analysis to CSV
storage.export_to_csv('daily_analysis', 'exports/analysis_data.csv')
```

#### 8. Data Cleanup

```python
def cleanup_old_data(self, days_to_keep: int = 365) -> bool
```

**Purpose:** Remove old data beyond retention period
**Default:** Keeps 1 year of data

## 🎯 DecisionTracker Class

### Initialization

```python
from src.data.storage import DecisionTracker

tracker = DecisionTracker(storage)
```

### Methods

#### 1. Analyze Decision Patterns

```python
def analyze_decision_patterns(self) -> Dict
```

**Purpose:** Analyze historical decision-making patterns
**Returns:** Pattern analysis including:

-   Decision type frequency
-   Sector preferences
-   Rating distribution
-   Analysis period summary

**Example Output:**

```python
{
    'total_decisions': 45,
    'decision_types': {'daily_stock_selection': 40, 'special_situation': 5},
    'sector_preferences': {'Technology': 15, 'Healthcare': 8, 'Finance': 5},
    'rating_distribution': {'Buy': 20, 'Strong Buy': 10, 'Hold': 15},
    'analysis_period_days': 90
}
```

#### 2. Generate Decision Summary

```python
def generate_decision_summary(self, selected_stocks: List[Dict], reasoning: str) -> Dict
```

**Purpose:** Create comprehensive decision summary for storage
**Returns:** Structured decision data with metadata

## 🔧 Usage Examples

### Daily Workflow

```python
from src.core.analyzer import StockAnalyzer
from src.data.storage import AnalysisStorage, DecisionTracker

# Initialize components
analyzer = StockAnalyzer()
storage = AnalysisStorage()
tracker = DecisionTracker(storage)

# Analyze stocks
symbols = ['AAPL', 'GOOGL', 'NVDA']
analyses = []

for symbol in symbols:
    analysis = analyzer.analyze_stock(symbol)
    if analysis:
        # Store individual analysis
        storage.store_daily_analysis(analysis)
        analyses.append(analysis)

# Make investment decision
top_picks = sorted(analyses, key=lambda x: x['score']['composite_score'], reverse=True)[:3]

# Generate and store decision
decision = tracker.generate_decision_summary(
    top_picks,
    "Selected top 3 growth stocks with strong fundamentals and positive momentum"
)
storage.store_daily_decision(decision)
```

### Performance Monitoring

```python
# Update performance for tracked stocks
tracked_symbols = ['AAPL', 'GOOGL', 'NVDA']

for symbol in tracked_symbols:
    # Get current price (from yfinance or other source)
    current_price = get_current_price(symbol)
    storage.update_performance(symbol, current_price)

# Get performance summary
performance = storage.get_performance_summary()
print(f"Portfolio Return: {performance['average_return']:.2f}%")
```

### Historical Analysis

```python
# Analyze decision patterns
patterns = tracker.analyze_decision_patterns()
print(f"Favorite sectors: {patterns['sector_preferences']}")

# Get stock history
nvda_history = storage.get_analysis_history('NVDA', 90)
scores = [h['composite_score'] for h in nvda_history]
print(f"NVDA average score: {sum(scores)/len(scores):.1f}")

# Export data for external analysis
storage.export_to_csv('daily_analysis', 'analysis_export.csv')
storage.export_to_csv('performance_tracking', 'performance_export.csv')
```

## 🎯 Key Features

### Comprehensive Data Storage

-   **Complete Analysis Records** - Full JSON storage of all analysis data
-   **Decision Tracking** - Investment reasoning and logic preservation
-   **Performance Monitoring** - Real-time tracking of recommendation outcomes
-   **Market Context** - Daily market condition snapshots

### Data Integrity

-   **Unique Constraints** - Prevents duplicate entries
-   **Automatic Timestamps** - Tracks creation and update times
-   **JSON Validation** - Structured data storage
-   **Error Handling** - Graceful failure handling

### Query Capabilities

-   **Historical Lookups** - Flexible date range queries
-   **Performance Analytics** - Return calculations and summaries
-   **Pattern Analysis** - Decision-making pattern identification
-   **Export Functions** - CSV export for external analysis

### Maintenance Features

-   **Data Cleanup** - Automated old data removal
-   **Database Optimization** - Efficient indexing and queries
-   **Backup Support** - SQLite file-based backup
-   **Migration Ready** - Structured for future enhancements

## 🔍 Data Flow

### Analysis Storage Flow

```
StockAnalyzer.analyze_stock()
    ↓
AnalysisStorage.store_daily_analysis()
    ↓
SQLite Database (daily_analysis table)
    ↓
Available for historical queries and reporting
```

### Decision Tracking Flow

```
Research Pipeline Results
    ↓
DecisionTracker.generate_decision_summary()
    ↓
AnalysisStorage.store_daily_decision()
    ↓
SQLite Database (daily_decisions table)
    ↓
Pattern analysis and reasoning tracking
```

### Performance Tracking Flow

```
Recommendation Made
    ↓
Performance Entry Created
    ↓
Regular Price Updates
    ↓
Return Calculations
    ↓
Performance Summary Reports
```

## 📊 Database Maintenance

### Regular Maintenance Tasks

```python
# Clean up old data (keep 1 year)
storage.cleanup_old_data(365)

# Export important data
storage.export_to_csv('daily_decisions', 'backup/decisions.csv')
storage.export_to_csv('performance_tracking', 'backup/performance.csv')

# Check database size
import os
db_size = os.path.getsize('data/stock_analysis.db')
print(f"Database size: {db_size / 1024 / 1024:.2f} MB")
```

### Performance Optimization

-   **Indexed Queries** - Date and symbol columns indexed
-   **Batch Operations** - Efficient bulk inserts
-   **Connection Management** - Proper connection handling
-   **Query Optimization** - Efficient SQL queries

## 🚀 Future Enhancements

### Advanced Analytics

-   **Time Series Analysis** - Stock performance trends
-   **Correlation Analysis** - Cross-stock relationships
-   **Sector Performance** - Sector-level analytics
-   **Risk Metrics** - Portfolio risk calculations

### Data Sources

-   **Real-time Integration** - Live data feeds
-   **Alternative Data** - Social sentiment, news feeds
-   **Economic Data** - Macro indicators integration
-   **Options Data** - Derivatives analysis

### Storage Enhancements

-   **Data Compression** - Efficient storage optimization
-   **Distributed Storage** - Multi-database support
-   **Cloud Integration** - Cloud database options
-   **Real-time Sync** - Live data synchronization
