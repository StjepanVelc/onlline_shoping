from routes import app
from fastapi.responses import JSONResponse
from services.exceptions import ValidationError

@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )