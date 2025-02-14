import uuid

from app.models import Item, ItemCreate

def create_item(*, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    pass
