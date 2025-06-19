import httpx
import asyncio

async def test():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://llm:11434/api/generate",
                json={
                    "model": "llama3",
                    "prompt": "Say hi",
                    "stream": False
                },
                timeout=30
            )
            print('A')
            print("STATUS:", response.status_code)
            print("\nRESPONSE:", response.text)
            print("\nRESPONSE AS JSON", response.json())
            print("\nRETURN VALUE",response.json().get("response", "").strip())
    except Exception as e:
        print("Error:", e)

asyncio.run(test())
