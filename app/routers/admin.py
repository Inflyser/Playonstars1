from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database import crud

router = APIRouter()

@router.post("/admin/login")
async def admin_login(admin_data: dict, db: Session = Depends(get_db)):
    """Простая авторизация по паролю"""
    password = admin_data.get("password", "")
    
    settings = crud.get_game_settings(db)
    if not settings:
        # Создаем настройки по умолчанию с паролем "admin"
        settings = crud.update_game_settings(db, admin_password="admin")
    
    if password != settings.admin_password:
        raise HTTPException(status_code=401, detail="Неверный пароль админа")
    
    return {"status": "success", "message": "Авторизация успешна"}

@router.post("/admin/update")
async def update_settings(admin_data: dict, db: Session = Depends(get_db)):
    """Обновление настроек - требует пароль админа"""
    password = admin_data.get("password", "")
    new_rtp = admin_data.get("crash_rtp")
    new_min = admin_data.get("crash_min_multiplier")
    new_max = admin_data.get("crash_max_multiplier")
    
    # Проверяем пароль
    settings = crud.get_game_settings(db)
    if password != settings.admin_password:
        raise HTTPException(status_code=401, detail="Неверный пароль админа")
    
    # Простая валидация
    if new_rtp is not None and not (0.5 <= new_rtp <= 0.99):
        raise HTTPException(400, "RTP должен быть между 0.5 и 0.99")
    
    # Обновляем настройки
    updated = crud.update_game_settings(
        db=db,
        crash_rtp=new_rtp,
        crash_min_multiplier=new_min,
        crash_max_multiplier=new_max
    )
    
    return {
        "status": "success",
        "message": "Настройки обновлены",
        "settings": {
            "crash_rtp": updated.crash_rtp,
            "crash_min_multiplier": updated.crash_min_multiplier,
            "crash_max_multiplier": updated.crash_max_multiplier
        }
    }

@router.post("/admin/change-password")
async def change_password(admin_data: dict, db: Session = Depends(get_db)):
    """Смена пароля админа"""
    old_password = admin_data.get("old", "")
    new_password = admin_data.get("new", "")
    
    if not new_password or len(new_password) < 4:
        raise HTTPException(status_code=400, detail="Новый пароль слишком короткий")
    
    settings = crud.get_game_settings(db)
    if old_password != settings.admin_password:
        raise HTTPException(status_code=401, detail="Неверный старый пароль")
    
    crud.update_game_settings(db=db, admin_password=new_password)
    return {"status": "success", "message": "Пароль успешно изменен"}


@router.get("/admin/check-status")
async def check_admin_status(
    request: Request,
    db: Session = Depends(get_db)
):
    """Проверяем является ли пользователь админом"""
    telegram_id = request.session.get("telegram_id")
    if not telegram_id:
        return {"isAdmin": False}
    
    is_admin = crud.is_user_admin(db, telegram_id)
    return {"isAdmin": is_admin}