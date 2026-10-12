import sys, io
from pathlib import Path

# Ensure utf-8 output
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from agent import run_agent

class TeeLogger:
    def __init__(self, *files):
        self.files = files
        self.encoding = "utf-8"
    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush()
    def flush(self):
        for f in self.files:
            f.flush()

# Prepare results directories
out_dir1 = Path(__file__).parent / "results"
out_dir2 = Path(__file__).parent.parent / "results"
out_dir1.mkdir(parents=True, exist_ok=True)
out_dir2.mkdir(parents=True, exist_ok=True)

log_f1 = open(out_dir1 / "agent_test.md", "w", encoding="utf-8")
log_f2 = open(out_dir2 / "agent_test.md", "w", encoding="utf-8")

orig_stdout = sys.stdout
sys.stdout = TeeLogger(orig_stdout, log_f1, log_f2)

tasks = [
    (1, "What is the standard annual leave allowance for full-time employees?"),
    (2, "What is the domestic daily meal allowance when traveling, and who must approve expense claims above ₹5,000?"),
    (3, "What is the company policy on employee 401(k) retirement matching?"),
]

for num, q in tasks:
    print(f"\n{'='*60}")
    print(f"TASK {num}: {q}")
    print(f"{'='*60}")
    ans = run_agent(q)
    print(f"\nFINAL ANSWER {num}:\n{ans}")

sys.stdout = orig_stdout
log_f1.close()
log_f2.close()
