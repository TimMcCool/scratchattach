import httpx

client = httpx.AsyncClient()


async def get_home() -> str:
    resp = await client.get("https://scratch.mit.edu")
    return resp.text


if __name__ == "__main__":
    import asyncio

    async def main():
        print(await get_home())

    asyncio.run(main())
