# Configuration Guide

## Environment Setup

### Required Environment Variables

Create a `.env.local` file in the project root with the following variables:

```bash
# Database Configuration (Neon PostgreSQL)
DATABASE_URL="postgresql://neondb_owner:your_password@your_host.us-east-1.aws.neon.tech/neondb?sslmode=require"

# LLM Configuration (DeepSeek API)
DEEPSEEK_API_KEY="sk-your_deepseek_api_key_here"
```

### DeepSeek API Setup

1. **Get API Key**: Visit [DeepSeek Platform](https://platform.deepseek.com/) to get your API key
2. **Add to Environment**: Add your key to `.env.local` as shown above
3. **API Integration**: The system uses OpenAI SDK with DeepSeek endpoint:

```python
from openai import OpenAI

client = OpenAI(
    api_key="your_deepseek_api_key",
    base_url="https://api.deepseek.com"
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ],
    stream=False
)
```

## LLM-Enhanced Analysis

### Scoring System Transformation

**Traditional Scoring (Fallback)**:

-   50% Fundamentals
-   25% Technical Analysis
-   15% Basic Sentiment
-   10% Risk Assessment

**LLM-Enhanced Scoring** (with DeepSeek):

-   40% Fundamentals
-   20% Technical Analysis
-   30% AI Analysis (DeepSeek)
-   10% Risk Assessment

### Usage Examples

#### Basic Analysis (Auto-detects LLM availability)

```python
from src.core import StockAnalyzer

# Initialize with LLM enabled (default)
analyzer = StockAnalyzer()
result = analyzer.analyze_stock("NVDA")

print(f"Analysis Method: {result['recommendation']['analysis_method']}")
print(f"Rating: {result['recommendation']['rating']}")
print(f"Investment Thesis: {result['recommendation']['investment_thesis']}")
```

#### Explicit LLM Configuration

```python
# Enable LLM with specific API key
analyzer = StockAnalyzer(enable_llm=True, deepseek_api_key="your_key")

# Disable LLM (traditional analysis only)
analyzer = StockAnalyzer(enable_llm=False)
```

### Enhanced Features with LLM

1. **Sophisticated News Analysis**

    - Beyond basic sentiment to impact assessment
    - Catalyst identification with timelines
    - Risk factor detection

2. **AI-Powered Investment Thesis**

    - Comprehensive reasoning for recommendations
    - Growth catalyst analysis
    - Market context interpretation

3. **Dynamic Scoring**
    - Confidence-adjusted ratings
    - Risk-adjusted scoring
    - Context-aware thresholds

## Fallback Behavior

The system gracefully handles LLM unavailability:

-   **API Key Missing**: Falls back to traditional analysis
-   **API Failures**: Automatic fallback with error logging
-   **Rate Limiting**: Retry logic with exponential backoff
-   **Network Issues**: Timeout handling and graceful degradation

## Testing LLM Integration

### Quick Test

```bash
# Test with a stock analysis
uv run master_stock_analyzer.py

# Choose option 1 (Single Stock Deep Dive)
# Enter symbol: NVDA
# Look for "LLM-enhanced analysis" in output
```

### Verify Configuration

```python
from src.llm import DeepSeekAnalyzer

try:
    analyzer = DeepSeekAnalyzer()
    print("✅ DeepSeek API configured correctly")
except Exception as e:
    print(f"❌ Configuration error: {e}")
```

## Cost Management

### API Usage Optimization

-   **Low Temperature**: 0.1 for consistent analysis
-   **Token Limits**: Optimized prompts (max 2000 tokens)
-   **Selective Usage**: LLM analysis for high-priority stocks
-   **Error Handling**: Prevents unnecessary API calls

### Expected Costs

-   **Per Analysis**: ~$0.01-0.03 (depending on news volume)
-   **Daily Usage**: ~$1-5 for active trading
-   **Monthly**: ~$30-150 for regular use

## Troubleshooting

### Common Issues

1. **"LLM analysis disabled"**

    - Check DEEPSEEK_API_KEY in .env.local
    - Verify API key is valid
    - Check internet connection

2. **"Fallback to traditional scoring"**

    - API rate limiting (wait and retry)
    - Invalid API response format
    - Network timeout

3. **Import errors**
    - Run: `uv add openai`
    - Verify src/llm module exists

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run analysis to see detailed logs
analyzer = StockAnalyzer()
result = analyzer.analyze_stock("AAPL")
```

## Performance Monitoring

### Key Metrics

-   **Analysis Method**: Check if 'llm_enhanced' or 'traditional'
-   **Confidence Scores**: Higher with LLM analysis
-   **Response Times**: ~2-5 seconds with LLM vs <1 second traditional
-   **API Success Rate**: Monitor fallback frequency

### Logging

The system logs LLM usage:

```
INFO: LLM-enhanced analysis enabled
INFO: Analyzing NVDA with DeepSeek
WARNING: LLM analysis failed, using fallback
```
