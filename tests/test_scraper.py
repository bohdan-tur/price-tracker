import httpx

from app.services.scraper import get_current_price


async def test_get_current_price_success(httpx_mock):
    fake_html = """
    <html>
        <body>
            <span class="price__value">1500.00</span>
        </body>
    </html>
    """

    httpx_mock.add_response(
        url="https://rozetka.com.ua/fake_item/", text=fake_html, status_code=200
    )

    price = await get_current_price("https://rozetka.com.ua/fake_item/")

    assert price == 1500.0


async def test_get_current_price_not_found(httpx_mock):

    httpx_mock.add_response(
        url="https://rozetka.com.ua/fake_item/",
        text="<html><body><h1>Product not found</h1></body></html>",
    )

    price = await get_current_price("https://rozetka.com.ua/fake_item/")

    assert price is None


async def test_get_current_price_network_error(httpx_mock):

    httpx_mock.add_exception(
        httpx.ReadTimeout("Connection timeout"), url="https://rozetka.com.ua/fake_item/"
    )

    price = await get_current_price("https://rozetka.com.ua/fake_item/")

    assert price is None
