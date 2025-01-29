import asyncio
import aiohttp
import random
import time

SERVER_URLS = ['http://127.0.0.1:5001/add_message', 'http://127.0.0.1:5002/add_message']
USERS = [
    "Alice", "Bob", "Charlie", "David", "Eve",
    "Frank", "Grace", "Heidi", "Ivan", "Judy",
]

async def send_message():
    async with aiohttp.ClientSession() as session:
        try:
            responses = []
            for _ in range(100):
                user = random.choice(USERS)
                url = random.choice(SERVER_URLS)
                async with session.post(url, params={'name': user, 'text': f"Hello world! {random.randint(10000, 99999)}"}) as response:
                    responses.append(await response.json())
            return response
        except aiohttp.ClientResponseError as e:
            print(f'Ошибка при отправке запроса: {e}')

async def main():
    tasks = []
    for _ in range(50): tasks.append(asyncio.create_task(send_message()))

    start_time = time.time()
    await asyncio.gather(*tasks)
    end_time = time.time()

    total_time = end_time - start_time
    time_per_request = total_time / 5000
    rps = 5000 / total_time

    print(f'Total 5000 requests: {total_time} seconds')
    print(f'One request: {time_per_request} seconds')
    print(f'RPS: {rps}')

if __name__ == '__main__':
    asyncio.run(main())
