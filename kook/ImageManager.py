class ImageManager:
    reg_process: str = 'satic/img/reg-1.png'


from PIL import Image, ImageDraw, ImageFont

# 创建一个新的白色背景图像
width, height = 400, 300
image = Image.new("RGB", (width, height), color="white")
draw = ImageDraw.Draw(image)

# 定义表格的行数和列数
rows = 5
cols = 4
cell_width = width // cols
cell_height = height // rows

# 绘制表格的行和列
for i in range(1, cols):
    # 绘制竖线
    draw.line((i * cell_width, 0, i * cell_width, height), fill="black")

for i in range(1, rows):
    # 绘制横线
    draw.line((0, i * cell_height, width, i * cell_height), fill="black")

# 在单元格中添加文本
font = ImageFont.load_default()
for row in range(rows):
    for col in range(cols):
        text = f"({row},{col})"
        text_width, text_height = draw.textsize(text, font=font)
        x = col * cell_width + (cell_width - text_width) // 2
        y = row * cell_height + (cell_height - text_height) // 2
        draw.text((x, y), text, fill="black", font=font)

# 保存图像
image.save("table_image.png")
image.show()
