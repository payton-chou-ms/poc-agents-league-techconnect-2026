# 📋 README.md 修改計畫

> 根據新架構設計，將 README.md 從「單一 Agent + Copilot SDK」調整為「多層式 Agent 架構 + Foundry Agent 路由」

---

## 🔄 變更總覽

| 區塊 | 目前狀態 | 修改後 | 變更類型 |
|------|---------|--------|---------|
| Key Features 表格 | 單一 Backend 欄位 | 依 4 階段分組 + Agent/MCP 欄位 | **重寫** |
| Architecture 圖 | 單一 Agent + Copilot SDK | 多層式架構 (介面→路由→Agent→MCP→資料) | **重寫** |
| Agent 權限模型 | _(不存在)_ | 6 個 Agent 依權限分類 | **新增** |
| Foundry Agent 路由邏輯 | _(不存在)_ | 意圖辨識→分派流程圖 | **新增** |
| Project Structure | 缺少 `data/` 目錄 | 加入 `data/` 結構 | **更新** |
| MCP Integration | 2 個 MCP | 6 個 MCP 連接器 | **擴充** |
| How It Works | Skill Loading → SDK 流程 | User → CLI → Foundry → Agent → MCP → Data | **重寫** |
| Getting Started | 維持 | 維持 | **不變** |
| Scenario | 維持 | 維持 | **不變** |
| Links | 維持 | 維持 | **不變** |

---

## 📝 各區塊修改細節

### 1. ✨ Key Features 表格 — 重寫

**目前：**
```
| # | Skill | Backend | Description |
```

**修改為 — 依 4 個 Demo 階段分組：**

```markdown
| 階段 | Demo | Agent / Tool | MCP | 資料來源 |
|------|------|--------------|-----|----------|
| **階段一：確認問題** | Demo 1 | Foundry Agent | Fabric MCP | Fabric Lakehouse (庫存表) |
| | Demo 2 | Foundry Agent | SharePoint MCP | SharePoint KM 文件 |
| **階段二：修改問題** | Demo 3 | GitHub Coding Agent | - | GitHub Repo (Bug 程式碼) |
| **階段三：確認成效** | Demo 4 | Foundry Agent | Bing Search MCP | Bing 搜尋結果 |
| | Demo 5 | Foundry Agent | Logistics MCP | 物流追蹤 DB |
| | Demo 6 | Foundry Agent | Azure Monitor MCP | Azure Logs / Metrics |
| **階段四：報告追蹤** | Demo 7 | GitHub Copilot | - | 事件上下文 |
| | Demo 8 | GitHub Copilot | WorkIQ MCP | M365 Calendar |
```

---

### 2. 🏗️ Architecture 區塊 — 完整重寫

**目前架構（移除）：**
- 單一 Copilot SDK Agent
- 技能直接掛在 SDK 上
- 只有 2 個 MCP

**新架構層級：**

| 層級 | 組件 | 說明 |
|------|------|------|
| **介面層** | GitHub Copilot CLI | 開發人員統一入口，透過 `gh copilot` 指令互動 |
| **Orchestration 層** | Foundry Agent | 統一路由入口，根據意圖分派給專業 Agent |
| **專業 Agent 層** | 6 類專業 Agent | 依權限分類，各司其職 |
| **MCP 層** | 6 個 MCP 連接器 | 標準化協議連接各種資料來源 |
| **資料層** | 7 種資料來源 | 企業內外部資料 |

**新 Mermaid 圖：** 將繪製多層架構圖，包含：
- 使用者 → GitHub Copilot CLI
- Foundry Agent 作為 Orchestrator
- 6 個專業 Agent（Inventory / Knowledge / Search / SRE / Coding / Copilot）
- 6 個 MCP 連接器
- 7 種資料來源

---

### 3. 🔐 Agent 權限分類 — 新增區塊

在 Architecture 區塊後新增：

```markdown
| Agent 類別 | Agent 名稱 | 權限等級 | 可存取資源 | Demo |
|------------|-----------|----------|-----------|------|
| 📊 Data Agent | Inventory Agent | 🔴 高 | Fabric Lakehouse (庫存資料) | Demo 1 |
| | Logistics Agent | 🔴 高 | 物流系統 DB | Demo 5 |
| 📚 Knowledge Agent | Knowledge Agent | 🟡 中 | SharePoint 內部文件 | Demo 2 |
| 🌐 External Agent | Search Agent | 🟢 低 | Bing 公開搜尋 | Demo 4 |
| ⚙️ Ops Agent | SRE Agent | 🔴 高 | Azure Monitor Logs/Metrics | Demo 6 |
| 🛠️ GitHub Agent | Coding Agent | 🔴 高 | GitHub Repo (寫入) | Demo 3 |
| 🛠️ GitHub Agent | Copilot | 🟡 中 | M365 Calendar | Demo 7-8 |
```

附帶 4 個分類理由：
1. 最小權限原則
2. 安全隔離
3. 審計追蹤
4. 彈性擴展

---

### 4. 🔀 Foundry Agent 路由邏輯 — 新增區塊

新增路由示意圖：

```
使用者輸入 → Foundry Agent (意圖辨識)
                    │
    ┌───────────────┼───────────────┬───────────────┐
    ▼               ▼               ▼               ▼
"查詢庫存"      "搜尋文件"      "查天氣"       "檢查系統"
    │               │               │               │
    ▼               ▼               ▼               ▼
Inventory       Knowledge        Search           SRE
Agent           Agent            Agent           Agent
(高權限)        (中權限)         (低權限)        (高權限)
```

---

### 5. 📁 Project Structure — 更新

新增 `data/` 目錄：

```
data/
├── customer-complaints/           # 客訴資料
│   ├── tw_complaints_jan25.json
│   ├── jp_complaints_jan25.json
│   └── us_complaints_jan25.json
├── inventory/                     # 庫存資料 (Fabric)
│   ├── tw_supplier_inventory.csv
│   ├── jp_supplier_inventory.csv
│   └── us_supplier_inventory.csv
└── sharepoint-km/                 # 知識管理文件
    ├── common-issues-faq.md
    ├── supplier-sync-guide.md
    └── inventory-troubleshoot.md
```

---

### 6. 🔌 MCP Integration — 擴充

**目前：** 2 個 MCP（GitHub MCP、WorkIQ MCP）

**修改為：** 6 個 MCP

| MCP | 使用 Agent | 資料來源 | 說明 |
|-----|-----------|---------|------|
| Fabric MCP | Inventory Agent | Fabric Lakehouse | 跨區域庫存查詢 |
| SharePoint MCP | Knowledge Agent | SharePoint 文件庫 | 內部知識管理文件搜尋 |
| Bing Search MCP | Search Agent | Bing 搜尋引擎 | 天氣/新聞等即時公開資訊 |
| Logistics MCP | Logistics Agent | 物流追蹤 DB | 出貨狀態與 ETA |
| Azure Monitor MCP | SRE Agent | Azure Logs/Metrics | 系統健康狀態監控 |
| WorkIQ MCP | Copilot | M365 Calendar | 會議排程與行事曆 |

> 注意：GitHub Coding Agent (Demo 3) 不透過 MCP，直接操作 GitHub Repo

---

### 7. 📋 How It Works — 重寫流程

**目前流程：**
1. Skill Loading → 2. Tool Registration → 3. Session Creation → 4. Conversation → 5. Permission Flow

**修改為新架構流程：**
1. **使用者輸入** — 透過 GitHub Copilot CLI 發送指令
2. **意圖辨識** — Foundry Agent 分析使用者意圖
3. **Agent 路由** — 根據意圖分派給對應的專業 Agent
4. **權限檢查** — 檢查該 Agent 是否有足夠權限執行操作
5. **MCP 呼叫** — 專業 Agent 透過 MCP 連接器存取資料來源
6. **結果彙整** — Foundry Agent 彙整回應，以自然語言回覆使用者

---

### 8. 🤖 GitHub Copilot Usage — 調整

**移除：**
- 「GitHub Copilot SDK 作為 AI Runtime」的描述

**調整為：**
- GitHub Copilot CLI 作為使用者入口
- Foundry Agent 作為 Orchestrator
- GitHub Copilot 負責 Demo 7（報告生成）與 Demo 8（會議排程）

---

## ❌ 不修改的區塊

| 區塊 | 理由 |
|------|------|
| 🎯 The Scenario | 情境不變（鳳梨酥缺貨） |
| Human-in-the-Loop | 權限升級概念不變，但融入 Agent 權限模型 |
| 🚀 Getting Started | 安裝流程保持一致 |
| Environment Variables | 維持 |
| 🔗 Links | 維持 |
| License | 維持 |

---

## ✅ 執行順序

1. 修改 Key Features 表格
2. 重寫 Architecture 區塊（含 Mermaid 圖）
3. 新增 Agent 權限分類表
4. 新增 Foundry Agent 路由邏輯
5. 更新 Project Structure（加入 `data/`）
6. 擴充 MCP Integration（2 → 6 個）
7. 重寫 How It Works 流程
8. 調整 GitHub Copilot Usage
