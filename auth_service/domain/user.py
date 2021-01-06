from dataclasses import dataclass

from ca_util import DomainModel


@dataclass
class UserEntity(DomainModel):
    id: int
    username: str

    def get_user_id(self):
        return self.id

    @classmethod
    def from_dict(cls, a_dict=None, **kwargs):
        if a_dict is None:
            a_dict = kwargs

        return cls(**a_dict)

    def to_dict(self):
        return dict(id=self.id, username=self.username)
