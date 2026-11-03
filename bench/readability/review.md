# Held-out set — human quality review

Mechanical checks passed by `scripts/check_held_out.py`. This file records the human
spot-check of ten items required before P2.04 closes. P2.05 uses this file as its
starting point.

## Spot-check (10 items: 4 mechanics, 3 waves_optics, 3 electricity)

For each row: read the item in `bench/readability/held_out.yaml`, then mark the three
columns. "Wrong misconception" means the item does not actually test the named
misconception_id. Any "N" requires editing the item before P2.05.

| item id | grade-appropriate | tests named misconception | assertion is correct | notes |
|---|---|---|---|---|
| mechanics-001 | | | | |
| mechanics-005 | | | | |
| mechanics-010 | | | | |
| mechanics-015 | | | | |
| waves_optics-002 | | | | |
| waves_optics-008 | | | | |
| waves_optics-014 | | | | |
| electricity-003 | | | | |
| electricity-009 | | | | |
| electricity-016 | | | | |

## Sign-off

- [ ] All spot-check rows have Y in all three columns.
- [ ] Spot-check found no items with hint-style phrasing (would also fail the mechanical check).
- [ ] No item's question_text duplicates a future canonical hint phrase (a judgment call: a
      canonical hint for the same misconception_id must not be a paraphrase of any held-out
      question_text).
- [ ] If any item was rejected, it has been replaced in held_out.yaml and check_held_out.py
      re-run and passed after the replacement.

Reviewer: ______________________  Date reviewed: ______________
