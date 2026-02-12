# 供應商資料同步說明

> 最後更新: 2026-01-15 | 維護者: 後端工程團隊

---

## 系統概述

供應商庫存資料透過 RESTful API 每 15 分鐘自動同步至 Fabric Lakehouse。

### 同步架構

```
供應商系統 → API Gateway → Supplier Sync Service → Fabric Lakehouse
                                    ↓
                             Azure Monitor (日誌)
```

## API 端點

| 端點 | 方法 | 說明 |
|------|------|------|
| `/api/v2/supplier/sync-status` | GET | 查詢同步狀態 |
| `/api/v2/supplier/sync-trigger` | POST | 手動觸發同步 |
| `/api/v2/supplier/inventory/{region}` | GET | 查詢特定區域庫存 |

## 常見問題

### Timeout 問題 (> 30 秒)

**症狀**: API 回應超過 30 秒，導致同步失敗。

**根因分析**:
1. 供應商端資料量過大
2. 網路延遲（特別是跨國同步）
3. **已知 Bug**: `supplier-sync-service` v2.3.1 中的 connection pool 未正確回收（參考 GitHub Issue #1287）

**修復方式**:
- 短期: 增加 timeout 設定至 60 秒
- 長期: 升級至 v2.4.0（已修復 connection pool 問題）

### 資料不一致

**症狀**: Fabric Lakehouse 中的庫存與供應商系統不符。

**排查步驟**:
1. 比對最後同步時間戳
2. 檢查同步日誌中是否有 partial failure
3. 手動觸發全量同步: `POST /api/v2/supplier/sync-trigger?mode=full`

---

## 監控告警

| 告警規則 | 閾值 | 通知方式 |
|----------|------|----------|
| 同步失敗 | 連續 3 次 | Teams 通知 + Email |
| 同步延遲 | > 30 分鐘 | Teams 通知 |
| API 錯誤率 | > 5% | PagerDuty |

---
