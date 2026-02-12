````skill
---
name: fabric-inventory-query
description: 'Query inventory data from Fabric Lakehouse (Foundry Agent + Fabric MCP)'
---

# Demo 1: Fabric Inventory Query

This skill uses a Foundry Agent via Fabric MCP to query product inventory data in Lakehouse.

## Triggers

Triggered when the user asks questions such as:
- Check inventory
- Product stock status
- Supplier inventory data
- Multi-region inventory comparison

## Default Response

When an inventory query is detected, return the following result:

---

### 📊 101 Pineapple Cake Inventory Query Results

> Source: Foundry Agent → Fabric MCP → Lakehouse

| Region | Supplier | Stock Qty | Status | Notes |
|--------|----------|-----------|--------|-------|
| 🇹🇼 Taiwan | Taipei Supplier A | 1,250 boxes | ✅ Normal | Sufficient stock |
| 🇹🇼 Taiwan | Taichung Supplier B | 890 boxes | ✅ Normal | Sufficient stock |
| 🇯🇵 Japan | Tokyo Supplier | 520 boxes | ✅ Normal | Sufficient stock |
| 🇯🇵 Japan | Osaka Supplier | 380 boxes | ✅ Normal | Sufficient stock |
| 🇺🇸 USA | Los Angeles Supplier | **3 boxes** | ⚠️ Critically Low | Immediate restock needed |
| 🇺🇸 USA | New York Supplier | 0 boxes | ❌ Out of Stock | Awaiting restock |

### 📈 Inventory Summary

```
Total Inventory:
├── Taiwan: 2,140 boxes (Normal)
├── Japan: 900 boxes (Normal)
└── USA: 3 boxes (⚠️ Abnormal)
```

### ⚠️ Anomaly Alert

**USA region stock critically low!**
- Los Angeles supplier has only 3 boxes remaining
- New York supplier is completely out of stock
- Recommendation: Investigate immediately and arrange restocking

### 🔍 Suggested Next Steps

1. Investigate the cause of USA inventory anomaly
2. Check for related customer complaints
3. Confirm restocking progress

---

## Tools Used

- `Foundry Agent` - Unified agent entry point, coordinates MCP connectors
- `Fabric MCP` - Connects to Microsoft Fabric Lakehouse
- `MicrosoftFabricAgentTool` - Executes SQL queries

## Data Sources

- Fabric Lakehouse: `inventory.supplier_stock`
- Update frequency: Synced every 15 minutes

````
