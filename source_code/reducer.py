#!/usr/bin/env python3
import sys

def emit(subreddit, total_mentions, sum_contro, sum_up, sum_down):
    if total_mentions > 0:
        pct_contro = (sum_contro / total_mentions) * 100
        pct_up = (sum_up / total_mentions) * 100
        pct_down = (sum_down / total_mentions) * 100
    else:
        pct_contro = pct_up = pct_down = 0.0
    # TSV output: subreddit \t total \t pct_contro \t pct_up \t pct_down
    print(f"{subreddit}\t{total_mentions}\t{pct_contro:.1f}\t{pct_up:.1f}\t{pct_down:.1f}")

def main():
    current = None
    total_mentions = sum_contro = sum_up = sum_down = 0

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        parts = line.split('\t')
        if len(parts) < 5:
            # malformed line
            continue
        subreddit, cont_s, up_s, down_s, tot_s = parts[:5]
        try:
            cont = int(cont_s); up = int(up_s); down = int(down_s); tot = int(tot_s)
        except:
            # skip bad lines
            continue

        if current == subreddit:
            total_mentions += tot
            sum_contro += cont
            sum_up += up
            sum_down += down
        else:
            if current is not None:
                emit(current, total_mentions, sum_contro, sum_up, sum_down)
            current = subreddit
            total_mentions = tot
            sum_contro = cont
            sum_up = up
            sum_down = down

    # last key
    if current is not None:
        emit(current, total_mentions, sum_contro, sum_up, sum_down)

if __name__ == "__main__":
    main()

