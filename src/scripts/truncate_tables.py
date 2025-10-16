from ..app.crud.crud_hand import crud_hands
from ..app.crud.crud_account import crud_account
from ..app.crud.crud_hand_player import crud_hands_player
from ..app.crud.crud_game import crud_game
from ..app.crud.crud_session import crud_session
from ..app.crud.crud_player import crud_player

from ..app.core.db.database import async_get_db
import asyncio

async def main():
    session = async_get_db()
    db = await session.__anext__()


    # override_multiple_deletes is a custom patch on fast crud source code 
    # just add a boolean before the value error
    await crud_hands_player.db_delete(db, allow_multiple=True, override_multiple_deletes=True)        
    await crud_hands.db_delete(db, allow_multiple=True, override_multiple_deletes=True)        
    await crud_session.db_delete(db, allow_multiple=True, override_multiple_deletes=True)        
    await crud_account.db_delete(db, allow_multiple=True, override_multiple_deletes=True)        
    await crud_game.db_delete(db, allow_multiple=True, override_multiple_deletes=True)        
    await crud_player.db_delete(db, allow_multiple=True, override_multiple_deletes=True)        
    

if __name__ == "__main__":
    asyncio.run(main())