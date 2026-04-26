# Dairy Management User Guide

This guide is for farm staff and supervisors.
It explains what to enter daily, weekly, and monthly in the Dairy Management app.

---

## 1) Quick Start

1. Login to ERPNext.
2. Open workspace: `Dairy Management`.
3. Use section cards/links for:
   - Masters
   - Daily Entries
   - Reports
   - Dashboard

**Screenshot placeholder:**  
`[Insert screenshot: Dairy Management workspace home]`

---

## 2) One-Time Setup (Masters)

Ask admin/supervisor to create these first:

- `Animal Breed`
- `Pen`
- `Animal`
- `Parlour`
- `Bulk Tank`
- `Disease`
- `Semen Batch`
- `Feed Inventory` items (linked to ERPNext Item)
- `Equipment`

**Screenshot placeholder:**  
`[Insert screenshot: Example Animal master form]`

---

## 3) Daily Data Entry (Most Important)

## A. Milk Recording

Open: `Milk Recording` -> New

Fill:
- `recording_date`
- `animal`
- `session` (Morning/Evening/Midday)
- `yield_litres`
- optional quality fields (`fat_percent`, `protein_percent`, `scc`)

Save.

Repeat for each animal and session.

**Screenshot placeholder:**  
`[Insert screenshot: Milk Recording filled form]`

## B. Bulk Tank Log

Open: `Bulk Tank Log` -> New

Fill:
- `log_date`
- `tank`
- `quantity_litres`
- `temperature_c`
- if dispatched: `dispatched`, `dispatch_litres`, `buyer`, `price_per_litre`

Save.

**Screenshot placeholder:**  
`[Insert screenshot: Bulk Tank Log with dispatch fields]`

## C. Feeding Log

Open: `Feeding Log` -> New

Fill:
- `log_date`
- `pen`
- `feed_item`
- `qty_kg`
- `cost` (if known)
- `ration_plan` (if applicable)

Save.

Note: `variance_kg` auto-calculates when ration plan is selected.

**Screenshot placeholder:**  
`[Insert screenshot: Feeding Log entry]`

---

## 4) Health and Vaccination

## A. Health Event

Use when animal is sick, injured, or checked.

Fill:
- `animal`, `event_date`, `event_type`
- diagnosis/treatment/medication as needed
- `withdrawal_days` if medicine affects milk

Note: `milk_safe_date` auto-calculates.

## B. Vaccination Schedule

Use for planned and completed vaccines.

Fill:
- `vaccine_name`, `scheduled_date`
- `animal` or `herd_group`
- `administered_date`, `next_due` when completed

**Screenshot placeholder:**  
`[Insert screenshot: Health Event and Vaccination forms]`

---

## 5) Breeding and Calving

## A. Breeding Event

Fill:
- `animal`, `event_date`, `method`
- optional `semen_batch` or `bull`
- update `result` when pregnancy test is done

Note: `expected_calving` auto-calculates.

## B. Calving Record

Fill:
- `dam`
- `calving_date`
- `calf`
- `calving_ease`, `calf_sex`

**Screenshot placeholder:**  
`[Insert screenshot: Breeding Event and Calving Record]`

---

## 6) Finance Entries

## A. Dairy Income Entry

Use for milk sale, calf sale, subsidy, etc.

Fill:
- `entry_date`
- `income_type`
- `amount`
- optional `customer`, `quantity`, `rate`, `invoice`

## B. Dairy Expense Entry

Use for feed, veterinary, labour, utilities, etc.

Fill:
- `entry_date`
- `expense_category`
- `description`
- `amount`
- optional `supplier`, `invoice`, `cost_centre`

**Screenshot placeholder:**  
`[Insert screenshot: Income and Expense entry forms]`

---

## 7) Compliance and Movement

## Animal Movement Record

Use for purchase, sale, transfer, death movement tracking.

Fill:
- `movement_date`
- `animal`
- `movement_type`
- optional `from_location`, `to_location`, `permit_no`, `authorized_by`

**Screenshot placeholder:**  
`[Insert screenshot: Animal Movement Record form]`

---

## 8) Reports to Check Regularly

Daily:
- `Daily Milk Production Report`
- `Milk Board Compliance Report`
- `Vaccination Due Report`

Weekly:
- `Feed Cost Per Litre Report`
- `Animal Health History Report`
- `Equipment Maintenance Due Report`

Monthly:
- `Profit & Loss Summary Report`
- `Cost Per Animal Per Month`
- `Breeding Performance Report`
- `Herd Traceability Report`

**Screenshot placeholder:**  
`[Insert screenshot: Query Report screen with filters]`

---

## 9) Dashboard Use

Open: `/app/herd-summary-report`

What you see:
- KPI cards (animal count, lactating count, average weight)
- Apex charts for all Dairy Management reports
- Quick link to each report

If chart not loading:
1. Click `Refresh`
2. Reload page
3. Inform admin if issue continues

**Screenshot placeholder:**  
`[Insert screenshot: Dairy Reports Dashboard page]`

---

## 10) Data Entry Rules (Important)

- Always select correct `Date`.
- Do not leave mandatory fields empty.
- Use correct `Animal` and `Pen` to avoid wrong reports.
- For medicine cases, always fill withdrawal details.
- For sales/expenses, always record `amount`.

---

## 11) Common Mistakes and Fix

- Wrong animal selected:
  - Cancel/amend entry immediately (as per your process).
- Missing session in milk entry:
  - Create correct entry for missed session.
- Vaccination overdue list too high:
  - Update `administered_date` and `next_due`.
- Report mismatch:
  - Check if source entries for that date are completed.

---

## 12) Supervisor Checklist

End of day:
- [ ] Milk sessions complete
- [ ] Bulk dispatch entries complete
- [ ] Feed logs complete
- [ ] Sick animals recorded

End of week:
- [ ] Health and vaccination review
- [ ] Equipment due checks
- [ ] Feed cost trend review

End of month:
- [ ] Income and expense entries complete
- [ ] Profit/loss reviewed
- [ ] Per-animal margin reviewed

---
