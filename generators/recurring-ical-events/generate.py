"""Generate the output files for the components of the icalendar files."""
from icalendar import Calendar, Component
from icalendar.tools import to_datetime
from icalendar.timezone import tzid_from_dt
from icalendar.alarms import Alarms
import json
import recurring_ical_events
from datetime import datetime, timezone, date
from pathlib import Path
import re

# configuration for the file generation
START = datetime(1970, 1, 1, tzinfo=timezone.utc)
END = datetime(2038, 1, 1, tzinfo=timezone.utc)

# constants
HERE = Path(__file__).parent
ROOT = HERE.parent.parent
CALENDARS = ROOT / "calendars"
CALENDAR_FILES = list(CALENDARS.glob("**/*.ics"))
CALENDAR_FILES.sort()
RECURRENCES = ROOT / "recurrences"

def date_to_json(dt: date|None) -> dict:
    if date is None:
        return None
    return {
        "iso": dt.isoformat(),
        "utc": to_datetime(dt).astimezone(timezone.utc).isoformat(),
        "tzid": tzid_from_dt(dt) if isinstance(dt, datetime) and dt.tzinfo is not None else None
    }
    

def component_to_json(component: Component):
    """Turn the most important information of a component into a JSON dict."""
    recurrence_id = component.get("recurrence-id", component.start)
    recurrence_datetime = recurrence_id.dt if recurrence_id is not None else None
    result = {
        "start": date_to_json(component.start),
        "recurrence-id": date_to_json(recurrence_datetime),
        "uid": component.get("uid", ""),
        "sequence": component.get("sequence", 0),
    }
    if component.name != "VJOURNAL":
        result["end"] = date_to_json(component.end)
    return result

def get_component(calendar:Calendar, component_name:str):
    result = []
    for component in recurring_ical_events.of(calendar, components=[component_name], skip_bad_series=True).between(START, END):
        result.append(component_to_json(component))
    result.sort(key=lambda c: c["start"]["utc"] + c["start"]["utc"])
    return result

def get_alarms(calendar:Calendar):
    result = []
    try:
        for component in recurring_ical_events.of(calendar, components=["VALARM"], skip_bad_series=True).between(START, END):
            try:
                alarms : Alarms = component.alarms
            except TypeError:
                print("Skipping, see https://github.com/niccokunzmann/python-recurring-ical-events/issues/234")
                continue
            for alarm in alarms.times:
                result.append({
                    "trigger": date_to_json(alarm.trigger),
                    "uid": alarm.alarm.get("uid", ""),
                    "parent": component_to_json(alarm.parent),
                    "acknowledged": not alarm.acknowledged
                })
    except TypeError:
        print("Skipping, see https://github.com/niccokunzmann/python-recurring-ical-events/issues/234")
    result.sort(key=lambda c: c["trigger"]["utc"] + c["trigger"]["utc"])
    return result

for i, calendar_file in enumerate(CALENDAR_FILES):
    with open(calendar_file) as f:
        calendar = Calendar.from_ical(f.read())
    calendar_id = calendar_file.relative_to(CALENDARS)
    if calendar_id.stem.startswith("skip"):
        print("SKIPPING", calendar_id)
        continue
    # print("Generating for calendar:", calendar_id)
    test_id = f"{i:03d}-{calendar_id.stem.replace('_', '-')}"
    print(test_id)
    description = ""
    issue = re.match(r"issue_(\d+)", calendar_id.stem)
    recurrence_file = RECURRENCES / f"{test_id}.json"
    config =  {
        "query": {
            "start": START.isoformat(),
            "end": END.isoformat(),
            "calendar": str(calendar_id),
        },
        "result": {
            "calendar": "",
            "events": get_component(calendar, "VEVENT"),
            "journals": get_component(calendar, "VJOURNAL"),
            "todos": get_component(calendar, "VTODO"),
            "alarms": get_alarms(calendar)
        },
        "description:": description,
    }
    recurrence_file.write_text(json.dumps(config, indent=4, sort_keys=True))
