# QQuill Markdown Exporter

As SpellBook is evolving into QQuill, a dear user asked for a script to convert his SpellBook Export into markdown files, to Obsidian / Zettelkasten usage. This repo contains a script to do just that.

## Instructions

### Method 1: Command Line Interface (Recommended)

The easiest way to use this tool is via the command line:

1. Clone or download this repo to your local computer
2. Put your SpellBook 1.3.4 (or QQuill) backup in the `./data` folder
3. Run the script from the command line:

```bash
# Basic usage
python qquill_to_md.py data/SpellBook_Backup_2024-02-10.json

# Specify custom output directory
python qquill_to_md.py data/SpellBook_Backup_2024-02-10.json --output ./my_notes

# Include ephemeris data
python qquill_to_md.py data/SpellBook_Backup_2024-02-10.json --ephemeris

# Customize YAML frontmatter fields
python qquill_to_md.py data/SpellBook_Backup_2024-02-10.json --fields id title created_at tags category

# Verbose output
python qquill_to_md.py data/SpellBook_Backup_2024-02-10.json --verbose
```

#### CLI Options

- `input_file`: Path to your QQuill/SpellBook JSON backup file (required)
- `-o, --output`: Output directory for markdown files (default: `./qquill`)
- `-e, --ephemeris`: Include ephemeris data in the export
- `-f, --fields`: Specify which fields to include in YAML frontmatter (default: `id title created_at tags`)
- `-v, --verbose`: Enable detailed output during processing
- `-h, --help`: Show help message with all options

### Method 2: Jupyter Notebook (Legacy)

If you prefer using a Jupyter notebook:

1. Clone or download this repo to your local computer   
2. Put your SpellBook 1.3.4 (or QQuill) backup in the `./data` folder
3. Open `qquill_to_md.ipynb` in [Cursor](https://cursor.com/), [Visual Studio Code](https://code.visualstudio.com/), or a [Jupyter Notebook](https://jupyter.org/). Make sure you're running `python 3` and have your kernels installed.

In the notebook, you'll see these configuration lines:

```python
FILE_PATH = './data/SpellBook_Backup_2024-02-10.json'
INCLUDE_EPHEMERIS = False
```

Ensure that `FILE_PATH` points to your JSON backup file.

4. Run the first test cell. If you see dates being returned, you're good to go!
5. Run the "export" cell to generate your markdown files.

## Output

The script will create:
- Individual markdown files for each note/mark in your backup
- A `resources/` subdirectory containing any embedded images
- YAML frontmatter in each markdown file with metadata
- Properly formatted element trees and content sections

## Requirements

- Python 3.6+
- PyYAML (`pip install pyyaml`)

## Troubleshooting

If you encounter issues:
1. Ensure your JSON backup file is valid and contains 'marks' data
2. Check that you have write permissions to the output directory
3. Verify Python dependencies are installed
4. Use the `--verbose` flag for detailed error information

