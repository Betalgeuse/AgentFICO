"""AgentFICO API main entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import contract_router, score_router
from .routes.agents import router as agents_router

app = FastAPI(
    title="AgentFICO API",
    description="AI Agent Credit Scoring System",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(score_router, prefix="/v1")
app.include_router(contract_router, prefix="/v1")
app.include_router(agents_router, prefix="/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {"name": "AgentFICO API", "version": "0.1.0", "docs": "/docs"}
