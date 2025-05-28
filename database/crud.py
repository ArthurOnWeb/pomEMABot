# database/crud.py

from sqlalchemy.orm import Session
from database.models import Pair

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
