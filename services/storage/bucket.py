import io
import aiohttp


class ImageS3Bucket:

    @staticmethod
    async def get_image_by_url(url: str) -> io.BytesIO:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                img = await resp.read()
        return io.BytesIO(img)
