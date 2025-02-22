from PIL import Image, ImageDraw, ImageFont

font_size = 36
font_path = '/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf'

def load(image_path):
    return Image.open(image_path)

def render_text(text):
    font = ImageFont.truetype(font_path, font_size)
    left, top, right, bottom = font.getbbox(text)
    text_width, text_height = right-left, bottom
    image = Image.new('RGB', (text_width, text_height), 'white')
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), text, fill='black', font=font)
    return image

def tile_images_horizontally(images, margin_pixels=50):
    widths, heights = zip(*(i.size for i in images))
    total_width = sum(widths) + margin_pixels*len(widths)
    max_height = max(heights)

    new_image = Image.new('RGB', (total_width, max_height), color='white')

    x_offset = 0
    for image in images:
        y_offset = (new_image.height-image.height)//2
        new_image.paste(image, (x_offset, y_offset))
        x_offset += image.width+margin_pixels

    return new_image

def tile_images_vertically(images, margin_pixels=50):
    widths, heights = zip(*(i.size for i in images))
    total_height = sum(heights) + margin_pixels*(len(heights)-1)
    max_width = max(widths)

    new_image = Image.new('RGB', (max_width, total_height), color='white')

    y_offset = 0
    for image in images:
        x_offset = (new_image.width-image.width)//2
        new_image.paste(image, (x_offset, y_offset))
        y_offset += image.height+margin_pixels

    return new_image
