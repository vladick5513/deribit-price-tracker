from fastapi import FastAPI

from app.prices.router import router as prices_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Deribit index prices",
        version="1.0.0",
    )
    app.include_router(prices_router)

    @app.get("/health", include_in_schema=False)
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
