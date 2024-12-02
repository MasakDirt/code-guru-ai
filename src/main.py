from fastapi import FastAPI

from src.code_guru.router import router as code_guru_router


app = FastAPI()

app.include_router(code_guru_router)


@app.get("/")
async def main():
    return {
        "message": "Welcome to Code Guru AI -"
                   " your Assignment Auto-Review Tool!"
    }
