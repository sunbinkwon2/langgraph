docker run --rm -it -v $(pwd):/app mypython \
  watchmedo auto-restart --directory=/app --pattern="*.py" --recursive -- \
  python main.py
