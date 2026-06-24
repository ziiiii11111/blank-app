#!/usr/bin/env python3
"""Test script to verify cycle day calculation."""

from datetime import date

def get_cycle_day_for_date(target_date, user_records):
    """Calculate the cycle day for a given date based on the latest cycle start date."""
    if not user_records:
        return -1
    
    # Find the latest cycle that should contain or precede the target date
    latest_cycle_start = None
    for record in user_records:
        if record["period_start"] <= target_date:
            if latest_cycle_start is None or record["period_start"] > latest_cycle_start:
                latest_cycle_start = record["period_start"]
    
    if latest_cycle_start is None:
        return -1
    
    return (target_date - latest_cycle_start).days + 1


# Simulate user records based on the JSON data
user_records = [
    {
        "period_start": date(2026, 6, 7),
        "period_end": date(2026, 6, 12),
        "skin_date": date(2026, 6, 23),
        "skin_status": ["Oily"],
    },
    {
        "period_start": date(2026, 6, 23),
        "period_end": date(2026, 6, 27),
        "skin_date": date(2026, 6, 22),
        "skin_status": ["Breakouts"],
    },
]

# Test cases
print("Testing cycle day calculation:")
print(f"Latest cycle start: {user_records[-1]['period_start']}")
print()

# Test 1: Skin record on 6/23 (breakouts)
skin_date_1 = date(2026, 6, 23)
cycle_day_1 = get_cycle_day_for_date(skin_date_1, user_records)
print(f"Test 1 - Skin date: {skin_date_1}")
print(f"  Expected cycle day: 1 (first day of latest cycle 6/23-6/27)")
print(f"  Actual cycle day: {cycle_day_1}")
print(f"  ✓ PASS" if cycle_day_1 == 1 else f"  ✗ FAIL")
print()

# Test 2: Skin record on 6/24
skin_date_2 = date(2026, 6, 24)
cycle_day_2 = get_cycle_day_for_date(skin_date_2, user_records)
print(f"Test 2 - Skin date: {skin_date_2}")
print(f"  Expected cycle day: 2 (second day of latest cycle 6/23-6/27)")
print(f"  Actual cycle day: {cycle_day_2}")
print(f"  ✓ PASS" if cycle_day_2 == 2 else f"  ✗ FAIL")
print()

# Test 3: Old skin record on 6/23 from first cycle (before latest)
# This should use the latest cycle start (6/23), so it should be day 1
# NOT day 17 (6/23 - 6/7 + 1 = 17)
print(f"Test 3 - Verifying old record 6/23 uses latest cycle:")
print(f"  Old period: 6/7-6/12")
print(f"  New period: 6/23-6/27")
print(f"  Old calculation (incorrect): (6/23 - 6/7) + 1 = 17")
print(f"  New calculation (correct): (6/23 - 6/23) + 1 = 1")
print(f"  Actual cycle day using new function: {cycle_day_1}")
print(f"  ✓ PASS" if cycle_day_1 == 1 else f"  ✗ FAIL")
