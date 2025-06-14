import os
import shutil
import difflib

def get_cwd():
    """
    Get the current working directory.
    
    Returns:
        str: The current working directory path.
    """
    try:
        return os.getcwd()
    except Exception as e:
        return f"Error getting current working directory: {e}"

def read_file(path, show_line_numbers=False, start_line=1, end_line=None, show_repr=False):
    """
    Read the contents of a file with optional line numbering, range selection, and debug formatting.
    
    Args:
        path (str): The path to the file to read.
        show_line_numbers (bool): Whether to include line numbers (defaults to False).
        start_line (int): First line to read, 1-indexed (defaults to 1).
        end_line (int): Last line to read, 1-indexed, None for all lines (defaults to None).
        show_repr (bool): Whether to show Python's repr() of each line, revealing whitespace and special characters (defaults to False).
        
    Returns:
        str: The contents of the file (potentially formatted), or an error message if reading fails.
    """
    try:
        if not os.path.isfile(path):
            return f"Not a file: {path}"
        
        # Read file contents
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Apply filtering if needed
        if show_line_numbers or start_line > 1 or end_line is not None:
            lines = content.splitlines()
            
            # Apply line range
            start_idx = max(0, start_line - 1)  # Convert to 0-indexed
            if end_line is not None:
                end_idx = min(len(lines), end_line)  # Convert to 0-indexed + 1
                filtered_lines = lines[start_idx:end_idx]
            else:
                filtered_lines = lines[start_idx:]
            
            # Format lines
            if show_line_numbers:
                if show_repr:
                    content = "\n".join(f"{i:>6}  {repr(line)}" for i, line in enumerate(filtered_lines, start_line))
                else:
                    content = "\n".join(f"{i:>6}  {line}" for i, line in enumerate(filtered_lines, start_line))
            else:
                if show_repr:
                    content = "\n".join(repr(line) for line in filtered_lines)
                else:
                    content = "\n".join(filtered_lines)
        elif show_repr:
            # Just show repr without line numbers
            content = "\n".join(repr(line) for line in content.splitlines())
        
        return content
        
    except FileNotFoundError:
        return f"File not found: {path}"
    except PermissionError:
        return f"Permission denied: {path}"
    except UnicodeDecodeError:
        return f"Error: Unable to decode file as UTF-8: {path}"
    except ValueError as e:
        return f"Value error: {e}"
    except Exception as e:
        return f"Error reading file: {e}"

def write_file(path, content):
    """
    Write content to a file.
    
    Args:
        path (str): The path to the file to write.
        content (str): The content to write to the file.
        
    Returns:
        str: A confirmation message, or an error message if writing fails.
    """
    try:
        with open(path, 'w') as file:
            file.write(content)
        return f"File written successfully: {path}"
    except PermissionError:
        return f"Permission denied: {path}"
    except Exception as e:
        return f"Error writing file: {e}"

def create_directory(path):
    """
    Create a new directory.
    
    Args:
        path (str): The path of the directory to create.
        
    Returns:
        str: A confirmation message, or an error message if creation fails.
    """
    try:
        os.makedirs(path, exist_ok=True)  # `exist_ok=True` ensures no error if the directory already exists
        return f"Directory created successfully: {path}"
    except PermissionError:
        return f"Permission denied: {path}"
    except Exception as e:
        return f"Error creating directory: {e}"

def list_directory(path="."):
    """
    List the contents of a directory.
    
    Args:
        path (str): The path of the directory to list. Defaults to the current directory (".").
        
    Returns:
        str: A list of files and directories, or an error message if listing fails.
    """
    try:
        import time
        contents = os.listdir(path)
        return f"Contents of directory '{path}': {', '.join(contents)}"
    except FileNotFoundError:
        return f"Directory not found: {path}"
    except PermissionError:
        return f"Permission denied: {path}"
    except Exception as e:
        return f"Error listing directory: {e}"

def copy_file(source, destination):
    """
    Copy a file from source to destination.
    
    Args:
        source (str): The path to the source file to copy.
        destination (str): The path where the file should be copied to.
        
    Returns:
        str: A confirmation message, or an error message if copying fails.
    """
    try:
        shutil.copy2(source, destination)
        return f"File copied successfully from {source} to {destination}"
    except FileNotFoundError:
        return f"Source file not found: {source}"
    except PermissionError:
        return f"Permission denied: Cannot copy from {source} to {destination}"
    except shutil.SameFileError:
        return f"Error: Source and destination are the same file: {source}"
    except IsADirectoryError:
        return f"Error: Destination is a directory: {destination}"
    except Exception as e:
        return f"Error copying file: {e}"

def remove_file(path):
    """
    Remove/delete a single file.
    
    Args:
        path (str): The path to the file to delete.
        
    Returns:
        str: A confirmation message, or an error message if deletion fails.
    """
    try:
        os.remove(path)
        return f"File removed successfully: {path}"
    except FileNotFoundError:
        return f"File not found: {path}"
    except PermissionError:
        return f"Permission denied: {path}"
    except IsADirectoryError:
        return f"Error: Path is a directory, not a file: {path}"
    except Exception as e:
        return f"Error removing file: {e}"

def remove_directory(path):
    """
    Remove/delete a directory and all its contents.
    
    Args:
        path (str): The path to the directory to delete.
        
    Returns:
        str: A confirmation message, or an error message if deletion fails.
    """
    try:
        shutil.rmtree(path)
        return f"Directory removed successfully: {path}"
    except FileNotFoundError:
        return f"Directory not found: {path}"
    except PermissionError:
        return f"Permission denied: {path}"
    except NotADirectoryError:
        return f"Error: Path is not a directory: {path}"
    except Exception as e:
        return f"Error removing directory: {e}"


def copy_directory(source, destination):
    """
    Copy a directory and all its contents to a new location.
    
    Args:
        source (str): The path to the source directory to copy.
        destination (str): The path where the directory should be copied to.
        
    Returns:
        str: A confirmation message, or an error message if copying fails.
    """
    try:
        shutil.copytree(source, destination)
        return f"Directory copied successfully from {source} to {destination}"
    except FileNotFoundError:
        return f"Source directory not found: {source}"
    except PermissionError:
        return f"Permission denied: Cannot copy from {source} to {destination}"
    except FileExistsError:
        return f"Error: Destination directory already exists: {destination}"
    except NotADirectoryError:
        return f"Error: Source is not a directory: {source}"
    except Exception as e:
        return f"Error copying directory: {e}"


def append_file(path, content):
    """
    Append content to an existing file.
    
    Args:
        path (str): The path to the file to append to.
        content (str): The content to append to the file.
        
    Returns:
        str: A confirmation message, or an error message if appending fails.
    """
    try:
        with open(path, 'a') as file:
            file.write(content)
        return f"Content appended successfully to: {path}"
    except FileNotFoundError:
        return f"File not found: {path}"
    except PermissionError:
        return f"Permission denied: {path}"
    except IsADirectoryError:
        return f"Error: Path is a directory, not a file: {path}"
    except Exception as e:
        return f"Error appending to file: {e}"


def edit_file(path, old_text, new_text, dry_run=False):
    """
    Make a line-based edit to a file by replacing old_text with new_text.
    The old_text must appear exactly once in the file for safety.
    
    Args:
        path (str): The path to the file to edit.
        old_text (str): Text to be replaced (must match exactly once).
        new_text (str): Replacement text.
        dry_run (bool): If True, just return the diff without making changes.
        
    Returns:
        str: A confirmation message with diff, or an error message if editing fails.
    """
    try:
        # Check if file exists and is actually a file
        if not os.path.isfile(path):
            return f"Error: Not a file: {path}"
        
        # Read current content
        with open(path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Make a copy for modifications
        modified_content = original_content
        
        # Ensure old_text appears exactly once
        if old_text not in modified_content:
            return f"Edit failed: Could not find text '{old_text}' in file"
        
        if modified_content.count(old_text) > 1:
            return f"Edit failed: Text '{old_text}' appears multiple times in file, but this tool only works with exactly one match."
        
        # Replace text
        modified_content = modified_content.replace(old_text, new_text)
        
        # Generate diff
        original_lines = original_content.splitlines(keepends=True)
        modified_lines = modified_content.splitlines(keepends=True)
        
        diff = ''.join(difflib.unified_diff(
            original_lines, 
            modified_lines,
            fromfile=f'a/{path}',
            tofile=f'b/{path}',
            n=3
        ))
        
        # Apply changes if not a dry run
        if not dry_run:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            return f"Successfully edited file: {path}\\n\\nDiff:\\n{diff}"
        else:
            return f"Dry run: Changes not applied to {path}\\n\\nDiff:\\n{diff}"
            
    except PermissionError:
        return f"Permission denied: {path}"
    except UnicodeDecodeError:
        return f"Error: Unable to decode file as UTF-8: {path}"
    except Exception as e:
        return f"Error editing file: {e}"
