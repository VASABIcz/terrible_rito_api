import asyncio
import aiohttp
from bucket import bucket


# TODO rewrite bucket
# if oyr bucket gets out of sync with ratelimit we are fucked
# TODO implement some sort of ratelimit sync mechanism


class LeagueOfWeebs:
    """
    AYAYA
    """
    #GLOBAL
    GLOBAL_1 = (20, 1)
    GLOBAL_2 = (100, 120)


    def __init__(self, key):
        self.key = key
        self.session = aiohttp.ClientSession(headers=self.headers)
        self.loop = asyncio.get_event_loop()
        self.region = "europe"
        self.base = f"https://{self.region}.api.riotgames.com"

    @property
    def headers(self):
        headers = {
            "X-Riot-Token": self.key
        }
        return headers

    @property
    def lol(self):
        return f"{self.base}/lol"

    @property
    def riot(self):
        return f"{self.base}/riot"

    @property
    def accounts(self, v=1):
        return f"{self.riot}/account/v{v}/accounts"

    @property
    def lol_matches(self, v=5):
        return f"{self.lol}/match/v{v}/matches"


    @bucket(500, 10)
    async def match_history(self, puuid, start=0, count=20, **kwargs) -> dict:
        url = f"{self.lol_matches}/by-puuid/{puuid}/ids"

        return await self.get(url, start=start, count=count, **kwargs)

    @bucket(250, 10)
    async def match(self, match_id, **kwargs):
        url = f"{self.lol_matches}/{match_id}"
        return await self.get(url, **kwargs)

    @bucket(1000, 60)
    async def puuid_by_name(self, name, tagline):
        url = f"{self.accounts}/by-riot-id/{name}/{tagline}"
        res = await self.get(url)

        if 'puuid' in res:
            return res['puuid']

        return res

    @bucket(*GLOBAL_2)
    @bucket(*GLOBAL_1)
    async def get(self, url, **kwargs) -> dict:
        print(url)
        res = await self.session.get(url, params=kwargs)
        return await res.json()


    @bucket(1, 1)
    async def test(self):
        return 404


async def main():
    client = LeagueOfWeebs("->OwO<-")

    await client.test()
    await client.test()
    await client.test()
    await client.test()
    await client.test()

if __name__ == '__main__':
    asyncio.run(main())
