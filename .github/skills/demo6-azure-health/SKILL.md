````skill
---
name: azure-system-health
description: 'Use Foundry Agent + Azure Monitor MCP to monitor system health and collect logs'
---

# Demo 6: Azure System Monitoring

This skill uses a Foundry Agent via Azure Monitor MCP to check system health status and collect relevant log information.

## Triggers

Triggered when the user asks questions such as:
- System health status
- Check service status
- Query error logs
- Azure resource monitoring

## Default Response

When a system health query is detected, return the following result:

---

### 🖥️ Azure System Health Check Results

> Source: Foundry Agent → Azure Monitor MCP → Azure Monitor
> Scope: US Region (West US 2)

---

### 📊 System Overview

| Service | Status | Availability | Latency |
|---------|--------|-------------|---------|
| Web App (US) | ✅ Normal | 99.98% | 45ms |
| API Gateway | ✅ Normal | 99.99% | 32ms |
| Database (US) | ✅ Normal | 99.97% | 28ms |
| Redis Cache | ✅ Normal | 99.99% | 5ms |
| Azure Functions | ✅ Normal | 99.95% | 120ms |
| Storage Account | ✅ Normal | 99.99% | 15ms |

**Overall Status: ✅ All systems operating normally**

---

### 📈 Performance Metrics (Last 24 Hours)

```
CPU Usage:
├── Web App: ████████░░ 78% (Normal)
├── API: ██████░░░░ 62% (Normal)
└── Functions: ████░░░░░░ 45% (Normal)

Memory Usage:
├── Web App: ██████░░░░ 65% (Normal)
├── API: █████░░░░░ 52% (Normal)
└── Functions: ███░░░░░░░ 38% (Normal)

Requests:
├── Total: 1,245,678
├── Successful: 1,243,890 (99.86%)
└── Failed: 1,788 (0.14%)
```

---

### 📋 Recent Error Logs (Last 6 Hours)

| Time | Severity | Service | Message |
|------|----------|---------|---------|
| 10:42:15 | ⚠️ Warning | supplier-sync | Retry attempt 2/3 for JP supplier |
| 10:15:30 | ℹ️ Info | cache | Cache refresh completed |
| 09:30:00 | ✅ Info | deployment | Hotfix deployed successfully |
| 08:45:22 | ⚠️ Warning | supplier-sync | API timeout, retrying... |
| 08:12:10 | ✅ Info | health-check | All services healthy |

---

### 🔍 Supplier Sync Service Detailed Status

```
Azure Function: supplier-sync-job

Status: ✅ Running
Last execution: 2026-01-31 10:45:00
Result: Success

Sync Status:
├── 🇹🇼 Taiwan supplier: ✅ Sync successful (10:45:02)
├── 🇯🇵 Japan supplier: ✅ Sync successful (10:45:05)
└── 🇺🇸 US supplier: ✅ Sync successful (10:45:08)

Fix Verification:
├── Timeout setting: 30s ✅ (Updated from 5s)
├── Retry mechanism: Enabled ✅
└── Error handling: Complete ✅
```

---

### 📊 Post-Fix Performance Comparison

| Metric | Before Fix | After Fix | Improvement |
|--------|-----------|-----------|-------------|
| Sync success rate | 87.3% | 99.8% | +12.5% |
| Avg sync time | 45s | 12s | -73% |
| API Timeout errors | 23/hour | 0/hour | -100% |
| False out-of-stock events | 15/day | 0/day | -100% |

---

### ✅ Health Check Conclusion

```
🎉 System Health Status Confirmed:

1. ✅ All Azure services operating normally
2. ✅ Supplier sync service has been fixed
3. ✅ Bug fix successfully deployed
4. ✅ Sync success rate improved from 87.3% to 99.8%
5. ✅ No new errors generated

📌 Fix verification complete, system operating normally!
```

---

### 📱 Monitoring Dashboard Links

- [Azure Portal - Resource Group](https://portal.azure.com/#resource/pineapple-cake-us)
- [Application Insights](https://portal.azure.com/#insights)
- [Log Analytics](https://portal.azure.com/#logs)

---

## Tools Used

- `Foundry Agent` - Natural language queries
- `Azure Monitor MCP` - Connects to Azure Monitor

## Data Sources

- Azure Monitor Metrics
- Application Insights
- Log Analytics Workspace

````
