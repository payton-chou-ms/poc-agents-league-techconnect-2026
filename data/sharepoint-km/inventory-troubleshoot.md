# 庫存異常排解指南

> 最後更新: 2026-01-22 | 維護者: 營運團隊

---

## 判斷流程

```
庫存異常通報
    │
    ├─ 單一門市 → 門市端盤點
    │
    ├─ 單一區域 → 檢查區域同步狀態
    │
    └─ 跨區域 → 啟動全面排查流程
                    │
                    ├─ 1. 檢查 API 同步狀態
                    ├─ 2. 檢查 Fabric 資料管線
                    ├─ 3. 檢查供應商端回報
                    └─ 4. 確認物流狀態
```

## 排查步驟

### Step 1: 確認異常範圍

```sql
-- 在 Fabric Lakehouse 中查詢各區域庫存
SELECT region, product_name, SUM(quantity) as total_qty, 
       MIN(last_updated) as oldest_update
FROM inventory.supplier_inventory
WHERE product_id LIKE 'P101%'
GROUP BY region, product_name
ORDER BY total_qty ASC;
```

### Step 2: 檢查同步狀態

```bash
# 查詢各區域最後同步時間
curl -H "Authorization: Bearer $TOKEN" \
  https://api.zava.com/v2/supplier/sync-status

# 預期回應
{
  "TW": {"last_sync": "2026-01-31T08:00:00Z", "status": "success"},
  "JP": {"last_sync": "2026-01-31T07:45:00Z", "status": "success"},
  "US": {"last_sync": "2026-01-31T06:30:00Z", "status": "failed", "error": "timeout"}
}
```

### Step 3: 歷史案例參考

| 日期 | 事件 | 根因 | 解決方式 | 耗時 |
|------|------|------|----------|------|
| 2025-11-15 | 日本區庫存歸零 | 供應商 API 格式變更 | 更新 API adapter | 4 小時 |
| 2025-09-03 | 全球庫存數據延遲 | Fabric 管線排程失敗 | 重啟排程 + 回補資料 | 2 小時 |
| 2025-06-20 | 美國庫存異常偏高 | 重複入庫記錄 | 資料清洗 + 對帳 | 6 小時 |

### Step 4: 緊急應對

若確認為系統問題：
1. 通知 SRE 團隊 (Slack #sre-oncall)
2. 在 Azure Monitor 建立即時監控 dashboard
3. 啟動供應商緊急補貨流程
4. 每 2 小時更新事件狀態

---
