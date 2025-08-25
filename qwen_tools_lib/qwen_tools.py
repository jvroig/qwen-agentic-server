def tools_to_string(tools_dict):
    """
    Convert the tools dictionary to a formatted string representation.
    
    Args:
        tools_dict (dict): Dictionary containing tool definitions.
        
    Returns:
        str: Formatted string describing all tools.
    """
    result = ""
    
    # Iterate through all tool categories
    for category, category_tools in tools_dict.items():
        # Iterate through each tool in the category
        for tool_name, tool_info in category_tools.items():
            # Add tool name and description
            result += f"-{tool_name}: {tool_info['description']}\n"
            
            # Add parameters
            result += "    Parameters:\n"
            if not tool_info['parameters']:
                result += "    None. This tool does not need a parameter.\n"
            else:
                for param in tool_info['parameters']:
                    required = "(required, " if param.get("required", True) else "(optional, "
                    result += f"    - {param['name']} {required}{param['type']}): {param['description']}\n"
            
            # Add return value
            result += f"    Returns: {tool_info['returns']}\n\n"
    
    return result


def get_tools_dict():
    """
    Define and return a dictionary of all available tools.
    
    Returns:
        dict: Dictionary containing all tool definitions organized by category.
    """
    tools = {
        "filesystem_tools": {
            "get_cwd": {
                "description": "Get the current working directory",
                "parameters": [],
                "returns": "String - information about the current working directory"
            },
            "read_file": {
                "description": "Read a file in the filesystem with optional line numbering, range selection, and debug formatting",
                "parameters": [
                    {"name": "path", "required": True, "type": "string", "description": "path and filename of the file to read"},
                    {"name": "show_line_numbers", "required": False, "type": "boolean", "description": "whether to include line numbers (defaults to False)"},
                    {"name": "start_line", "required": False, "type": "integer", "description": "first line to read, 1-indexed (defaults to 1)"},
                    {"name": "end_line", "required": False, "type": "integer", "description": "last line to read, 1-indexed, None for all lines (defaults to None)"},
                    {"name": "show_repr", "required": False, "type": "boolean", "description": "whether to show Python's repr() of each line, revealing whitespace and special characters (defaults to False)"}
                ],
                "returns": "String - the contents of the file (potentially formatted with line numbers or repr), or an error message if reading fails"
            },
            "write_file": {
                "description": "Write content to a file in the filesystem",
                "parameters": [
                    {"name": "path", "required": True, "type": "string", "description": "path and filename of the file to write"},
                    {"name": "content", "required": True, "type": "string", "description": "the content to write to the file"}
                ],
                "returns": "String - confirmation message indicating success or failure"
            },
            "append_file": {
                "description": "Append content to an existing file in the filesystem",
                "parameters": [
                    {"name": "path", "required": True, "type": "string", "description": "path and filename of the file to append to"},
                    {"name": "content", "required": True, "type": "string", "description": "the content to append to the file"}
                ],
                "returns": "String - confirmation message indicating success or failure"
            },
            "edit_file": {
                "description": "Make a line-based edit to a file by replacing old_text with new_text. The old_text must appear exactly once in the file for safety.",
                "parameters": [
                    {"name": "path", "required": True, "type": "string", "description": "path and filename of the file to edit"},
                    {"name": "old_text", "required": True, "type": "string", "description": "text to be replaced (must match exactly once)"},
                    {"name": "new_text", "required": True, "type": "string", "description": "replacement text"},
                    {"name": "dry_run", "required": False, "type": "boolean", "description": "if True, just return the diff without making changes (defaults to False)"}
                ],
                "returns": "String - confirmation message with diff showing changes, or error message if editing fails"
            },
            "create_directory": {
                "description": "Create a new directory in the filesystem",
                "parameters": [
                    {"name": "path", "required": True, "type": "string", "description": "path of the directory to create"}
                ],
                "returns": "String - confirmation message indicating success or failure"
            },
            "list_directory": {
                "description": "List the contents of a directory in the filesystem",
                "parameters": [
                    {"name": "path", "required": False, "type": "string", "description": "path of the directory to list. If not provided, lists the current working directory."}
                ],
                "returns": "String - a list of files and directories in the specified path"
            },
            "copy_file": {
                "description": "Copy a file from source to destination",
                "parameters": [
                    {"name": "source", "required": True, "type": "string", "description": "path to the source file to copy"},
                    {"name": "destination", "required": True, "type": "string", "description": "path where the file should be copied to"}
                ],
                "returns": "String - confirmation message indicating success or failure"
            },
            "remove_file": {
                "description": "Remove/delete a single file",
                "parameters": [
                    {"name": "path", "required": True, "type": "string", "description": "path to the file to delete"}
                ],
                "returns": "String - confirmation message indicating success or failure"
            },
            "remove_directory": {
                "description": "Remove/delete a directory and all its contents",
                "parameters": [
                    {"name": "path", "required": True, "type": "string", "description": "path to the directory to delete"}
                ],
                "returns": "String - confirmation message indicating success or failure"
            },
            "copy_directory": {
                "description": "Copy a directory and all its contents to a new location",
                "parameters": [
                    {"name": "source", "required": True, "type": "string", "description": "path to the source directory to copy"},
                    {"name": "destination", "required": True, "type": "string", "description": "path where the directory should be copied to"}
                ],
                "returns": "String - confirmation message indicating success or failure"
            }
        },
        
        "git_tools": {
            "git_clone": {
                "description": "Clone a git repository using HTTPS",
                "parameters": [
                    {"name": "repo_url", "required": True, "type": "string", "description": "The HTTPS URL of the repository to clone"},
                    {"name": "target_path", "required": False, "type": "string", "description": "The path where to clone the repository"}
                ],
                "returns": "String - confirmation message indicating success or failure"
            },
            "git_commit": {
                "description": "Stage all changes and create a commit",
                "parameters": [
                    {"name": "message", "required": True, "type": "string", "description": "The commit message"},
                    {"name": "path", "required": False, "type": "string", "description": "The path to the git repository (defaults to current directory)"}
                ],
                "returns": "String - confirmation message indicating success or failure"
            },
            "git_restore": {
                "description": "Restore the repository or specific files to a previous state",
                "parameters": [
                    {"name": "commit_hash", "required": False, "type": "string", "description": "The commit hash to restore to. If not provided, unstages all changes"},
                    {"name": "path", "required": False, "type": "string", "description": "The path to the git repository (defaults to current directory)"},
                    {"name": "files", "required": False, "type": "list", "description": "List of specific files to restore. If not provided, restores everything"}
                ],
                "returns": "String - confirmation message indicating success or failure"
            },
            "git_push": {
                "description": "Push commits to a remote repository",
                "parameters": [
                    {"name": "remote", "required": False, "type": "string", "description": "The remote name (defaults to 'origin')"},
                    {"name": "branch", "required": False, "type": "string", "description": "The branch name to push to (defaults to 'main')"},
                    {"name": "path", "required": False, "type": "string", "description": "The path to the git repository (defaults to current directory)"}
                ],
                "returns": "String - confirmation message indicating success or failure"
            },
            "git_log": {
                "description": "Get the commit history of the repository",
                "parameters": [
                    {"name": "path", "required": False, "type": "string", "description": "The path to the git repository (defaults to current directory)"},
                    {"name": "max_count", "required": False, "type": "integer", "description": "Maximum number of commits to return"},
                    {"name": "since", "required": False, "type": "string", "description": "Get commits since this date (e.g., \"2024-01-01\" or \"1 week ago\")"}
                ],
                "returns": "String - JSON formatted commit history with hash, author, date, and message for each commit"
            },
            "git_show": {
                "description": "Get detailed information about a specific commit",
                "parameters": [
                    {"name": "commit_hash", "required": True, "type": "string", "description": "The hash of the commit to inspect"},
                    {"name": "path", "required": False, "type": "string", "description": "The path to the git repository (defaults to current directory)"}
                ],
                "returns": "String - JSON formatted commit details including metadata and changed files"
            },
            "git_status": {
                "description": "Get the current status of the repository",
                "parameters": [
                    {"name": "path", "required": False, "type": "string", "description": "The path to the git repository (defaults to current directory)"}
                ],
                "returns": "String - JSON formatted repository status including staged, unstaged, and untracked changes"
            },
            "git_diff": {
                "description": "Get the differences between commits, staged changes, or working directory",
                "parameters": [
                    {"name": "path", "required": False, "type": "string", "description": "The path to the git repository (defaults to current directory)"},
                    {"name": "commit1", "required": False, "type": "string", "description": "First commit hash for comparison"},
                    {"name": "commit2", "required": False, "type": "string", "description": "Second commit hash for comparison"},
                    {"name": "staged", "required": False, "type": "boolean", "description": "If True, show staged changes (ignored if commits are specified)"},
                    {"name": "file_path", "required": False, "type": "string", "description": "Path to specific file to diff"}
                ],
                "returns": "String - JSON formatted diff information including: Summary (files changed, total additions/deletions) and Detailed changes per file with hunks showing exact line modifications"
            }
        },
        
        "web_tools": {
            "brave_web_search": {
                "description": "Search the web using Brave Search API. The responses here only contain summaries. Use fetch_web_page to get the full contents of interesting search results.",
                "parameters": [
                    {"name": "query", "required": True, "type": "string", "description": "the search query to submit to Brave"},
                    {"name": "count", "required": False, "type": "integer", "description": "the number of results to return, defaults to 10"}
                ],
                "returns": "Object - a JSON object containing search results or error information from the Brave Search API"
            },
            "fetch_web_page": {
                "description": "Fetch content from a specified URL. This is a good tool to use after doing a brave_web_search, in order to get more details from interesting search results.",
                "parameters": [
                    {"name": "url", "required": True, "type": "string", "description": "the URL to fetch content from"},
                    {"name": "headers", "required": False, "type": "dictionary", "description": "custom headers to include in the request, defaults to a standard User-Agent"},
                    {"name": "timeout", "required": False, "type": "integer", "description": "request timeout in seconds, defaults to 30"},
                    {"name": "clean", "required": False, "type": "boolean", "description": "whether to extract only the main content, defaults to True"}
                ],
                "returns": "String - the cleaned web page content as text, or an error object if the request fails"
            }
        },
        
        "python_tools": {
            "python_execute_file": {
                "description": "Execute a Python file and return its output",
                "parameters": [
                    {"name": "file_path", "required": True, "type": "string", "description": "Path to the Python file to execute"}
                ],
                "returns": "String - The output of the execution or an error message if execution fails"
            },
            "python_check_syntax": {
                "description": "Check the syntax of Python code",
                "parameters": [
                    {"name": "code", "required": False, "type": "string", "description": "Python code to check"},
                    {"name": "file_path", "required": False, "type": "string", "description": "Path to a Python file to check"}
                ],
                "returns": "String - Result of the syntax check"
            },
            "python_execute_code": {
                "description": "Execute arbitrary Python code and return its output",
                "parameters": [
                    {"name": "code", "required": True, "type": "string", "description": "Python code to execute"}
                ],
                "returns": "String - The output of the execution or an error message if execution fails"
            }
        },
        
        "sqlite_tools": {
            "sqlite_connect": {
                "description": "Connect to a SQLite database file and verify the connection",
                "parameters": [
                    {"name": "database_path", "required": True, "type": "string", "description": "Path to the SQLite database file"}
                ],
                "returns": "String - confirmation message with basic database info, or error message if connection fails"
            },
            "sqlite_execute_query": {
                "description": "Execute a SELECT query on SQLite database (read-only operations)",
                "parameters": [
                    {"name": "database_path", "required": True, "type": "string", "description": "Path to the SQLite database file"},
                    {"name": "query", "required": True, "type": "string", "description": "SQL SELECT query to execute"},
                    {"name": "limit", "required": False, "type": "integer", "description": "Maximum number of rows to return (defaults to 1000)"},
                    {"name": "timeout", "required": False, "type": "integer", "description": "Query timeout in seconds (defaults to 30)"}
                ],
                "returns": "String - JSON formatted results with columns and rows, or error message if execution fails"
            },
            "sqlite_execute_command": {
                "description": "Execute INSERT, UPDATE, DELETE, or DDL commands on SQLite database",
                "parameters": [
                    {"name": "database_path", "required": True, "type": "string", "description": "Path to the SQLite database file"},
                    {"name": "command", "required": True, "type": "string", "description": "SQL command to execute (INSERT, UPDATE, DELETE, CREATE, DROP, etc.)"},
                    {"name": "timeout", "required": False, "type": "integer", "description": "Command timeout in seconds (defaults to 30)"}
                ],
                "returns": "String - confirmation message with affected rows count, or error message if execution fails"
            },
            "sqlite_get_schema": {
                "description": "Get the complete database schema including all tables, columns, and their types",
                "parameters": [
                    {"name": "database_path", "required": True, "type": "string", "description": "Path to the SQLite database file"}
                ],
                "returns": "String - JSON formatted schema information, or error message if retrieval fails"
            },
            "sqlite_list_tables": {
                "description": "List all tables and views in the SQLite database",
                "parameters": [
                    {"name": "database_path", "required": True, "type": "string", "description": "Path to the SQLite database file"}
                ],
                "returns": "String - JSON formatted list of tables and views, or error message if retrieval fails"
            }
        }
    }
    
    return tools


def list_tools():
    """
    Get a formatted string description of all available tools.
    
    Returns:
        str: Formatted string describing all tools.
    """
    tools_dict = get_tools_dict()
    return tools_to_string(tools_dict)


def get_harmony_tools_format():
    """
    Get the Harmony format for tool definitions and calling instructions.
    
    Returns:
        str: Harmony-compatible tool definitions and instructions.
    """
    tools_dict = get_tools_dict()
    
    # Generate comprehensive tool definitions with detailed information
    tool_definitions = []
    
    for category, category_tools in tools_dict.items():
        # Add category header
        category_name = category.replace('_', ' ').title()
        tool_definitions.append(f"## {category_name}")
        tool_definitions.append("")
        
        for tool_name, tool_info in category_tools.items():
            # Tool name and description
            tool_definitions.append(f"### {tool_name}")
            tool_definitions.append(f"**Description**: {tool_info['description']}")
            
            # Parameters section
            if not tool_info['parameters']:
                tool_definitions.append("**Parameters**: None")
            else:
                tool_definitions.append("**Parameters**:")
                for param in tool_info['parameters']:
                    required_str = "required" if param.get("required", True) else "optional"
                    param_line = f"- `{param['name']}` ({required_str}, {param['type']}): {param['description']}"
                    tool_definitions.append(param_line)
            
            # Returns section
            tool_definitions.append(f"**Returns**: {tool_info['returns']}")
            tool_definitions.append("")
    
        # Generate TypeScript namespace for function signatures
        namespace_lines = ["namespace functions {"]

        for category, category_tools in tools_dict.items():
            for tool_name, tool_info in category_tools.items():
                # Build parameter type definition
                if not tool_info['parameters']:
                    param_type = "() => any"
                else:
                    param_parts = []
                    for param in tool_info['parameters']:
                        optional = "?" if not param.get("required", True) else ""
                        param_parts.append(f"{param['name']}{optional}: {param['type']}")
                    param_type = f"(_: {{{', '.join(param_parts)}}}) => any"

                # Add tool to namespace with description
                description = tool_info['description']
                namespace_lines.append(f"    // {description}")
                namespace_lines.append(f"    type {tool_name} = {param_type};")

        namespace_lines.append("}")

        harmony_format = f"""
        # Tools

        {chr(10).join(namespace_lines)}

        # Detailed Tool Descriptions

        {chr(10).join(tool_definitions)}

        """
    
    return harmony_format

def get_tools_format():
    """
    Get the format to use when making tool calls.
    
    Returns:
        str: Instructions for how to format tool calls.
    """
    import os
    
    # Check if Harmony mode is enabled to include Harmony-specific examples
    use_harmony = os.getenv('USE_OPENAI_HARMONY', 'false')
    
    ##Section 1: Universal tool calling
    tools_format = """

When you want to use a tool, make a tool call (no explanations) using this exact format:

[[qwen-tool-start]]
```
{
    "name": "tool_name",
    "input": {
        "param1": "value1",
        "param2": "value2"
    }
}
```
[[qwen-tool-end]]

Note that the triple backticks (```) are part of the format!

Example 1:
************************
User: What is your current working directory?
Assistant:
[[qwen-tool-start]]
```
{
    "name": "get_cwd",
    "input": ""
}
```
[[qwen-tool-end]]
**********************


Example 2:
************************
User: List the files in your current working directory.
Assistant:
[[qwen-tool-start]]
```
{
    "name": "list_directory",
    "input": {
        "path": "."
    }
}
```
[[qwen-tool-end]]
**********************

Example 3:
************************
User: Can you check the syntax of my Python code?
Assistant:
[[qwen-tool-start]]
```
{
    "name": "python_check_syntax",
    "input": {
        "code": "print('Hello world'"
    }
}
```
[[qwen-tool-end]]
**********************

"""

    #Section 2: Harmony-specific
    if use_harmony == 'true':
        tools_format += """For the "analysis" and "commentary" channels: 
- Use the same tool calling format as above when you need to use tools during "analysis" and "commentary" channels, and all problem-solving steps. 
- Always use the [[qwen-tool-start]] tag as part of the message to call the tool.
- Example:
    ***********
     Assistant:
     <|channel|>analysis<|message|>We need to query SQLite database. Use sqlite_execute_query. Query: SELECT COUNT(*) FROM orders JOIN customers ON orders.customer_id=customers.id WHERE orders.amount>50000 AND customers.department='Engineering'. Path: /example/path/to/tale.db. Then write JSON file with key num_big_orders. Use write_file.<|end|><|start|>assistant<|channel|>commentary to=tool.run code<|message|>[[qwen-tool-start]]\n```\n{\n    \"name\": \"sqlite_execute_query\",\n    \"input\": {\n        \"database_path\": \"/example/path/to/tale.db\",\n        \"query\": \"SELECT COUNT(*) AS num_big_orders FROM orders JOIN customers ON orders.customer_id=customers.id WHERE orders.amount>50000 AND customers.department='Engineering';\",\n        \"limit\": 1000\n    }\n}\n```\n[[qwen-tool-end]]
    ************

CONSTRAINT: ONLY ONE TOOL CALL IS ALLOWED PER MESSAGE
- This includes any appearance of the [[qwen-tool-start]] before your final <|message|>
- For example, this will fail:
    ***********
    Assistant:
    <|channel|>analysis<|message|>Now write JSON file. I should use [[qwen-tool-start]]\n```\n{\n    \"name\": \"write_file\",\n    \"input\": {\n        \"path\": \"/example/path/to/big_orders_count.json\",\n        \"content\": \"{\\n  \\\"num_big_orders\\\": 1\\n}\"\n    }\n}\n```\n[[qwen-tool-end]]<|end|><|start|>assistant<|channel|>commentary to=tool.run code<|message|>[[qwen-tool-start]]\n```\n{\n    \"name\": \"write_file\",\n    \"input\": {\n        \"path\": \"/example/path/to/big_orders_count.json\",\n        \"content\": \"{\\n  \\\"num_big_orders\\\": 1\\n}\"\n    }\n}\n```\n[[qwen-tool-end]]
    ************
- To avoid that, only use [[qwen-tool-start]] for the final message, like this:
    ***********
    Assistant:
    <|channel|>analysis<|message|>Now write JSON file.<|end|><|start|>assistant<|channel|>commentary to=tool.run code<|message|>[[qwen-tool-start]]\n```\n{\n    \"name\": \"write_file\",\n    \"input\": {\n        \"path\": \"/example/path/to/big_orders_count.json\",\n        \"content\": \"{\\n  \\\"num_big_orders\\\": 1\\n}\"\n    }\n}\n```\n[[qwen-tool-end]]
    ************

    """

    #Section 3: Final universal constraints
    tools_format += """Immediately end your response after calling a tool and the final triple backticks.

NOTE: User messages that start with "Tool result:" are actually TOOL MESSAGES (automated, from tool execution) and do not come from the user.

After receiving the results of a tool call, do not parrot everything back to the user.
Instead, just briefly summarize the results in 1-2 sentences.

"""
    return tools_format



print(tools_to_string(get_tools_dict()))