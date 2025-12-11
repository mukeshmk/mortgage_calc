import os
import pandas as pd
from typing import List, Dict, Any

def export_reports(results: List[Dict[str, Any]], output_dir: str):
    """
    Generates CSV for cheapest scenario and Excel for comparison.
    """
    if not results:
        print("No results to export.")
        return

    sorted_by_total_int = sorted(results, key=lambda x: x['lifetime_interest'])
    cheapest = sorted_by_total_int[0]
    
    # Ensure output dir exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # CSV Export
    if 'schedule' in cheapest:
        df_cheapest = pd.DataFrame(cheapest['schedule'])
        csv_path = os.path.join(output_dir, "mortgage_schedule.csv")
        df_cheapest.to_csv(csv_path, index=False)
        print(f"[{'CSV Export':^20}] Saved to {csv_path}")

    # Excel Comparison
    # Filter out results that don't have schedules
    all_schedules = {r['name']: pd.DataFrame(r['schedule']) for r in results if 'schedule' in r}
    
    if not all_schedules:
        return

    merged = None
    for name, df in all_schedules.items():
        if df.empty: continue
        temp = df[['Month', 'Rate (%)']].copy()
        temp.columns = ['Month', f'Rate_{name}']
        if merged is None:
            merged = temp
        else:
            merged = pd.merge(merged, temp, on='Month', how='outer')
            
    if merged is None:
        return

    rate_cols = [c for c in merged.columns if c.startswith('Rate_')]
    if not rate_cols:
        return

    merged['diff'] = merged[rate_cols].max(axis=1) != merged[rate_cols].min(axis=1)
    diff_months = merged[merged['diff']]['Month'].tolist()
    
    excel_path = os.path.join(output_dir, "scenario_comparison.xlsx")
    
    if not diff_months:
        print(f"[{'Excel Export':^20}] No rate differences found. Skipping.")
    else:
        min_month = min(diff_months)
        max_month = max(diff_months)
        print(f"[{'Excel Export':^20}] Differing Period: Month {min_month} to {max_month}. Exporting...")
        
        with pd.ExcelWriter(excel_path) as writer:
            for name, df in all_schedules.items():
                mask = (df['Month'] >= min_month) & (df['Month'] <= max_month)
                filtered_df = df[mask]
                
                sheet_name = name.replace("Scenario -> ", "").replace("Rate ", "").replace("%", "")[:30]
                # invalid chars
                for ch in ['[', ']', ':', '*', '?', '/', '\\']:
                    sheet_name = sheet_name.replace(ch, '')
                
                filtered_df.to_excel(writer, sheet_name=sheet_name, index=False)
        print(f"[{'Excel Export':^20}] Saved to {excel_path}")
