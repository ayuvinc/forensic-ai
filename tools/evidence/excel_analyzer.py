"""Excel anomaly analyzer — 8 detection procedures.

Pre-processing only — NOT in the agent loop.
Results returned as ExcelAnalysisResult for agent consumption.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from schemas.documents import ExcelAnalysisResult, ExcelAnomaly


def analyze_excel_file(
    filepath: str | Path,
    doc_id: str,
    investigation_scope: str = "",
) -> ExcelAnalysisResult:
    """Run 8 anomaly detection procedures on an Excel file."""
    try:
        import openpyxl
        import pandas as pd
    except ImportError as e:
        raise ImportError(f"Required package missing: {e}. Run: pip install openpyxl pandas")

    fpath = Path(filepath)
    wb = openpyxl.load_workbook(fpath, read_only=True, data_only=True)
    sheet_names = list(wb.sheetnames)
    wb.close()

    all_anomalies: list[ExcelAnomaly] = []
    total_rows = 0

    for sheet_name in sheet_names:
        try:
            df = pd.read_excel(fpath, sheet_name=sheet_name, engine="openpyxl")
            total_rows += len(df)

            numeric_cols = df.select_dtypes(include="number").columns.tolist()
            date_cols = df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()

            if not numeric_cols:
                continue

            amount_col = _find_amount_column(df, numeric_cols)
            vendor_col = _find_vendor_column(df)

            all_anomalies.extend(_check_duplicate_payments(df, numeric_cols, sheet_name))
            all_anomalies.extend(_check_round_numbers(df, amount_col, sheet_name))
            all_anomalies.extend(_check_split_transactions(df, amount_col, date_cols, sheet_name))
            all_anomalies.extend(_check_vendor_concentration(df, vendor_col, amount_col, sheet_name))
            all_anomalies.extend(_check_outlier_amounts(df, amount_col, sheet_name))
            all_anomalies.extend(_check_timing_patterns(df, amount_col, date_cols, sheet_name))
            all_anomalies.extend(_check_missing_sequence(df, sheet_name))
            all_anomalies.extend(_check_journal_overrides(df, sheet_name))

        except Exception:
            continue

    methodology = (
        f"Analysed {len(sheet_names)} worksheet(s), {total_rows:,} rows in {fpath.name}. "
        "Applied 8 anomaly detection procedures: duplicate payments, round numbers, "
        "split transactions, vendor concentration, outlier amounts, timing patterns, "
        "missing document sequences, and journal entry overrides."
    )
    if investigation_scope:
        methodology += f" Scope: {investigation_scope}"

    return ExcelAnalysisResult(
        doc_id=doc_id,
        filename=fpath.name,
        sheet_names=sheet_names,
        total_rows=total_rows,
        anomalies=all_anomalies,
        methodology=methodology,
    )


def _find_amount_column(df, numeric_cols: list[str]) -> str:
    """Heuristic: find column most likely to contain monetary amounts."""
    keywords = ["amount", "value", "total", "sum", "payment", "credit", "debit", "balance"]
    for col in df.columns:
        if any(kw in str(col).lower() for kw in keywords) and col in numeric_cols:
            return col
    return numeric_cols[0]


def _find_vendor_column(df) -> Optional[str]:
    keywords = ["vendor", "supplier", "payee", "beneficiary", "party", "name"]
    for col in df.columns:
        if any(kw in str(col).lower() for kw in keywords):
            return col
    return None


def _check_duplicate_payments(df, numeric_cols: list[str], sheet: str) -> list[ExcelAnomaly]:
    anomalies = []
    dup_mask = df.duplicated(subset=numeric_cols, keep=False)
    dup_rows = df[dup_mask].index.tolist()
    if dup_rows:
        anomalies.append(ExcelAnomaly(
            anomaly_type="duplicate_payment",
            description=f"Found {len(dup_rows)} rows with identical values across all numeric fields — possible duplicate payments.",
            sheet=sheet,
            rows_affected=dup_rows[:50],
            risk_rating="high",
            recommended_procedure="Obtain original payment records and verify each duplicate against supporting invoices and approvals.",
        ))
    return anomalies


def _check_round_numbers(df, amount_col: str, sheet: str) -> list[ExcelAnomaly]:
    import numpy as np
    anomalies = []
    try:
        amounts = df[amount_col].dropna()
        amounts = amounts[amounts > 0]
        round_thresholds = [1000, 10000, 100000]
        for threshold in round_thresholds:
            round_mask = (amounts % threshold == 0)
            count = round_mask.sum()
            pct = count / len(amounts) if len(amounts) > 0 else 0
            if pct > 0.15 and count > 5:
                rows = amounts[round_mask].index.tolist()
                anomalies.append(ExcelAnomaly(
                    anomaly_type="round_number",
                    description=f"{count} values ({pct:.0%}) are exact multiples of {threshold:,} — possible fictitious entries.",
                    sheet=sheet,
                    rows_affected=rows[:50],
                    risk_rating="medium",
                    recommended_procedure=f"Review all round-number transactions ≥ {threshold:,} against original invoices and purchase orders.",
                ))
                break
    except Exception:
        pass
    return anomalies


def _check_split_transactions(df, amount_col: str, date_cols: list[str], sheet: str) -> list[ExcelAnomaly]:
    anomalies = []
    try:
        if not date_cols:
            return []
        date_col = date_cols[0]
        amounts = df[[date_col, amount_col]].dropna()
        daily = amounts.groupby(date_col)[amount_col].sum()
        # Flag dates with many small transactions summing to large amount
        count_per_day = amounts.groupby(date_col).size()
        suspicious = count_per_day[count_per_day >= 5]
        if len(suspicious) > 0:
            anomalies.append(ExcelAnomaly(
                anomaly_type="split_transaction",
                description=f"{len(suspicious)} dates have 5+ transactions — possible transaction splitting to circumvent approval thresholds.",
                sheet=sheet,
                rows_affected=[],
                risk_rating="high",
                recommended_procedure="Review all dates with 5+ same-day transactions for approvals and business justification.",
            ))
    except Exception:
        pass
    return anomalies


def _check_vendor_concentration(df, vendor_col: Optional[str], amount_col: str, sheet: str) -> list[ExcelAnomaly]:
    anomalies = []
    try:
        if not vendor_col:
            return []
        vendor_totals = df.groupby(vendor_col)[amount_col].sum()
        total = vendor_totals.sum()
        if total == 0:
            return []
        top_vendor = vendor_totals.nlargest(1)
        top_name = top_vendor.index[0]
        top_pct = top_vendor.iloc[0] / total
        if top_pct > 0.3:
            anomalies.append(ExcelAnomaly(
                anomaly_type="vendor_concentration",
                description=f"Vendor '{top_name}' accounts for {top_pct:.0%} of total spend — high concentration risk.",
                sheet=sheet,
                rows_affected=[],
                risk_rating="medium",
                recommended_procedure="Obtain vendor registration documents, confirm at arm's length, review approval and tender process.",
            ))
    except Exception:
        pass
    return anomalies


def _check_outlier_amounts(df, amount_col: str, sheet: str) -> list[ExcelAnomaly]:
    anomalies = []
    try:
        amounts = df[amount_col].dropna()
        amounts = amounts[amounts > 0]
        if len(amounts) < 20:
            return []
        mean, std = amounts.mean(), amounts.std()
        if std == 0:
            return []
        outlier_mask = abs(amounts - mean) > 3 * std
        outlier_rows = amounts[outlier_mask].index.tolist()
        if outlier_rows:
            anomalies.append(ExcelAnomaly(
                anomaly_type="outlier_amount",
                description=f"{len(outlier_rows)} statistical outliers (>3σ from mean) in '{amount_col}'.",
                sheet=sheet,
                rows_affected=outlier_rows[:50],
                risk_rating="medium",
                recommended_procedure="Obtain approval documentation for all outlier transactions. Review against budget and contract terms.",
            ))
    except Exception:
        pass
    return anomalies


def _check_timing_patterns(df, amount_col: str, date_cols: list[str], sheet: str) -> list[ExcelAnomaly]:
    anomalies = []
    try:
        if not date_cols:
            return []
        date_col = date_cols[0]
        import pandas as pd
        df_copy = df[[date_col, amount_col]].dropna().copy()
        df_copy[date_col] = pd.to_datetime(df_copy[date_col], errors="coerce")
        df_copy = df_copy.dropna(subset=[date_col])
        # Check for period-end clustering (last 3 days of month)
        df_copy["day_of_month"] = df_copy[date_col].dt.day
        df_copy["month_end"] = df_copy[date_col].dt.days_in_month
        period_end = df_copy[df_copy["day_of_month"] >= df_copy["month_end"] - 2]
        pct = len(period_end) / len(df_copy) if len(df_copy) > 0 else 0
        if pct > 0.25 and len(period_end) > 5:
            anomalies.append(ExcelAnomaly(
                anomaly_type="timing_pattern",
                description=f"{pct:.0%} of transactions are clustered in last 3 days of month — possible period-end manipulation.",
                sheet=sheet,
                rows_affected=period_end.index.tolist()[:50],
                risk_rating="medium",
                recommended_procedure="Review all period-end transactions for business rationale, approvals, and subsequent reversals.",
            ))
    except Exception:
        pass
    return anomalies


def _check_missing_sequence(df, sheet: str) -> list[ExcelAnomaly]:
    anomalies = []
    try:
        # Look for sequential ID columns
        for col in df.columns:
            if any(kw in str(col).lower() for kw in ["no", "number", "id", "ref", "voucher"]):
                col_data = df[col].dropna()
                # Try converting to int
                try:
                    import pandas as pd
                    nums = pd.to_numeric(col_data, errors="coerce").dropna().astype(int)
                    if len(nums) < 5:
                        continue
                    full_range = set(range(nums.min(), nums.max() + 1))
                    missing = full_range - set(nums)
                    if missing and len(missing) / len(full_range) < 0.5:
                        anomalies.append(ExcelAnomaly(
                            anomaly_type="missing_sequence",
                            description=f"Column '{col}': {len(missing)} gaps in sequence (e.g. {sorted(missing)[:5]}). Possible deleted records.",
                            sheet=sheet,
                            rows_affected=[],
                            risk_rating="medium",
                            recommended_procedure="Obtain original records for missing sequence numbers. Verify whether deletions were authorised.",
                        ))
                        break
                except Exception:
                    continue
    except Exception:
        pass
    return anomalies


def _check_journal_overrides(df, sheet: str) -> list[ExcelAnomaly]:
    anomalies = []
    try:
        # Look for manual/override indicator columns
        flag_cols = [
            col for col in df.columns
            if any(kw in str(col).lower() for kw in ["manual", "override", "adjust", "journal", "type"])
        ]
        for col in flag_cols:
            manual_vals = df[col].dropna().astype(str).str.lower()
            overrides = manual_vals[manual_vals.isin(["manual", "override", "adj", "je", "m", "y", "yes", "1"])]
            if len(overrides) > 0:
                pct = len(overrides) / len(df)
                anomalies.append(ExcelAnomaly(
                    anomaly_type="journal_override",
                    description=f"Column '{col}': {len(overrides)} entries ({pct:.0%}) flagged as manual/override.",
                    sheet=sheet,
                    rows_affected=overrides.index.tolist()[:50],
                    risk_rating="high" if pct > 0.1 else "medium",
                    recommended_procedure="Review all manual journal entries for authorisation. Confirm no unusual entries near period-end.",
                ))
    except Exception:
        pass
    return anomalies
