# Dairy Management

Comprehensive dairy farm operations app for ERPNext/Frappe.

It covers:
- Animal and herd master data
- Milk production and dispatch
- Breeding and calving
- Veterinary and vaccination tracking
- Feed and nutrition management
- Equipment and utility operations
- Finance and compliance reporting
- Workspace + Apex dashboard for all module reports

## Tech Stack

- Frappe Framework v15
- ERPNext v15
- App: `dairy_management` (`0.0.1`)

## Installation

```bash
cd $PATH_TO_BENCH
bench get-app <repo-url> --branch develop
bench --site <your-site> install-app dairy_management
bench --site <your-site> migrate
bench build --app dairy_management
```

## Workspace and Dashboard Flow

### 1) Workspace

- Workspace: `Dairy Management`
- Includes custom HTML block: `Dairy Workspace Hub`
- Section-wise quick links for all DocTypes and reports
- Dashboard route shortcut: `/app/herd-summary-report`

### 2) Dashboard Page

- Page: `herd-summary-report`
- Title: `Dairy Reports Dashboard`
- Features:
  - Top KPI cards from `Herd Summary Report`
  - Auto-loads all reports where `module = Dairy Management`
  - Renders Apex chart card for each report
  - Refresh button for live reload

### 3) Report Name Compatibility

To avoid Python import errors for report IDs containing `&`, report document names are normalized:

- `Milk Dispatch and Revenue Report` (display title stays `Milk Dispatch & Revenue Report`)
- `Profit and Loss Summary Report` (display title stays `Profit & Loss Summary Report`)

Compatibility and migration support:
- Method override in `hooks.py` for `frappe.desk.query_report.run`
- Alias resolver in `dairy_management/dairy_management/query_report.py`
- Patch: `dairy_management.patches.v15_0.rename_dairy_report_ids`

## End-to-End Business Flow

## Phase A: Master Setup

Create foundational records first:

- Animal masters:
  - `Animal Breed`
  - `Pen`
  - `Animal`
- Milk and facility masters:
  - `Parlour`
  - `Bulk Tank`
- Breeding/health masters:
  - `Semen Batch`
  - `Disease`
- Feed/ops masters:
  - ERPNext `Item` (feed + medicines)
  - ERPNext `Supplier`, `Customer`, `Employee`, `Asset`, `Cost Center`

## Phase B: Daily Farm Operations

### Milk Operations

- Record milking sessions in `Milk Recording`
  - Morning/Evening/Midday yields
  - Quality fields (fat/protein/lactose/SCC)
- Maintain tank logs in `Bulk Tank Log`
  - Quantity + temperature
  - Dispatch quantity, buyer, and rate

### Health Operations

- Log treatment/illness in `Health Event`
  - Auto-calculates `milk_safe_date` from `event_date + withdrawal_days`
- Plan boosters in `Vaccination Schedule`

### Feed Operations

- Track stock in `Feed Inventory`
- Define rations in `Ration Plan`
- Log actual feeding in `Feeding Log`
  - Auto-calculates `variance_kg` against selected ration plan

### Breeding Operations

- Capture service attempts in `Breeding Event`
  - Auto-calculates `expected_calving = event_date + 280 days`
- Register births in `Calving Record`

### Operations & Maintenance

- Register assets in `Equipment`
- Log services in `Maintenance Log`
- Track monthly utilities in `Utility Log`

### Finance & Compliance

- Record income in `Dairy Income Entry`
- Record costs in `Dairy Expense Entry`
- Track movement trail in `Animal Movement Record`

## Phase C: Monitoring and Decision-Making

Use reports and dashboard for control:

- Herd:
  - `Herd Summary Report`
- Milk:
  - `Daily Milk Production Report`
  - `Milk Dispatch & Revenue Report`
  - `Milk Board Compliance Report`
- Breeding:
  - `Breeding Performance Report`
- Health:
  - `Animal Health History Report`
  - `Vaccination Due Report`
- Feed:
  - `Feed Cost Per Litre Report`
- Operations:
  - `Equipment Maintenance Due Report`
- Finance:
  - `Profit & Loss Summary Report`
  - `Cost Per Animal Per Month`
- Compliance:
  - `Herd Traceability Report`

## DocTypes in This App

- `Animal`
- `Animal Breed`
- `Pen`
- `Parlour`
- `Bulk Tank`
- `Milk Recording`
- `Bulk Tank Log`
- `Semen Batch`
- `Breeding Event`
- `Calving Record`
- `Disease`
- `Health Event`
- `Vaccination Schedule`
- `Feed Inventory`
- `Ration Plan`
- `Feeding Log`
- `Equipment`
- `Maintenance Log`
- `Utility Log`
- `Dairy Income Entry`
- `Dairy Expense Entry`
- `Animal Movement Record`

## Reports in This App

- `Herd Summary Report`
- `Daily Milk Production Report`
- `Milk Dispatch & Revenue Report`
- `Breeding Performance Report`
- `Animal Health History Report`
- `Vaccination Due Report`
- `Feed Cost Per Litre Report`
- `Equipment Maintenance Due Report`
- `Profit & Loss Summary Report`
- `Cost Per Animal Per Month`
- `Milk Board Compliance Report`
- `Herd Traceability Report`

## Key Calculations Implemented

- `Breeding Event.expected_calving`: +280 days from service date
- `Health Event.milk_safe_date`: +withdrawal days from event date
- `Feeding Log.variance_kg`: actual qty - planned qty
- Report-level formulas (examples):
  - Dispatch revenue
  - Net P/L by period
  - Feed cost per litre
  - SCC compliance flags
  - Days to service / days overdue

## Developer Notes

- Fixtures:
  - `Custom HTML Block` fixture includes `Dairy Workspace Hub`
- Method overrides:
  - `frappe.desk.query_report.run` mapped in `hooks.py`
- Patches:
  - `patches.txt` includes `dairy_management.patches.v15_0.rename_dairy_report_ids`

## Common Commands

```bash
# apply schema, report and patch updates
bench --site <your-site> migrate

# rebuild JS/CSS for dashboard changes
bench build --app dairy_management

# clear cache if desk still shows old routes
bench --site <your-site> clear-cache
```

## License

MIT
