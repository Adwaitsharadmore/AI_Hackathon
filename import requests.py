import requests

def get_all_courses(api_url, headers):
    courses = []
    while api_url:
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            courses.extend(response.json())
            links = response.links
            api_url = links['next']['url'] if 'next' in links else None
        else:
            print("Failed to retrieve courses")
            break
    return courses

def list_courses(courses):
    for course in courses:
        print(f"Course ID: {course['id']}, Course Name: {course.get('name', 'No Course Name Available')}")

def user_select_courses(courses):
    selected_course_ids = input("Enter the Course IDs of the courses you're interested in, separated by commas: ").split(',')
    selected_course_ids = [id.strip() for id in selected_course_ids]
    return [course for course in courses if str(course['id']) in selected_course_ids]

def get_course_data(selected_courses, headers, api_base_url):
    for course in selected_courses:
        print(f"\nFetching data for Course ID: {course['id']}, Course Name: {course.get('name', 'No Course Name Available')}")
        # Fetch assignments for the course
        assignments_url = f"{api_base_url}/courses/{course['id']}/assignments"
        assignments_response = requests.get(assignments_url, headers=headers)
        
        if assignments_response.status_code == 200:
            assignments = assignments_response.json()
            if assignments:
                print(f"Assignments for {course.get('name', 'No Course Name Available')}:")
                for assignment in assignments:
                    print(f"- {assignment.get('name')} (Due: {assignment.get('due_at', 'No due date')})")
            else:
                print("No assignments found.")
        else:
            print(f"Failed to fetch assignments for course {course.get('name', 'No Course Name Available')}")


# Main script execution starts here
api_base_url = "https://canvas.asu.edu/api/v1"
api_url = f"{api_base_url}/courses?per_page=100"
api_key = "7236~S4hTI1YNv5PncjZyzeEDNvSaCbgl7Hnm4ZCluNtzXIjC6BmiinQioEalgLcYFw2C"
headers = {"Authorization": "Bearer " + api_key}

all_courses = get_all_courses(api_url, headers)
list_courses(all_courses)

selected_courses = user_select_courses(all_courses)
get_course_data(selected_courses, headers, api_base_url)  # Corrected line
