
import json
import os
import base64
from datetime import datetime
import yaml
import argparse
import sys

output_dir = './qquill'

def generate_yaml_section(obj, fields):
    yaml_section = "---\n"
    for field in fields:
        if field in obj:
            # Check if the field value is a dictionary (nested object)
            if isinstance(obj[field], dict):
                # Recursively generate YAML for the nested object
                nested_yaml = yaml.dump({field: obj[field]}, default_flow_style=False)
                yaml_section += nested_yaml
            else:
                yaml_section += f"{field}: {obj[field]}\n"
    yaml_section += "---\n"
    return yaml_section

def addTabs(text, depth):
    # Split the text into lines
    lines = text.split("\n")
    # Indent each line with the specified number of tabs
    indentedLines = ['\t' * depth + line for line in lines]
    # Join the lines back together into a string
    indentedText = '\n'.join(indentedLines)
    return indentedText

def convert_to_iso(date_string):
    # Parse the date string into a datetime object
    date = datetime.strptime(date_string, '%Y%m%d%H%M%S')
    
    # Convert the datetime object to an ISO string
    iso_string = date.isoformat()
    
    return iso_string

def save_base64_image(base64_string, filename, resources_dir):
    """Save a base64 image to the resources directory and return the relative path"""
    try:
        # Remove data URL prefix if present
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        # Decode base64
        image_data = base64.b64decode(base64_string)
        
        # Save to resources directory
        file_path = os.path.join(resources_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(image_data)
        
        return f"resources/{filename}"
    except Exception as e:
        print(f"Error saving image {filename}: {e}")
        return None

def process_images(pictures, thing_id, resources_dir, prefix=""):
    """Process images from pictures object and return markdown references"""
    if not pictures or not pictures.get('photos'):
        return ""
    
    image_refs = []
    for photo_id, photo_data in pictures['photos'].items():
        if photo_data.get('base64'):
            # Generate filename
            extension = photo_data.get('extension', 'jpg')
            filename = f"{thing_id}_{prefix}{photo_id}.{extension}"
            
            # Save image
            relative_path = save_base64_image(photo_data['base64'], filename, resources_dir)
            if relative_path:
                image_refs.append(f"![{photo_data.get('name', photo_id)}]({relative_path})")
    
    return "\n".join(image_refs) if image_refs else ""

def getMDElementTree(thing, resources_dir):
    elements = thing['elements']
    elements_selected = thing['elements_selected']
    elements_row = thing['elements_row']
    el_tree = thing['el_tree']
    el_ids = thing['el_ids']
    el_depth = thing['el_depth']
    el_parents = thing['el_parents']
    el_num_child = thing['el_num_child']

    element_section_string = "## Element Section\n\n"

    for kk, el in thing['elements'].items():
        depth = thing['el_depth'][kk]
        element = el['element']
        content = elements[el['id']]['content']

        for j in range(depth):
            element_section_string += ''
        element_section_string += '- ' + element + '\n'
        element_section_string += addTabs(content, depth)
        element_section_string += '\n'
        
        # Process images for this element
        element_images = process_images(
            elements[el['id']].get('pictures', {}), 
            thing['id'], 
            resources_dir, 
            f"element_{kk}_"
        )
        if element_images:
            element_section_string += addTabs(element_images, depth)
            element_section_string += '\n'
    
    return element_section_string

def process_marks_and_save(marks_dict, fields):
    # Ensure the directories exist
    output_dir = './qquill/'
    resources_dir = os.path.join(output_dir, 'resources')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.path.exists(resources_dir):
        os.makedirs(resources_dir)
    
    # Iterate through each key in the MARKS dictionary
    for key in marks_dict:
        obj = marks_dict[key]

        # Process main images
        main_images = process_images(obj.get('pictures', {}), obj['id'], resources_dir)
        
        # Create element tree with images
        g = getMDElementTree(obj, resources_dir)

        # Convert the key to an ISO date
        iso_date = convert_to_iso(key)

        # Generate YAML section
        yaml_section = generate_yaml_section(obj, fields)

        # Compose markdown with YAML section and images
        markdown_parts = [yaml_section, f"# {obj['title']}", iso_date, ""]
        
        # Add main images if any
        if main_images:
            markdown_parts.extend(["## Images", main_images, ""])
        
        # Add content
        markdown_parts.append(obj['content'])
        markdown_parts.append("")
        
        # Add element section
        markdown_parts.append(g)
        
        markdown = "\n".join(markdown_parts)

        # Define the output file path using the object's ID
        output_file_path = os.path.join(output_dir, f"{obj['id']}.md")
        
        # Save the markdown file
        with open(output_file_path, 'w') as outfile:
            outfile.write(markdown)

def main():
    parser = argparse.ArgumentParser(
        description='Convert QQuill/SpellBook JSON backup to Markdown files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s data/SpellBook_Backup_2024-02-10.json
  %(prog)s data/backup.json --output ./my_notes --ephemeris
  %(prog)s data/backup.json --fields id title created_at tags
        """
    )
    
    parser.add_argument(
        'input_file',
        help='Path to the QQuill/SpellBook JSON backup file'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='./qquill',
        help='Output directory for markdown files (default: ./qquill)'
    )
    
    parser.add_argument(
        '-e', '--ephemeris',
        action='store_true',
        help='Include ephemeris data in the export'
    )
    
    parser.add_argument(
        '-f', '--fields',
        nargs='*',
        default=['id', 'title', 'created_at', 'tags'],
        help='Fields to include in YAML frontmatter (default: id title created_at tags)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found.", file=sys.stderr)
        sys.exit(1)
    
    # Set global output directory
    global output_dir
    output_dir = args.output
    
    try:
        # Load the JSON data
        if args.verbose:
            print(f"Loading data from {args.input_file}...")
        
        with open(args.input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract marks data
        marks = data.get('marks', {})
        if not marks:
            print("Warning: No 'marks' data found in the JSON file.", file=sys.stderr)
            sys.exit(1)
        
        if args.verbose:
            print(f"Found {len(marks)} marks to process")
        
        # Process the marks
        if args.ephemeris:
            process_marks_and_save(marks, args.fields + ['ephemeris'] if 'ephemeris' not in args.fields else args.fields)
        else:
            process_marks_and_save(marks, args.fields)
        
        if args.verbose:
            print(f"Export completed successfully!")
            print(f"Markdown files saved to: {args.output}")
            print(f"Resources saved to: {os.path.join(args.output, 'resources')}")
        else:
            print(f"Exported {len(marks)} markdown files to {args.output}")
            
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON file - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()