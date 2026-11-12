class UnitOfWork:
    """Una confirmación por caso de uso; flush de repositorios no confirma."""
    def __init__(self, session):
        self._session = session

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        if exc_type is not None:
            self._session.rollback()
            return False
        try:
            self._session.commit()
        except Exception:
            self._session.rollback()
            raise
        return False
