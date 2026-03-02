---
name: "ai-stock-picker"
description: "Generates daily AI-powered stock/ETF recommendations with reasoning. Invoke when user asks for stock analysis, market outlook, or wants to run daily stock picking routine."
---

# AI Stock Picker

This skill provides AI-powered stock market analysis and recommendations, focusing on sectors and ETFs with clear reasoning and data logging for backtesting.

## Core Functions

### 1. Daily Market Analysis
- Analyze current market conditions
- Identify bullish and bearish sectors/ETFs
- Provide detailed reasoning for each recommendation
- Generate confidence scores

### 2. Data Logging & Tracking
- Store all recommendations in structured format
- Track historical predictions for accuracy analysis
- Export data for backtesting and quantitative analysis

### 3. Reporting
- Generate daily reports
- Create performance tracking dashboards
- Export data in multiple formats (JSON, CSV)

## Usage

When invoked, this skill will:

1. **Market Analysis Phase**
   - Fetch latest market data and trends
   - Analyze sector performance
   - Review economic indicators
   - Consider technical and fundamental factors

2. **Recommendation Generation**
   - Identify top 3-5 bullish sectors/ETFs
   - Identify top 3-5 bearish sectors/ETFs
   - Provide detailed reasoning for each
   - Assign confidence levels (1-10)

3. **Data Storage**
   - Save recommendations to `.trae/skills/ai-stock-picker/data/recommendations.json`
   - Append daily entries with timestamps
   - Include all reasoning and metadata

4. **Output Format**
   - Display formatted report to user
   - Save structured data for analysis
   - Optionally export to CSV for quantitative use

## Data Structure

Each recommendation entry includes:
```json
{
  "date": "YYYY-MM-DD",
  "timestamp": "ISO timestamp",
  "market_condition": "bullish/bearish/neutral",
  "recommendations": {
    "bullish": [
      {
        "sector": "Technology",
        "etf": "XLK",
        "confidence": 8,
        "reasoning": [
          "Strong earnings growth",
          "AI sector momentum",
          "Technical breakout pattern"
        ],
        "risk_factors": ["Valuation concerns", "Regulatory risks"]
      }
    ],
    "bearish": [
      {
        "sector": "Utilities",
        "etf": "XLU",
        "confidence": 7,
        "reasoning": [
          "Rising interest rates pressure",
          "Weak demand growth",
          "Technical breakdown"
        ],
        "potential_catalysts": ["Rate cuts", "Infrastructure spending"]
      }
    ]
  },
  "market_summary": "Overall market assessment...",
  "key_indicators": {
    "vix": 18.5,
    "spy_trend": "uptrend",
    "market_breadth": "positive"
  }
}
```

## Analysis Framework

### Technical Analysis
- Trend analysis (MA, MACD, RSI)
- Support/resistance levels
- Volume patterns
- Sector rotation signals

### Fundamental Analysis
- Earnings growth trends
- Valuation metrics (P/E, PEG, P/B)
- Economic indicators
- Industry cycles

### Sentiment Analysis
- Market sentiment indicators
- News sentiment
- Institutional flow data
- Options market positioning

## Workflow

1. User invokes skill (daily or on-demand)
2. Skill performs comprehensive market analysis
3. Generates structured recommendations
4. Displays human-readable report
5. Saves data for tracking and backtesting
6. Optionally sends notifications

## Future Enhancements

- Integration with real-time data APIs
- Automated daily execution
- Performance tracking dashboard
- Backtesting framework
- WeChat公众号 integration for subscribers
- Customizable risk parameters
- Multi-timeframe analysis (day/week/month)

## Files Structure

```
.trae/skills/ai-stock-picker/
├── SKILL.md (this file)
├── data/
│   ├── recommendations.json (historical recommendations)
│   ├── performance.json (tracking accuracy)
│   └── exports/ (CSV exports for quantitative analysis)
└── templates/
    └── report_template.md
```

## Important Notes

- All recommendations are for educational and research purposes
- Past performance does not guarantee future results
- This is a tool for data collection and analysis, not financial advice
- Users should conduct their own due diligence before making investment decisions
- The goal is to evaluate AI prediction accuracy over time
