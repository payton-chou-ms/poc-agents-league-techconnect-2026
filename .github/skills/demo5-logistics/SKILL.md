---
name: logistics-tracking-query
description: 'Use Foundry Agent + Logistics MCP to query US supplier restocking shipment progress'
---

# Demo 5: Logistics Tracking Query

This skill simulates using Foundry Agent via Logistics MCP to query supplier restocking logistics progress.

## Triggers

Triggered when the user asks questions such as:
- Restocking progress
- Logistics status
- Shipment tracking
- Estimated arrival time

## Default Response

When a logistics query is detected, the following result is returned:

---

### 🚚 Logistics Tracking Query Result

> Query Time: 2026-01-31 10:50:00 UTC+8
> Data Source: Foundry Agent → Logistics MCP
> Query Target: US supplier restocking order

---

### 📦 Restocking Order Tracking

#### Order Information

| Field | Details |
|-------|---------|
| Order Number | `PO-2026-US-0131-001` |
| Product | 101 Pineapple Cake (Decorative) |
| Quantity | **300 boxes** |
| Origin Warehouse | Taiwan Taoyuan Logistics Center |
| Destination | US Los Angeles Supplier Warehouse |
| Shipping Method | Air Express (DHL Express) |

---

### 📍 Shipment Status Tracking

```
Tracking: PO-2026-US-0131-001

✅ 2026-01-28 09:00 Taiwan - Order created
✅ 2026-01-28 14:00 Taiwan - Shipment preparation complete
✅ 2026-01-28 18:00 Taiwan - Handed to DHL
✅ 2026-01-28 22:00 Taiwan - Departed Taoyuan Airport
✅ 2026-01-29 06:00 Japan - Tokyo transit hub
✅ 2026-01-29 14:00 USA - Alaska transit
⏳ 2026-01-30 08:00 USA - Los Angeles customs clearance in progress
🔄 2026-01-31 -- USA - Delivery delayed due to snowstorm

📅 Estimated Arrival: 2026-01-31 afternoon (local time)
```

---

### 🗺️ Shipping Route Map

```
Taiwan Taoyuan (TPE)
    |
    | ✈️ 4 hours
    v
Tokyo, Japan (NRT) - Transit
    |
    | ✈️ 10 hours
    v
Anchorage, USA (ANC) - Transit
    |
    | ✈️ 5 hours
    v
Los Angeles, USA (LAX) - Customs clearance ⏳
    |
    | 🚚 Out for delivery
    v
LA Supplier Warehouse - Expected arrival this afternoon
```

---

### 📊 Logistics Status Summary

| Status | Details |
|--------|---------|
| Current Location | 🇺🇸 Los Angeles, USA |
| Current Status | Customs clearance complete, awaiting delivery |
| Delay Reason | Snowstorm affecting East Coast; slight delay on West Coast deliveries |
| Estimated Arrival | **2026-01-31 3:00 PM PST** |
| Restocking Quantity | **300 boxes** |

---

### ✅ Conclusion

```
📦 Restocking Status Confirmed:

1. 300 boxes of 101 Pineapple Cake (Decorative) are in the US
2. Customs clearance has been completed
3. Expected delivery at 3:00 PM (Pacific Time) to the LA warehouse
4. Inventory will be updated upon arrival, resuming normal sales

⏰ Estimated recovery time: This afternoon (approx. 7:00 AM Feb 1 Taiwan time)
```

---

### 📞 Carrier Contact Information

| Carrier | Tracking Number | Customer Service |
|---------|-----------------|------------------|
| DHL Express | `1234567890` | +1-800-225-5345 |

---

## Tools Used

- `Foundry Agent` - Natural language queries
- `Logistics MCP` - Connection to logistics tracking system

## Data Sources

- DHL Tracking API
- Internal order system
