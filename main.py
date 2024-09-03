from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app import crud
from app.deps import get_db, lifespan, templates
from app.task_route import router as task_route

app = FastAPI(lifespan=lifespan)
app.include_router(task_route, prefix=f'/task', tags=['task'])


@app.get("/", response_class=HTMLResponse)
async def read_tasks(request: Request, db: Session = Depends(get_db)):
    tasks = crud.get_tasks(db)
    return templates.TemplateResponse("index.html", {"request": request, "tasks": tasks})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
