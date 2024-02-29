import sys
import re
import requests
from rich import print as rprint


def check_rst_links(file_path):
    """
    Reads a reStructuredText Format document and parse its external links, like this one:

    `free online courses on Coursera <https://www.coursera.org/learn/python>`__

    re.compile(r".*?__"): This line of code uses the re.compile() method to create a regular expression pattern object.

    re.compile(): This function compiles a regular expression pattern provided as a string into a regex pattern object.
    The pattern object can then be used to search for occurrences of the same pattern inside different target strings without rewriting it.

    r".*?__": This is the regular expression pattern itself.

    r"  : The r prefix indicates that the string is a raw string, which means escape sequences (like \n or \t) are treated as literal characters.
    .*? : This part of the pattern matches any sequence of characters (except newline characters) between backticks (`).
          The .*? is a non-greedy match, meaning it will match the shortest possible sequence of characters between backticks.
    __  : This part of the pattern matches the double underscore (__) literally."""
    try:
        with open(file_path, "r") as rst_file:
            content = rst_file.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return

    # Regular expression to match URLs in the .rst file.
    url_pattern = re.compile(r"`[^`]+`_+|`[^`]+`__", flags=re.DOTALL)

    # Secondary check for "< >".
    occurrences = len(re.findall(r"<(?!/)[^>]+>", content, flags=re.DOTALL))

    # Initialize error and warning counts.
    error_count = 0
    warning_count = 0

    # Iterate over matches
    for match in url_pattern.finditer(content):
        url_tag = match.group(0)
        rprint(f"[dark_cyan]<> {url_tag}[/dark_cyan]", sep="\n")
        # Skip false positive url tags without urls.
        if "http" not in str(url_tag):
            rprint(f"[gold3]Skipped {url_tag}[/gold3]", sep="\n")
            continue
        try:
            # Check if the URL is valid
            url = (
                url_tag.replace(">`__", "")
                .replace(">`_", "")
                .replace("[", "")
                .replace("]", "")
                .replace("\\", "")
                .split("<")[1]
            )
            rprint(f"[steel_blue]🔗 {url}[/steel_blue]", sep="\n")
        except:
            rprint("[red]❌ Failed to extract url from tag.[/red]", sep="\n")
            error_count += 1
        is_valid = validate_rst_url_tag(url_tag)
        if is_valid:
            rprint(
                "[dark_cyan]✅ Meets .rst url tag requirements.[/dark_cyan]", sep="\n"
            )
        else:
            rprint(
                "[red]❌ Tag doesn't meet .rst url tag requirements.[/red]", sep="\n"
            )
            error_count += 1
        try:
            response = requests.head(url, allow_redirects=True, timeout=15)
            if response.status_code == 200:
                rprint("[dark_cyan]✅ URL loaded successfully.[/dark_cyan]", sep="\n")
            elif response.status_code == 301:
                redirect_url = response.url
                line = content.count("\n", 0, match.start()) + 1
                rprint(
                    f"[gold3]🛈  Warning: URL is a 301 redirect to {redirect_url} found on line {line} with status code {response.status_code}[/gold3]",
                    sep="\n",
                )
                warning_count += 1
                print("\n")
            elif response.status_code == 403:
                rprint(
                    f"[gold3]🛈  Warning: Unable to validate URL, permission denied with status code {response.status_code}[/gold3]",
                    sep="\n",
                )
                warning_count += 1
                print("\n")
            elif response.status_code != 200:
                line = content.count("\n", 0, match.start()) + 1
                rprint(
                    f"[red]❌ Error: Invalid URL '{url}' found on line {line} with status code {response.status_code}[/red]",
                    sep="\n",
                )
                error_count += 1
            print("\n")
        except requests.Timeout:
            rprint(
                f"[red]❌ Error: Request timed out '{url}' on line {content.count('\n', 0, match.start()) + 1}[/red]",
                sep="\n",
            )
            error_count += 1
            print("\n")
        except requests.RequestException:
            rprint(
                f"[red]❌ Error: Unable to check URL '{url}' on line {content.count('\n', 0, match.start()) + 1}[/red]",
                sep="\n",
            )
            error_count += 1
            print("\n")

    print(f"File: {file_path}")
    matches = len(list(url_pattern.finditer(content)))
    print(f"Scanned {matches} urls.")
    if error_count == 0:
        print("✅ No errors found.")
    else:
        print(f"❌ {error_count} total error(s) found.")

    if warning_count == 0:
        print("✅ No warnings.")
    else:
        print(f"🛈  {warning_count} total warning(s).")
    if occurrences != matches:
        print(f"❌ Possible discrepancy: found {occurrences} occurrences of <> brackets and only {matches} url matches. Check for document for invalid urls.")
    return None


def validate_rst_url_tag(url_tag):
    """
    Validates an .rst URL tag to ensure it contains the required characters: <, >, `, _, and expected multi-character combinations.
    Args:
        url_tag (str): The .rst URL tag to validate.
    Returns:
        bool: True if the URL tag is valid, False otherwise.
    """
    required_characters = {"<", ">", "`", "_", "`_", ">`_"}
    return all(char in url_tag for char in required_characters)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python rst-url-validator.py <path_to_rst_file>")
    else:
        rst_file_path = sys.argv[1]
        check_rst_links(rst_file_path)
