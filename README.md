# Simple FastAPI Project

> [!WARNING]
> This project is currently under construction.

This is a minimal FastAPI application.

## Files
- `main.py` – the FastAPI app.
- `requirements.txt` – required dependencies.

## Setup
```bash
# Create a virtual environment (optional)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Run the server
```bash
uvicorn main:app --reload
```

Open your browser and go to `http://127.0.0.1:8000/` to see the JSON response.

## API Docs
FastAPI automatically generates interactive documentation:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
