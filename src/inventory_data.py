"""Load real inventory data from CSV files and generate Markdown reports.

Replaces the static SKILL.md response with live data from
data/inventory/{tw,jp,us}_supplier_inventory.csv.

Ported from ref/02_inventory_agent.py's embedded INVENTORY_DATA and
anomaly detection logic.
"""

import csv
from dataclasses import dataclass, field
from pathlib import Path


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

STATUS_ICONS = {
    "normal": "✅ Normal",
    "low": "🟡 Low",
    "critical": "⚠️ Critical",
    "out_of_stock": "❌ Out of Stock",
}

REGION_FLAGS = {
    "TW": "🇹🇼 Taiwan",
    "JP": "🇯🇵 Japan",
    "US": "🇺🇸 USA",
}


@dataclass
class InventoryRecord:
    product_id: str
    product_name: str
    region: str
    warehouse: str
    quantity: int
    unit: str
    status: str
    last_updated: str
    reorder_point: int
    supplier: str
    note: str = ""

    @property
    def status_display(self) -> str:
        return STATUS_ICONS.get(self.status, self.status)

    @property
    def is_anomaly(self) -> bool:
        return self.status in ("critical", "out_of_stock")

    @property
    def is_low(self) -> bool:
        return self.status == "low"


@dataclass
class RegionSummary:
    region: str
    total_qty: int = 0
    records: list[InventoryRecord] = field(default_factory=list)

    @property
    def worst_status(self) -> str:
        priority = ["out_of_stock", "critical", "low", "normal"]
        for s in priority:
            if any(r.status == s for r in self.records):
                return s
        return "normal"


# ---------------------------------------------------------------------------
# CSV loading
# ---------------------------------------------------------------------------

_CSV_FILES = {
    "TW": "tw_supplier_inventory.csv",
    "JP": "jp_supplier_inventory.csv",
    "US": "us_supplier_inventory.csv",
}


def _data_dir() -> Path:
    return Path(__file__).parent.parent / "data" / "inventory"


def load_inventory(data_dir: Path | None = None) -> list[InventoryRecord]:
    """Load all inventory records from CSV files.

    Args:
        data_dir: Override data directory (for testing).

    Returns:
        List of InventoryRecord sorted by region then product_id.
    """
    base = data_dir or _data_dir()
    records: list[InventoryRecord] = []

    for region, filename in _CSV_FILES.items():
        csv_path = base / filename
        if not csv_path.exists():
            continue

        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(InventoryRecord(
                    product_id=row["product_id"],
                    product_name=row["product_name"],
                    region=row["region"],
                    warehouse=row["warehouse"],
                    quantity=int(row["quantity"]),
                    unit=row["unit"],
                    status=row["status"],
                    last_updated=row["last_updated"],
                    reorder_point=int(row["reorder_point"]),
                    supplier=row["supplier"],
                    note=row.get("note", ""),
                ))

    records.sort(key=lambda r: (r.region, r.product_id))
    return records


def _summarize_regions(records: list[InventoryRecord]) -> dict[str, RegionSummary]:
    """Group records by region and compute totals."""
    summaries: dict[str, RegionSummary] = {}
    for rec in records:
        if rec.region not in summaries:
            summaries[rec.region] = RegionSummary(region=rec.region)
        s = summaries[rec.region]
        s.total_qty += rec.quantity
        s.records.append(rec)
    return summaries


# ---------------------------------------------------------------------------
# Anomaly detection
# ---------------------------------------------------------------------------

@dataclass
class Anomaly:
    severity: str  # "critical" | "warning"
    region: str
    warehouse: str
    message: str


def detect_anomalies(records: list[InventoryRecord]) -> list[Anomaly]:
    """Detect inventory anomalies (critical + low stock warnings)."""
    anomalies: list[Anomaly] = []
    for rec in records:
        if rec.status == "out_of_stock":
            msg = f"{rec.warehouse}: **0** boxes — out of stock"
            if rec.note:
                msg += f" ({rec.note})"
            anomalies.append(Anomaly("critical", rec.region, rec.warehouse, msg))
        elif rec.status == "critical":
            msg = (
                f"{rec.warehouse}: only **{rec.quantity}** boxes "
                f"(reorder point: {rec.reorder_point})"
            )
            if rec.note:
                msg += f" — {rec.note}"
            anomalies.append(Anomaly("critical", rec.region, rec.warehouse, msg))
        elif rec.status == "low":
            msg = (
                f"{rec.warehouse}: {rec.quantity} boxes "
                f"(reorder point: {rec.reorder_point}) — still above threshold"
            )
            anomalies.append(Anomaly("warning", rec.region, rec.warehouse, msg))
    return anomalies


# ---------------------------------------------------------------------------
# Markdown report generation
# ---------------------------------------------------------------------------

def generate_inventory_report(records: list[InventoryRecord] | None = None) -> str:
    """Generate a full Markdown inventory report with anomaly alerts.

    This replaces 02_inventory_agent.py's static INVENTORY_DATA and the
    static SKILL.md response with real data from CSV files.

    Args:
        records: Pre-loaded records, or None to load from CSV.

    Returns:
        Markdown string suitable for LLM consumption or direct display.
    """
    if records is None:
        records = load_inventory()

    if not records:
        return "⚠️ No inventory data found. CSV files may be missing from data/inventory/."

    summaries = _summarize_regions(records)
    anomalies = detect_anomalies(records)
    last_updated = records[0].last_updated if records else "unknown"

    lines: list[str] = []
    lines.append("### 📊 101 Pineapple Cake Inventory Query Results\n")
    lines.append(f"> Source: Foundry Agent → Fabric MCP → Lakehouse (`inventory.supplier_stock`)")
    lines.append(f"> Last sync: {last_updated}\n")

    # Per-region detail tables
    for region_code in ["TW", "JP", "US"]:
        summary = summaries.get(region_code)
        if not summary:
            continue

        flag = REGION_FLAGS.get(region_code, region_code)
        lines.append(f"#### {flag}\n")
        lines.append("| Product ID | Product Name | Warehouse | Qty | Unit | Status | Reorder Pt | Supplier |")
        lines.append("|------------|-------------|-----------|-----|------|--------|------------|----------|")
        for rec in summary.records:
            qty_str = f"**{rec.quantity}**" if rec.is_anomaly else f"{rec.quantity:,}"
            note_suffix = f" 📝 {rec.note}" if rec.note else ""
            lines.append(
                f"| {rec.product_id} | {rec.product_name} | {rec.warehouse} "
                f"| {qty_str} | {rec.unit} | {rec.status_display} "
                f"| {rec.reorder_point} | {rec.supplier}{note_suffix} |"
            )
        lines.append(f"\n**{flag} Total: {summary.total_qty:,} boxes**\n")

    # Global summary table
    global_total = sum(s.total_qty for s in summaries.values())
    lines.append("#### 📈 Global Summary\n")
    lines.append("| Region | Total Stock | Status |")
    lines.append("|--------|------------|--------|")
    for region_code in ["TW", "JP", "US"]:
        summary = summaries.get(region_code)
        if not summary:
            continue
        flag = REGION_FLAGS.get(region_code, region_code)
        status = STATUS_ICONS.get(summary.worst_status, summary.worst_status)
        lines.append(f"| {flag} | {summary.total_qty:,} boxes | {status} |")
    lines.append(f"| **Global Total** | **{global_total:,} boxes** | |")
    lines.append("")

    # Anomaly alerts
    if anomalies:
        critical = [a for a in anomalies if a.severity == "critical"]
        warnings = [a for a in anomalies if a.severity == "warning"]

        lines.append("#### ⚠️ Anomaly Alert\n")
        if critical:
            for a in critical:
                flag = REGION_FLAGS.get(a.region, a.region)
                lines.append(f"- 🔴 **{flag}**: {a.message}")
        if warnings:
            for a in warnings:
                flag = REGION_FLAGS.get(a.region, a.region)
                lines.append(f"- 🟡 {flag}: {a.message}")
        lines.append("")

    # Suggested next steps
    lines.append("#### 🔍 Suggested Next Steps\n")
    if any(a.severity == "critical" for a in anomalies):
        lines.append("1. **Investigate cause** of critical stock shortage")
        lines.append("2. Check for related **customer complaints**")
        lines.append("3. Confirm **restocking progress** and ETA")
    else:
        lines.append("1. Continue monitoring stock levels")
        lines.append("2. Review reorder schedules for low-stock warehouses")
    lines.append("")

    return "\n".join(lines)
