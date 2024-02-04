import re


def update_badge_in_readme(readme_path, new_badge_url):
    """
    Updates the README.md file with the new badge URL.

    :param readme_path: Path to the README.md file
    :param new_badge_url: The new URL to be embedded in the badge
    """
    badge_pattern = re.compile(r'\[!\[PyLint\]\(.*?\)\]\(.*?\)')  # Regex to find the existing badge markdown
    new_badge_md = f'[![PyLint]({new_badge_url})](https://github.com/arturogonzalezm/azure_function/actions/workflows/pylint.yml)'  # New badge markdown

    # Read the existing README.md content
    with open(readme_path, 'r', encoding='utf-8') as file:
        readme_content = file.read()

    # Replace the old badge URL with the new one
    updated_content = badge_pattern.sub(new_badge_md, readme_content)

    # Write the updated content back to README.md
    with open(readme_path, 'w', encoding='utf-8') as file:
        file.write(updated_content)


# Example usage
if __name__ == "__main__":
    new_badge_url = "https://img.shields.io/badge/PyLint-9.5%2F10-green"
    readme_path = "README.md"
    update_badge_in_readme(readme_path, new_badge_url)
