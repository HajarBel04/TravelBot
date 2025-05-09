import uvicorn
import os
from pathlib import Path

if __name__ == "__main__":
    # Get the port from environment or use default
    port = int(os.environ.get("PORT", 8000))
    
    # Run the FastAPI app
    uvicorn.run("src.api.app:app", host="0.0.0.0", port=port, reload=True)