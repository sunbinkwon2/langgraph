docker run --rm -it -v $(pwd):/app langgraph:1.0.1 bash
  # watchmedo auto-restart --directory=/app --pattern="*.py" --recursive -- \
  # python3 main.py
