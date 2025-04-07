import asyncio
import json
import os

import nodriver as uc
from nodriver import cdp

from .parser_utils import get_cf_template
from .logger import logger
from .redis_utils import set_cookies


async def parse_cf_clearance_cookies(
    url,
    browser_config_args,
    task_id
):
    browser_config_args = browser_config_args or {}
    browser_config_args = {
        "headless": False,
        "browser_args": [],
        "lang": "en-US",
        **browser_config_args
    }
    browser = await uc.start(**browser_config_args)

    logger.info(f"Browser info:- {browser.info}")

    # await tab.send(cdp.network.set_user_agent_override(
    #     user_agent=browser.info.get("User-Agent").replace("Headless", "")
    #         ))

    page = await browser.get(url, new_tab=True)

    # await page.save_screenshot('first_page.png')
    await click_check_box(page)
    # await page.save_screenshot('final_page.png')

    cookie_obj_list = (await browser.cookies.get_all())
    cookies_list_req_format = [
        {
            "name": cookie_obj.name,
            "value": cookie_obj.value,
            "domain": cookie_obj.domain,
            "path": "/"
        }
        for
        cookie_obj
        in
        cookie_obj_list
    ]

    cookies_response = {}
    cookies_response.update({
            "cookies": cookies_list_req_format,
            "userAgent": browser.info.get('User-Agent')
        })

    set_cookies(
        task_id, state="Finished",
        cookies=cookies_response,
        error=None)

    browser.stop()


async def template_location(
    page,
    template_img=None
):
    """
    attempts to find the location of given template image in the current viewport
    the only real use case for this is bot-detection systems.
    you can find for example the location of a 'verify'-checkbox,
    which are hidden from dom using shadow-root's or workers.

    template_image can be custom (for example your language, included is english only),
    but you need to create the template image yourself, which is just a cropped
    image of the area, see example image, where the target is exactly in the center.
    template_image can be custom (for example your language), but you need to
    create the template image yourself, where the target is exactly in the center.

    example (111x71)
    ---------
    this includes the white space on the left, to make the box center

    .. image:: template_example.png
        :width: 111
        :alt: example template image


    :param template_img:
    :type template_img:
    :return:
    :rtype:
    """
    try:
        import cv2
    except ImportError:
        logger.warning(
            """
            missing package
            ----------------
            template_location function needs the computer vision library "opencv-python" installed
            to install:
            pip install opencv-python

        """
        )
        return
    try:

        # await self.save_screenshot("screen.jpg")
        await page.save_screenshot("screen.jpg")
        await asyncio.sleep(0.05)
        im = cv2.imread("screen.jpg")
        im_gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

        if template_img:
            template = cv2.imread(str(template_img))
        else:
            with open("cf_template.png", "w+b") as fh:
                fh.write(get_cf_template())

            template = cv2.imread("cf_template.png")
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        match = cv2.matchTemplate(im_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        (min_v, max_v, min_l, max_l) = cv2.minMaxLoc(match)
        (xs, ys) = max_l
        tmp_h, tmp_w = template_gray.shape[:2]
        xe = xs + tmp_w
        ye = ys + tmp_h
        cx = (xs + xe) // 2
        cy = (ys + ye) // 2
        return cx, cy
    except (Exception) as e:
        logger.warning(f"Error occured {e}")
    finally:
        try:
            os.remove("cf_template.png")
            os.remove("screen.jpg")
        except Exception:
            logger.warning("could not unlink temporary screenshot")
        if template_img:
            return


async def click_check_box(page, template_img=None):
    logger.info("Waiting for Human verify checkbox")
    await page
    await page.sleep(20)
    coordinates = await template_location(page, template_img)
    x, y = coordinates
    await click_action(page, x, y)
    await page.wait(20)
    logger.info("Clicked Human verify checkbox")


async def click_action(tab, x, y):
    await tab.send(
        cdp.input_.dispatch_mouse_event(
            "mousePressed",
            x=x,
            y=y,
            modifiers=0,
            button=cdp.input_.MouseButton("left"),
            buttons=1,
            click_count=1,
        )
    )

    await tab.send(
        cdp.input_.dispatch_mouse_event(
            "mouseReleased",
            x=x,
            y=y,
            modifiers=0,
            button=cdp.input_.MouseButton("left"),
            buttons=1,
            click_count=1,
        )
    )
