import io
import math
import random
import hashlib

import numpy as np
import streamlit as st
from PIL import Image, ImageDraw, ImageFilter, ImageOps
from streamlit_drawable_canvas import st_canvas


# =========================================================
# AI NAIL STYLIST — pink premium edition
# =========================================================

st.set_page_config(
    page_title="Nail Studio | AI Nail Stylist",
    page_icon="💅",
    layout="wide",
    initial_sidebar_state="collapsed",
)

MAX_SIDE = 850
MASK_COLOR = "#FF00FF"  # Яркий цвет кисти для точного выделения


# ------------------------- СТИЛИ -------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700&display=swap');

.stApp {
    background: linear-gradient(145deg, #fff8fb 0%, #ffffff 48%, #fff0f6 100%);
    font-family: 'DM Sans', sans-serif;
}
.block-container {
    max-width: 1250px;
    padding-top: 1.2rem;
    padding-bottom: 3rem;
}
h1, h2, h3 {
    font-family: 'Playfair Display', serif !important;
    color: #38232d;
}
.hero {
    padding: 28px;
    border-radius: 26px;
    background: linear-gradient(120deg, #f9dfe9, #fff4f7 58%, #f4e5f2);
    border: 1px solid #f1dce5;
    margin-bottom: 20px;
}
.eyebrow {
    color: #a15a78;
    text-transform: uppercase;
    letter-spacing: 3px;
    font-size: 11px;
    font-weight: 700;
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: clamp(30px, 5vw, 48px);
    line-height: 1.12;
    color: #38232d;
    margin: 8px 0;
}
.hero-sub {
    color: #795d6a;
    font-size: 15px;
    max-width: 650px;
}
div.stButton > button,
div.stDownloadButton > button {
    border-radius: 14px;
    min-height: 44px;
    font-weight: 600;
    border: 1px solid #e9c7d6;
}
div.stButton > button[kind="primary"] {
    background: #a34e73;
    color: white;
    border: none;
}
div[data-testid="stFileUploader"] {
    background: white;
    border: 1px dashed #e2b8cb;
    padding: 12px;
    border-radius: 18px;
}
div[data-testid="stAlert"] {
    border-radius: 14px;
}
.small-note {
    color: #907987;
    font-size: 12px;
}
.design-name {
    color: #38232d;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)


# ---------------------- КАТАЛОГ -------------------------

DESIGNS = [
    {"name": "Milky Nude", "category": "Нюд", "kind": "solid",
     "color": "#EBCBC6", "accent": "#FFFFFF"},
    {"name": "Rose Quartz", "category": "Нюд", "kind": "solid",
     "color": "#D995A8", "accent": "#FCEAF0"},
    {"name": "Latte", "category": "Нюд", "kind": "solid",
     "color": "#B88A73", "accent": "#F0D7C4"},
    {"name": "Soft Pink", "category": "Нюд", "kind": "solid",
     "color": "#F2B9CC", "accent": "#FFFFFF"},
    {"name": "Cherry Red", "category": "Классика", "kind": "solid",
     "color": "#A91338", "accent": "#F5A7B8"},
    {"name": "Black Cherry", "category": "Классика", "kind": "solid",
     "color": "#471729", "accent": "#B33B5C"},
    {"name": "Classic White", "category": "Френч", "kind": "french",
     "color": "#F3DCD7", "accent": "#FFFFFF"},
    {"name": "Pink French", "category": "Френч", "kind": "french",
     "color": "#EBA8BE", "accent": "#FFF8FB"},
    {"name": "Chocolate French", "category": "Френч", "kind": "french",
     "color": "#D8B6A0", "accent": "#603D35"},
    {"name": "Vanilla Chrome", "category": "Хром", "kind": "chrome",
     "color": "#D8C8B7", "accent": "#FFFFFF"},
    {"name": "Pink Chrome", "category": "Хром", "kind": "chrome",
     "color": "#D887B4", "accent": "#FFE6F3"},
    {"name": "Silver Mirror", "category": "Хром", "kind": "chrome",
     "color": "#BFC4D0", "accent": "#FFFFFF"},
    {"name": "Emerald Cat Eye", "category": "Кошачий глаз", "kind": "cat",
     "color": "#145C4B", "accent": "#8DE8BD"},
    {"name": "Bordeaux Cat Eye", "category": "Кошачий глаз", "kind": "cat",
     "color": "#621E3D", "accent": "#F0A0D1"},
    {"name": "Blue Cat Eye", "category": "Кошачий глаз", "kind": "cat",
     "color": "#203E78", "accent": "#9BD9FF"},
    {"name": "Sunset Ombre", "category": "Омбре", "kind": "ombre",
     "color": "#E88A9F", "accent": "#F8D6B8"},
    {"name": "Lilac Dream", "category": "Омбре", "kind": "ombre",
     "color": "#A997D5", "accent": "#F5C9E0"},
    {"name": "Peach Glow", "category": "Омбре", "kind": "ombre",
     "color": "#F3A783", "accent": "#FFF0D4"},
    {"name": "Golden Sparkle", "category": "Блёстки", "kind": "glitter",
     "color": "#C9A04D", "accent": "#FFF0AC"},
    {"name": "Pink Stardust", "category": "Блёстки", "kind": "glitter",
     "color": "#D985B0", "accent": "#FFE4F1"},
    {"name": "Midnight Glitter", "category": "Блёстки", "kind": "glitter",
     "color": "#302A50", "accent": "#C8B9FF"},
    {"name": "Daisy Garden", "category": "Цветы", "kind": "flowers",
     "color": "#F2D2D9", "accent": "#FFFFFF"},
    {"name": "Cherry Blossom", "category": "Цветы", "kind": "flowers",
     "color": "#E7A5BC", "accent": "#FFF1F5"},
    {"name": "Blue Porcelain", "category": "Узоры", "kind": "flowers",
     "color": "#F1EDE6", "accent": "#547AA5"},
    {"name": "Rose Marble", "category": "Узоры", "kind": "marble",
     "color": "#DFA6B9", "accent": "#FFF3F6"},
    {"name": "Ocean Marble", "category": "Узоры", "kind": "marble",
     "color": "#5E9EA6", "accent": "#D8F3F0"},
    {"name": "Sage Green", "category": "Минимализм", "kind": "solid",
     "color": "#9CAD93", "accent": "#E6ECDD"},
    {"name": "Butter Yellow", "category": "Минимализм", "kind": "solid",
     "color": "#EAD78A", "accent": "#FFF5C8"},
    {"name": "Mocha", "category": "Минимализм", "kind": "solid",
     "color": "#806052", "accent": "#D5B4A2"},
    {"name": "Bridal Pearl", "category": "Свадебный", "kind": "pearl",
     "color": "#E9DDD8", "accent": "#FFFFFF"},
    {"name": "Champagne Pearl", "category": "Свадебный", "kind": "pearl",
     "color": "#D6C09A", "accent": "#FFF5D9"},
    {"name": "Midnight Blue", "category": "Вечерний", "kind": "chrome",
     "color": "#182B54", "accent": "#8CB4F5"},
    {"name": "Plum Velvet", "category": "Вечерний", "kind": "cat",
     "color": "#552849", "accent": "#E0A0D1"},
    {"name": "Coral Crush", "category": "Яркий", "kind": "solid",
     "color": "#F16F6B", "accent": "#FFD4C9"},
    {"name": "Electric Lilac", "category": "Яркий", "kind": "chrome",
     "color": "#A98BEE", "accent": "#F0E5FF"},
    {"name": "Tropical Green", "category": "Яркий", "kind": "solid",
     "color": "#198C70", "accent": "#B1F2D6"},
    {"name": "Polka Dot", "category": "Узоры", "kind": "dots",
     "color": "#F1B5C8", "accent": "#FFFFFF"},
    {"name": "Minimal Lines", "category": "Минимализм", "kind": "lines",
     "color": "#E7D5C9", "accent": "#634C50"},
    {"name": "Heart Mood", "category": "Романтика", "kind": "hearts",
     "color": "#F3CAD7", "accent": "#BD315E"},
    {"name": "Lavender Fields", "category": "Цветы", "kind": "flowers",
     "color": "#C4B5E4", "accent": "#FDF7FF"},
]

CATEGORIES = ["Все"] + list(dict.fromkeys(
    design["category"] for design in DESIGNS
))


# -------------------- ОБРАБОТКА ФОТО ---------------------

def load_image(upload):
    """Безопасно загружает фото, исправляет ориентацию и уменьшает размер."""
    if upload is None:
        return None

    try:
        image = Image.open(upload)
        image = ImageOps.exif_transpose(image).convert("RGB")
        image.thumbnail((MAX_SIDE, MAX_SIDE), Image.Resampling.LANCZOS)
        return image
    except (OSError, ValueError, TypeError):
        return None


def image_fingerprint(image):
    """Уникальная подпись изображения для сброса старой маски."""
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=90)
    return hashlib.sha256(buffer.getvalue()).hexdigest()


def hex_rgb(value):
    value = value.lstrip("#")
    return tuple(
        int(value[index:index + 2], 16)
        for index in (0, 2, 4)
    )


def make_pattern(size, design, seed=12):
    """Создаёт узор покрытия заданного размера."""
    width, height = size
    base = hex_rgb(design["color"])
    accent = hex_rgb(design["accent"])
    rng = random.Random(seed)

    if width <= 0 or height <= 0:
        return Image.new("RGB", (1, 1), base)

    yy, xx = np.mgrid[0:height, 0:width]
    x = xx / max(width - 1, 1)
    y = yy / max(height - 1, 1)

    pixels = np.empty((height, width, 3), dtype=np.uint8)
    pixels[:] = base

    kind = design["kind"]

    if kind == "french":
        pixels[y > 0.77] = accent

    elif kind == "ombre":
        blend = y[:, :, None]
        top = np.asarray(accent, dtype=float)
        bottom = np.asarray(base, dtype=float)
        pixels = (
            top[None, None, :] * (1 - blend)
            + bottom[None, None, :] * blend
        ).clip(0, 255).astype(np.uint8)

    elif kind == "chrome":
        shine = np.exp(-((x - 0.36) / 0.15) ** 2) * 0.65
        shine += np.exp(-((x - 0.78) / 0.08) ** 2) * 0.22
        shine = np.clip(shine, 0, 0.8)[:, :, None]

        pixels = (
            pixels.astype(float) * (1 - shine)
            + np.asarray(accent)[None, None, :] * shine
        ).clip(0, 255).astype(np.uint8)

    elif kind == "cat":
        stripe = np.exp(
            -((x - (0.25 + 0.48 * y)) / 0.075) ** 2
        )
        stripe = (stripe * 0.85)[:, :, None]

        pixels = (
            pixels.astype(float) * (1 - stripe)
            + np.asarray(accent)[None, None, :] * stripe
        ).clip(0, 255).astype(np.uint8)

    texture = Image.fromarray(pixels, mode="RGB")
    draw = ImageDraw.Draw(texture)

    if kind == "glitter":
        count = min(1200, max(25, width * height // 65))
        for _ in range(count):
            px = rng.randrange(width)
            py = rng.randrange(height)
            radius = rng.choice([1, 1, 1, 2])
            draw.ellipse(
                (px - radius, py - radius, px + radius, py + radius),
                fill=accent,
            )

    elif kind == "dots":
        step = max(8, min(width, height) // 5)
        radius = max(1, step // 12)

        for py in range(step // 2, height, step):
            for px in range(step // 2, width, step):
                draw.ellipse(
                    (px-radius, py-radius, px+radius, py+radius),
                    fill=accent,
                )

    elif kind == "lines":
        line_width = max(1, width // 35)

        for fraction in (0.25, 0.55, 0.78):
            px = int(width * fraction)
            draw.line(
                (px, 0, px - int(width * 0.12), height),
                fill=accent,
                width=line_width,
            )

    elif kind == "flowers":
        flower_count = 3 if min(width, height) < 100 else 5
        radius = max(2, min(width, height) // 12)

        for _ in range(flower_count):
            cx = rng.randint(0, max(0, width - 1))
            cy = rng.randint(0, max(0, height - 1))

            for angle in range(0, 360, 72):
                rad = math.radians(angle)
                px = cx + int(math.cos(rad) * radius)
                py = cy + int(math.sin(rad) * radius)
                petal = max(1, radius // 2)

                draw.ellipse(
                    (px-petal, py-petal, px+petal, py+petal),
                    fill=accent,
                )

            center = max(1, radius // 3)
            draw.ellipse(
                (cx-center, cy-center, cx+center, cy+center),
                fill=base,
            )

    elif kind == "hearts":
        radius = max(2, min(width, height) // 14)

        for _ in range(3):
            cx = rng.randint(0, max(0, width - 1))
            cy = rng.randint(0, max(0, height - 1))

            draw.ellipse(
                (cx-radius, cy-radius, cx, cy),
                fill=accent,
            )
            draw.ellipse(
                (cx, cy-radius, cx+radius, cy),
                fill=accent,
            )
            draw.polygon(
                [
                    (cx-radius, cy-radius // 2),
                    (cx+radius, cy-radius // 2),
                    (cx, cy+radius*2),
                ],
                fill=accent,
            )

    elif kind == "marble":
        line_width = max(1, width // 35)

        for index in range(5):
            start = rng.randint(-height // 3, max(0, height - 1))
            points = []

            for px in range(0, width + 1, max(1, width // 12)):
                py = start + int(
                    math.sin(px / max(width, 1) * 8 + index)
                    * height * 0.08
                )
                points.append((px, py))

            draw.line(points, fill=accent, width=line_width)

    elif kind == "pearl":
        step = max(8, min(width, height) // 5)
        radius = max(1, step // 10)

        for py in range(step // 2, height, step):
            for px in range(step // 2, width, step):
                draw.ellipse(
                    (px-radius, py-radius, px+radius, py+radius),
                    fill=accent,
                )
                draw.point((max(0, px-1), max(0, py-1)), fill="#FFFFFF")

    return texture


def extract_mask(canvas_image, photo):
    """
    Извлекает мазки по специальному цвету кисти.
    Не использует белый цвет, так как белый может присутствовать на фото.
    """
    if canvas_image is None:
        return None

    try:
        canvas = np.asarray(canvas_image.convert("RGBA"))
        height, width = photo.height, photo.width

        if canvas.shape[0] != height or canvas.shape[1] != width:
            canvas_pil = Image.fromarray(canvas, mode="RGBA")
            canvas_pil = canvas_pil.resize(
                (width, height), Image.Resampling.LANCZOS
            )
            canvas = np.asarray(canvas_pil)

        red = canvas[:, :, 0].astype(np.int16)
        green = canvas[:, :, 1].astype(np.int16)
        blue = canvas[:, :, 2].astype(np.int16)
        alpha = canvas[:, :, 3]

        # Пурпурная кисть: красный и синий высокие, зелёный низкий.
        selected = (
            (alpha > 0)
            & (red > 170)
            & (blue > 130)
            & (green < 120)
            & ((red - green) > 70)
            & ((blue - green) > 50)
        )

        mask = Image.fromarray(
            (selected.astype(np.uint8) * 255),
            mode="L",
        )

        if mask.getbbox() is None:
            return None

        return mask

    except (ValueError, TypeError, OSError):
        return None


def apply_design(original, mask, design, strength=0.88):
    """Накладывает цвет и узор только на выбранную область."""
    base = original.convert("RGB")

    if mask is None:
        return base.copy()

    mask = mask.convert("L").resize(
        base.size, Image.Resampling.LANCZOS
    )

    if mask.getbbox() is None:
        return base.copy()

    # Мягкий край помогает убрать резкие пиксельные границы.
    mask = mask.filter(ImageFilter.GaussianBlur(radius=0.8))

    pattern = make_pattern(base.size, design)

    # Интенсивность влияет на заметность покрытия.
    strength = max(0.0, min(1.0, float(strength)))
    overlay = Image.blend(base, pattern, strength)

    return Image.composite(overlay, base, mask)


def to_png_bytes(image):
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer.getvalue()


# ---------------------- СОСТОЯНИЕ ------------------------

defaults = {
    "photo": None,
    "photo_id": None,
    "mask": None,
    "result": None,
    "result_id": None,
    "favorites": [],
    "selected_design": DESIGNS[0]["name"],
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ------------------------- ШАПКА -------------------------

st.markdown("""
<div class="hero">
  <div class="eyebrow">Your personal nail studio</div>
  <div class="hero-title">Маникюр, который создан для Вас ✨</div>
  <div class="hero-sub">
    Загрузите фото, выберите любимый дизайн и примерьте новое покрытие
    прямо на своих ногтях.
  </div>
</div>
""", unsafe_allow_html=True)

tab_try, tab_catalog, tab_help = st.tabs(
    ["💅 Примерка", "✨ Каталог дизайнов", "♡ Как пользоваться"]
)


# ---------------------- ПРИМЕРКА -------------------------

with tab_try:
    st.subheader("Ваша виртуальная примерка")
    st.write(
        "Сделайте фото руки или выберите снимок из галереи. "
        "Для лучшего результата используйте хорошее освещение."
    )

    camera_col, upload_col = st.columns(2)

    with camera_col:
        camera_file = st.camera_input(
            "Сделать фото ногтей",
            key="nail_camera",
        )

    with upload_col:
        uploaded_file = st.file_uploader(
            "Выбрать фото из галереи",
            type=["jpg", "jpeg", "png", "webp"],
            key="nail_upload",
        )

    # Приоритет у файла, выбранного из галереи.
    chosen_file = (
        uploaded_file if uploaded_file is not None else camera_file
    )

    if chosen_file is not None:
        new_photo = load_image(chosen_file)

        if new_photo is None:
            st.error(
                "Не удалось открыть фотографию. "
                "Попробуйте выбрать другое изображение."
            )
        else:
            new_id = image_fingerprint(new_photo)

            if new_id != st.session_state.photo_id:
                st.session_state.photo = new_photo
                st.session_state.photo_id = new_id
                st.session_state.mask = None
                st.session_state.result = None
                st.session_state.result_id = None

    photo = st.session_state.photo

    if photo is None:
        st.info(
            "📸 Сделайте снимок камерой или выберите фотографию, "
            "чтобы начать примерку."
        )

    else:
        st.success("Фото готово. Выделите ногтевые пластины кистью.")

        with st.expander("Советы для лучшего результата"):
            st.markdown("""
            - Держите руку неподвижно.
            - Используйте мягкий дневной свет.
            - По возможности расположите ногти отдельно друг от друга.
            - Выделяйте только ногтевую пластину, избегая кожи.
            """)

        left, right = st.columns([1.05, 0.95], gap="large")

        with left:
            st.markdown("#### 1. Выделите ногти")
            st.caption(
                "Проведите пальцем по каждому ногтю. "
                "Пурпурные мазки обозначают область нанесения."
            )

            brush = st.slider(
                "Размер кисти",
                min_value=4,
                max_value=35,
                value=12,
                step=1,
                key="brush_size",
            )

            # Canvas использует фото как фон, а яркую кисть —
            # как легко обнаруживаемый цвет выделения.
            canvas_result = st_canvas(
                fill_color="rgba(255, 0, 255, 0.20)",
                stroke_width=brush,
                stroke_color=MASK_COLOR,
                background_image=photo,
                update_streamlit=True,
                height=photo.height,
                width=photo.width,
                drawing_mode="freedraw",
                display_toolbar=True,
                key=f"nail_canvas_{st.session_state.photo_id[:12]}",
            )

            if canvas_result.image_data is not None:
                canvas_pil = Image.fromarray(
                    canvas_result.image_data.astype(np.uint8),
                    mode="RGBA",
                )
                detected_mask = extract_mask(canvas_pil, photo)

                # Не заменяем старую маску пустой маской, если
                # пользователь просто переключил элемент интерфейса.
                if detected_mask is not None:
                    st.session_state.mask = detected_mask

            if st.session_state.mask is not None:
                st.caption("Выделение сохранено для текущей фотографии.")
                with st.expander("Проверить маску выделения"):
                    st.image(
                        st.session_state.mask,
                        caption="Белое — область нанесения дизайна",
                        use_container_width=True,
                    )

            if st.button(
                "Очистить выделение",
                key="clear_mask",
                use_container_width=True,
            ):
                st.session_state.mask = None
                st.session_state.result = None
                st.session_state.result_id = None
                st.rerun()

        with right:
            st.markdown("#### 2. Выберите дизайн")

            category = st.selectbox(
                "Категория",
                CATEGORIES,
                key="try_category",
            )

            filtered = [
                item for item in DESIGNS
                if category == "Все" or item["category"] == category
            ]

            design_names = [item["name"] for item in filtered]

            if st.session_state.selected_design not in design_names:
                st.session_state.selected_design = design_names[0]

            selected_name = st.selectbox(
                "Дизайн",
                design_names,
                index=design_names.index(
                    st.session_state.selected_design
                ),
                key="try_design",
            )

            st.session_state.selected_design = selected_name
            design = next(
                item for item in DESIGNS
                if item["name"] == selected_name
            )

            strength = st.slider(
                "Интенсивность покрытия",
                min_value=35,
                max_value=100,
                value=88,
                step=5,
                key="coverage_strength",
            ) / 100.0

            st.markdown("#### Предпросмотр оттенка")

            swatch = Image.new(
                "RGB", (320, 72), hex_rgb(design["color"])
            )
            draw_swatch = ImageDraw.Draw(swatch)
            draw_swatch.rounded_rectangle(
                (3, 3, 317, 69),
                radius=18,
                outline=hex_rgb(design["accent"]),
                width=3,
            )
            st.image(swatch, use_container_width=True)
            st.markdown(
                f"**{design['name']}** · {design['category']}"
            )

            if st.button(
                "✨ Примерить дизайн",
                type="primary",
                use_container_width=True,
                key="apply_design",
            ):
                current_mask = st.session_state.mask

                if current_mask is None or current_mask.getbbox() is None:
                    st.warning(
                        "Сначала выделите ногти пурпурной кистью."
                    )
                else:
                    try:
                        result = apply_design(
                            photo,
                            current_mask,
                            design,
                            strength,
                        )
                        st.session_state.result = result
                        st.session_state.result_id = (
                            st.session_state.photo_id,
                            design["name"],
                        )
                    except (ValueError, TypeError, OSError) as exc:
                        st.error(
                            "Не удалось создать предпросмотр. "
                            "Попробуйте ещё раз или выберите другое фото."
                        )

            result = st.session_state.result
            result_id = st.session_state.result_id

            if result is not None and result_id is not None:
                if result_id[0] == st.session_state.photo_id:
                    st.markdown("#### Ваш результат")
                    st.image(result, use_container_width=True)

                    st.download_button(
                        "⬇️ Сохранить результат в PNG",
                        data=to_png_bytes(result),
                        file_name="nail_stylist_result.png",
                        mime="image/png",
                        use_container_width=True,
                        key="download_result",
                    )

                    if st.button(
                        "♡ Добавить дизайн в избранное",
                        use_container_width=True,
                        key="favorite_current",
                    ):
                        if design["name"] not in st.session_state.favorites:
                            st.session_state.favorites.append(
                                design["name"]
                            )
                        st.toast("Дизайн добавлен в избранное!")

        if st.session_state.favorites:
            st.markdown("#### ♡ Ваши любимые дизайны")
            st.write(" · ".join(st.session_state.favorites))


# ------------------------ КАТАЛОГ -------------------------

with tab_catalog:
    st.subheader("Коллекция маникюра")
    st.write(
        "Выбирайте оттенки и узоры, сохраняйте понравившиеся "
        "варианты и используйте их для примерки."
    )

    search = st.text_input(
        "🔎 Поиск дизайна",
        placeholder="Например, nude, chrome, French...",
        key="catalog_search",
    )

    catalog_category = st.selectbox(
        "Фильтр по стилю",
        CATEGORIES,
        key="catalog_category",
    )

    query = search.strip().casefold()

    catalog = [
        item for item in DESIGNS
        if (
            catalog_category == "Все"
            or item["category"] == catalog_category
        )
        and query in (
            item["name"] + " " + item["category"]
        ).casefold()
    ]

    if not catalog:
        st.info("Ничего не найдено. Попробуйте другой запрос.")

    else:
        columns = st.columns(3)

        for index, item in enumerate(catalog):
            with columns[index % 3]:
                preview = make_pattern(
                    (260, 180),
                    item,
                    seed=index + 20,
                )

                st.image(preview, use_container_width=True)
                st.markdown(f"**{item['name']}**")
                st.caption(item["category"])

                is_favorite = (
                    item["name"] in st.session_state.favorites
                )

                if st.button(
                    "♥ В избранном" if is_favorite else "♡ В избранное",
                    key=f"favorite_{item['name']}",
                    use_container_width=True,
                ):
                    if is_favorite:
                        st.session_state.favorites.remove(item["name"])
                    else:
                        st.session_state.favorites.append(item["name"])
                    st.rerun()

                if st.button(
                    "Выбрать для примерки",
                    key=f"choose_{item['name']}",
                    use_container_width=True,
                ):
                    st.session_state.selected_design = item["name"]
                    st.toast(
                        "Дизайн выбран. Откройте вкладку «Примерка»."
                    )


# ------------------------- ПОМОЩЬ -------------------------

with tab_help:
    st.subheader("Как пользоваться приложением")

    st.markdown("""
    **1. Загрузите фото.** Сделайте снимок камерой или выберите
    изображение из галереи.

    **2. Выделите ногти.** Пурпурной кистью проведите внутри
    ногтевых пластин. Чем аккуратнее выделение, тем лучше результат.

    **3. Выберите стиль.** В каталоге доступны нюд, френч, хром,
    кошачий глаз, омбре, блёстки, цветы и другие варианты.

    **4. Примерьте покрытие.** Нажмите «Примерить дизайн».
    Наложение будет ограничено выделенной маской.

    **5. Сохраните изображение.** Готовый результат можно скачать
    в формате PNG.

    **Важно:** приложение создаёт визуальный предпросмотр, а не
    профессиональную нейросетевую симуляцию гель-лака. Для точного
    автоматического определения контуров ногтей потребуется отдельная
    модель компьютерного зрения.
    """)


# ------------------------- ПОДВАЛ -------------------------

st.markdown("---")
st.markdown(
    "<div class='small-note'>NAIL STUDIO · "
    "Find your next favorite manicure</div>",
    unsafe_allow_html=True,
)
