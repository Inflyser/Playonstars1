from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.dependencies import get_current_admin, require_permission
from app.database import crud

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/crash-settings")
async def get_crash_settings(
    db: Session = Depends(get_db),
    admin: dict = Depends(require_permission("manage_games"))
):
    """Получить текущие настройки краш-игры"""
    settings = crud.get_crash_game_settings(db)
    if not settings:
        raise HTTPException(404, "Настройки не найдены")
    
    return {
        "rtp": settings.rtp,
        "house_edge": settings.house_edge,
        "min_multiplier": settings.min_multiplier,
        "max_multiplier": settings.max_multiplier,
        "crash_point_distribution": settings.crash_point_distribution,
        "volatility": settings.volatility,
        "is_active": settings.is_active
    }

@router.post("/crash-settings")
async def update_crash_settings(
    settings_data: dict,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_permission("manage_games"))
):
    """Обновить настройки краш-игры"""
    try:
        # Валидация данных
        if 'rtp' in settings_data and not (0.5 <= settings_data['rtp'] <= 0.99):
            raise HTTPException(400, "RTP должен быть между 0.5 и 0.99")
        
        if 'house_edge' in settings_data and not (0.01 <= settings_data['house_edge'] <= 0.5):
            raise HTTPException(400, "Комиссия должна быть между 1% и 50%")
        
        settings = crud.update_crash_game_settings(db, settings_data)
        
        return {
            "status": "success",
            "message": "Настройки обновлены",
            "settings": {
                "rtp": settings.rtp,
                "house_edge": settings.house_edge,
                "min_multiplier": settings.min_multiplier,
                "max_multiplier": settings.max_multiplier,
                "volatility": settings.volatility,
                "distribution": settings.crash_point_distribution
            }
        }
        
    except Exception as e:
        raise HTTPException(500, f"Ошибка обновления настроек: {str(e)}")

@router.get("/game-stats")
async def get_game_stats(
    db: Session = Depends(get_db),
    admin: dict = Depends(require_permission("view_stats"))
):
    """Статистика игры для админки"""
    stats = crud.get_game_stats(db)
    
    # Добавляем текущие теоретические настройки
    settings = crud.get_crash_game_settings(db)
    stats["theoretical_rtp"] = settings.rtp if settings else 0.95
    stats["house_edge"] = settings.house_edge if settings else 0.05
    
    return stats