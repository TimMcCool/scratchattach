import os
import asyncio

import scratchattach.async_api as sa
from dotenv import load_dotenv

load_dotenv()


async def main():
    # resp = await sa.login(os.environ["SADEMOU"] + "hello", os.environ["SADEMOP"])
    resp = await sa.login_by_id(os.environ["SADEMOID"])
    print(resp)


if __name__ == "__main__":
    asyncio.run(main())
