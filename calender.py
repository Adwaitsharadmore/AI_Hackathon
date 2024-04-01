import requests
from icalendar import Calendar
from pathlib import Path

def download_calendar_ics(url, local_file_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(local_file_path, 'wb') as file:
            file.write(response.content)
        print("Calendar downloaded successfully.")
        return True
    else:
        print(f"Failed to download calendar. Status code: {response.status_code}")
        return False

def ics_to_text(ics_file_path, output_text_path):
    with open(ics_file_path, 'rb') as file:
        ics_content = file.read()
    
    cal = Calendar.from_ical(ics_content)
    
    with open(output_text_path, 'w') as text_file:
        for component in cal.walk():
            if component.name == "VEVENT":
                summary = component.get('summary')
                start = component.get('dtstart')
                end = component.get('dtend')
                description = component.get('description')

                # Format start and end dates if they are not None
                start_dt = start.dt.strftime('%Y-%m-%d %H:%M:%S') if start else 'Not specified'
                end_dt = end.dt.strftime('%Y-%m-%d %H:%M:%S') if end else 'Not specified'
                
                # Safely handle potentially missing fields
                summary_text = summary if summary else 'No summary'
                description_text = description if description else 'No description'

                text_file.write(f"Event: {summary_text}\nStart: {start_dt}\nEnd: {end_dt}\nDescription: {description_text}\n\n")
    
    print("Calendar events converted to text.")


# Define URLs and file paths
ics_url = 'https://canvas.asu.edu/feeds/calendars/user_atOd71gtPvujCgvxl1axuWSxYeUr3Zy5FHL5DnsR.ics'
local_ics_path = Path('/Users/aryanredhu/hackathon/AI_Hackathon/files')  # Adjust as needed
output_text_path = Path('/Users/aryanredhu/hackathon/AI_Hackathon/files')  # Adjust as needed

# Download and convert
if download_calendar_ics(ics_url, local_ics_path):
    ics_to_text(local_ics_path, output_text_path)
