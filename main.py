from routes import app
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from services.exceptions import ValidationError

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )