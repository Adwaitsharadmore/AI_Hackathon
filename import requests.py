import os
import requests
import html
def get_all_courses(api_url, headers):
    courses = []
    while api_url:
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            courses.extend(response.json())
            api_url = response.links['next']['url'] if 'next' in response.links else None
        else:
            print("Failed to retrieve courses")
            break
    return courses

def list_courses(courses):
    for course in courses:
        print(f"Course ID: {course['id']}, Course Name: {course.get('name', 'No Course Name Available')}")

def user_select_courses(courses):
    selected_course_ids = input("Enter the Course IDs of the courses you're interested in, separated by commas: ").split(',')
    return [course for course in courses if str(course['id']) in [id.strip() for id in selected_course_ids]]

def sanitize_filename(filename):
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '-')
    filename = filename.replace('/', '-').replace('\\', '-')
    return filename.strip(".")

def download_file(file_metadata, local_path, headers):
    # Check if 'file_metadata' is a string, indicating a direct URL was passed
    if isinstance(file_metadata, str):
        file_url = file_metadata
    else:
        # Assume 'file_metadata' is a dictionary and extract the file URL
        file_url = html.unescape(file_metadata.get('url', ''))

    directory = os.path.dirname(local_path)
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    
    try:
        with requests.get(file_url, headers=headers, stream=True, allow_redirects=True) as r:
            r.raise_for_status()
            with open(local_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"Downloaded to {local_path}")
    except Exception as e:
        print(f"Error downloading file: {e}")

def fetch_files_and_download(course_id, headers, api_base_url, download_dir):
    files_url = f"{api_base_url}/courses/{course_id}/files"
    while files_url:
        response = requests.get(files_url, headers=headers)
        if response.status_code == 200:
            files = response.json()
            for file in files:
                filename = sanitize_filename(file.get('filename'))
                file_url = file.get('url')  # Direct download URL assumed
                local_path = os.path.join(download_dir, filename)
                download_file(file_url, local_path, headers)
            files_url = response.links['next']['url'] if 'next' in response.links else None
        else:
            print(f"Failed to fetch files for Course ID: {course_id}")
            break

def get_course_data(selected_courses, headers, api_base_url, download_dir):
    for course in selected_courses:
        print(f"\nFetching data for Course ID: {course['id']}, Course Name: {course.get('name', 'No Course Name Available')}")
        fetch_files_and_download(course['id'], headers, api_base_url, download_dir)
def fetch_and_download_module_files(course_id, headers, api_base_url, download_dir):
    modules_url = f"{api_base_url}/courses/{course_id}/modules?include=items&per_page=100"
    while modules_url:
        response = requests.get(modules_url, headers=headers)
        if response.status_code == 200:
            modules = response.json()
            for module in modules:
                for item in module.get('items', []):
                    # Check if the module item is a type of File
                    if item['type'] == 'File':
                        # Direct API call to fetch file metadata, if necessary
                        file_response = requests.get(item['url'], headers=headers)
                        if file_response.status_code == 200:
                            file_metadata = file_response.json()
                            # Use 'display_name' from the metadata for filename
                            filename = sanitize_filename(file_metadata['display_name'])
                            local_path = os.path.join(download_dir, filename)
                            # Use 'url' from the metadata for downloading the file
                            file_url = file_metadata.get('url')
                            if file_url:
                                download_file(file_url, local_path, headers)
                        else:
                            print(f"Failed to fetch file metadata for item ID: {item['id']}")
                    # Additional handling for other item types can be added here
            modules_url = response.links['next']['url'] if 'next' in response.links else None
        else:
            print(f"Failed to fetch modules for Course ID: {course_id}")
            break
def fetch_and_download_files_in_folder(folder_id, headers, api_base_url, download_dir):
    folder_files_url = f"{api_base_url}/folders/{folder_id}/files"
    while folder_files_url:
        response = requests.get(folder_files_url, headers=headers)
        if response.status_code == 200:
            files = response.json()
            for file in files:
                filename = sanitize_filename(file['display_name'])
                file_url = file['url']
                local_path = os.path.join(download_dir, filename)
                download_file(file_url, local_path, headers)
            folder_files_url = response.links['next']['url'] if 'next' in response.links else None
        else:
            print(f"Failed to fetch files for Folder ID: {folder_id}")
            break
def fetch_and_download_from_nested_folders(folder_id, headers, api_base_url, download_dir):
    # First, download files in the current folder
    fetch_and_download_files_in_folder(folder_id, headers, api_base_url, download_dir)

    # Then, list subfolders and recursively fetch their contents
    subfolders_url = f"{api_base_url}/folders/{folder_id}/folders"
    while subfolders_url:
        response = requests.get(subfolders_url, headers=headers)
        if response.status_code == 200:
            subfolders = response.json()
            for subfolder in subfolders:
                subfolder_id = subfolder['id']
                fetch_and_download_from_nested_folders(subfolder_id, headers, api_base_url, download_dir)
            subfolders_url = response.links['next']['url'] if 'next' in response.links else None
        else:
            print(f"Failed to fetch subfolders for Folder ID: {folder_id}")
            break
def get_course_root_folder_id(course_id, headers, api_base_url):
    folders_url = f"{api_base_url}/courses/{course_id}/folders/root"
    response = requests.get(folders_url, headers=headers)
    if response.status_code == 200:
        folder_data = response.json()
        return folder_data['id']
    else:
        print(f"Failed to retrieve root folder for Course ID: {course_id}")
        return None

def main():
# Main script execution starts here
    api_base_url = "https://canvas.asu.edu/api/v1"
    api_url = f"{api_base_url}/courses?per_page=100"
    api_key = "7236~S4hTI1YNv5PncjZyzeEDNvSaCbgl7Hnm4ZCluNtzXIjC6BmiinQioEalgLcYFw2C"
    headers = {"Authorization": "Bearer " + api_key}
    download_dir = "/Users/aryanredhu/hackathon"

    all_courses = get_all_courses(api_url, headers)
    list_courses(all_courses)
    selected_courses = user_select_courses(all_courses)

    for course in selected_courses:
        course_id = course['id']
        print(f"\nHandling Course ID: {course_id}, Course Name: {course.get('name', 'No Course Name Available')}")

        # Existing file and module fetch and download calls
        fetch_files_and_download(course_id, headers, api_base_url, download_dir)
        fetch_and_download_module_files(course_id, headers, api_base_url, download_dir)
        
        # New: Fetch and download from nested folders starting with the root folder
        root_folder_id = get_course_root_folder_id(course_id, headers, api_base_url)
        if root_folder_id:
            fetch_and_download_from_nested_folders(root_folder_id, headers, api_base_url, download_dir)

if __name__ == "__main__":
    main()