import sqlite3
import json
import os
from pathlib import Path

def sqlite_connect(database_path):
    """
    Connect to a SQLite database file and verify the connection.
    
    Args:
        database_path (str): Path to the SQLite database file.
        
    Returns:
        str: A confirmation message with basic database info, or an error message if connection fails.
    """
    try:
        # Validate path
        if not database_path:
            return "Error: Database path cannot be empty"
        
        # Convert to Path object for better handling
        db_path = Path(database_path)
        
        # Check if file exists (for existing databases)
        file_exists = db_path.exists()
        
        # Connect to database (creates file if it doesn't exist)
        conn = sqlite3.connect(database_path, timeout=30)
        cursor = conn.cursor()
        
        # Test the connection with a simple query
        cursor.execute("SELECT sqlite_version()")
        sqlite_version = cursor.fetchone()[0]
        
        # Get basic database info
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        table_count = cursor.fetchone()[0]
        
        conn.close()
        
        status = "Connected to existing database" if file_exists else "Created new database"
        return f"{status}: {database_path}\nSQLite version: {sqlite_version}\nTables found: {table_count}"
        
    except sqlite3.Error as e:
        return f"SQLite error connecting to database: {e}"
    except PermissionError:
        return f"Permission denied: {database_path}"
    except Exception as e:
        return f"Error connecting to database: {e}"

def sqlite_execute_query(database_path, query, limit=1000, timeout=30):
    """
    Execute a SELECT query on SQLite database (read-only operations).
    
    Args:
        database_path (str): Path to the SQLite database file.
        query (str): SQL SELECT query to execute.
        limit (int): Maximum number of rows to return (default 1000).
        timeout (int): Query timeout in seconds (default 30).
        
    Returns:
        str: JSON formatted results with columns and rows, or an error message if execution fails.
    """
    try:
        # Basic validation
        if not database_path or not query:
            return "Error: Database path and query cannot be empty"
        
        # Check if file exists
        if not os.path.isfile(database_path):
            return f"Error: Database file not found: {database_path}"
        
        # Basic safety check - only allow SELECT statements
        query_upper = query.strip().upper()
        if not query_upper.startswith('SELECT'):
            return "Error: Only SELECT queries are allowed. Use sqlite_execute_command for other operations."
        
        # Connect and execute
        conn = sqlite3.connect(database_path, timeout=timeout)
        conn.row_factory = sqlite3.Row  # Enable column name access
        cursor = conn.cursor()
        
        # Add LIMIT if not already present
        if 'LIMIT' not in query_upper:
            query = f"{query.rstrip(';')} LIMIT {limit}"
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Get column names
        columns = [description[0] for description in cursor.description] if cursor.description else []
        
        # Convert rows to list of dictionaries
        results = []
        for row in rows:
            results.append(dict(row))
        
        conn.close()
        
        # Format response
        response = {
            "success": True,
            "columns": columns,
            "row_count": len(results),
            "data": results
        }
        
        return json.dumps(response, indent=2)
        
    except sqlite3.Error as e:
        return f"SQLite error executing query: {e}"
    except PermissionError:
        return f"Permission denied: {database_path}"
    except Exception as e:
        return f"Error executing query: {e}"

def sqlite_execute_command(database_path, command, timeout=30):
    """
    Execute INSERT, UPDATE, DELETE, or DDL commands on SQLite database.
    
    Args:
        database_path (str): Path to the SQLite database file.
        command (str): SQL command to execute (INSERT, UPDATE, DELETE, CREATE, DROP, etc.).
        timeout (int): Command timeout in seconds (default 30).
        
    Returns:
        str: Confirmation message with affected rows count, or an error message if execution fails.
    """
    try:
        # Basic validation
        if not database_path or not command:
            return "Error: Database path and command cannot be empty"
        
        # Check if file exists
        if not os.path.isfile(database_path):
            return f"Error: Database file not found: {database_path}"
        
        # Basic safety check - prevent SELECT statements (use sqlite_execute_query instead)
        command_upper = command.strip().upper()
        if command_upper.startswith('SELECT'):
            return "Error: Use sqlite_execute_query for SELECT statements."
        
        # Connect and execute
        conn = sqlite3.connect(database_path, timeout=timeout)
        cursor = conn.cursor()
        
        cursor.execute(command)
        rows_affected = cursor.rowcount
        
        # Commit the transaction
        conn.commit()
        conn.close()
        
        return f"Command executed successfully. Rows affected: {rows_affected}"
        
    except sqlite3.Error as e:
        return f"SQLite error executing command: {e}"
    except PermissionError:
        return f"Permission denied: {database_path}"
    except Exception as e:
        return f"Error executing command: {e}"

def sqlite_get_schema(database_path):
    """
    Get the complete database schema including all tables, columns, and their types.
    
    Args:
        database_path (str): Path to the SQLite database file.
        
    Returns:
        str: JSON formatted schema information, or an error message if retrieval fails.
    """
    try:
        # Basic validation
        if not database_path:
            return "Error: Database path cannot be empty"
        
        # Check if file exists
        if not os.path.isfile(database_path):
            return f"Error: Database file not found: {database_path}"
        
        # Connect to database
        conn = sqlite3.connect(database_path, timeout=30)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("""
            SELECT name, type, sql 
            FROM sqlite_master 
            WHERE type IN ('table', 'view') 
            ORDER BY type, name
        """)
        tables_info = cursor.fetchall()
        
        schema = {
            "database": database_path,
            "tables": [],
            "views": []
        }
        
        # Process each table/view
        for name, obj_type, create_sql in tables_info:
            # Get column information
            cursor.execute(f"PRAGMA table_info({name})")
            columns_info = cursor.fetchall()
            
            columns = []
            for col_info in columns_info:
                columns.append({
                    "name": col_info[1],
                    "type": col_info[2],
                    "not_null": bool(col_info[3]),
                    "default_value": col_info[4],
                    "primary_key": bool(col_info[5])
                })
            
            obj_info = {
                "name": name,
                "columns": columns,
                "create_sql": create_sql
            }
            
            if obj_type == 'table':
                schema["tables"].append(obj_info)
            else:
                schema["views"].append(obj_info)
        
        conn.close()
        
        return json.dumps(schema, indent=2)
        
    except sqlite3.Error as e:
        return f"SQLite error getting schema: {e}"
    except PermissionError:
        return f"Permission denied: {database_path}"
    except Exception as e:
        return f"Error getting schema: {e}"

def sqlite_list_tables(database_path):
    """
    List all tables and views in the SQLite database.
    
    Args:
        database_path (str): Path to the SQLite database file.
        
    Returns:
        str: JSON formatted list of tables and views, or an error message if retrieval fails.
    """
    try:
        # Basic validation
        if not database_path:
            return "Error: Database path cannot be empty"
        
        # Check if file exists
        if not os.path.isfile(database_path):
            return f"Error: Database file not found: {database_path}"
        
        # Connect to database
        conn = sqlite3.connect(database_path, timeout=30)
        cursor = conn.cursor()
        
        # Get all tables and views
        cursor.execute("""
            SELECT name, type 
            FROM sqlite_master 
            WHERE type IN ('table', 'view') 
            ORDER BY type, name
        """)
        objects = cursor.fetchall()
        
        # Organize by type
        tables = []
        views = []
        
        for name, obj_type in objects:
            if obj_type == 'table':
                tables.append(name)
            else:
                views.append(name)
        
        conn.close()
        
        result = {
            "database": database_path,
            "tables": tables,
            "views": views,
            "total_tables": len(tables),
            "total_views": len(views)
        }
        
        return json.dumps(result, indent=2)
        
    except sqlite3.Error as e:
        return f"SQLite error listing tables: {e}"
    except PermissionError:
        return f"Permission denied: {database_path}"
    except Exception as e:
        return f"Error listing tables: {e}"
