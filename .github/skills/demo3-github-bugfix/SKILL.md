````skill
---
name: github-bugfix-agent
description: 'Use GitHub Coding Agent to automatically fix code bugs and verify compliance'
---

# Demo 3: GitHub Coding Agent Bug Fix

This skill uses GitHub Coding Agent to automatically analyze and fix code bugs, while ensuring the code meets compliance requirements.

## Triggers

Triggered when the user asks questions such as:
- Fix a bug
- Code issue analysis
- Auto-fix code
- Code compliance check

## Default Response

When a bug fix request is detected, return the following result:

---

### 🔧 GitHub Coding Agent Execution Results

> Source: GitHub Coding Agent → GitHub Repository
> Repository: `pineapple-cake-shop/supplier-sync-service`

---

### 📋 Issue Analysis

**Issue #1847**: Supplier data sync delay causing false out-of-stock

```
Problem Description:
- Taiwan/Japan supplier data sync is delayed
- Website shows "Out of Stock" but items are actually available
- Affected Product: 101 Pineapple Cake

Root Cause:
- API connection timeout set too short (5 seconds)
- No retry mechanism
- Incomplete error handling
```

---

### 🛠️ Auto-Fix Details

#### Modified File: `src/services/supplier-sync.ts`

```diff
// supplier-sync.ts

- const API_TIMEOUT = 5000; // 5 seconds
+ const API_TIMEOUT = 30000; // 30 seconds

- async function fetchSupplierData(supplierId: string) {
-   const response = await fetch(supplierEndpoints[supplierId]);
-   return response.json();
- }
+ async function fetchSupplierData(supplierId: string, retries = 3) {
+   for (let attempt = 1; attempt <= retries; attempt++) {
+     try {
+       const controller = new AbortController();
+       const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT);
+
+       const response = await fetch(supplierEndpoints[supplierId], {
+         signal: controller.signal
+       });
+       clearTimeout(timeoutId);
+
+       if (!response.ok) {
+         throw new Error(`HTTP ${response.status}`);
+       }
+       return response.json();
+     } catch (error) {
+       console.error(`Attempt ${attempt} failed for ${supplierId}:`, error);
+       if (attempt === retries) throw error;
+       await sleep(1000 * attempt); // Exponential backoff
+     }
+   }
+ }
```

#### Modified File: `src/services/inventory-cache.ts`

```diff
// inventory-cache.ts

- function updateCache(data: InventoryData) {
-   cache.set(data.productId, data.quantity);
- }
+ function updateCache(data: InventoryData) {
+   // Only update when new data is more recent
+   const existing = cache.get(data.productId);
+   if (!existing || data.timestamp > existing.timestamp) {
+     cache.set(data.productId, {
+       quantity: data.quantity,
+       timestamp: data.timestamp,
+       syncStatus: 'success'
+     });
+     console.log(`Cache updated for ${data.productId}: ${data.quantity}`);
+   }
+ }
```

---

### ✅ MDC Compliance Check

| Check Item | Status | Details |
|------------|--------|---------|
| Code Style | ✅ Pass | Meets ESLint standards |
| Unit Tests | ✅ Pass | 3 new test cases added, all passing |
| Security Scan | ✅ Pass | No security vulnerabilities |
| Dependency Check | ✅ Pass | No packages with known vulnerabilities |
| Documentation Update | ✅ Pass | README updated |

---

### 📝 Pull Request Created

```
PR #1892: Fix supplier sync timeout and add retry mechanism

Status: ✅ Ready for review
Branch: fix/supplier-sync-timeout → main
Reviewers: @harry-dev, @almond-pm

Change Summary:
- Increased API timeout to 30 seconds
- Added 3-retry mechanism with exponential backoff
- Improved cache update logic
- Added comprehensive error handling

CI/CD Status:
✅ Build: Passed
✅ Tests: 47/47 passed
✅ Security Scan: No issues
✅ MDC Compliance: Verified
```

---

### 🚀 Deployment Status

```
Auto-deployment triggered:
├── Staging: ✅ Deployed successfully (10:42:15)
├── Validation Tests: ✅ Passed (10:43:30)
└── Production: ⏳ Awaiting review before deployment
```

---

## Tools Used

- `GitHub Copilot Coding Agent` - Automated code analysis and fix
- `GitHub Actions` - CI/CD pipeline
- `MDC Scanner` - Compliance check

## Data Sources

- Repository: `supplier-sync-service`
- Issue: #1847
- PR: #1892

````
