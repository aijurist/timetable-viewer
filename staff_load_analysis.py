import json
import os

def normalize_day(day_str):
    day_map = {
        "mon": "monday",
        "tue": "tuesday",
        "wed": "wednesday",
        "thu": "thursday",
        "thur": "thursday",
        "fri": "friday",
        "sat": "saturday",
        "sun": "sunday",
        "monday": "monday",
        "tuesday": "tuesday",
        "wednesday": "wednesday",
        "thursday": "thursday",
        "friday": "friday",
        "saturday": "saturday",
        "sunday": "sunday"
    }
    return day_map.get(day_str.lower(), day_str.lower())

def is_morning_slot(time_str):
    # Morning: 8-10 AM
    # Times like "8:00 - 8:50", "9:00 - 9:50", or Lab "8:00 - 9:40"
    if not time_str: return False
    start_time = time_str.split('-')[0].strip()
    return start_time.startswith("8:") or start_time.startswith("08:") or start_time.startswith("9:") or start_time.startswith("09:")

def is_evening_slot(time_str):
    # Evening: 3-5 PM
    # Times like "3:00 - 3:50", "4:00 - 4:50", "3:00 - 4:40"
    # Note: 3 PM is 15:00, but data seems to use "3:00" format.
    if not time_str: return False
    start_time = time_str.split('-')[0].strip()
    return start_time.startswith("3:") or start_time.startswith("03:") or start_time.startswith("4:") or start_time.startswith("04:")

def analyze_staff_load():
    # Load Data
    try:
        with open('data/theory_schedule.json', 'r') as f:
            theory_data = json.load(f)
        with open('data/lab_schedule.json', 'r') as f:
            lab_data = json.load(f)
    except FileNotFoundError as e:
        print(f"Error loading files: {e}")
        return

    # Structure: staff_code -> { name: str, days: { day_name: { morning: bool, evening: bool } } }
    staff_schedule = {}

    # Process Theory
    for entry in theory_data:
        staff_code = str(entry.get('staff_code'))
        # Skip if no staff code or generic placeholder if any (checking simplified)
        if not staff_code or staff_code == "None": continue
        
        staff_name = entry.get('teacher_name', 'Unknown')
        day = normalize_day(entry.get('day', ''))
        time_slot = entry.get('time_slot', '')

        if staff_code not in staff_schedule:
            staff_schedule[staff_code] = {'name': staff_name, 'days': {}}
        
        if day not in staff_schedule[staff_code]['days']:
            staff_schedule[staff_code]['days'][day] = {'morning': False, 'evening': False}

        if is_morning_slot(time_slot):
            staff_schedule[staff_code]['days'][day]['morning'] = True
        if is_evening_slot(time_slot):
            staff_schedule[staff_code]['days'][day]['evening'] = True

    # Process Lab
    for entry in lab_data:
        staff_code = str(entry.get('staff_code'))
        if not staff_code or staff_code == "None": continue

        staff_name = entry.get('teacher_name', 'Unknown')
        # Lab uses 'time_range' usually, but let's check keys
        time_slot = entry.get('time_range', entry.get('time_slot', ''))
        day = normalize_day(entry.get('day', ''))

        if staff_code not in staff_schedule:
            staff_schedule[staff_code] = {'name': staff_name, 'days': {}}
        
        if day not in staff_schedule[staff_code]['days']:
            staff_schedule[staff_code]['days'][day] = {'morning': False, 'evening': False}

        if is_morning_slot(time_slot):
            staff_schedule[staff_code]['days'][day]['morning'] = True
        if is_evening_slot(time_slot):
            staff_schedule[staff_code]['days'][day]['evening'] = True

    # Analysis
    heavy_load_staff_count = 0
    total_staff = len(staff_schedule)
    report_lines = []
    
    report_lines.append("Staff Load Analysis Report")
    report_lines.append("==========================")
    report_lines.append(f"Total Staff Processed: {total_staff}")
    report_lines.append("")
    report_lines.append("Criteria for Heavy Load:")
    report_lines.append("- Has class in Morning (8-10 AM) AND Evening (3-5 PM) on the SAME day.")
    report_lines.append("- This occurs on MORE THAN 3 days.")
    report_lines.append("")
    report_lines.append("Staff with Heavy Load:")
    report_lines.append("----------------------")

    found_any = False
    
    for staff_code, info in staff_schedule.items():
        heavy_days = []
        for day, times in info['days'].items():
            if times['morning'] and times['evening']:
                heavy_days.append(day)
        
        if len(heavy_days) > 2:
            found_any = True
            heavy_load_staff_count += 1
            report_lines.append(f"Name: {info['name']} (Code: {staff_code})")
            report_lines.append(f"  Heavy Days Count: {len(heavy_days)}")
            report_lines.append(f"  Days: {', '.join(sorted(heavy_days))}")
            report_lines.append("")

    if not found_any:
        report_lines.append("No staff members found matching the heavy load criteria.")

    report_lines.append("Summary:")
    report_lines.append(f"Found {heavy_load_staff_count} staff members with heavy load out of {total_staff} total staff.")

    # Write Report
    with open('staff_load_report.txt', 'w') as f:
        f.write('\n'.join(report_lines))
    
    print(f"Analysis complete. Report written to staff_load_report.txt")

if __name__ == "__main__":
    analyze_staff_load()
