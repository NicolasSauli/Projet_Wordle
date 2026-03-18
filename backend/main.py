from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth_router, lobby_router, game_router

app = FastAPI(title="Wordle API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(lobby_router.router)
app.include_router(game_router.router)


@app.get("/")
def root():
    return {"message": "Wordle API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
