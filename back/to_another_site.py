import json

import aiohttp


async def get_kkal(product: str) -> dict:
    """
    Example out:
    {
        "clazz": "foodstuff",
        "id": "402879bf0a2ee9e8",
        "url": "blinchiki-s-tvorogom",
        "title": "Блинчики с творогом",
        "type": None,
        "unit": "г",
        "value": "183",
        "favorite": False,
        "energy": None,
        "energyUnit": "ккал",
        "status": 0,
        "visibility": "public",
        "isLiquid": False,
        "hasImage": True,
        "multiplier": None,
        "locked": True,
    }
    """
    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=False)
    ) as session:
        async with session.get(
            f"https://www.tablicakalorijnosti.ru/autocomplete/foodstuff-activity-meal?query={product}&format=json"
        ) as response:
            response_text = await response.text()
            response_json = json.loads(response_text)
            if len(response_json) > 0:
                return response_json[0]
            return {}
