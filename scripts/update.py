"""Pull the latest Freddie Mac PMMS weekly averages and write rate.json.

Primary source: Freddie Mac's published history file. Backup: the same
series as republished by the St. Louis Fed (FRED, MORTGAGE30US / MORTGAGE15US).
"""
import csv, io, json, sys, urllib.request
from datetime import datetime, timezone

UA = {"User-Agent": "Mozilla/5.0 (rate feed for a CMA tool; github.com/grahamgrouphawaii/mortgage-rate)"}

def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return r.read().decode("utf-8-sig")

def from_freddie():
    rows = [r for r in csv.DictReader(io.StringIO(get("https://www.freddiemac.com/pmms/docs/PMMS_history.csv"))) if (r.get("pmms30") or "").strip()]
    last = rows[-1]
    week = datetime.strptime(last["date"].strip(), "%m/%d/%Y").date().isoformat()
    return {"rate30": float(last["pmms30"]), "rate15": float(last["pmms15"]) if (last.get("pmms15") or "").strip() else None,
            "week": week, "source": "Freddie Mac Primary Mortgage Market Survey", "url": "https://www.freddiemac.com/pmms"}

def from_fred():
    def last(series):
        rows = [r for r in csv.reader(io.StringIO(get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}")))][1:]
        rows = [r for r in rows if len(r) > 1 and r[1] not in ("", ".")]
        return rows[-1]
    d30, r30 = last("MORTGAGE30US"); _, r15 = last("MORTGAGE15US")
    return {"rate30": float(r30), "rate15": float(r15), "week": d30, "source": "Freddie Mac PMMS via FRED (St. Louis Fed)", "url": "https://fred.stlouisfed.org/series/MORTGAGE30US"}

def main():
    data = None
    for f in (from_freddie, from_fred):
        try:
            data = f(); break
        except Exception as e:
            print(f"{f.__name__} failed: {e}", file=sys.stderr)
    if not data or not (2 < data["rate30"] < 20):
        sys.exit("No usable rate found; leaving rate.json unchanged.")
    try:
        old = json.load(open("rate.json"))
        if old.get("week") == data["week"] and old.get("rate30") == data["rate30"]:
            print("No new week yet."); return
    except FileNotFoundError:
        pass
    data["fetched"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    json.dump(data, open("rate.json", "w"), indent=2); open("rate.json", "a").write("\n")
    print("Updated:", data)

if __name__ == "__main__":
    main()
