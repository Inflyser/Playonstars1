from fastapi import APIRouter, HTTPException, Depends
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
        # Создаем настройки по умолчанию
        settings = crud.update_game_settings(db)
    
    if password != settings.admin_password:
        raise HTTPException(status_code=401, detail="Неверный пароль админа")
    
    return {
        "status": "success", 
        "message": "Авторизация успешна",
        "settings": {
            "crash_rtp": settings.crash_rtp,
            "crash_min_multiplier": settings.crash_min_multiplier,
            "crash_max_multiplier": settings.crash_max_multiplier
        }
    }

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
    old_password = admin_data.get("old_password", "")
    new_password = admin_data.get("new_password", "")
    
    if not new_password or len(new_password) < 4:
        raise HTTPException(status_code=400, detail="Новый пароль слишком короткий")
    
    # Проверяем старый пароль
    settings = crud.get_game_settings(db)
    if old_password != settings.admin_password:
        raise HTTPException(status_code=401, detail="Неверный старый пароль")
    
    # Меняем пароль
    updated = crud.update_game_settings(db=db, admin_password=new_password)
    
    return {"status": "success", "message": "Пароль успешно изменен"}