source venv/bin/activate
venv/bin/pip install -r requirements.txt

# Pass model name if provided as first argument
if [ -n "$1" ]; then
    venv/bin/python qwen_api.py --model "$1"
else
    venv/bin/python qwen_api.py
