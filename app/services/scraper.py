import asyncio
import ipaddress
import json
import logging
import re
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger("root")

COMMON_SELECTORS = [
    ".product_price_current",
    ".js-current-price",
    ".price--current",
    ".price__value",
    ".product-price",
]


async def is_safe_url(url: str) -> bool:

    try:
        parsed = urlparse(url)
        if parsed.scheme not in ["http", "https"]:
            return False

        hostname = parsed.hostname
        if not hostname:
            return False

        loop = asyncio.get_running_loop()

        addr_info = await loop.getaddrinfo(hostname, None)

        ip_str = addr_info[0][4][0]
        ip_obj = ipaddress.ip_address(ip_str)

        if ip_obj.is_loopback or ip_obj.is_private or ip_obj.is_multicast:
            return False

        return True
    except Exception as e:
        logger.warning(f"URL validation failed for {url}: {e}")
        return False


async def get_current_price(url: str) -> float | None:

    if not await is_safe_url(url):
        logger.error(f"SSRF attempt blocked or invalid URL: {url}")
        return None

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.google.com/",
    }

    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        try:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")

            scripts = soup.find_all("script", type="application/ld+json")
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, list):
                        data = data[0]
                    if data.get("@type") == "Product":
                        offers = data.get("offers")
                        if isinstance(offers, dict):
                            return float(offers.get("price"))
                        elif isinstance(offers, list):
                            return float(offers[0].get("price"))
                except (ValueError, KeyError, TypeError):
                    continue

            price_meta = soup.find("meta", property="product:price:amount")
            if price_meta:
                return float(price_meta["content"])

            price_element = soup.select_one(", ".join(COMMON_SELECTORS))
            if price_element:
                raw_text = price_element.get_text(strip=True)
                cleaned_text = re.sub(r"[^\d.]", "", raw_text.replace(",", "."))

                if cleaned_text and len(cleaned_text) < 10:
                    return float(cleaned_text)

            logger.warning(f"Price not found in HTML for {url}")

        except Exception as e:
            logger.error(f"Parsing error for {url}: {e}")
            return None

    return None
