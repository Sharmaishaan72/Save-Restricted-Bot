from .. import config 

def access_only(func):
    """only people in config will be able to access the files"""
    async def wrapper(client, message, *args, **kwargs):
        if message.from_user and message.from_user.id in config.config.owner_ids:
            return await func(client, message, *args, **kwargs)
        return
    return wrapper