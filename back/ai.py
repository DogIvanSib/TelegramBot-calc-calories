import time
import aiohttp
import json
from gigachat import GigaChat


class AI:
    def __init__(self, credentials: str) -> None:
        self.giga = GigaChat(
            credentials=credentials,
            verify_ssl_certs=False,
        )
        self.headers = None
        self.expires_at = self.get_token()
        self.base_url = "https://gigachat.devices.sberbank.ru/api/v1/"
        self.payload = {}

    def get_token(self) -> tuple:
        print("Получаю токен для AI")
        response = self.giga.get_token()
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {response.access_token}",
        }
        return response.expires_at / 1000  # секунд

    def upload_file(self, path: str):
        print(f"Загрузил файл: {path}")
        return self.giga.upload_file(open(path, "rb"))

    def delete_file(self, image_id: str):
        print(f"Удалил файл: {image_id}")
        self.giga.delete_file(image_id)

    async def photo_analysis(self, path) -> dict:
        """{name: <name>, calories: <calories>}"""
        now = time.time()
        if now - self.expires_at > -5:
            self.expires_at = self.get_token()
        image = self.upload_file(path)
        data = {
            "model": "GigaChat-Max",  # Типа новый самый
            "messages": [
                {
                    "role": "user",
                    "content": """Определи блюдо на фото и его калорийность с учетом массы на фото. Ответ в JSON: {name: <name>, calories: int(<calories>)}""",
                    "attachments": [image.id_],
                }
            ],
            "stream": False,
            "temperature": 0.1,
            "repetition_penalty": 1,
        }
        food_data = {}
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=False)
        ) as session:
            async with session.post(
                f"{self.base_url}chat/completions",
                json=data,
                headers=self.headers,
            ) as response:
                response_text = await response.text()
                print(f"response_text_from AI photo=={response_text}")
                response_json = json.loads(response_text)
                print(
                    f'total_tokens на запрос:{response_json["usage"]["total_tokens"]}'
                )
                response = response_json["choices"][0]["message"]["content"]

                json_start = response.find("{")
                json_end = response.rfind("}") + 1

                if json_start != -1 and json_end != 0:
                    json_str = response[json_start:json_end]
                    food_data = json.loads(json_str)
                else:
                    print("Не смог извлечь json из ответа")
        self.delete_file(image.id_)
        print(f"food_data==={food_data}")
        return food_data

    async def menu_analysis(
        self, stat_week_kcal: dict, like_menu: list[dict], user_info: dict
    ):
        now = time.time()
        if now - self.expires_at > -5:
            self.expires_at = self.get_token()
        content = "Ты врач диетолог. Посоветуй пациенту, что кушать в ближайшую неделю. Ответ краткий с заключением, не более 200 символов. Используй стикеры. "
        user_info_str = f"""Возраст:{user_info["age"]} лет, вес: {user_info["weight"]} кг, рост: {user_info["height"]} см, пол: {'мужской' if user_info["gender"]=="м" else "женский"}, рекомендуется потреблять {user_info["calories"]} килокалорий. """
        stat_week_kcal_str = ""
        if stat_week_kcal:
            stat_week_kcal_str = "Потребление килокалорий по дням: "
            for day in stat_week_kcal:
                if day["calories"]:
                    stat_week_kcal_str += f"{day["date"]}:{day["calories"]}, "
        like_menu_str = ""
        if like_menu:
            like_menu_str = "Любимые блюда за неделю: "
            for menu in like_menu:
                like_menu_str += f"{menu["product_name"]}:{menu["frequency"]} раз, "
        prompt = content + user_info_str + stat_week_kcal_str + like_menu_str
        print(f"Prompt: {prompt}")

        data = {
            "model": "GigaChat",
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "stream": False,
            "temperature": 0.1,
            "repetition_penalty": 1,
        }
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=False)
        ) as session:
            async with session.post(
                f"{self.base_url}chat/completions",
                json=data,
                headers=self.headers,
            ) as response:
                response_text = await response.text()
                print()
                print(f"response_text_recomendation=={response_text}")
                response_json = json.loads(response_text)
                print(
                    f'total_tokens на запрос:{response_json["usage"]["total_tokens"]}'
                )
                response = response_json["choices"][0]["message"]["content"]
                return response

    async def get_kcal(self, product: str):
        now = time.time()
        if now - self.expires_at > -5:
            self.expires_at = self.get_token()
        content = (
            f"Определи блюдо по описанию и его калорийность(ответ дай числом в килокалорий за 100 грамм): {product}. "
            + "Дай краткий ответ. В ответе только JSON: {name: <name>, calories: int(<calories>)}"
        )
        print(f"Prompt: {content}")

        data = {
            "model": "GigaChat",
            "messages": [
                {
                    "role": "user",
                    "content": content,
                }
            ],
            "stream": False,
            "temperature": 0.1,
            "repetition_penalty": 1,
        }
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=False)
        ) as session:
            async with session.post(
                f"{self.base_url}chat/completions",
                json=data,
                headers=self.headers,
            ) as response:
                response_text = await response.text()
                print()
                print(f"response_text_recomendation=={response_text}")
                response_json = json.loads(response_text)
                print(
                    f'total_tokens на запрос:{response_json["usage"]["total_tokens"]}'
                )
                response = response_json["choices"][0]["message"]["content"]

                json_start = response.find("{")
                json_end = response.rfind("}") + 1

                if json_start != -1 and json_end != 0:
                    json_str = response[json_start:json_end]
                    food_data = json.loads(json_str)
                    print(f"food_data_get_kcal==={food_data}")
                    return {
                        "title": product,
                        "value": food_data["calories"],
                    }
                else:
                    print("Не смог извлечь json из ответа")
        return {}
