# built in
import json
import os
import string

# external
from canvasapi import Canvas
from canvasapi.exceptions import ResourceDoesNotExist, Unauthorized

from singlefile import download_page

import dateutil.parser
import jsonpickle
import requests
import yaml


try:
    with open("credentials.yaml", 'r') as f:
        credentials = yaml.full_load(f)
except OSError:
    # Canvas API URL
    API_URL = ""
    # Canvas API key
    API_KEY = ""
    # My Canvas User ID
    USER_ID = 0000000
    # Browser Cookies File
    COOKIES_PATH = ""
else:
    API_URL = credentials["API_URL"]
    API_KEY = credentials["API_KEY"]
    USER_ID = credentials["USER_ID"]
    COOKIES_PATH = credentials["COOKIES_PATH"]

# Directory in which to download course information to (will be created if not
# present)
DL_LOCATION = "./output"
# List of Course IDs that should be skipped (need to be integers)
COURSES_TO_SKIP = [288290, 512033]

DATE_TEMPLATE = "%B %d, %Y %I:%M %p"

# Max PATH length is 260 characters on Windows. 70 is just an estimate for a reasonable max folder name to prevent the chance of reaching the limit
# Applies to modules, assignments, announcements, and discussions
# If a folder exceeds this limit, a "-" will be added to the end to indicate it was shortened ("..." not valid)
MAX_FOLDER_NAME_SIZE = 70

class moduleItemView():
    id = 0
    
    title = ""
    content_type = ""
    
    url = ""
    external_url = ""


class moduleView():
    id = 0

    name = ""
    items = []

    def __init__(self):
        self.items = []


class pageView():
    id = 0

    title = ""
    body = ""
    created_date = ""
    last_updated_date = ""


class topicReplyView():
    id = 0

    author = ""
    posted_date = ""
    body = ""


class topicEntryView():
    id = 0

    author = ""
    posted_date = ""
    body = ""
    topic_replies = []

    def __init__(self):
        self.topic_replies = []


class discussionView():
    id = 0

    title = ""
    author = ""
    posted_date = ""
    body = ""
    topic_entries = []

    url = ""
    amount_pages = 0

    def __init__(self):
        self.topic_entries = []


class submissionView():
    id = 0

    attachments = []
    grade = ""
    raw_score = ""
    submission_comments = ""
    total_possible_points = ""
    attempt = 0
    user_id = "no-id"

    preview_url = ""
    ext_url = ""

    def __init__(self):
        self.attachments = []

class attachmentView():
    id = 0

    filename = ""
    url = ""

class assignmentView():
    id = 0

    title = ""
    description = ""
    assigned_date = ""
    due_date = ""
    submissions = []

    html_url = ""
    ext_url = ""
    updated_url = ""
    
    def __init__(self):
        self.submissions = []


class courseView():
    course_id = 0
    
    term = ""
    course_code = ""
    name = ""
    assignments = []
    announcements = []
    discussions = []
    modules = []

    def __init__(self):
        self.assignments = []
        self.announcements = []
        self.discussions = []
        self.modules = []

def makeValidFilename(input_str):
    if(not input_str):
        return input_str

    # Remove invalid characters
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    input_str = input_str.replace("+"," ") # Canvas default for spaces
    input_str = input_str.replace(":","-")
    input_str = input_str.replace("/","-")
    input_str = "".join(c for c in input_str if c in valid_chars)

    # Remove leading and trailing whitespace
    input_str = input_str.lstrip().rstrip()

    # Remove trailing periods
    input_str = input_str.rstrip(".")

    return input_str

def makeValidFolderPath(input_str):
    # Remove invalid characters
    valid_chars = "-_.()/ %s%s" % (string.ascii_letters, string.digits)
    input_str = input_str.replace("+"," ") # Canvas default for spaces
    input_str = input_str.replace(":","-")
    input_str = "".join(c for c in input_str if c in valid_chars)

    # Remove leading and trailing whitespace, separators
    input_str = input_str.lstrip().rstrip().strip("/").strip("\\")

    # Remove trailing periods
    input_str = input_str.rstrip(".")

    # Replace path separators with OS default
    input_str=input_str.replace("/",os.sep)

    return input_str

def shortenFileName(string, shorten_by) -> str:
    if (not string or shorten_by <= 0):
        return string

    # Shorten string by specified value + 1 for "-" to indicate incomplete file name (trailing periods not allowed)
    string = string[:len(string)-(shorten_by + 1)]

    string = string.rstrip().rstrip(".").rstrip("-")
    string += "-"
    
    return string


def findCourseModules(course, course_view):
    modules_dir = os.path.join(DL_LOCATION, course_view.term,
                               course_view.course_code, "modules")

    # Create modules directory if not present
    if not os.path.exists(modules_dir):
        os.makedirs(modules_dir)

    module_views = []

    try:
        modules = course.get_modules()

        for module in modules:
            module_view = moduleView()

            # ID
            module_view.id = module.id if hasattr(module, "id") else ""

            # Name
            module_view.name = str(module.name) if hasattr(module, "name") else ""

            try:
                # Get module items
                module_items = module.get_module_items()

                for module_item in module_items:
                    module_item_view = moduleItemView()

                    # ID
                    module_item_view.id = module_item.id if hasattr(module_item, "id") else 0

                    # Title
                    module_item_view.title = str(module_item.title) if hasattr(module_item, "title") else ""
                    # Type
                    module_item_view.content_type = str(module_item.type) if hasattr(module_item, "type") else ""

                    # URL
                    module_item_view.url = str(module_item.html_url) if hasattr(module_item, "html_url") else ""
                    # External URL
                    module_item_view.external_url = str(module_item.external_url) if hasattr(module_item, "external_url") else ""

                    if module_item_view.content_type == "File":
                        # If problems arise due to long pathnames, changing module.name to module.id might help
                        # A change would also have to be made in downloadCourseModulePages(api_url, course_view, cookies_path)
                        

                        try:
                            module_file = course.get_file(str(module_item.content_id))
                            if module_file.display_name.lower().endswith('.pdf'):
                                module_name = makeValidFilename(str(module.name))
                                module_name = shortenFileName(module_name, len(module_name) - MAX_FOLDER_NAME_SIZE)
                                module_dir = os.path.join(modules_dir, module_name, "files")
                                # Create directory for current module if not present
                                if not os.path.exists(module_dir):
                                    os.makedirs(module_dir)

                                # Get the file object
                                

                                # Create path for module file download
                                module_file_path = os.path.join(module_dir, makeValidFilename(str(module_file.display_name)))

                                # Download file if it doesn't already exist
                                if not os.path.exists(module_file_path):
                                    module_file.download(module_file_path)
                                else:
                                    print(f'File already exists: {module_file.display_name}')
                            else:
                                print(f"Skipping non-PDF file: {module_file.display_name}")
                        except Exception as e:
                            print("Skipping module file download that gave the following error:")
                            print(e)

                    module_view.items.append(module_item_view)
            except Exception as e:
                print("Skipping module item that gave the following error:")
                print(e)

            module_views.append(module_view)

    except Exception as e:
        print("Skipping entire module that gave the following error:")
        print(e)

    return module_views


def downloadCourseFiles(course, course_view):
    # file full_name starts with "course files"
    dl_dir = os.path.join(DL_LOCATION, course_view.term,
                          course_view.course_code)

    # Create directory if not present
    if not os.path.exists(dl_dir):
        os.makedirs(dl_dir)

    try:
        files = course.get_files()

        for file in files:
            if file.display_name.lower().endswith('.pdf'):
                file_folder=course.get_folder(file.folder_id)
                
                folder_dl_dir=os.path.join(dl_dir, makeValidFolderPath(file_folder.full_name))
                
                if not os.path.exists(folder_dl_dir):
                    os.makedirs(folder_dl_dir)
            
                dl_path = os.path.join(folder_dl_dir, makeValidFilename(str(file.display_name)))

                # Download file if it doesn't already exist
                if not os.path.exists(dl_path):
                    print('Downloading: {}'.format(dl_path))
                    file.download(dl_path)
            else:
                print(f"Skipping non-PDF file: {file.display_name}")        
    except Exception as e:
        print("Skipping file download that gave the following error:")
        print(e)





def getCoursePageUrls(course):
    page_urls = []

    try:
        # Get all pages
        pages = course.get_pages()

        for page in pages:
            if hasattr(page, "url"):
                page_urls.append(str(page.url))
    except Exception as e:
        if e.message != "Not Found":
            print("Skipping page that gave the following error:")
            print(e)

    return page_urls


def findCoursePages(course):
    page_views = []

    try:
        # Get all page URLs
        page_urls = getCoursePageUrls(course)

        for url in page_urls:
            page = course.get_page(url)

            page_view = pageView()

            # ID
            page_view.id = page.id if hasattr(page, "id") else 0

            # Title
            page_view.title = str(page.title) if hasattr(page, "title") else ""
            # Body
            page_view.body = str(page.body) if hasattr(page, "body") else ""
            # Date created
            page_view.created_date = dateutil.parser.parse(page.created_at).strftime(DATE_TEMPLATE) if \
                hasattr(page, "created_at") else ""
            # Date last updated
            page_view.last_updated_date = dateutil.parser.parse(page.updated_at).strftime(DATE_TEMPLATE) if \
                hasattr(page, "updated_at") else ""

            page_views.append(page_view)
    except Exception as e:
        print("Skipping page download that gave the following error:")
        print(e)

    return page_views


def findCourseAssignments(course):
    assignment_views = []

    # Get all assignments
    assignments = course.get_assignments()
    
    try:
        for assignment in assignments:
            # Create a new assignment view
            assignment_view = assignmentView()

            #ID
            assignment_view.id = assignment.id if \
                hasattr(assignment, "id") else ""

            # Title
            assignment_view.title = makeValidFilename(str(assignment.name)) if \
                hasattr(assignment, "name") else ""
            # Description
            assignment_view.description = str(assignment.description) if \
                hasattr(assignment, "description") else ""
            
            # Assigned date
            assignment_view.assigned_date = assignment.created_at_date.strftime(DATE_TEMPLATE) if \
                hasattr(assignment, "created_at_date") else ""
            # Due date
            assignment_view.due_date = assignment.due_at_date.strftime(DATE_TEMPLATE) if \
                hasattr(assignment, "due_at_date") else ""    

            # HTML Url
            assignment_view.html_url = assignment.html_url if \
                hasattr(assignment, "html_url") else ""   
            # External URL
            assignment_view.ext_url = str(assignment.url) if \
                hasattr(assignment, "url") else ""
            # Other URL (more up-to-date)
            assignment_view.updated_url = str(assignment.submissions_download_url).split("submissions?")[0] if \
                hasattr(assignment, "submissions_download_url") else ""

            
            assignment_views.append(assignment_view)
    except Exception as e:
        print("Skipping course assignments that gave the following error:")
        print(e)

    return assignment_views


def findCourseAnnouncements(course):
    announcement_views = []

    try:
        announcements = course.get_discussion_topics(only_announcements=True)

        for announcement in announcements:
            discussion_view = getDiscussionView(announcement)

            announcement_views.append(discussion_view)
    except Exception as e:
        print("Skipping announcement that gave the following error:")
        print(e)

    return announcement_views


def getCourseView(course):
    course_view = courseView()

    # Course ID
    course_view.course_id = course.id if hasattr(course, "id") else 0

    # Course term
    course_view.term = makeValidFilename(course.term["name"] if hasattr(course, "term") and "name" in course.term.keys() else "")

    # Course code
    course_view.course_code = makeValidFilename(course.course_code if hasattr(course, "course_code") else "")

    # Course name
    course_view.name = course.name if hasattr(course, "name") else ""

    print("Working on " + course_view.term + ": " + course_view.name)

    # Course assignments
    print("  Getting assignments")
    course_view.assignments = findCourseAssignments(course)

    # Course announcements
    print("  Getting announcements")
    course_view.announcements = findCourseAnnouncements(course)



    # Course pages
    print("  Getting pages")
    course_view.pages = findCoursePages(course)

    return course_view


def exportAllCourseData(course_view):
    json_str = json.dumps(json.loads(jsonpickle.encode(course_view, unpicklable = False)), indent = 4)

    course_output_dir = os.path.join(DL_LOCATION, course_view.term,
                                     course_view.course_code)

    # Create directory if not present
    if not os.path.exists(course_output_dir):
        os.makedirs(course_output_dir)

    course_output_path = os.path.join(course_output_dir,
                                      course_view.course_code + ".json")

    with open(course_output_path, "w") as out_file:
        out_file.write(json_str)

def downloadCourseHTML(api_url, cookies_path):
    if(cookies_path == ""):
        return

    course_dir = DL_LOCATION

    if not os.path.exists(course_dir):
        os.makedirs(course_dir)

    course_list_path = os.path.join(course_dir, "course_list.html")

    # Downloads the course list.
    if not os.path.exists(course_list_path):
        download_page(api_url + "/courses/", cookies_path, course_dir, "course_list.html")

def downloadCourseHomePageHTML(api_url, course_view, cookies_path):
    if(cookies_path == ""):
        return

    dl_dir = os.path.join(DL_LOCATION, course_view.term,
                         course_view.course_code)

    # Create directory if not present
    if not os.path.exists(dl_dir):
        os.makedirs(dl_dir)

    homepage_path = os.path.join(dl_dir, "homepage.html")

    # Downloads the course home page.
    if not os.path.exists(homepage_path):
        download_page(api_url + "/courses/" + str(course_view.course_id), cookies_path, dl_dir, "homepage.html")

def downloadAssignmentPages(api_url, course_view, cookies_path):
    if(cookies_path == "" or len(course_view.assignments) == 0):
        return

    base_assign_dir = os.path.join(DL_LOCATION, course_view.term,
        course_view.course_code, "assignments")

    # Create directory if not present
    if not os.path.exists(base_assign_dir):
        os.makedirs(base_assign_dir)

    assignment_list_path = os.path.join(base_assign_dir, "assignment_list.html")

    # Download assignment list (theres a chance this might be the course homepage if the course has the assignments page disabled)
    if not os.path.exists(assignment_list_path):
        download_page(api_url + "/courses/" + str(course_view.course_id) + "/assignments/", cookies_path, base_assign_dir, "assignment_list.html")

    for assignment in course_view.assignments:
        assignment_title = makeValidFilename(str(assignment.title))
        assignment_title = shortenFileName(assignment_title, len(assignment_title) - MAX_FOLDER_NAME_SIZE)  
        assign_dir = os.path.join(base_assign_dir, assignment_title)

        # Download an html image of each assignment (includes assignment instructions and other stuff). 
        # Currently, this will only download the main assignment page and not external pages, this is
        # because these external pages are given in a json format. Saving these would require a lot
        # more work then normal.
        if assignment.html_url != "":
            if not os.path.exists(assign_dir):
                os.makedirs(assign_dir)

            assignment_page_path = os.path.join(assign_dir, "assignment.html")

            # Download assignment page, this usually has instructions and etc.
            if not os.path.exists(assignment_page_path):
                download_page(assignment.html_url, cookies_path, assign_dir, "assignment.html")

        for submission in assignment.submissions:
            submission_dir = assign_dir

            # If theres more then 1 submission, add unique id to download dir
            if len(assignment.submissions) != 1:
                submission_dir = os.path.join(assign_dir, str(submission.user_id))

            if submission.preview_url != "":
                if not os.path.exists(submission_dir):
                    os.makedirs(submission_dir)

                submission_page_dir = os.path.join(submission_dir, "submission.html")

                # Download submission url, this is typically a more focused page
                if not os.path.exists(submission_page_dir):
                    download_page(submission.preview_url, cookies_path, submission_dir, "submission.html")    

            # If theres more then 1 attempt, save each attempt in attempts folder
            if (submission.attempt != 1 and assignment.updated_url != "" and assignment.html_url != "" 
                and assignment.html_url.rstrip("/") != assignment.updated_url.rstrip("/")):
                submission_dir = os.path.join(assign_dir, "attempts")
                
                if not os.path.exists(submission_dir):
                    os.makedirs(submission_dir)

                # Saves the attempts if multiple were taken, doesn't account for
                # different ID's however, as I wasnt able to find out what the url 
                # for the specific id's attempts would be. 
                for i in range(submission.attempt):
                    filename = "attempt_" + str(i+1) + ".html"
                    submission_page_attempt_dir = os.path.join(submission_dir, filename)

                    if not os.path.exists(submission_page_attempt_dir):
                        download_page(assignment.updated_url + "/history?version=" + str(i+1), cookies_path, submission_dir, filename)

def downloadCourseModulePages(api_url, course_view, cookies_path): 
    if(cookies_path == "" or len(course_view.modules) == 0):
        return

    modules_dir = os.path.join(DL_LOCATION, course_view.term,
        course_view.course_code, "modules")

    # Create modules directory if not present
    if not os.path.exists(modules_dir):
        os.makedirs(modules_dir)

    module_list_dir = os.path.join(modules_dir, "modules_list.html")

    # Downloads the modules page (possible this is disabled by the teacher)
    if not os.path.exists(module_list_dir):
        download_page(api_url + "/courses/" + str(course_view.course_id) + "/modules/", COOKIES_PATH, modules_dir, "modules_list.html")

    for module in course_view.modules:
        for item in module.items:
            # If problems arise due to long pathnames, changing module.name to module.id might help, this can also be done with item.title
            # A change would also have to be made in findCourseModules(course, course_view)
            module_name = makeValidFilename(str(module.name))
            module_name = shortenFileName(module_name, len(module_name) - MAX_FOLDER_NAME_SIZE)
            items_dir = os.path.join(modules_dir, module_name)
            
            # Create modules directory if not present
            if item.url != "":
                if not os.path.exists(items_dir):
                    os.makedirs(items_dir)

                filename = makeValidFilename(str(item.title)) + ".html"
                module_item_dir = os.path.join(items_dir, filename)

                # Download the module page.
                if not os.path.exists(module_item_dir):
                    download_page(item.url, cookies_path, items_dir, filename)

def downloadCourseAnnouncementPages(api_url, course_view, cookies_path):
    if(cookies_path == "" or len(course_view.announcements) == 0):
        return

    base_announce_dir = os.path.join(DL_LOCATION, course_view.term,
        course_view.course_code, "announcements")

    # Create directory if not present
    if not os.path.exists(base_announce_dir):
        os.makedirs(base_announce_dir)

    announcement_list_dir = os.path.join(base_announce_dir, "announcement_list.html")
    
    # Download assignment list (theres a chance this might be the course homepage if the course has the assignments page disabled)
    if not os.path.exists(announcement_list_dir):
        download_page(api_url + "/courses/" + str(course_view.course_id) + "/announcements/", cookies_path, base_announce_dir, "announcement_list.html")

    for announcements in course_view.announcements:
        announcements_title = makeValidFilename(str(announcements.title))
        announcements_title = shortenFileName(announcements_title, len(announcements_title) - MAX_FOLDER_NAME_SIZE)
        announce_dir = os.path.join(base_announce_dir, announcements_title)

        if announcements.url == "":
            continue

        if not os.path.exists(announce_dir):
            os.makedirs(announce_dir)

        # Downloads each page that a discussion takes.
        for i in range(announcements.amount_pages):
            filename = "announcement_" + str(i+1) + ".html"
            announcement_page_dir = os.path.join(announce_dir, filename)

            # Download assignment page, this usually has instructions and etc.
            if not os.path.exists(announcement_page_dir):
                download_page(announcements.url + "/page-" + str(i+1), cookies_path, announce_dir, filename)
        

if __name__ == "__main__":

    print("Welcome to the Canvas Student Data Export Tool\n")

    if API_URL == "":
        # Canvas API URL
        print("We will need your organization's Canvas Base URL. This is "
              "probably something like https://{schoolName}.instructure.com)")
        API_URL = input("Enter your organization's Canvas Base URL: ")

    if API_KEY == "":
        # Canvas API key
        print("\nWe will need a valid API key for your user. You can generate "
              "one in Canvas once you are logged in.")
        API_KEY = input("Enter a valid API key for your user: ")

    if USER_ID == 0000000:
        # My Canvas User ID
        print("\nWe will need your Canvas User ID. You can find this by "
              "logging in to canvas and then going to this URL in the same "
              "browser {yourCanvasBaseUrl}/api/v1/users/self")
        USER_ID = input("Enter your Canvas User ID: ")
    
    if COOKIES_PATH == "": 
        # Cookies path
        print("\nWe will need your browsers cookies file. This needs to be "
              "exported using another tool. This needs to be a path to a file "
              "formatted in the NetScape format. This can be left blank if an html "
              "images aren't wanted. ")
        COOKIES_PATH = input("Enter your cookies path: ")

    print("\nConnecting to canvas\n")

    # Initialize a new Canvas object
    canvas = Canvas(API_URL, API_KEY)

    print("Creating output directory: " + DL_LOCATION + "\n")
    # Create directory if not present
    if not os.path.exists(DL_LOCATION):
        os.makedirs(DL_LOCATION)

    all_courses_views = []

    print("Getting list of all courses\n")
    courses = canvas.get_courses(include="term")

    skip = set(COURSES_TO_SKIP)


    if (COOKIES_PATH):
        print("  Downloading course list page")
        downloadCourseHTML(API_URL, COOKIES_PATH)

    for course in courses:
        if course.id in skip or not hasattr(course, "name") or not hasattr(course, "term"):
            continue

        course_view = getCourseView(course)

        all_courses_views.append(course_view)

        print("  Downloading all files")
        downloadCourseFiles(course, course_view)

        
        print("  Getting modules and downloading module files")
        course_view.modules = findCourseModules(course, course_view)

        if(COOKIES_PATH):
            print("  Downloading course home page")
            downloadCourseHomePageHTML(API_URL, course_view, COOKIES_PATH)

            print("  Downloading assignment pages")
            downloadAssignmentPages(API_URL, course_view, COOKIES_PATH)

            print("  Downloading course module pages")
            downloadCourseModulePages(API_URL, course_view, COOKIES_PATH)

            print("  Downloading course announcements pages")
            downloadCourseAnnouncementPages(API_URL, course_view, COOKIES_PATH)   

            

        print("  Exporting all course data")
        exportAllCourseData(course_view)

    print("Exporting data from all courses combined as one file: "
          "all_output.json")
    # Awful hack to make the JSON pretty. Decode it with Python stdlib json
    # module then re-encode with indentation
    json_str = json.dumps(json.loads(jsonpickle.encode(all_courses_views,
                                                       unpicklable=False)),
                          indent=4)

    all_output_path = os.path.join(DL_LOCATION, "all_output.json")

    with open(all_output_path, "w") as out_file:
        out_file.write(json_str)

    print("\nProcess complete. All canvas data exported!")
