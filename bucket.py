import asyncio
import time

from asyncio import Queue

class Bucket:
    """
    Custom ratelimit bucket
    all times are in seconds
    """
    def __init__(self, function, amount, per):
        self.f = function

        self.amount = amount
        self.per = per

        self.invokes = 0
        self.last = 0

        self.processed = Queue()
        self.to_process = Queue()
        self.loop = asyncio.get_event_loop()

        self.task = None

    async def __call__(self, *args, **kwargs):
        if not self.task:
            asyncio.create_task(self.core())
        await self.to_process.put(1)
        await self.processed.get()
        return await self.f(*args, **kwargs)

    def __repr__(self):
        return f"<amount: {self.amount}, time: {self.per}, ratelimited: {self.invokes >= self.amount}>"

    @property
    def diff(self):
        return time.perf_counter()-self.last

    async def core(self):
        while True:
            print("waiting for invoke")
            await self.to_process.get()
            if self.diff >= self.per:
                print("resetting bucket")
                self.last = time.perf_counter()
                self.invokes = 0
            else:
                if self.invokes >= self.amount:
                    print(f"ratelimited waiting {self.per-self.diff}")
                    await asyncio.sleep(self.per-self.diff)
                    print("resetting bucket 2")
                    self.last = time.perf_counter()
                    self.invokes = 0
                else:
                    print("free to go")

            self.invokes += 1
            await self.processed.put(1)


def bucket(amount, per, cls=Bucket):
    def initiate(f):
        b = cls(f, amount, per)

        def wrapped(*args, **kwargs):
            return b(*args, **kwargs)
        return wrapped
    return initiate
