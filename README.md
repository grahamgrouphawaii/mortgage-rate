# Mortgage rate feed

A tiny public file with this week's average 30-year and 15-year fixed mortgage rates, used by Graham Group's CMA tool.

- `rate.json` is the feed. Read it at `https://raw.githubusercontent.com/grahamgrouphawaii/mortgage-rate/main/rate.json`.
- A GitHub Action runs every Thursday afternoon and Friday morning (Hawaii is 5-6 hours behind Eastern), pulls the latest Freddie Mac Primary Mortgage Market Survey (PMMS) numbers, and updates `rate.json` when a new week is out.
- Source: Freddie Mac PMMS, https://www.freddiemac.com/pmms. Backup source: the same series on FRED (St. Louis Fed).

The PMMS is a national average for a 30-year fixed loan with about 20% down and strong credit. A borrower's actual rate will differ.
