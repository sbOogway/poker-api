from fastcrud import FastCRUD

from ..models.hand_user import HandUser
from ..schemas.hand_user import HandUserCreate, HandUserCreateInternal, HandUserRead, HandUserUpdate, HandUserUpdateInternal, HandUserDelete

CRUDHandUser = FastCRUD[HandUserCreate, HandUserCreateInternal, HandUserRead, HandUserUpdate, HandUserUpdateInternal, HandUserDelete]
crud_hands_user = CRUDHandUser(HandUser)