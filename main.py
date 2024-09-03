from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi_htmx import htmx_init
from sqlalchemy.orm import Session

from app import crud
from app.models import SessionLocal, init_db

# Инициализация FastAPI и HTMX
app = FastAPI()
templates = Jinja2Templates(directory="app/templates")
htmx_init(templates=templates)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

# Главная страница с отображением списка задач и детализированной области
@app.get("/", response_class=HTMLResponse)
async def read_tasks(request: Request, db: Session = Depends(get_db)):
    tasks = crud.get_tasks(db)
    return templates.TemplateResponse("index.html", {"request": request, "tasks": tasks})

# Детализированная информация по задаче (обновляется через HTMX)
@app.get("/task/{task_id}", response_class=HTMLResponse)
async def read_task(task_id: int, request: Request, db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id)
    return templates.TemplateResponse("task_detail.html", {"request": request, "task": task})

# Добавление новой задачи и обновление списка с открытием новой задачи
@app.post("/task/add", response_class=HTMLResponse)
async def add_task(request: Request, title: str = Form(...), description: str = Form(...),
                   db: Session = Depends(get_db)):
    new_task = crud.create_task(db, title=title, description=description)
    tasks = crud.get_tasks(db)
    # Обновляем список задач
    task_list_html = templates.TemplateResponse("task_item.html", {"request": request, "tasks": tasks}).body.decode("utf-8")
    response_html = f"""
    {task_list_html}
    <script>
        hx.get('/task/{new_task.id}', {{target: '#task-detail', swap: 'innerHTML'}});
        document.querySelector('form').reset();
    </script>
    """
    return HTMLResponse(content=response_html)


@app.post("/task/delete/{task_id}", response_class=HTMLResponse)
async def delete_task(task_id: int, request: Request, db: Session = Depends(get_db)):
    # Удаление задачи из базы данных
    crud.delete_task(db, task_id)
    response_html = f"""
    <div hx-swap-oob="outerHTML" id="task-{task_id}"></div>
    <div id="task-detail" hx-swap-oob="innerHTML"></div>
    """
    return HTMLResponse(content=response_html)




@app.post("/task/update/{task_id}", response_class=HTMLResponse)
async def update_task(task_id: int, request: Request, completed: bool = Form(False), db: Session = Depends(get_db)):
    crud.update_task_status(db, task_id, completed)
    task = crud.get_task(db, task_id)
    return templates.TemplateResponse("task_detail.html", {"request": request, "task": task})




if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
