from typing import Generic, TypeVar
from sqlalchemy.orm import Session

Entity = TypeVar("Entity")

class Repository(Generic[Entity]):
    def __init__(self, session: Session, model: type[Entity]):
        self.session = session
        self.model = model

    def get(self, entity_id: int) -> Entity | None:
        return self.session.get(self.model, entity_id)

    def add(self, entity: Entity) -> Entity:
        self.session.add(entity)
        self.session.flush()
        return entity
