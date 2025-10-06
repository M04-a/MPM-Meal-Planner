import uvicorn
from meal.api.api_run import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)