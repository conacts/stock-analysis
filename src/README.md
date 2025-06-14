# 🏗️ Source Code Architecture

**Modular, professional stock research system with clean separation of concerns**

## 📁 Directory Structure

```
src/
├── __init__.py              # Package initialization
├── README.md               # This architecture overview
├── core/                   # Core analysis engine
│   ├── __init__.py
│   ├── analyzer.py         # StockAnalyzer class
│   └── README.md          # Core module documentation
├── data/                   # Data management system
│   ├── __init__.py
│   ├── storage.py          # AnalysisStorage & DecisionTracker
│   └── README.md          # Data module documentation
└── pipeline/               # Automated research pipeline
    ├── __init__.py
    ├── research_engine.py  # ResearchEngine, StockScreener, ResearchTrigger
    └── README.md          # Pipeline module documentation
```

## 🎯 Architecture Overview

This modular architecture follows **clean code principles** with clear separation of concerns:

### 🧠 Core Module (`core/`)

**Responsibility:** Individual stock analysis and scoring

-   **Single Responsibility:** Stock analysis only
-   **No Dependencies:** Self-contained analysis logic
-   **Pure Functions:** Deterministic analysis results
-   **Sector-Aware:** Context-aware benchmarking

### 💾 Data Module (`data/`)

**Responsibility:** Persistent storage and data management

-   **Database Abstraction:** SQLite with clean interface
-   **Decision Tracking:** Investment reasoning preservation
-   **Performance Monitoring:** Real-time tracking
-   **Data Integrity:** Validation and error handling

### 🔄 Pipeline Module (`pipeline/`)

**Responsibility:** Orchestration and automation

-   **Workflow Management:** End-to-end research pipeline
-   **Stock Screening:** Universe management and filtering
-   **Batch Processing:** Efficient multi-stock analysis
-   **Trigger System:** Automated execution

## 🔗 Module Dependencies

```
pipeline/  →  core/     (uses StockAnalyzer)
pipeline/  →  data/     (uses AnalysisStorage)
core/      →  (no deps) (independent)
data/      →  (no deps) (independent)
```

**Dependency Flow:**

-   **Pipeline** orchestrates **Core** and **Data**
-   **Core** and **Data** are independent modules
-   Clean interfaces between all modules
-   No circular dependencies

## 🎮 Usage Patterns

### 1. Direct Core Usage

```python
from src.core.analyzer import StockAnalyzer

analyzer = StockAnalyzer()
result = analyzer.analyze_stock('AAPL')
print(f"Score: {result['score']['composite_score']}")
```

### 2. Direct Data Usage

```python
from src.data.storage import AnalysisStorage

storage = AnalysisStorage()
history = storage.get_analysis_history('NVDA', 30)
```

### 3. Full Pipeline Usage

```python
from src.pipeline.research_engine import ResearchEngine

engine = ResearchEngine()
report = await engine.run_daily_research('growth', 25)
```

### 4. Combined Usage

```python
from src.core.analyzer import StockAnalyzer
from src.data.storage import AnalysisStorage
from src.pipeline.research_engine import StockScreener

# Individual components
analyzer = StockAnalyzer()
storage = AnalysisStorage()
screener = StockScreener()

# Custom workflow
symbols = screener.get_stock_universe('ai_stocks')
for symbol in symbols:
    analysis = analyzer.analyze_stock(symbol)
    if analysis:
        storage.store_daily_analysis(analysis)
```

## 📊 Data Flow Architecture

### High-Level Data Flow

```
External APIs (Yahoo Finance)
    ↓
Core Analyzer (Individual Analysis)
    ↓
Pipeline Engine (Batch Processing)
    ↓
Data Storage (SQLite Persistence)
    ↓
Reports & LLM Prompts (Output)
```

### Detailed Component Flow

```
StockScreener.get_stock_universe()
    ↓
StockScreener.apply_filters()
    ↓
ResearchEngine._analyze_stock_batch()
    ├─→ StockAnalyzer.analyze_stock() (for each stock)
    └─→ AnalysisStorage.store_daily_analysis()
    ↓
ResearchEngine._select_top_picks()
    ↓
DecisionTracker.generate_decision_summary()
    ↓
AnalysisStorage.store_daily_decision()
    ↓
ResearchEngine._generate_research_report()
    ↓
ResearchEngine.generate_llm_prompt()
```

## 🔧 Configuration & Customization

### Core Configuration

```python
# Sector benchmarks (in core/analyzer.py)
sector_benchmarks = {
    'Technology': {'avg_pe': 25, 'avg_roe': 0.20, 'avg_debt_equity': 0.3},
    # ... other sectors
}

# Scoring weights
weights = {
    'fundamental': 0.50,
    'technical': 0.25,
    'sentiment': 0.15,
    'risk': 0.10
}
```

### Data Configuration

```python
# Database path (in data/storage.py)
storage = AnalysisStorage("custom/path/analysis.db")

# Data retention
storage.cleanup_old_data(days_to_keep=365)
```

### Pipeline Configuration

```python
# Stock universes (in pipeline/research_engine.py)
universes = {
    'sp500': self._get_sp500_symbols(),
    'growth': self._get_growth_symbols(),
    # ... other universes
}

# Strategy filters
filters = {
    'growth': {'min_revenue_growth': 0.10},
    'value': {'max_pe': 20, 'min_roe': 0.10},
    # ... other strategies
}
```

## 🎯 Key Design Principles

### 1. Single Responsibility Principle

-   **Core:** Only handles stock analysis
-   **Data:** Only handles storage and retrieval
-   **Pipeline:** Only handles orchestration

### 2. Open/Closed Principle

-   **Extensible:** Easy to add new analysis methods
-   **Stable:** Core interfaces remain unchanged
-   **Modular:** New modules can be added without modification

### 3. Dependency Inversion

-   **Abstractions:** Modules depend on interfaces, not implementations
-   **Injection:** Dependencies injected rather than hard-coded
-   **Testable:** Easy to mock and test individual components

### 4. Interface Segregation

-   **Focused Interfaces:** Each module exposes only necessary methods
-   **Clean APIs:** Simple, intuitive method signatures
-   **Minimal Coupling:** Modules interact through well-defined interfaces

## 🔍 Error Handling Strategy

### Core Module Error Handling

```python
def analyze_stock(self, symbol: str) -> Optional[Dict]:
    try:
        # Analysis logic
        return analysis_result
    except Exception as e:
        print(f"Error analyzing {symbol}: {e}")
        return None
```

### Data Module Error Handling

```python
def store_daily_analysis(self, analysis_data: Dict) -> bool:
    try:
        # Storage logic
        return True
    except Exception as e:
        self.logger.error(f"Error storing analysis: {e}")
        return False
```

### Pipeline Module Error Handling

```python
async def run_daily_research(self, strategy: str, max_stocks: int) -> Dict:
    try:
        # Pipeline logic
        return report
    except Exception as e:
        self.logger.error(f"Research pipeline failed: {e}")
        return {'error': str(e), 'status': 'failed'}
```

## 📈 Performance Considerations

### Core Performance

-   **Caching:** Sector benchmarks cached in memory
-   **Efficient Calculations:** Optimized scoring algorithms
-   **Error Recovery:** Graceful handling of missing data

### Data Performance

-   **Indexed Queries:** Database indexes on date and symbol
-   **Batch Operations:** Efficient bulk inserts
-   **Connection Pooling:** Proper SQLite connection management

### Pipeline Performance

-   **Asynchronous Processing:** Non-blocking batch analysis
-   **Rate Limiting:** API throttling to avoid limits
-   **Memory Management:** Efficient data structures

## 🧪 Testing Strategy

### Unit Testing Structure

```
tests/
├── test_core/
│   └── test_analyzer.py
├── test_data/
│   └── test_storage.py
└── test_pipeline/
    └── test_research_engine.py
```

### Testing Patterns

```python
# Core testing
def test_stock_analysis():
    analyzer = StockAnalyzer()
    result = analyzer.analyze_stock('AAPL')
    assert result is not None
    assert 'score' in result

# Data testing
def test_storage():
    storage = AnalysisStorage(":memory:")  # In-memory DB
    success = storage.store_daily_analysis(mock_analysis)
    assert success is True

# Pipeline testing
async def test_research_pipeline():
    engine = ResearchEngine()
    report = await engine.run_daily_research('growth', 5)
    assert 'top_picks' in report
```

## 🚀 Extension Points

### Adding New Analysis Methods

```python
# In core/analyzer.py
def _analyze_options_flow(self, ticker, symbol: str) -> Dict:
    """New analysis method for options data"""
    # Implementation
    return options_analysis

# Update main analyze_stock method to include new analysis
```

### Adding New Storage Tables

```python
# In data/storage.py
def _init_database(self):
    # Add new table creation
    conn.execute("""
        CREATE TABLE IF NOT EXISTS new_table (
            id INTEGER PRIMARY KEY,
            # ... columns
        )
    """)
```

### Adding New Stock Universes

```python
# In pipeline/research_engine.py
def _get_custom_universe(self) -> List[str]:
    """Custom stock universe"""
    return ['SYMBOL1', 'SYMBOL2', ...]

# Add to get_stock_universe method
universes['custom'] = self._get_custom_universe()
```

## 🔮 Future Architecture Enhancements

### Microservices Architecture

```
API Gateway
    ├─→ Analysis Service (core/)
    ├─→ Data Service (data/)
    └─→ Pipeline Service (pipeline/)
```

### Event-Driven Architecture

```
Event Bus
    ├─→ Stock Analysis Events
    ├─→ Decision Events
    └─→ Performance Events
```

### Plugin Architecture

```
Plugin Manager
    ├─→ Analysis Plugins
    ├─→ Data Source Plugins
    └─→ Notification Plugins
```

## 📚 Documentation Standards

### Code Documentation

-   **Docstrings:** All public methods documented
-   **Type Hints:** Full type annotation
-   **Comments:** Complex logic explained
-   **Examples:** Usage examples in docstrings

### Module Documentation

-   **README.md:** Comprehensive module documentation
-   **API Reference:** Method signatures and parameters
-   **Usage Examples:** Real-world usage patterns
-   **Architecture Diagrams:** Visual system overview

### System Documentation

-   **Architecture Overview:** High-level system design
-   **Data Flow Diagrams:** Component interactions
-   **Configuration Guide:** Setup and customization
-   **Deployment Guide:** Production deployment

## 🛠️ Development Workflow

### Local Development

```bash
# Setup development environment
uv sync

# Run individual modules
uv run -m src.core.analyzer
uv run -m src.data.storage
uv run -m src.pipeline.research_engine

# Run full application
uv run main_app.py
```

### Code Quality

```bash
# Linting
ruff check src/

# Type checking
mypy src/

# Testing
pytest tests/
```

### Module Development

1. **Design Interface** - Define clean API
2. **Implement Core Logic** - Focus on single responsibility
3. **Add Error Handling** - Graceful failure handling
4. **Write Tests** - Comprehensive test coverage
5. **Document API** - Clear documentation
6. **Integration Testing** - Test module interactions

## 🎯 Best Practices

### Code Organization

-   **One Class Per File** - Clear module boundaries
-   **Logical Grouping** - Related functionality together
-   **Clean Imports** - Explicit, organized imports
-   **Consistent Naming** - Clear, descriptive names

### Error Handling

-   **Fail Gracefully** - Return None/False rather than crash
-   **Log Errors** - Comprehensive error logging
-   **User-Friendly Messages** - Clear error communication
-   **Recovery Strategies** - Fallback mechanisms

### Performance

-   **Lazy Loading** - Load data only when needed
-   **Caching** - Cache expensive operations
-   **Async Operations** - Non-blocking I/O
-   **Resource Management** - Proper cleanup

### Security

-   **Input Validation** - Validate all external inputs
-   **SQL Injection Prevention** - Parameterized queries
-   **API Rate Limiting** - Respect external API limits
-   **Data Sanitization** - Clean user inputs

---

**This architecture provides a solid foundation for a professional stock research system with room for growth and enhancement.**
