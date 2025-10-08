from fastcrud import FastCRUD

from ..models.hand import Hand
from ..schemas.hand import HandCreate, HandCreateInternal, HandRead, HandUpdate, HandUpdateInternal, HandDelete

CRUDHand = FastCRUD[HandCreate, HandCreateInternal, HandRead, HandUpdate, HandUpdateInternal, HandDelete]
crud_hands = CRUDHand(Hand)