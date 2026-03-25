from __future__ import annotations

import argparse
import asyncio
import base64
import json
import os
import platform
import subprocess
import sys
from pathlib import Path

import httpx

LOGIN_BUTTON_SELECTORS = [
    'button:has-text("登录")',
    'button[role="button"]:has-text("登录")',
    'text=登录 >> button',
    'a:has-text("我")',
    'li:has-text("我")',
    'text=我',
]

QRCODE_TAB_SELECTORS = [
    'text=扫码登录',
    'text=二维码登录',
    'text=小红书 App 扫码登录',
]

QRCODE_IMAGE_SELECTORS = [
    'img[alt*="二维码"]',
    'img[src*="qrcode"]',
    '[class*="qrcode"] img',
    '[role="dialog"] img:visible',
]

QRCODE_CANVAS_SELECTORS = [
    '[class*="qrcode"] canvas',
    '[role="dialog"] canvas:visible',
    'canvas',
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Start MediaCrawler QR-code auth flow")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--platform", default="xhs")
    parser.add_argument("--qr-output", required=True)
    parser.add_argument("--auth-ready-marker", required=True)
    parser.add_argument("--open-qr", action="store_true")
    return parser


def save_base64_png(base64_data: str, output_path: Path) -> None:
    payload = base64_data.split(",", 1)[1] if "," in base64_data else base64_data
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(base64.b64decode(payload))


def open_qr_image(image_path: Path) -> None:
    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.Popen(["open", str(image_path)])
        elif system == "Windows":
            os.startfile(str(image_path))  # type: ignore[attr-defined]
        else:
            subprocess.Popen(["xdg-open", str(image_path)])
    except Exception:
        pass


async def write_debug_artifacts(page, *, prefix: str, output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    screenshot_path = output_dir / f"{prefix}.png"
    html_path = output_dir / f"{prefix}.html"
    try:
        await page.screenshot(path=str(screenshot_path), full_page=True)
    except Exception:
        pass
    try:
        html_path.write_text(await page.content(), encoding="utf-8")
    except Exception:
        pass
    return {
        "debug_screenshot": str(screenshot_path),
        "debug_html": str(html_path),
        "page_url": page.url,
    }


async def click_first_visible(page, selectors: list[str], *, timeout_ms: int = 5000) -> str:
    for selector in selectors:
        try:
            locator = page.locator(selector).first
            await locator.wait_for(state="visible", timeout=timeout_ms)
            await locator.click()
            return selector
        except Exception:
            continue
    raise RuntimeError(f"未找到可点击元素，候选选择器: {selectors}")


async def wait_for_dialog(page, *, timeout_ms: int = 10000) -> None:
    dialog_selectors = ['[role="dialog"]', 'div:has-text("小红书 App 扫码登录")', 'div:has-text("手机号登录")']
    for selector in dialog_selectors:
        try:
            await page.locator(selector).first.wait_for(state="visible", timeout=timeout_ms)
            return
        except Exception:
            continue


async def try_switch_to_qrcode_tab(page) -> None:
    for selector in QRCODE_TAB_SELECTORS:
        try:
            locator = page.locator(selector).first
            if await locator.is_visible(timeout=1500):
                await locator.click()
                await page.wait_for_timeout(800)
                return
        except Exception:
            continue


async def extract_qrcode_base64(page) -> tuple[str | None, str | None]:
    for selector in QRCODE_IMAGE_SELECTORS:
        try:
            locator = page.locator(selector).first
            await locator.wait_for(state="visible", timeout=4000)
            src = await locator.get_attribute("src")
            if not src:
                continue
            if src.startswith("data:image"):
                return src, selector
            if src.startswith("http://") or src.startswith("https://"):
                async with httpx.AsyncClient(follow_redirects=True) as client:
                    response = await client.get(src, headers={"User-Agent": "Mozilla/5.0"})
                    response.raise_for_status()
                    return base64.b64encode(response.content).decode("utf-8"), selector
        except Exception:
            continue

    for selector in QRCODE_CANVAS_SELECTORS:
        try:
            locator = page.locator(selector).first
            await locator.wait_for(state="visible", timeout=2500)
            screenshot = await locator.screenshot()
            return base64.b64encode(screenshot).decode("utf-8"), selector
        except Exception:
            continue

    return None, None


async def run_auth(repo_root: Path, platform_name: str, qr_output: Path, auth_ready_marker: Path, open_qr: bool) -> int:
    sys.path.insert(0, str(repo_root))
    os.chdir(repo_root)

    import config
    from media_platform.xhs.core import XiaoHongShuCrawler
    from media_platform.xhs.login import XiaoHongShuLogin
    from playwright.async_api import async_playwright
    from tenacity import RetryError
    from tools import utils

    if platform_name != "xhs":
        raise SystemExit("当前二维码授权只支持 xhs。")

    config.PLATFORM = "xhs"
    config.LOGIN_TYPE = "qrcode"
    config.HEADLESS = False
    config.CDP_HEADLESS = False
    config.ENABLE_CDP_MODE = True
    config.SAVE_LOGIN_STATE = True

    crawler = XiaoHongShuCrawler()
    async with async_playwright() as playwright:
        browser_context = await crawler.launch_browser_with_cdp(
            playwright=playwright,
            playwright_proxy=None,
            user_agent=crawler.user_agent,
            headless=False,
        )
        crawler.browser_context = browser_context
        crawler.context_page = await browser_context.new_page()
        await crawler.context_page.goto(f"{crawler.index_url}/explore", wait_until="domcontentloaded", timeout=30000)
        await crawler.context_page.wait_for_timeout(2500)

        try:
            current_cookie = await browser_context.cookies()
            _, cookie_dict = utils.convert_cookies(current_cookie)
            current_web_session = cookie_dict.get("web_session")
            if current_web_session:
                login_probe = crawler.context_page.locator('a[href*="/user/profile/"], text=我').first
                if await login_probe.is_visible(timeout=2000):
                    auth_ready_marker.parent.mkdir(parents=True, exist_ok=True)
                    auth_ready_marker.write_text("auth_ready=1\n", encoding="utf-8")
                    print(
                        json.dumps(
                            {
                                "status": "login_success",
                                "platform": platform_name,
                                "auth_ready_marker": str(auth_ready_marker),
                                "already_logged_in": True,
                                "next_action_user": "登录态已就绪，可以继续刚才的社媒或全流程任务。",
                            },
                            ensure_ascii=False,
                        ),
                        flush=True,
                    )
                    return 0
        except Exception:
            pass

        try:
            clicked_selector = await click_first_visible(crawler.context_page, LOGIN_BUTTON_SELECTORS, timeout_ms=8000)
        except Exception:
            debug_payload = await write_debug_artifacts(
                crawler.context_page,
                prefix=f"{platform_name}-login-button-missing",
                output_dir=qr_output.parent,
            )
            print(
                json.dumps(
                    {
                        "status": "error",
                        "reason": "login_button_not_found",
                        "candidate_selectors": LOGIN_BUTTON_SELECTORS,
                        **debug_payload,
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )
            return 1
        await crawler.context_page.wait_for_timeout(1500)
        if "/user/profile/" in crawler.context_page.url:
            auth_ready_marker.parent.mkdir(parents=True, exist_ok=True)
            auth_ready_marker.write_text("auth_ready=1\n", encoding="utf-8")
            print(
                json.dumps(
                    {
                        "status": "login_success",
                        "platform": platform_name,
                        "auth_ready_marker": str(auth_ready_marker),
                        "login_button_selector": clicked_selector,
                        "page_url": crawler.context_page.url,
                        "detected_after_click": True,
                        "next_action_user": "登录态已就绪，可以继续刚才的社媒或全流程任务。",
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )
            return 0
        await wait_for_dialog(crawler.context_page, timeout_ms=10000)
        await try_switch_to_qrcode_tab(crawler.context_page)
        base64_qrcode_img, matched_qr_selector = await extract_qrcode_base64(crawler.context_page)
        if not base64_qrcode_img:
            debug_payload = await write_debug_artifacts(
                crawler.context_page,
                prefix=f"{platform_name}-qrcode-missing",
                output_dir=qr_output.parent,
            )
            print(
                json.dumps(
                    {
                        "status": "error",
                        "reason": "qrcode_not_found",
                        "login_button_selector": clicked_selector,
                        **debug_payload,
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )
            return 1

        save_base64_png(base64_qrcode_img, qr_output)
        if open_qr:
            open_qr_image(qr_output)

        current_cookie = await browser_context.cookies()
        _, cookie_dict = utils.convert_cookies(current_cookie)
        no_logged_in_session = cookie_dict.get("web_session")

        print(
            json.dumps(
                {
                    "status": "qrcode_ready",
                    "platform": platform_name,
                    "qr_code_path": str(qr_output),
                    "auth_ready_marker": str(auth_ready_marker),
                    "login_button_selector": clicked_selector,
                    "qrcode_selector": matched_qr_selector,
                    "next_action_user": "请现在用小红书 App 扫码，扫完后回复：扫好了",
                    "reply_when_done": "扫好了",
                },
                ensure_ascii=False,
            ),
            flush=True,
        )

        login_obj = XiaoHongShuLogin(
            login_type="qrcode",
            browser_context=browser_context,
            context_page=crawler.context_page,
        )

        try:
            await login_obj.check_login_state(no_logged_in_session)
        except RetryError:
            print(
                json.dumps(
                    {
                        "status": "timeout",
                        "platform": platform_name,
                        "next_action_user": "二维码已超时，请重新运行 /本地调研授权。",
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )
            return 1

        auth_ready_marker.parent.mkdir(parents=True, exist_ok=True)
        auth_ready_marker.write_text("auth_ready=1\n", encoding="utf-8")
        print(
            json.dumps(
                {
                    "status": "login_success",
                    "platform": platform_name,
                    "auth_ready_marker": str(auth_ready_marker),
                    "qr_code_path": str(qr_output),
                    "next_action_user": "登录态已就绪，可以继续刚才的社媒或全流程任务。",
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
        await asyncio.sleep(2)
        return 0


def main() -> int:
    args = build_parser().parse_args()
    return asyncio.run(
        run_auth(
            repo_root=Path(args.repo_root).expanduser(),
            platform_name=args.platform,
            qr_output=Path(args.qr_output).expanduser(),
            auth_ready_marker=Path(args.auth_ready_marker).expanduser(),
            open_qr=args.open_qr,
        )
    )


if __name__ == "__main__":
    raise SystemExit(main())
