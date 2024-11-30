from fastapi import FastAPI


app = FastAPI()


@app.get("/")
async def main():
    return {
        "message": "Welcome to Code Guru AI -"
                   " your Assignment Auto-Review Tool!"
    }
