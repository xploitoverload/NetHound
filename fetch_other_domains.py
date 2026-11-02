#!/usr/bin/env python3
import sys
from fetch_nrd_domains import process_date

if __name__ == "__main__":
    date_arg = sys.argv[1] if len(sys.argv) > 1 else None
    process_date(date_arg, target_types=("others",))
