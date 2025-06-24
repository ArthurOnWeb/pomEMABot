# database/crud.py

from sqlalchemy.orm import Session
from database.models import Pair, PriceAlert

def get_pairs(db: Session, chat_id: int):
    return db.query(Pair).filter(Pair.chat_id == chat_id).all()

def add_pair(db: Session, chat_id: int, symbol: str, timeframe: str):
    pair = Pair(chat_id=chat_id, symbol=symbol, timeframe=timeframe)
    db.add(pair)
    try:
        db.commit()
        db.refresh(pair)
        return pair
    except:
        db.rollback()
        return None  # déjà existant ou erreur

def remove_pair(db: Session, chat_id: int, symbol: str):
    count = db.query(Pair).filter(
        Pair.chat_id == chat_id,
        Pair.symbol == symbol
    ).delete()
    db.commit()
    return count  # nombre de lignes supprimées


def add_price_alert(db: Session, chat_id: int, symbol: str, target_price: float, direction: str):
    alert = PriceAlert(
        chat_id=chat_id,
        symbol=symbol,
        target_price=target_price,
        direction=direction,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def get_price_alerts(db: Session, chat_id: int):
    return db.query(PriceAlert).filter(
        PriceAlert.chat_id == chat_id,
        PriceAlert.active == True,
    ).all()


def remove_price_alert(db: Session, alert_id: int):
    db.query(PriceAlert).filter(PriceAlert.id == alert_id).delete()
    db.commit()


def remove_price_alert_by_value(
    db: Session, chat_id: int, symbol: str, target_price: float
) -> int:
    """Supprime une alerte de prix identifiée par sa valeur."""
    count = (
        db.query(PriceAlert)
        .filter(
            PriceAlert.chat_id == chat_id,
            PriceAlert.symbol == symbol,
            PriceAlert.target_price == target_price,
            PriceAlert.active == True,
        )
        .delete()
    )
    db.commit()
    return count

