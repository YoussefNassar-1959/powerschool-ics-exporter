#!/usr/bin/env python3
"""
PowerSchool to ICS Calendar Exporter — African Leadership Academy Edition

Automatically extracts your weekly schedule from PowerSchool and exports it as an .ics file.
Just log in → wait for schedule → press ENTER → import to Google Calendar!
"""

import os
import sys
import re
from datetime import datetime, timedelta
from ics import Calendar, Event
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# Default config
POWER_SCHOOL_URL = "https://ala.powerschool.com/guardian/myschedule.html"
TIMEZONE = "Africa/Johannesburg"

# Load user config if exists
if os.path.exists("config.py"):
    sys.path.insert(0, os.getcwd())
    try:
        from config import POWER_SCHOOL_URL, TIMEZONE
        print("✅ Loaded custom config.py")
    except ImportError as e:
        print(f"⚠️  Warning: config.py missing values: {e}")

def parse_time(time_str):
    """Parse '08:00 AM' → datetime.time"""
    time_str = time_str.strip()
    for fmt in ["%I:%M %p", "%H:%M"]:
        try:
            return datetime.strptime(time_str, fmt).time()
        except ValueError:
            continue
    raise ValueError(f"Unrecognized time: {time_str}")

def extract_semester_dates(html_content):
    """Auto-extract semester start/end from embedded JS"""
    start_match = re.search(r"psc_firstDay = parseDate\('(\d{8})'\)", html_content)
    end_match = re.search(r"psc_lastDay = parseDate\('(\d{8})'\)", html_content)
    if start_match and end_match:
        start = start_match.group(1)
        end = end_match.group(1)
        return f"{start[:4]}-{start[4:6]}-{start[6:8]}", f"{end[:4]}-{end[4:6]}-{end[6:8]}"
    # Fallback
    return "2025-08-22", "2025-10-08"

def parse_schedule(html_content):
    """Parse ALA PowerSchool schedule table"""
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table', id='tableStudentSchedMatrix')
    if not table:
        raise ValueError("Schedule table not found")

    # Extract day headers (Monday, Tuesday, etc.)
    header_row = table.find('tr')
    days = []
    for th in header_row.find_all('th')[1:-1]:  # Skip first and last empty columns
        b = th.find('b')
        if b:
            parts = b.get_text().split('\n')
            if len(parts) >= 2:
                day_name = parts[0].strip()
                date_str = parts[1].strip()  # e.g., "09/22/2025"
                days.append((day_name, date_str))

    # Find all class cells (those with class info)
    class_cells = table.find_all('td', class_=lambda x: x and 'scheduleClass' in x)
    classes = []

    for cell in class_cells:
        text = cell.get_text(separator='\n', strip=True)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if len(lines) < 4:
            continue

        class_name = lines[0]
        teacher = lines[1]
        room = lines[2]
        time_range = lines[3]

        # Extract time
        time_match = re.search(r'(\d{1,2}:\d{2}\s*[AP]M)\s*-\s*(\d{1,2}:\d{2}\s*[AP]M)', time_range)
        if not time_match:
            continue
        start_time_str, end_time_str = time_match.groups()

        # Determine day from cell position
        row = cell.find_parent('tr')
        if not row:
            continue
        all_cells = row.find_all('td', recursive=False)
        try:
            idx = all_cells.index(cell)
            day_index = idx - 1  # Adjust for time column
            if 0 <= day_index < len(days):
                day_name, date_str = days[day_index]
                classes.append({
                    'name': class_name,
                    'teacher': teacher,
                    'room': room,
                    'start_time': start_time_str,
                    'end_time': end_time_str,
                    'day': day_name,
                    'date': date_str
                })
        except (ValueError, IndexError):
            continue

    return classes

def main():
    print("🚀 PowerSchool → ICS Exporter (ALA Edition)")
    print("1. A browser will open — log in to PowerSchool")
    print("2. Go to your schedule page if not already there")
    print("3. Wait until your full weekly schedule is visible")
    print("4. Switch back here and press ENTER\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(POWER_SCHOOL_URL)
        input("✅ Press ENTER when your schedule is fully loaded...")

        # Wait for table to stabilize
        try:
            page.wait_for_selector("#tableStudentSchedMatrix", timeout=10000)
        except:
            print("⚠️  Table not found — proceeding anyway...")

        html = page.content()
        browser.close()

    # Auto-detect semester dates
    SEMESTER_START, SEMESTER_END = extract_semester_dates(html)
    print(f"📅 Semester: {SEMESTER_START} to {SEMESTER_END}")

    # Parse schedule
    try:
        classes = parse_schedule(html)
        print(f"✅ Found {len(classes)} class entries")
    except Exception as e:
        print(f"❌ Parsing failed: {e}")
        return

    if not classes:
        print("❌ No classes found. Is the schedule visible?")
        return

    # Build ICS calendar
    cal = Calendar()
    start_date = datetime.strptime(SEMESTER_START, "%Y-%m-%d").date()
    end_date = datetime.strptime(SEMESTER_END, "%Y-%m-%d").date()

    day_to_weekday = {
        "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3,
        "Friday": 4, "Saturday": 5, "Sunday": 6
    }

    for entry in classes:
        weekday = day_to_weekday.get(entry['day'])
        if weekday is None:
            continue

        # Find first occurrence of this weekday on/after semester start
        current = start_date
        while current.weekday() != weekday:
            current += timedelta(days=1)

        # Create weekly recurring events
        while current <= end_date:
            event = Event()
            event.name = entry['name']
            event.description = f"Teacher: {entry['teacher']}\nRoom: {entry['room']}"
            event.location = entry['room']
            event.begin = datetime.combine(current, parse_time(entry['start_time']))
            event.end = datetime.combine(current, parse_time(entry['end_time']))
            event.timezone = TIMEZONE
            cal.events.add(event)
            current += timedelta(weeks=1)

    # Save ICS file
    output_file = "ala_schedule.ics"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(str(cal))

    print(f"\n🎉 Success! Calendar saved to: {os.path.abspath(output_file)}")
    print("\n📥 To import into Google Calendar:")
    print("   1. Go to https://calendar.google.com")
    print("   2. Click ⚙️ Settings → 'Import & export'")
    print("   3. Upload this .ics file")

if __name__ == "__main__":
    main()
