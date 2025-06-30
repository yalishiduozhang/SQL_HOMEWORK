from PIL import Image
import os

def create_icon():
    """创建应用图标"""
    try:
        # 创建一个简单的图标
        size = 256
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        
        # 绘制一个简单的电影图标
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        
        # 背景圆
        margin = 20
        draw.ellipse([margin, margin, size-margin, size-margin], 
                    fill=(64, 128, 255, 255), outline=(32, 64, 128, 255), width=4)
        
        # 播放按钮
        triangle_margin = 80
        triangle_points = [
            (triangle_margin, triangle_margin),
            (triangle_margin, size-triangle_margin),
            (size-triangle_margin, size//2)
        ]
        draw.polygon(triangle_points, fill=(255, 255, 255, 255))
        
        # 保存图标
        if not os.path.exists('static/images'):
            os.makedirs('static/images')
            
        # 保存为ICO文件（多尺寸）
        icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        icons = []
        for icon_size in icon_sizes:
            resized = img.resize(icon_size, Image.Resampling.LANCZOS)
            icons.append(resized)
        
        icons[0].save('static/images/logo.ico', format='ICO', sizes=icon_sizes)
        
        # 也保存为PNG格式
        img.save('static/images/logo.png', format='PNG')
        
        print("✓ 图标文件创建成功")
        print("  - static/images/logo.ico")
        print("  - static/images/logo.png")
        return True
        
    except Exception as e:
        print(f"✗ 图标创建失败: {e}")
        return False

if __name__ == "__main__":
    create_icon()
