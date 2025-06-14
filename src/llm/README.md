# LLM Integration Module

This module provides AI-powered stock analysis capabilities using DeepSeek API to enhance traditional financial analysis with sophisticated natural language processing and reasoning.

## Overview

The LLM integration transforms our scoring system from traditional metrics to AI-enhanced analysis:

**Traditional Scoring (Fallback)**:

-   50% Fundamentals
-   25% Technical Analysis
-   15% Basic Sentiment
-   10% Risk Assessment

**LLM-Enhanced Scoring**:

-   40% Fundamentals
-   20% Technical Analysis
-   30% AI Analysis (DeepSeek)
-   10% Risk Assessment

## Components

### DeepSeekAnalyzer

The core AI analysis engine that provides:

#### Comprehensive Stock Analysis

-   **Financial Data Interpretation**: AI analysis of financial metrics, ratios, and trends
-   **News Impact Assessment**: Sophisticated sentiment analysis and catalyst identification
-   **Technical Context**: Integration of price action with fundamental analysis
-   **Market Context**: Broader market conditions and sector analysis

#### News Analysis Capabilities

-   **Sentiment Analysis**: Beyond basic positive/negative to nuanced impact assessment
-   **Catalyst Identification**: Specific growth drivers and timeline estimation
-   **Risk Factor Detection**: Potential headwinds and threat analysis
-   **Timeline Impact**: Immediate vs. long-term news implications

#### Growth Catalyst Analysis

-   **Catalyst Discovery**: AI identification of specific growth drivers
-   **Impact Potential**: High/medium/low impact classification
-   **Timeline Estimation**: Realistic timeframes for catalyst realization
-   **Probability Assessment**: Likelihood of catalyst success (0-100)

### LLMScorer

Enhanced scoring system that integrates AI analysis:

#### Enhanced Composite Scoring

```python
# LLM-Enhanced Weights
composite_score = (
    fundamental_score * 0.40 +
    technical_score * 0.20 +
    llm_score * 0.30 +
    risk_score * 0.10
)
```

#### Intelligent Rating System

-   **Confidence-Adjusted Ratings**: Low confidence downgrades ratings
-   **Risk-Adjusted Scoring**: AI-powered risk assessment integration
-   **Dynamic Thresholds**: Context-aware rating boundaries

## API Integration

### DeepSeek Configuration

```python
from src.llm import DeepSeekAnalyzer

# Initialize with API key
analyzer = DeepSeekAnalyzer(api_key="your_deepseek_api_key")

# Or use environment variable
# export DEEPSEEK_API_KEY="your_api_key"
analyzer = DeepSeekAnalyzer()
```

### Usage Examples

#### Comprehensive Analysis

```python
analysis = analyzer.analyze_stock_comprehensive(
    symbol="AAPL",
    financial_data={
        'market_cap': 3000000000000,
        'pe_ratio': 25.5,
        'revenue_growth': 0.08,
        'profit_margin': 0.25
    },
    news_data=[
        {
            'title': 'Apple Reports Strong Q4 Results',
            'summary': 'Revenue up 8% year-over-year...',
            'date': '2024-01-15'
        }
    ],
    technical_data={
        'trend': 'upward',
        'rsi': 65,
        'ma_position': 'above'
    },
    market_context={
        'market_trend': 'bullish',
        'sector_performance': 'outperforming'
    }
)
```

#### News Impact Analysis

```python
news_impact = analyzer.analyze_news_impact(
    symbol="NVDA",
    news_data=recent_news_articles
)

print(f"Impact Score: {news_impact['impact_score']}")
print(f"Key Catalysts: {news_impact['key_catalysts']}")
```

#### Growth Catalyst Identification

```python
catalysts = analyzer.identify_growth_catalysts(
    symbol="TSLA",
    financial_data=financial_metrics,
    news_data=recent_news
)

for catalyst in catalysts['catalysts']:
    print(f"Catalyst: {catalyst['catalyst']}")
    print(f"Impact: {catalyst['impact_potential']}")
    print(f"Timeline: {catalyst['timeline']}")
```

## Enhanced Scoring Integration

### LLMScorer Usage

```python
from src.llm import LLMScorer

# Initialize scorer
scorer = LLMScorer(deepseek_api_key="your_api_key")

# Calculate enhanced score
enhanced_score = scorer.calculate_enhanced_score(
    symbol="MSFT",
    fundamental_score=75.0,
    technical_score=68.0,
    sentiment_score=72.0,
    risk_score=85.0,
    financial_data=financial_metrics,
    news_data=news_articles,
    technical_data=technical_indicators,
    market_context=market_data
)

print(f"Rating: {enhanced_score['rating']}")
print(f"Composite Score: {enhanced_score['composite_score']}")
print(f"Investment Thesis: {enhanced_score['llm_analysis']['investment_thesis']}")
```

## Response Formats

### Comprehensive Analysis Response

```json
{
    "overall_score": 78,
    "confidence": 85,
    "investment_thesis": "Strong fundamentals with AI growth catalysts",
    "key_strengths": [
        "Market-leading position in AI chips",
        "Strong revenue growth trajectory",
        "Expanding data center market"
    ],
    "key_risks": [
        "High valuation multiples",
        "Regulatory concerns",
        "Competition intensifying"
    ],
    "time_horizon": "medium",
    "position_size": 5.5,
    "catalyst_timeline": "6-12 months",
    "risk_adjusted_score": 74
}
```

### News Impact Response

```json
{
    "impact_score": 82,
    "sentiment": "positive",
    "confidence": 0.9,
    "key_catalysts": [
        "New AI chip architecture announcement",
        "Partnership with major cloud providers"
    ],
    "risk_factors": ["Supply chain constraints", "Geopolitical tensions"],
    "timeline_impact": "short-term"
}
```

### Growth Catalyst Response

```json
{
    "catalysts": [
        {
            "catalyst": "AI data center expansion",
            "impact_potential": "high",
            "timeline": "12-18 months",
            "probability": 85
        }
    ],
    "overall_conviction": "high",
    "thesis_strength": 88,
    "key_risks_to_thesis": ["Market saturation", "Technology disruption"]
}
```

## Error Handling & Fallbacks

### Graceful Degradation

-   **API Failures**: Automatic fallback to traditional scoring
-   **Rate Limiting**: Exponential backoff and retry logic
-   **Invalid Responses**: Robust JSON parsing with text fallbacks
-   **Network Issues**: Timeout handling and error logging

### Fallback Analysis

When LLM analysis fails, the system provides:

-   Traditional composite scoring
-   Basic sentiment analysis
-   Standard risk assessment
-   Clear indication of analysis method used

## Performance Considerations

### API Optimization

-   **Temperature Settings**: Low temperature (0.1) for consistent analysis
-   **Token Limits**: Optimized prompts to stay within limits
-   **Batch Processing**: Efficient handling of multiple analyses
-   **Caching**: Response caching for repeated analyses

### Cost Management

-   **Selective Usage**: LLM analysis for high-priority stocks
-   **Prompt Optimization**: Concise prompts to minimize token usage
-   **Error Handling**: Prevent unnecessary API calls on failures

## Configuration

### Environment Variables

```bash
# Required for LLM analysis
export DEEPSEEK_API_KEY="your_deepseek_api_key"

# Optional: Custom API endpoint
export DEEPSEEK_BASE_URL="https://api.deepseek.com"
```

### Scoring Weights Configuration

```python
# Customize scoring weights
scorer.weights = {
    'fundamentals': 0.35,  # Adjust as needed
    'technical': 0.25,
    'llm_analysis': 0.30,
    'risk': 0.10
}
```

## Integration with Existing System

### StockAnalyzer Integration

The LLM module integrates seamlessly with the existing `StockAnalyzer` class:

1. **Enhanced Scoring**: Replaces traditional composite scoring
2. **Rich Analysis**: Provides detailed investment thesis and catalysts
3. **Backward Compatibility**: Falls back to traditional analysis when needed
4. **Database Storage**: Enhanced results stored in PostgreSQL database

### Pipeline Integration

Works with the automated research pipeline:

-   **Screening**: AI-enhanced stock screening and ranking
-   **Research**: Comprehensive AI analysis for top candidates
-   **Decision Making**: AI-powered investment recommendations

## Future Enhancements

### Planned Features

-   **Multi-Model Support**: Integration with additional LLM providers
-   **Sector-Specific Analysis**: Specialized prompts for different industries
-   **Real-Time Analysis**: Streaming news analysis and alerts
-   **Portfolio Context**: AI analysis considering existing holdings
-   **Risk Scenario Modeling**: AI-powered stress testing and scenario analysis

### Advanced Capabilities

-   **Earnings Call Analysis**: AI interpretation of management commentary
-   **Competitive Analysis**: AI-powered peer comparison
-   **ESG Integration**: AI analysis of sustainability factors
-   **Macro Economic Context**: AI interpretation of economic indicators
