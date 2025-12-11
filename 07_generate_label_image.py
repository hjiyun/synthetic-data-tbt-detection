import json
import os
from PIL import Image, ImageDraw, ImageFont
import textwrap

def draw_fda_label(product_data, output_filename, fonts):
    """
    개별 제품 데이터를 받아 FDA 라벨 이미지를 그리기는 함수 (로직 동일)
    """
    # 1. 캔버스 설정
    width, height = 400, 650
    background_color = (255, 255, 255)
    text_color = (0, 0, 0)
    
    image = Image.new('RGB', (width, height), background_color)
    draw = ImageDraw.Draw(image)

    title_font, header_font, regular_font, small_font = fonts
    margin = 20
    current_y = margin

    # [Title] Nutrition Facts
    draw.text((margin, current_y), "Nutrition Facts", font=title_font, fill=text_color)
    current_y += 40
    draw.rectangle([(margin, current_y), (width - margin, current_y + 5)], fill=text_color)
    current_y += 15

    # [Serving Info]
    serving_size = product_data.get('serving_size', 'N/A')
    draw.text((margin, current_y), f"Serving size: {serving_size}", font=regular_font, fill=text_color)
    current_y += 30
    draw.rectangle([(margin, current_y), (width - margin, current_y + 5)], fill=text_color)
    current_y += 10

    # [Calories]
    draw.text((margin, current_y), "Amount per serving", font=small_font, fill=text_color)
    current_y += 20
    calories = product_data.get('calories_per_serving', 'N/A')
    draw.text((margin, current_y), "Calories", font=header_font, fill=text_color)
    
    cal_value = str(calories).replace('kcal', '').replace('Calories', '').strip()
    draw.text((width - margin - 110, current_y - 5), cal_value, font=title_font, fill=text_color)
    current_y += 45
    draw.rectangle([(margin, current_y), (width - margin, current_y + 3)], fill=text_color)
    current_y += 10

    # [Nutrients]
    nf = product_data.get('nutrition_facts', {})
    
    def draw_nutrient_line(name, value, is_bold=False, indent=0):
        nonlocal current_y
        font = header_font if is_bold else regular_font
        draw.text((margin + indent, current_y), name, font=font, fill=text_color)
        
        val_text = str(value)
        text_width = draw.textlength(val_text, font=font)
        draw.text((width - margin - text_width, current_y), val_text, font=font, fill=text_color)
        current_y += 25
        draw.rectangle([(margin, current_y), (width - margin, current_y + 1)], fill="#cccccc")
        current_y += 5

    draw_nutrient_line("Total Fat", nf.get('total_fat', '0g'), is_bold=True)
    draw_nutrient_line("Sodium", nf.get('sodium', '0mg'), is_bold=True)
    draw_nutrient_line("Total Carbohydrate", nf.get('total_carbohydrate', '0g'), is_bold=True)
    draw_nutrient_line("Protein", nf.get('protein', '0g'), is_bold=True)

    current_y += 20

    # [Allergens & Product Name]
    allergen = product_data.get('allergen_statement', '')
    if allergen:
        draw.text((margin, current_y), "INGREDIENTS INFO:", font=header_font, fill=text_color)
        current_y += 25
        lines = textwrap.wrap(allergen, width=40)
        for line in lines:
            draw.text((margin, current_y), line, font=regular_font, fill=text_color)
            current_y += 20
            
    current_y += 20
    product_name = product_data.get('product_name_en', 'Unknown Product')
    # 상품명이 너무 길면 자르기
    if len(product_name) > 35:
        product_name = product_name[:32] + "..."
    draw.text((margin, current_y), f"Product: {product_name}", font=small_font, fill=(50, 50, 50))

    # 이미지 저장
    image.save(output_filename)
    print(f"Generating: {output_filename}")


def generate_all_images():
    print("=" * 60)
    print("[Step 7] 지정된 경로에 FDA 라벨 이미지 생성")
    print("=" * 60)

    # 1. 데이터 로드 (현재 폴더에 있다고 가정)
    json_path = r'C:\Users\julie\Desktop\2025-2\TBT 무역장벽\food\synthetic_labels.json'
    
    # 혹시 파일이 없으면 절대 경로로 시도 (경로 수정 필요시 변경)
    if not os.path.exists(json_path):
         base_dir = r"C:\Users\julie\Desktop\2025-2\TBT 무역장벽\food"
         json_path = os.path.join(base_dir, 'synthetic_labels.json')

    if not os.path.exists(json_path):
        print(f"[ERROR] '{json_path}' 파일을 찾을 수 없습니다.")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data_list = json.load(f)
    
    if not data_list:
        print("[ERROR] 데이터가 비어있습니다.")
        return

    print(f"[INFO] 총 {len(data_list)}개의 제품 이미지를 생성합니다.")

    # 2. 폰트 설정
    try:
        fonts = (
            ImageFont.truetype("arialbd.ttf", 32),
            ImageFont.truetype("arialbd.ttf", 18),
            ImageFont.truetype("arial.ttf", 18),
            ImageFont.truetype("arial.ttf", 14)
        )
    except IOError:
        print("[Info] 기본 폰트를 사용합니다.")
        def_font = ImageFont.load_default()
        fonts = (def_font, def_font, def_font, def_font)

    # 3. 저장 경로 설정
    output_dir = r"C:\Users\julie\Desktop\2025-2\TBT 무역장벽\food\output_images"
    
    # 폴더가 없으면 생성
    os.makedirs(output_dir, exist_ok=True)
    print(f"[INFO] 저장 위치: {output_dir}")

    # 4. 이미지 생성 반복
    for i, product in enumerate(data_list):
        # 파일명 설정
        filename = os.path.join(output_dir, f"fda_label_product_{i+1}.png")
        draw_fda_label(product, filename, fonts)

    print("\n" + "="*60)
    print(f"✅ [완료] 지정하신 폴더에 이미지 생성이 완료되었습니다.")
    print("="*60)

if __name__ == "__main__":
    generate_all_images()