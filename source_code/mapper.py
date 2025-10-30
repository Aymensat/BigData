#!/usr/bin/env python3
import sys
import csv
import re

# We'll match whole words: jew, jews, jewish (case-insensitive)
KEYWORDS = re.compile(r'\b(jew|jews|jewish)\b', re.IGNORECASE)

def safe_int(x):
    try:
        return int(x)
    except:
        return 0

def main():
    reader = csv.reader(sys.stdin)
    # try to skip header if present
    header = next(reader, None)

    # If header exists and looks like 'subreddit' etc, we skip it.
    if header and len(header) >= 1 and header[0].lower() == 'subreddit':
        pass
    else:
        # the first row was data; process it
        if header:
            row = header
            if len(row) >= 4:
                process_row(row)

    for row in reader:
        if not row or len(row) < 4:
            # skip malformed or very short rows
            continue
        process_row(row)

def process_row(row):
    # Expected layout: [subreddit, body, controversiality, score]
    subreddit = row[0].strip() if len(row) > 0 else "UNKNOWN"
    body = row[1] if len(row) > 1 else ""
    cont = row[2] if len(row) > 2 else "0"
    score = row[3] if len(row) > 3 else "0"

    if not body:
        return

    if KEYWORDS.search(body):
        try:
            controversiality = safe_int(cont)
            score_val = safe_int(score)
        except Exception:
            controversiality = 0
            score_val = 0

        up = 1 if score_val > 0 else 0
        down = 1 if score_val < 0 else 0
        total = 1
        # Emit: subreddit \t controversiality \t up \t down \t total
        print(f"{subreddit}\t{controversiality}\t{up}\t{down}\t{total}")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
import sys
import csv
import re

# We'll match whole words: jew, jews, jewish (case-insensitive)
KEYWORDS = re.compile(r'\b(jew|jews|jewish)\b', re.IGNORECASE)

def safe_int(x):
    try:
        return int(x)
    except:
        return 0

def main():
    reader = csv.reader(sys.stdin)
    # try to skip header if present
    header = next(reader, None)

    # If header exists and looks like 'subreddit' etc, we skip it.
    if header and len(header) >= 1 and header[0].lower() == 'subreddit':
        pass
    else:
        # the first row was data; process it
        if header:
            row = header
            if len(row) >= 4:
                process_row(row)

    for row in reader:
        if not row or len(row) < 4:
            # skip malformed or very short rows
            continue
        process_row(row)

def process_row(row):
    # Expected layout: [subreddit, body, controversiality, score]
    subreddit = row[0].strip() if len(row) > 0 else "UNKNOWN"
    body = row[1] if len(row) > 1 else ""
    cont = row[2] if len(row) > 2 else "0"
    score = row[3] if len(row) > 3 else "0"

    if not body:
        return

    if KEYWORDS.search(body):
        try:
            controversiality = safe_int(cont)
            score_val = safe_int(score)
        except Exception:
            controversiality = 0
            score_val = 0

        up = 1 if score_val > 0 else 0
        down = 1 if score_val < 0 else 0
        total = 1
        # Emit: subreddit \t controversiality \t up \t down \t total
        print(f"{subreddit}\t{controversiality}\t{up}\t{down}\t{total}")

if __name__ == "__main__":
    main()

