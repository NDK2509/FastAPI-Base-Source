from sqlmodel import Session


class BaseUseCase:
    def __init__(self, session: Session):
        self.session = session

    def invoke(self, *args, **kwargs):
        raise NotImplementedError