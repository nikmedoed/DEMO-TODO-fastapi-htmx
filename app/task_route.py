from fastapi import Depends, Form, APIRouter
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import HTMLResponse

from app import crud
from app.deps import get_db, templates

router = APIRouter()


@router.get("/{task_id}", response_class=HTMLResponse)
async def read_task(task_id: int, request: Request, db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id)
    return templates.TemplateResponse("task_detail.html", {"request": request, "task": task})


@router.post("/add", response_class=HTMLResponse)
async def add_task(request: Request, title: str = Form(...), description: str = Form(...),
                   db: Session = Depends(get_db)):
    new_task = crud.create_task(db, title=title, description=description)
    task_html = (templates.TemplateResponse(
        "task_item.html",
        {"request": request, "task": new_task})
                 .body.decode("utf-8"))

    return HTMLResponse(content=task_html)


@router.post("/delete/{task_id}", response_class=HTMLResponse)
async def delete_task(task_id: int, request: Request, db: Session = Depends(get_db)):
    crud.delete_task(db, task_id)

    response_html = f"""
    <div id="task-{task_id}" hx-swap-oob="delete"></div>
    <div id="task-detail" hx-swap-oob="innerHTML"></div>
    """

    return HTMLResponse(content=response_html)


@router.post("/update/{task_id}", response_class=HTMLResponse)
async def update_task(task_id: int, request: Request, completed: bool = Form(False), db: Session = Depends(get_db)):
    # Обновление статуса задачи в базе данных
    crud.update_task_status(db, task_id, completed)

    # Ничего не возвращаем, так как обновления HTML не требуется
    return HTMLResponse(status_code=204)  # 204 No Content
