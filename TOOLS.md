# Available Tools

This document describes all available tools and their usage.

## Table of Contents

### [File System Operations](#file-system-operations)
- [get_cwd](#get_cwd) - Get the current working directory
- [read_file](#read_file) - Read a file with optional formatting options
- [write_file](#write_file) - Write content to a file
- [append_file](#append_file) - Append content to an existing file
- [edit_file](#edit_file) - Make line-based edits to a file
- [copy_file](#copy_file) - Copy a file from source to destination
- [remove_file](#remove_file) - Remove/delete a single file

### [Directory Operations](#directory-operations)
- [create_directory](#create_directory) - Create a new directory
- [list_directory](#list_directory) - List the contents of a directory
- [remove_directory](#remove_directory) - Remove/delete a directory and all its contents
- [copy_directory](#copy_directory) - Copy a directory and all its contents

### [Git Operations](#git-operations)
- [git_clone](#git_clone) - Clone a git repository using HTTPS
- [git_commit](#git_commit) - Stage all changes and create a commit
- [git_restore](#git_restore) - Restore the repository or specific files to a previous state
- [git_push](#git_push) - Push commits to a remote repository
- [git_log](#git_log) - Get the commit history of the repository
- [git_show](#git_show) - Get detailed information about a specific commit
- [git_status](#git_status) - Get the current status of the repository
- [git_diff](#git_diff) - Get the differences between commits, staged changes, or working directory

### [Web Operations](#web-operations)
- [brave_web_search](#brave_web_search) - Search the web using Brave Search API
- [fetch_web_page](#fetch_web_page) - Fetch content from a specified URL

### [Python Operations](#python-operations)
- [python_execute_file](#python_execute_file) - Execute a Python file and return its output
- [python_check_syntax](#python_check_syntax) - Check the syntax of Python code
- [python_execute_code](#python_execute_code) - Execute arbitrary Python code and return its output

### [SQLite Database Operations](#sqlite-database-operations)
- [sqlite_connect](#sqlite_connect) - Connect to a SQLite database file and verify the connection
- [sqlite_execute_query](#sqlite_execute_query) - Execute a SELECT query on SQLite database (read-only operations)
- [sqlite_execute_command](#sqlite_execute_command) - Execute INSERT, UPDATE, DELETE, or DDL commands on SQLite database
- [sqlite_get_schema](#sqlite_get_schema) - Get the complete database schema including all tables, columns, and their types
- [sqlite_list_tables](#sqlite_list_tables) - List all tables and views in the SQLite database

---

## File System Operations

### get_cwd
Get the current working directory.

**Parameters:** None

**Returns:** String containing information about the current working directory

---

### read_file
Read a file in the filesystem with optional line numbering, range selection, and debug formatting.

**Parameters:**
- `path` (required, string): Path and filename of the file to read
- `show_line_numbers` (optional, boolean): Whether to include line numbers (defaults to False)
- `start_line` (optional, integer): First line to read, 1-indexed (defaults to 1)
- `end_line` (optional, integer): Last line to read, 1-indexed, None for all lines (defaults to None)
- `show_repr` (optional, boolean): Whether to show Python's repr() of each line, revealing whitespace and special characters (defaults to False)

**Returns:** String containing the file contents (potentially formatted with line numbers or repr), or an error message if reading fails

---

### write_file
Write content to a file in the filesystem.

**Parameters:**
- `path` (required, string): Path and filename of the file to write
- `content` (required, string): The content to write to the file

**Returns:** String containing confirmation message indicating success or failure

---

### append_file
Append content to an existing file in the filesystem.

**Parameters:**
- `path` (required, string): Path and filename of the file to append to
- `content` (required, string): The content to append to the file

**Returns:** String containing confirmation message indicating success or failure

---

### edit_file
Make a line-based edit to a file by replacing old_text with new_text. The old_text must appear exactly once in the file for safety.

**Parameters:**
- `path` (required, string): Path and filename of the file to edit
- `old_text` (required, string): Text to be replaced (must match exactly once)
- `new_text` (required, string): Replacement text
- `dry_run` (optional, boolean): If True, just return the diff without making changes (defaults to False)

**Returns:** String containing confirmation message with diff showing changes, or error message if editing fails

---

## Directory Operations

### create_directory
Create a new directory in the filesystem.

**Parameters:**
- `path` (required, string): Path of the directory to create

**Returns:** String containing confirmation message indicating success or failure

---

### list_directory
List the contents of a directory in the filesystem.

**Parameters:**
- `path` (optional, string): Path of the directory to list. If not provided, lists the current working directory

**Returns:** String containing a list of files and directories in the specified path

---

### copy_file
Copy a file from source to destination.

**Parameters:**
- `source` (required, string): Path to the source file to copy
- `destination` (required, string): Path where the file should be copied to

**Returns:** String containing confirmation message indicating success or failure

---

### remove_file
Remove/delete a single file.

**Parameters:**
- `path` (required, string): Path to the file to delete

**Returns:** String containing confirmation message indicating success or failure

---

### remove_directory
Remove/delete a directory and all its contents.

**Parameters:**
- `path` (required, string): Path to the directory to delete

**Returns:** String containing confirmation message indicating success or failure

---

### copy_directory
Copy a directory and all its contents to a new location.

**Parameters:**
- `source` (required, string): Path to the source directory to copy
- `destination` (required, string): Path where the directory should be copied to

**Returns:** String containing confirmation message indicating success or failure

---

## Git Operations

### git_clone
Clone a git repository using HTTPS.

**Parameters:**
- `repo_url` (required, string): The HTTPS URL of the repository to clone
- `target_path` (optional, string): The path where to clone the repository

**Returns:** String containing confirmation message indicating success or failure

---

### git_commit
Stage all changes and create a commit.

**Parameters:**
- `message` (required, string): The commit message
- `path` (optional, string): The path to the git repository (defaults to current directory)

**Returns:** String containing confirmation message indicating success or failure

---

### git_restore
Restore the repository or specific files to a previous state.

**Parameters:**
- `commit_hash` (optional, string): The commit hash to restore to. If not provided, unstages all changes
- `path` (optional, string): The path to the git repository (defaults to current directory)
- `files` (optional, list): List of specific files to restore. If not provided, restores everything

**Returns:** String containing confirmation message indicating success or failure

---

### git_push
Push commits to a remote repository.

**Parameters:**
- `remote` (optional, string): The remote name (defaults to 'origin')
- `branch` (optional, string): The branch name to push to (defaults to 'main')
- `path` (optional, string): The path to the git repository (defaults to current directory)

**Returns:** String containing confirmation message indicating success or failure

---

### git_log
Get the commit history of the repository.

**Parameters:**
- `path` (optional, string): The path to the git repository (defaults to current directory)
- `max_count` (optional, integer): Maximum number of commits to return
- `since` (optional, string): Get commits since this date (e.g., "2024-01-01" or "1 week ago")

**Returns:** String containing JSON formatted commit history with hash, author, date, and message for each commit

---

### git_show
Get detailed information about a specific commit.

**Parameters:**
- `commit_hash` (required, string): The hash of the commit to inspect
- `path` (optional, string): The path to the git repository (defaults to current directory)

**Returns:** String containing JSON formatted commit details including metadata and changed files

---

### git_status
Get the current status of the repository.

**Parameters:**
- `path` (optional, string): The path to the git repository (defaults to current directory)

**Returns:** String containing JSON formatted repository status including staged, unstaged, and untracked changes

---

### git_diff
Get the differences between commits, staged changes, or working directory.

**Parameters:**
- `path` (optional, string): The path to the git repository (defaults to current directory)
- `commit1` (optional, string): First commit hash for comparison
- `commit2` (optional, string): Second commit hash for comparison
- `staged` (optional, boolean): If True, show staged changes (ignored if commits are specified)
- `file_path` (optional, string): Path to specific file to diff

**Returns:** String containing JSON formatted diff information including summary (files changed, total additions/deletions) and detailed changes per file with hunks showing exact line modifications

---

## Web Operations

### brave_web_search
Search the web using Brave Search API. The responses here only contain summaries. Use fetch_web_page to get the full contents of interesting search results.

**Parameters:**
- `query` (required, string): The search query to submit to Brave
- `count` (optional, integer): The number of results to return, defaults to 10

**Returns:** Object containing JSON formatted search results or error information from the Brave Search API

---

### fetch_web_page
Fetch content from a specified URL. This is a good tool to use after doing a brave_web_search, in order to get more details from interesting search results.

**Parameters:**
- `url` (required, string): The URL to fetch content from
- `headers` (optional, dictionary): Custom headers to include in the request, defaults to a standard User-Agent
- `timeout` (optional, integer): Request timeout in seconds, defaults to 30
- `clean` (optional, boolean): Whether to extract only the main content, defaults to True

**Returns:** String containing the cleaned web page content as text, or an error object if the request fails

---

## Python Operations

### python_execute_file
Execute a Python file and return its output.

**Parameters:**
- `file_path` (required, string): Path to the Python file to execute

**Returns:** String containing the output of the execution or an error message if execution fails

---

### python_check_syntax
Check the syntax of Python code.

**Parameters:**
- `code` (optional, string): Python code to check
- `file_path` (optional, string): Path to a Python file to check

**Returns:** String containing the result of the syntax check

---

### python_execute_code
Execute arbitrary Python code and return its output.

**Parameters:**
- `code` (required, string): Python code to execute

**Returns:** String containing the output of the execution or an error message if execution fails

---

## SQLite Database Operations

### sqlite_connect
Connect to a SQLite database file and verify the connection.

**Parameters:**
- `database_path` (required, string): Path to the SQLite database file

**Returns:** String containing confirmation message with basic database info, or error message if connection fails

---

### sqlite_execute_query
Execute a SELECT query on SQLite database (read-only operations).

**Parameters:**
- `database_path` (required, string): Path to the SQLite database file
- `query` (required, string): SQL SELECT query to execute
- `limit` (optional, integer): Maximum number of rows to return (defaults to 1000)
- `timeout` (optional, integer): Query timeout in seconds (defaults to 30)

**Returns:** String containing JSON formatted results with columns and rows, or error message if execution fails

---

### sqlite_execute_command
Execute INSERT, UPDATE, DELETE, or DDL commands on SQLite database.

**Parameters:**
- `database_path` (required, string): Path to the SQLite database file
- `command` (required, string): SQL command to execute (INSERT, UPDATE, DELETE, CREATE, DROP, etc.)
- `timeout` (optional, integer): Command timeout in seconds (defaults to 30)

**Returns:** String containing confirmation message with affected rows count, or error message if execution fails

---

### sqlite_get_schema
Get the complete database schema including all tables, columns, and their types.

**Parameters:**
- `database_path` (required, string): Path to the SQLite database file

**Returns:** String containing JSON formatted schema information, or error message if retrieval fails

---

### sqlite_list_tables
List all tables and views in the SQLite database.

**Parameters:**
- `database_path` (required, string): Path to the SQLite database file

**Returns:** String containing JSON formatted list of tables and views, or error message if retrieval fails

---

## Quick Reference

### File System
- `get_cwd` - Get current directory
- `read_file` - Read file contents
- `write_file` - Write to file
- `append_file` - Append to file
- `edit_file` - Edit file content
- `create_directory` - Create directory
- `list_directory` - List directory contents
- `copy_file` - Copy file
- `remove_file` - Delete file
- `remove_directory` - Delete directory
- `copy_directory` - Copy directory

### Git
- `git_clone` - Clone repository
- `git_commit` - Commit changes
- `git_restore` - Restore files/repo
- `git_push` - Push to remote
- `git_log` - View commit history
- `git_show` - Show commit details
- `git_status` - Check repo status
- `git_diff` - Show differences

### Web
- `brave_web_search` - Search the web
- `fetch_web_page` - Fetch webpage content

### Python
- `python_execute_file` - Run Python file
- `python_check_syntax` - Check Python syntax
- `python_execute_code` - Execute Python code

### SQLite
- `sqlite_connect` - Connect to database
- `sqlite_execute_query` - Run SELECT queries
- `sqlite_execute_command` - Run INSERT/UPDATE/DELETE/DDL
- `sqlite_get_schema` - Get database schema
- `sqlite_list_tables` - List tables and views
