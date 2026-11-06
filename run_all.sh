#!/bin/bash
# Re-run the whole project from the raw CSV. Usage (from the project root): bash run_all.sh
set -e
for s in step1_load step2_clean step3_sql step4_eda step5_cohort step6_hypothesis step7_powerbi_export; do
  echo "=== Running $s ==="
  python3 src/$s.py
done
echo "All steps finished OK. See the outputs/ folder."
