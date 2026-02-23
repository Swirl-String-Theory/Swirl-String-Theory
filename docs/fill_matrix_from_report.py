"""Fill SST_v2_matrix_all_papers_with_indices.csv from paper_rating_full_report.md table."""
import csv
import re

# Report table data: (SLV, TRC, NWO, CPR, FCP, ES, RC, PEC, Total, Role) in order SST-66 down to SST-00
REPORT_ROWS = [
    (4, 4, 5, 4, 3, 3, 3, 3, 29, "Bridge"),
    (4, 4, 4, 5, 3, 3, 4, 4, 31, "Bridge"),
    (5, 4, 4, 5, 3, 4, 4, 3, 32, "Bridge"),
    (4, 4, 5, 5, 2, 2, 3, 3, 28, "Bridge"),
    (3, 4, 3, 4, 3, 3, 4, 4, 28, "Support"),
    (5, 5, 4, 4, 3, 5, 5, 4, 35, "Anchor"),
    (5, 5, 4, 5, 4, 5, 5, 5, 38, "Anchor"),
    (4, 4, 4, 5, 3, 3, 4, 4, 34, "Bridge"),
    (4, 4, 4, 3, 4, 4, 4, 4, 31, "Bridge"),
    (3, 4, 3, 3, 3, 4, 5, 4, 29, "Support"),
    (5, 4, 4, 3, 3, 4, 5, 4, 32, "Bridge"),
    (4, 4, 4, 4, 3, 3, 3, 4, 29, "Bridge"),
    (5, 4, 4, 4, 5, 4, 4, 4, 34, "Anchor/Constraint"),
    (3, 3, 3, 3, 2, 2, 3, 3, 22, "Support (high-risk)"),
    (4, 3, 3, 4, 2, 3, 4, 4, 27, "Bridge/Support"),
    (4, 4, 4, 4, 4, 4, 4, 4, 32, "Anchor/Bridge"),
    (4, 4, 4, 4, 3, 3, 3, 3, 28, "Support/Bridge"),
    (4, 4, 4, 4, 4, 4, 4, 4, 32, "Bridge (redundant)"),
    (4, 4, 4, 4, 3, 4, 4, 4, 31, "Bridge"),
    (3, 5, 2, 2, 1, 4, 5, 5, 27, "Auxiliary"),
    (3, 3, 4, 5, 2, 2, 2, 3, 24, "Capstone"),
    (5, 5, 2, 5, 3, 5, 5, 4, 34, "Infrastructure Anchor"),
    (4, 3, 3, 3, 2, 4, 4, 4, 27, "Support"),
    (4, 5, 3, 3, 3, 4, 4, 5, 31, "Bridge"),
    (4, 4, 2, 3, 2, 5, 5, 5, 30, "Support"),
    (3, 4, 2, 3, 2, 2, 3, 4, 23, "Support"),
    (5, 4, 2, 5, 3, 4, 5, 4, 32, "Anchor (Infrastructure)"),
    (4, 3, 4, 3, 4, 2, 3, 4, 27, "Support"),
    (4, 4, 4, 4, 3, 3, 3, 4, 29, "Bridge"),
    (5, 5, 3, 5, 4, 5, 5, 5, 37, "Anchor (Methods)"),
    (4, 4, 3, 4, 4, 3, 4, 3, 29, "Bridge/Constraint"),
    (5, 4, 4, 4, 4, 4, 3, 4, 32, "Anchor/Bridge"),
    (4, 3, 4, 5, 3, 2, 2, 3, 26, "Capstone"),
    (2, 3, 3, 5, 2, 1, 1, 3, 20, "Internal Canon"),
    (4, 4, 3, 5, 3, 4, 4, 4, 31, "Bridge"),
    (4, 5, 4, 4, 4, 4, 4, 4, 33, "Anchor/Constraint"),
    (4, 4, 5, 5, 2, 3, 3, 4, 30, "Bridge/Foundation"),
    (3, 4, 4, 2, 4, 1, 2, 4, 24, "Internal/Applied"),
    (2, 3, 4, 3, 2, 1, 2, 3, 20, "Internal/High-risk"),
    (4, 4, 4, 5, 2, 3, 2, 3, 27, "Support"),
    (5, 5, 4, 5, 4, 4, 4, 4, 35, "Anchor"),
    (4, 4, 5, 5, 3, 3, 4, 5, 33, "Bridge / Anchor"),
    (4, 5, 3, 5, 3, 3, 4, 5, 32, "Bridge / Reference"),
    (4, 5, 4, 5, 3, 3, 4, 4, 32, "Infrastructure Anchor"),
    (5, 4, 4, 5, 3, 4, 4, 4, 33, "Bridge / Mini-Anchor"),
    (4, 4, 4, 5, 3, 2, 3, 3, 28, "Capstone / Bridge"),
    (3, 3, 4, 5, 2, 2, 3, 4, 26, "Capstone / Bridge"),
    (5, 4, 4, 4, 4, 3, 4, 4, 32, "Bridge"),
    (3, 3, 4, 4, 3, 2, 2, 3, 24, "Internal / Research"),
    (5, 5, 4, 4, 4, 5, 5, 4, 36, "Anchor"),
    (3, 3, 3, 3, 4, 1, 2, 4, 23, "Internal"),
    (3, 3, 4, 3, 2, 2, 3, 3, 23, "Support / High-risk"),
    (4, 4, 3, 4, 3, 3, 4, 4, 29, "Bridge"),
    (3, 5, 2, 5, 4, 2, 5, 5, 31, "Bridge"),
    (5, 5, 3, 4, 5, 4, 5, 4, 35, "Anchor"),
    (5, 5, 3, 5, 4, 5, 5, 4, 36, "Anchor"),
    (4, 4, 4, 5, 3, 4, 4, 4, 32, "Bridge"),
    (5, 5, 3, 5, 4, 5, 5, 5, 37, "Anchor"),
    (4, 4, 4, 5, 3, 4, 4, 4, 32, "Bridge"),
    (4, 3, 3, 4, 2, 3, 4, 4, 27, "Bridge"),
    (2, 2, 3, 4, 1, 1, 2, 3, 18, "Internal"),
    (3, 2, 3, 4, 2, 1, 2, 2, 19, "Internal"),
    (3, 2, 4, 5, 2, 2, 3, 3, 24, "Infrastructure"),
    (5, 5, 3, 5, 3, 5, 5, 5, 36, "Anchor"),
    (4, 4, 5, 5, 4, 3, 4, 3, 32, "Capstone"),
]

CSV_PATH = "SST_v2_matrix_all_papers_with_indices.csv"

def main():
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
    header = rows[0]
    out_rows = [header]
    for i, data_row in enumerate(rows[1:], start=1):
        if i > len(REPORT_ROWS):
            out_rows.append(data_row)
            continue
        slv, trc, nwo, cpr, fcp, es, rc, pec, total, role = REPORT_ROWS[i - 1]
        # Paper, SLV, TRC, NWO, CPR, FCP_E, FCP_T, ES_Now, ES_Future, RC, RCL, ORC, RDR, DCP, MRS, PEC, Kill, Total, Role_Vector, then formulas
        paper = data_row[0]
        formulas = data_row[19:24] if len(data_row) > 19 else ["", "", "", "", ""]
        new_row = [
            paper,
            slv, trc, nwo, cpr,
            fcp, "", es, "", rc,  # FCP_E, FCP_T(empty), ES_Now, ES_Future(empty), RC
            "", "", "", "", "", "",  # RCL, ORC, RDR, DCP, MRS, Kill(empty)
            pec, "", total, role.strip(),  # PEC, Kill, Total, Role_Vector
        ] + formulas
        out_rows.append(new_row)
    with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(out_rows)
    print(f"Filled {len(REPORT_ROWS)} rows in {CSV_PATH}")

if __name__ == "__main__":
    main()
