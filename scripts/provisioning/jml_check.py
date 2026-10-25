"""Joiner-mover-leaver check for the RCH IAM project.

Compares the HR export with the identity provider export and lists:
- joiners who need an account
- leavers whose account must be disabled within 15 minutes
- movers whose role has changed
"""
import csv
import sys


def load(path):
    with open(path, newline="") as f:
        return {row["employee_id"]: row for row in csv.DictReader(f)}


def main(hr_file, idp_file):
    hr = load(hr_file)
    idp = load(idp_file)

    joiners = [e for e in hr if e not in idp and hr[e]["status"] == "active"]
    leavers = [e for e in idp if e not in hr or hr[e]["status"] == "terminated"]
    movers = [e for e in hr if e in idp and hr[e]["role"] != idp[e]["role"]]

    print(f"Joiners to create: {len(joiners)}")
    for e in joiners:
        print(f"  CREATE  {e}  {hr[e]['role']}")
    print(f"Leavers to disable: {len(leavers)}")
    for e in leavers:
        print(f"  DISABLE {e}")
    print(f"Movers to update: {len(movers)}")
    for e in movers:
        print(f"  UPDATE  {e}  {idp[e]['role']} -> {hr[e]['role']}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python jml_check.py hr_export.csv idp_export.csv")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
