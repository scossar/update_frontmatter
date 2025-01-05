import typer
import datetime
import random
import re
from pathlib import Path


app = typer.Typer()


def generate_id(base_name):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    random_suffix = format(random.randint(0, 0xffff), "04x")
    return f"{base_name}_{timestamp}_{random_suffix}"


def parse_filename(filepath):
    path = Path(filepath)
    return path.stem.replace(" ", "_")


def get_front_matter(content):
    front_matter_pattern = r"^---\s*\n(.*?)\n---\s*\n"
    front_matter_match = re.match(front_matter_pattern, content, re.DOTALL)

    if front_matter_match:
        front_matter = front_matter_match.group(1)
        rest_of_content = content[front_matter_match.end():]
        return front_matter, rest_of_content
    return None, content


def check_front_matter_for_file_id(content):
    front_matter, _ = get_front_matter(content)
    return front_matter is not None and "file_id:" in front_matter


def add_or_update_front_matter(content, file_id):
    front_matter, rest_of_content = get_front_matter(content)

    if front_matter is not None:
        new_front_matter = f"file_id: {file_id}\n{front_matter}"
        return f"---\n{new_front_matter}---\n{rest_of_content}"
    else:
        return f"---\nfile_id: {file_id}\n---\n\n{content}"


def process_markdown_files(root_dir):
    processed_count = 0
    updated_count = 0

    root_path = Path(root_dir)
    for filepath in root_path.rglob("*"):
        if filepath.suffix.lower() in (".md", ".markdown"):
            processed_count += 1

            try:
                content = filepath.read_text(encoding="utf-8")

                if not check_front_matter_for_file_id(content):
                    base_name = parse_filename(filepath)
                    file_id = generate_id(base_name)

                    new_content = add_or_update_front_matter(content, file_id)
                    filepath.write_text(new_content, encoding="utf-8")

                    updated_count += 1
                    print(f"Updated: {filepath}")

            except Exception as e:
                print(f"Error processing {filepath}: {str(e)}")

    print("\nProcessing complete")
    print(f"Total files processed: {processed_count}")
    print(f"Files updated: {updated_count}")


@app.command()
def main(root_dir: str):
    """
    Iterate through all markdown files in root_dir and its subdirectories.
    Add a file_id front matter property to any markdown files on which it's not already set.
    """

    path = Path(root_dir)

    if not path.exists():
        typer.echo(f"Error: Directory '{root_dir}' does not exist")
        raise typer.Exit(1)

    if not path.is_dir():
        typer.echo(f"Error: '{root_dir}' is not a directory")
        raise typer.Exit(1)

    if not typer.confirm(f"Update all markdown files in '{root_dir}' and its subdirectories?"):
        print("Operation cancelled")
        raise typer.Abort()

    process_markdown_files(root_dir)


if __name__ == "__main__":
    app()

