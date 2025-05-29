import logging
import uvicorn
from fastapi import FastAPI
from app.config import get_settings
from app.routers.library_router import router as lib_router
from app.routers.document_router import router as doc_router
from app.routers.chunk_router import router as chunk_router

# Configure root logger
logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    level=logging.INFO,
)

settings = get_settings()
app = FastAPI(title="Vector DB API", debug=settings.DEBUG)

app.include_router(lib_router)
app.include_router(doc_router)
app.include_router(chunk_router)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG,
        log_config=None,
    )
