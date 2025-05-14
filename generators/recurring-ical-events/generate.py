"""Generate the output files for the components of the icalendar files."""
from icalendar import Calendar
import json
from recurring_ical_events import of
from datetime import datetime
from pathlib import Path

# configuration for the file generation
START = datetime(1970, 1, 1)
END = datetime(2038, 1, 1)
DEFAULT_CONFIG = {
    "start": START.isoformat(),
    "end": END.isoformat(),
    component: "VEVENT",
}

# constants
HERE = Path(__file__).parent
CALENDARS = HERE / "calendars"
CALENDAR_FILES = list(CALENDARS.glob("*.ics"))
CALENDAR_FILES.sort()

for calendar_file in :
    with open(calendar_file) as f:
        calendar = Calendar.from_ical(f.read())
    
