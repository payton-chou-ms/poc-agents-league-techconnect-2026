````skill
---
name: bing-weather-search
description: 'Use Foundry Agent + Bing Search MCP to query real-time news and weather information'
---

# Demo 4: Bing News & Weather Query

This skill uses a Foundry Agent via Bing Search MCP to query real-time news, weather forecasts, and related information.

## Triggers

Triggered when the user asks questions such as:
- Real-time news query
- Weather forecast
- External information search
- News event lookup

## Default Response

When a weather query is detected, return the following result:

---

### 🌨️ Bing Weather & News Query Results

> Source: Foundry Agent → Bing Search MCP → Bing Search API
> Search Keywords: `US East Coast weather storm January 2026`

---

### 📰 Real-Time News

#### 🔴 Breaking News

**"Winter Storm Juno" Sweeps US East Coast, Multiple States Declare Emergency**

> Source: CNN Weather | 2026-01-30 18:00 EST

The US East Coast is being hit by this year's largest blizzard, "Winter Storm Juno." New York, New Jersey, Connecticut, and other states have declared a state of emergency. Expected snowfall is 18-24 inches, with some areas potentially exceeding 30 inches.

---

### 🗞️ Related News

| # | Title | Source | Date |
|---|-------|--------|------|
| 1 | **Major Blizzard Hits US East Coast, Thousands of Flights Canceled** | AP News | 2026-01-30 |
| 2 | **NYC Declares Snow Emergency, All Non-Essential Travel Banned** | NY Times | 2026-01-30 |
| 3 | **Supply Chain Disruptions Expected as Storm Paralyzes Northeast** | Reuters | 2026-01-30 |
| 4 | **UPS, FedEx Suspend Deliveries in Affected Areas** | Bloomberg | 2026-01-30 |
| 5 | **Storm Expected to Clear by Thursday Afternoon** | Weather.com | 2026-01-30 |

---

### 🌡️ Weather Forecast Summary

```
US East Coast Weather Overview (2026-01-30 ~ 02-01):

📍 New York City
├── 1/30: Blizzard ❄️ -5°C / Snowfall 20-25cm
├── 1/31: Heavy Snow 🌨️ -3°C / Snowfall 10-15cm
└── 2/01: Cloudy ☁️ 2°C / Gradually clearing

📍 Los Angeles (West Coast)
├── 1/30: Sunny ☀️ 18°C
├── 1/31: Sunny ☀️ 19°C
└── 2/01: Sunny ☀️ 20°C
```

---

### 📦 Logistics Impact Assessment

Based on news analysis, the blizzard's impact on logistics:

| Impact Area | Status | Details |
|-------------|--------|---------|
| Air Cargo | ⛔ Suspended | JFK, EWR, LGA airports closed |
| Road Transport | ⚠️ Delayed | I-95 partially closed |
| Express Delivery | ⛔ Suspended | UPS/FedEx suspended pickups & deliveries |
| Estimated Recovery | 📅 2/1 afternoon | Blizzard expected to weaken by 1/31 evening |

---

### 💡 Analysis Conclusion

**External factor confirmed for US inventory shortage:**

1. ❄️ Blizzard causing full logistics delay
2. 🚚 Restock shipments stuck in transit
3. 📅 Weather expected to improve by 2/1 afternoon, logistics to resume
4. ✅ This is a **force majeure event**, not a system issue

---

## Tools Used

- `Foundry Agent` - Natural language queries
- `Bing Search MCP` - Real-time web information search

## Data Sources

- Bing Search API
- Real-time news index

````
