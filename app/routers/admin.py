from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database import crud
from app.database.models import CrashGameSettings, CrashBetHistory, CrashGameResult

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/crash-settings")
async def get_crash_settings(db: Session = Depends(get_db)):
    """Получить текущие настройки краш-игры"""
    settings = crud.get_crash_game_settings(db)
    if not settings:
        # Создаем настройки по умолчанию
        settings = CrashGameSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
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
async def update_crash_settings(settings_data: dict, db: Session = Depends(get_db)):
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
async def get_game_stats(db: Session = Depends(get_db)):
    """Статистика игры для админки"""
    from sqlalchemy import func
    
    # Статистика по играм
    total_games = db.query(func.count(CrashGameResult.id)).scalar()
    total_bets = db.query(func.count(CrashBetHistory.id)).scalar()
    total_bet_amount = db.query(func.sum(CrashBetHistory.bet_amount)).scalar() or 0
    total_payout = db.query(func.sum(CrashBetHistory.win_amount)).scalar() or 0
    
    # Расчет реального RTP
    actual_rtp = (total_payout / total_bet_amount) if total_bet_amount > 0 else 0
    
    return {
        "total_games": total_games,
        "total_bets": total_bets,
        "total_bet_amount": round(total_bet_amount, 2),
        "total_payout": round(total_payout, 2),
        "house_profit": round(total_bet_amount - total_payout, 2),
        "actual_rtp": round(actual_rtp, 4),
        "theoretical_rtp": crud.get_crash_game_settings(db).rtp
    }