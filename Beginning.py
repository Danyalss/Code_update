import os
import requests
import base64
import tempfile
import difflib
# Define constants for colored output
COLORS = {
    'black': '\033[30m',
    'white': '\033[37m',
    'blue': "\033[1;34m",
    'yellow': '\033[33m',
    'red': "\033[1;31m",
    'green': "\033[1;33m",
    'pink': "\033[95m",
    'grey': "\033[1;30m",
    'reset': "\033[0m",
    'cyan': "\033[36m",
    'purple': "\033[35m",
}

Username = "Danyalss"
Repository = "Phone_bot"
file_names = {"main.py", "a.py"}
##           Example: file_names = {"main.py", "a.py"}


# Personal GitHub access token (should use environmental variable in production)
##           Example: github_token = 'ghp_wI6S2uUkssVTlcOJq5aY4kchaVA5WR1Fh2rn'
github_token = 'YOUR_GITHUB_TOKEN'



urls = [
    f'https://api.github.com/repos/{Username}/{Repository}/contents/{file_name}?ref=master'
    for file_name in file_names
]



def print_in_color(text, color):
    print(f"{COLORS.get(color, COLORS['reset'])}{text}{COLORS['reset']}")


def fetch_file(url, headers):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.HTTPError as http_err:
        print_in_color(f"HTTP error occurred: {http_err}", 'red')
    except Exception as err:
        print_in_color(f"An error occurred: {err}", 'red')
    else:
        return base64.b64decode(response.json()['content']).decode('utf-8')


def update_cache(file_path, content):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    print_in_color("Code updated and cache file written.", 'blue')


def diff_and_write(file_path, content):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            old_content = file.read()
        if old_content == content:
            print_in_color("No changes detected.", 'yellow')
            return
        else:
            diff = difflib.unified_diff(
                old_content.splitlines(keepends=True),
                content.splitlines(keepends=True),
                fromfile="old_content",
                tofile="new_content",
            )
            print_in_color(''.join(diff), 'purple')
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    print_in_color("New content written to file.", 'green')

headers = {'Authorization': f'token {github_token}'}

temp_dir = tempfile.TemporaryDirectory()

for url in urls:
    new_content = fetch_file(url, headers)
    if new_content:
        file_name = url.split('/')[-1].split('?')[0]
        cache_file_path = os.path.join(temp_dir.name, file_name)
        
        update_cache(cache_file_path, new_content)
        diff_and_write(file_name, new_content)
        print_in_color("Executing the updated file.", 'cyan')
        os.system(f'python3 {file_name}')

temp_dir.cleanup()  # Make sure to clean up the temporary directory