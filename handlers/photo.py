import os
from PIL import Image
from aiogram.types import Message


async def photo_processing(message: Message, ai) -> None:
    """{"title": food_data["name"], "value": {food_data["calories"]}, "photo":True}"""
    # Обработка фото
    compressed_filename = None
    try:
        os.makedirs("tmp_photo", exist_ok=True)
        # Получаем файл фото (берем самое большое качество)
        photo = message.photo[-1]
        file_id = photo.file_id
        file = await message.bot.get_file(file_id)
        file_path = file.file_path

        # Генерируем имя файла
        user_id = message.from_user.id
        timestamp = int(message.date.timestamp())
        filename = f"tmp_photo/{user_id}_{timestamp}.jpg"

        # Скачиваем фото
        await message.bot.download_file(file_path, filename)

        # Сжимаем фото до 800x600
        compressed_filename = compress_image(filename)
        print(f"compressed_filename==={compressed_filename}")
        food_data = await ai.photo_analysis(compressed_filename)

        if compressed_filename and os.path.exists(compressed_filename):
            try:
                os.remove(compressed_filename)
                print(f"Файл удален: {compressed_filename}")
            except Exception as e:
                print(f"Ошибка удаления файла: {e}")

        return {
            "title": food_data["name"],
            "value": food_data["calories"],
            "photo": True,
        }
    except Exception as e:
        print(f"Ошибка обработки фото: {e}")
        await message.answer(
            "❌ Произошла ошибка при обработке фото.\nПопробуйте позже или опишите блюдо словами."
        )


def compress_image(input_path: str, max_size: tuple = (400, 300)) -> str:
    """
    Сжимает изображение до указанного размера
    """
    try:
        # Открываем изображение
        with Image.open(input_path) as img:
            # Конвертируем в RGB если нужно
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            # Изменяем размер сохраняя пропорции
            img.thumbnail(max_size, Image.Resampling.LANCZOS)

            # Создаем имя для сжатого файла
            base_name = os.path.splitext(input_path)[0]
            output_path = f"{base_name}_compressed.jpg"

            # Сохраняем с оптимизацией качества
            img.save(output_path, "JPEG", quality=85, optimize=True)

            # Удаляем оригинальный файл если нужно
        if output_path != input_path and os.path.exists(input_path):
            os.remove(input_path)

        return output_path

    except Exception as e:
        print(f"Ошибка сжатия изображения: {e}")
        return input_path
