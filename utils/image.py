import aiohttp
from PIL import Image
from io import BytesIO
import asyncio

async def create_collage(session: aiohttp.ClientSession, image_urls: list[str], size: int = 3) -> BytesIO:
    """
    creates a square collage from a list of image urls.
    size: 3 for 3x3, 5 for 5x5
    """
    if not image_urls:
        return None

    # determine individual image size (e.g., 300x300 for 3x3 results in 900x900)
    IMG_DIM = 300
    CANVAS_SIZE = size * IMG_DIM

    canvas = Image.new("RGB", (CANVAS_SIZE, CANVAS_SIZE), color=(20, 20, 20))

    async def fetch_image(url):
        if not url:
            return Image.new("RGB", (IMG_DIM, IMG_DIM), color=(50, 50, 50)) # placeholder
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    img = Image.open(BytesIO(data)).convert("RGB")
                    return img.resize((IMG_DIM, IMG_DIM))
        except Exception:
            pass
        return Image.new("RGB", (IMG_DIM, IMG_DIM), color=(50, 50, 50))

    # fetch all images concurrently
    tasks = [fetch_image(url) for url in image_urls[:size*size]]
    images = await asyncio.gather(*tasks)
    
    # fill remaining slots with placeholder if we don't have enough images
    while len(images) < size * size:
        images.append(Image.new("RGB", (IMG_DIM, IMG_DIM), color=(50, 50, 50)))

    # paste images onto canvas
    for i, img in enumerate(images):
        x = (i % size) * IMG_DIM
        y = (i // size) * IMG_DIM
        canvas.paste(img, (x, y))

    output = BytesIO()
    canvas.save(output, format="PNG")
    output.seek(0)
    return output

async def get_dominant_color(session: aiohttp.ClientSession, url: str) -> int:
    """
    downloads image and returns the dominant color as a hex integer.
    returns default discord dark grey (0x2F3136) on failure.
    """
    if not url:
        return 0x2F3136
        
    try:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.read()
                img = Image.open(BytesIO(data)).convert("RGB")
                
                # resize to 1x1 to get average color efficiently
                img = img.resize((1, 1))
                color = img.getpixel((0, 0))
                
                # convert (r, g, b) to hex integer
                return (color[0] << 16) + (color[1] << 8) + color[2]
    except Exception:
        pass
        
    return 0x2F3136
