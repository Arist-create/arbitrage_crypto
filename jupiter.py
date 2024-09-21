import asyncio
import json
import httpx
class Jupiter:
    def __init__(self):
        self._base_url = "https://quote-api.jup.ag/v6"
    async def get_price(self, client, sell_token, buy_token, amount):
        data = {
            "inputMint": sell_token,
            "outputMint": buy_token,
            "amount": amount
        }

        resp = await client.get(f"{self._base_url}/quote", params=data)
        resp = resp.json()
        return resp
        
async def main():
    client = httpx.AsyncClient()
    jupiter = Jupiter()
    resp = await jupiter.get_price(client, "2FPyTwcZLUg1MDrwsyoP4D6s1tM7hAkHYRjkNb5w6Pxk", "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB", 1000000000000000000)
    print(json.dumps(resp, indent=4))

asyncio.run(main())