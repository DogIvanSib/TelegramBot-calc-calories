import matplotlib.pyplot as plt
import io
from aiogram.types import BufferedInputFile


async def graph_week(message, stat_week_kcal: dict, itogo_week: float):

    # Создание графика
    plt.figure(figsize=(12, 6))

    # Данные для графика
    day_names = [f"{day["date"]} {day["day_name"]}" for day in stat_week_kcal]
    calories = [day["calories"] for day in stat_week_kcal]

    # Создаем столбчатую диаграмму
    bars = plt.bar(
        day_names,
        calories,
        color=[
            "#ff9999",
            "#66b3ff",
            "#99ff99",
            "#ffcc99",
            "#ff99cc",
            "#c2c2f0",
            "#ffb3e6",
        ],
    )

    # Настройки графика
    plt.title("Потребление калорий за неделю", fontsize=16, fontweight="bold")
    plt.ylabel("Калории", fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(axis="y", alpha=0.3)

    # Добавляем значения на столбцы
    for bar, value in zip(bars, calories):
        if value > 0:
            height = bar.get_height()
            plt.text(
                bar.get_x() + bar.get_width() / 2.0,
                height + 100,
                f"{int(value)}",
                ha="center",
                va="bottom",
                fontweight="bold",
            )

    plt.tight_layout()

    # Сохраняем график в буфер
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    buf.seek(0)

    # Отправляем график
    chart = BufferedInputFile(buf.getvalue(), filename="weekly_stats.png")
    await message.answer_photo(
        photo=chart,
        caption=f"📊 <b>Статистика за неделю</b>\n\n"
        f"🔥 <b>Всего потреблено:</b> {int(itogo_week)} ккал\n\n"
        f"📈 В среднем в день: {itogo_week/7:.0f} ккал",
    )

    # Закрываем график
    plt.close()
