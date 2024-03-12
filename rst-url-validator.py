import sys
import re
import requests
from rich import print as rprint
import http.client as http_client


def check_rst_links(file_path):
    """
    Reads a reStructuredText Format document and parse its external links, like this one:

    `free online courses on Coursera <https://www.coursera.org/learn/python>`__

    This code matches the urls: re.compile(r"`[^`]+`_+", flags=re.DOTALL)

    re.compile() creates a compiled regex object that can be used for pattern matching.

    `[^`]   matches any character except a backtick `
    +       1st + matches one or more occurrences of a backtick `
    _       matches a literal underscore character.
    +       2nd + matches one or more underscores.
    
    This part of the pattern matches backticked text followed by one or more underscores (e.g., ` some_text_

    The re.DOTALL flag allows the dot (.) to match newline characters as well.
    """
    try:
        with open(file_path, "r") as rst_file:
            content = rst_file.read()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return

    # Regular expression to match URLs in the .rst file.
    url_pattern = re.compile(r"`[^`]+`_+", flags=re.DOTALL)

    # Secondary check for "< >" and ignore HTML tags like "</p>".
    occurrences = len(re.findall(r"<(?!/)[^>]+>", content, flags=re.DOTALL))

    # Initialize error and warning counts.
    error_count = 0
    warning_count = 0

    # Iterate over matches.
    for match in url_pattern.finditer(content):
        url_tag = match.group(0)
        rprint(f"[dark_cyan]<> {url_tag}[/dark_cyan]", sep="\n")
        # Skip false positive url tags without HTTP urls.
        if "http" not in str(url_tag):
            rprint(f"[gold3]🛈  Warning: skipped {url_tag}, url is not http.[/gold3]", sep="\n")
            warning_count += 1
            print("\n")
            continue
        try:
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
        # Check if the URL is valid.
        required_characters = {"<", ">", "`", "_", "`_", ">`_"}
        is_valid = all(char in url_tag for char in required_characters)
        if is_valid:
            rprint(
                "[dark_cyan]✅ Meets .rst url tag requirements.[/dark_cyan]", sep="\n"
            )
        else:
            rprint(
                "[red]❌ Tag doesn't meet .rst url tag requirements.[/red]", sep="\n"
            )
            error_count += 1
        line = content.count("\n", 0, match.start()) + 1
        try:
            response = requests.head(url, allow_redirects=True, timeout=15)
            if response.status_code == 200:
                rprint("[dark_cyan]✅ URL loaded successfully.[/dark_cyan]", sep="\n")
            elif response.status_code == 301:
                redirect_url = response.url
                rprint(
                    f"[gold3]🛈  Warning: URL is a 301 redirect to {redirect_url} found on line # {line} with status code {response.status_code}[/gold3]",
                    sep="\n",
                )
                warning_count += 1
            elif response.status_code == 403:
                rprint(
                    f"[gold3]🛈  Warning: Unable to validate URL found on line # {line}, permission denied with status code {response.status_code}[/gold3]",
                    sep="\n",
                )
                warning_count += 1
            elif response.status_code == 406:
                rprint(
                    f"[red]❌ Error: resource not available in requested format, found on line # {line} with status code {response.status_code}[/red]",
                    sep="\n",
                )
                error_count += 1
            elif response.status_code != 200:
                rprint(
                    f"[red]❌ Error: unable to validate URL '{url}', found on line # {line} with status code {response.status_code}[/red]",
                    sep="\n",
                )
                error_count += 1
            print("\n")
        except requests.Timeout:
            rprint(
                f"[red]❌ Error: Request timed out for '{url}' on line # {line}[/red]",
                sep="\n",
            )
            error_count += 1
            print("\n")
        except requests.RequestException:
            rprint(f"[red]❌ Error: Unable to validate URL '{url}' on line # {line}, connection was terminated by host.[/red]", sep="\n",)
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
        print(f"❌ Possible discrepancy: found {occurrences} occurrences of <> brackets and only {matches} url matches. Check the document for invalid urls.")
    return None


if __name__ == "__main__":
    # http_client.HTTPConnection.debuglevel = 1
    if len(sys.argv) != 2:
        print("Usage: python rst-url-validator.py <path_to_rst_file>")
    else:
        rst_file_path = sys.argv[1]
        check_rst_links(rst_file_path)
