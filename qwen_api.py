from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from openai import OpenAI
import os
import json
import time
import argparse
import sys
import qwen_tools_lib

from http import HTTPStatus
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)

# Global variables to store configuration
api_key = None
base_url = None
model_name = None
delay_secs = None
port = None

def load_configuration():
    """Load configuration from command line arguments with .env fallback"""
    global api_key, base_url, model_name, delay_secs, port
    
    parser = argparse.ArgumentParser(description='Qwen API Server')
    parser.add_argument('--api-key', type=str, help='API key for the service')
    parser.add_argument('--base-url', type=str, help='Base URL for the API endpoint')
    parser.add_argument('--model', type=str, help='Model name to use')
    parser.add_argument('--rate-limit', type=int, help='Rate limit pause in seconds')
    parser.add_argument('--port', type=int, default=5002, help='Port to run the server on (default: 5002)')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    
    args = parser.parse_args()
    
    # Load .env file as fallback
    load_dotenv()
    
    # Use command line arguments if provided, otherwise fall back to .env
    api_key = args.api_key or os.getenv('USE_API_KEY')
    base_url = args.base_url or os.getenv('USE_BASE_URL') 
    model_name = args.model or os.getenv('MODEL_NAME')
    delay_secs = args.rate_limit or int(os.getenv('RATE_LIMIT_PAUSE_SECS', 0))
    port = args.port
    
    # Validate required parameters
    if not api_key:
        print("Error: API key is required. Provide via --api-key or USE_API_KEY in .env")
        sys.exit(1)
    if not base_url:
        print("Error: Base URL is required. Provide via --base-url or USE_BASE_URL in .env")
        sys.exit(1)
    if not model_name:
        print("Error: Model name is required. Provide via --model or MODEL_NAME in .env")
        sys.exit(1)
    
    print(f"Configuration loaded:")
    print(f"  API Key: {'*' * len(api_key[:-4]) + api_key[-4:] if len(api_key) > 4 else '***'}")
    print(f"  Base URL: {base_url}")
    print(f"  Model: {model_name}")
    print(f"  Rate Limit: {delay_secs}s")
    print(f"  Port: {port}")
    
    return args.debug



@app.route('/api/chat', methods=['POST'])
def query_endpoint():
    try:
        # Parse JSON payload from the request
        payload = request.get_json()
        messages = payload.get('messages', [])
        temperature = float(payload.get('temperature', 0.7))
        max_output_tokens = int(payload.get('max_output_tokens', 5000))

        # Format messages (you can replace this with your actual logic)
        data = format_messages(messages)
        messages = data['messages']

        print("Received messages:", messages)

        # Use a generator to stream responses back to the frontend
        def generate_responses():
            yield from inference_loop(messages, temperature, max_output_tokens)

        # Return a streaming response with the correct content type
        return Response(generate_responses(), content_type='text/event-stream')

    except Exception as e:
        # Handle errors gracefully
        return {"error": str(e)}, 400


def inference_loop(messages, temperature=0.7, max_tokens=1000):
    while True:
        #Slight pause for rate limit observance
        time.sleep(delay_secs)

        client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            stream=True,
            stop=["[[qwen-tool-end]]"],
            temperature=temperature,
            max_tokens=max_tokens
        )

        # # Extract the assistant's response
        # assistant_response = response.choices[0].message.content
        # print("Assistant Response:", assistant_response)
        # messages.append({"role": "assistant", "content": assistant_response})
        # yield json.dumps({'role': 'assistant', 'content': assistant_response}) + "\n"

        # FULL STREAMING CODE STUB
        assistant_response = ""

        print(response)

        # Iterate through the streaming response
        for chunk in response:
            # Handle edge cases where choices might be empty or missing delta
            if not chunk.choices or not hasattr(chunk.choices[0], 'delta') or not chunk.choices[0].delta:
                continue
                
            if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content is not None:
                # Get the text chunk
                content = chunk.choices[0].delta.content
                
                # Accumulate the full response
                assistant_response += content
                
                # Stream the chunk to the frontend
                yield json.dumps({'role': 'assistant', 'content': content, 'type': 'chunk'}) + "\n"

        # After streaming is complete, add the full response to messages
        messages.append({"role": "assistant", "content": assistant_response})

        # Send a completion signal
        yield json.dumps({'role': 'assistant', 'content': '', 'type': 'done'}) + "\n"


        occurrences = assistant_response.count("[[qwen-tool-start]]")
        if occurrences > 1:
            #Multiple tool calls are not allowed
            ToolErrorMsg="Tool Call Error: Multiple tool calls found. Please only use one tool at a time."
            yield json.dumps({'role': 'tool_call', 'content': ToolErrorMsg}) + "\n"

            messages.append({"role": "user", "content": ToolErrorMsg})
            print(ToolErrorMsg)
        elif occurrences == 1:
            tool_call_data = None
            try:
                tool_call_data = parse_tool_call(assistant_response)
            except:
                print(f"No valid tool call found")
                tool_message = f"Tool result: No valid tool call found. Please make sure tool request is valid JSON, and escape necessary characters. Try again with better-formatted JSON"
                messages.append({"role": "user", "content": tool_message})
                yield json.dumps({'role': 'tool_call', 'content': tool_message}) + "\n"

            if tool_call_data:
                # Stream the tool call message back to the frontend
                # yield json.dumps({'role': 'tool_call', 'content': f"Tool call: {tool_call_data}"}) + "\n"

                # Execute the tool with the provided parameters
                tool_name = tool_call_data["name"]
                tool_input = tool_call_data.get("input", {})
                print(f"Executing tool: {tool_name} with input: {tool_input}")
                
                try:
                    # Execute the tool
                    tool_result = execute_tool(tool_name, tool_input)
                    print(f"Tool executed. Result: {tool_result}")
                    
                    # Add the tool result as a "user" message in the conversation
                    tool_message = f"Tool result: ```{tool_result}```"
                    messages.append({"role": "user", "content": tool_message})
                    
                    # Stream the tool result back to the frontend
                    yield json.dumps({'role': 'tool_call', 'content': tool_message}) + "\n"
                    
                except Exception as e:
                    # Handle tool execution errors gracefully - don't crash the connection
                    error_message = f"Tool execution error: {str(e)}"
                    print(f"Tool execution failed: {e}")
                    
                    # Add error message to conversation so LLM can see it and adapt
                    messages.append({"role": "user", "content": error_message})
                    yield json.dumps({'role': 'tool_call', 'content': error_message}) + "\n"

        else:
            # If no tool call, terminate the loop
            break

def format_messages(messages):
    model = ''
    endpoint = ''

    tools_available = qwen_tools_lib.list_tools()
    tools_format = qwen_tools_lib.get_tools_format()
    print(tools_available)
    print(tools_format)
    system_prompt = f"""You are Qwen-Max, an advanced AI model. You will assist the user with tasks, using tools available to you.

You have the following tools available:
{tools_available}

{tools_format}

"""
    system_message = {"role": "system", "content": system_prompt}
    messages.insert(0, system_message)

    return {'messages': messages, 'model': model, 'endpoint': endpoint } 

def parse_tool_call(response):
    """
    Parses the tool call information from an LLM response.
    
    Args:
        response (str): The LLM's response containing the tool call.
        
    Returns:
        dict: A dictionary containing the tool name and input parameters.
              Example: {"name": "tool_name", "input": {"param1": "value1", "param2": "value2"}}
              
    Raises:
        ValueError: If the tool call format is invalid or cannot be parsed.
    """
    # Define markers for the tool call block
    start_marker_pos = response.find("[[qwen-tool-start]]")
    
    try:
        if start_marker_pos == -1:
            raise ValueError("Tool call markers not found in the response.")
        
        json_start = response.find("{", start_marker_pos)
        
        if json_start == -1:
            raise ValueError("No JSON object found between tool call markers.")
        
        # Find the matching closing curly brace
        # This handles nested JSON objects properly
        brace_count = 1
        json_end = json_start + 1
        
        while brace_count > 0:
            if response[json_end] == '{':
                brace_count += 1
            elif response[json_end] == '}':
                brace_count -= 1
            json_end += 1
        
        if brace_count != 0:
            raise ValueError("Unbalanced JSON object in tool call.")
        
        # Extract the complete JSON object
        tool_call_block = response[json_start:json_end]
        
        # Parse the JSON content
        tool_call_data = json.loads(tool_call_block)
        
        # Validate the structure of the tool call
        if "name" not in tool_call_data:
            raise ValueError("Tool call must include a 'name' field.")

        return tool_call_data

    except json.JSONDecodeError as e:
        print(f"Failed to parse tool call JSON: {e}. Please make sure the tool call is valid JSON")
        raise
    
    except ValueError as e:
        print(f"Value Error: {e}.")
        raise

def execute_tool(tool_name, tool_input):
    """
    Executes the specified tool with the given input parameters.

    Args:
        tool_name (str): The name of the tool to execute.
        tool_input (dict): A dictionary containing the input parameters for the tool.

    Returns:
        str: The result of the tool execution.

    Raises:
        ValueError: If the tool_name is invalid or the tool function raises an error.
    """

    # Check if the tool exists
    if hasattr(qwen_tools_lib, tool_name):
        tool = getattr(qwen_tools_lib, tool_name)
        if callable(tool):
            pass
        else:
            raise ValueError(f"Unknown tool or uncallable tool: {tool_name}")
    else:
        raise ValueError(f"Unknown tool: {tool_name}")

    try:
        # Execute the tool function with the provided input
        if tool_input == "":
            result = tool()
        else:
            result = tool(**tool_input)
        return result
    except Exception as e:
        raise ValueError(f"Error executing tool '{tool_name}': {e}")

if __name__ == '__main__':
    debug_mode = load_configuration()
    app.run(debug=debug_mode, port=port)
