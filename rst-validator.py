import sys
import re
import requests
from rich import print as rprint

def check_rst_links(file_path):
    try:
        with open(file_path, "r") as rst_file:
            content = rst_file.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return

    # Regular expression to match URLs in the .rst file
    url_pattern = re.compile(r"`.*?`__")

    # Initialize error count
    error_count = 0

    # Iterate over matches
    for match in url_pattern.finditer(content):
        url_tag = match.group(0)
        # Skip false positive url tags without urls.
        if "http" not in str(url_tag):
            rprint(f"[gold]Skipped {url_tag}[/gold]", sep="\n")
            continue
        rprint(f"[dark_cyan]{url_tag}[/dark_cyan]", sep="\n")
        is_valid = validate_rst_url_tag(url_tag)
        if is_valid:
            rprint("[dark_cyan]Tag meets url requirements.[/dark_cyan]", sep="\n")
        else:
            rprint("[red]Tag doesn't meet .rst url tag requirements.[/red]", sep="\n")
        try:
            # Check if the URL is valid
            url = extract_url_from_rst_link(url_tag)
            rprint(f"[steel_blue]{url}[/steel_blue]", sep="\n")
            response = requests.head(url)
            if response.status_code == 200:
                rprint(f"[dark_cyan]URL successfully loaded.[/dark_cyan]", sep="\n")
            if response.status_code != 200:
                print(
                    f"Error: Invalid URL '{url}' found on line {content.count('\\n', 0, match.start()) + 1} with status code {response.status_code}"
                )
                error_count += 1
        except requests.RequestException:
            print(
                f"Error: Unable to check URL '{url}' on line {content.count('\\n', 0, match.start()) + 1}"
            )
            print(response.text)
            error_count += 1

    if error_count == 0:
        print(f"No errors found in {file_path}.")
    else:
        print(f"Total {error_count} error(s) found in {file_path}.")


def extract_url_from_rst_link(url_tag):
    # Regular expression to extract the URL from an .rst link
    url = (
        url_tag.replace(">`__", "")
        .replace("[", "")
        .replace("]", "")
        .replace("\\", "")
        .split("<")[1]
    )
    return url


def validate_rst_url_tag(url_tag):
    """
    Validates an .rst URL tag to ensure it contains the required characters: <, >, `, and _
    Args:
        url_tag (str): The .rst URL tag to validate.
    Returns:
        bool: True if the URL tag is valid, False otherwise.
    """
    required_characters = {'<', '>', '`', '_'}
    return all(char in url_tag for char in required_characters)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python check_rst_links.py <path_to_rst_file>")
    else:
        rst_file_path = sys.argv[1]
        check_rst_links(rst_file_path)
        
