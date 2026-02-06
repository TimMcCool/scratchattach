import asyncio
import util
import warnings
import pytest


@pytest.mark.asyncio
async def test_async_login():
    if not util.credentials_available():
        warnings.warn("Skipped test_activity because there were no credentials available.")
        return
    async with await util.async_session() as sess:
        print(sess.user_id)
        await sess.update()
        print(repr(sess))


if __name__ == "__main__":
    asyncio.run(test_async_login())
