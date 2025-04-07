import asyncio

from fastapi import FastAPI, BackgroundTasks, status
from fastapi.responses import JSONResponse

from cf_clearance_collector.parser import parse_cf_clearance_cookies
from cf_clearance_collector.models import Payload, TaskPayload
from cf_clearance_collector.logger import logger
from cf_clearance_collector.redis_utils import set_cookies

from cf_clearance_collector.redis_utils import (
    get_uuid, initialize_redis, fetch_cookies
)


app = FastAPI()


@app.post("/solve_captcha/clouflare/create_task/")
async def create_captcha_solve_task(
    payload: Payload,
    background_tasks: BackgroundTasks
):

    uuid_ = get_uuid()
    initialize_redis(uuid_)
    error = None
    state = "Created Task"
    status_code = status.HTTP_201_CREATED

    logger.info(f"Request payload: {payload}")
    try:
        background_tasks.add_task(
            combined_task,
            url=payload.url,
            browser_config_args=payload.browser_config_args.dict() if payload.browser_config_args else {},
            task_id=uuid_
        )
    except Exception as e:
        logger.error(f"Error occured: {e}")
        error = str(e)
        state = "Failed to create task"
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=status_code,
        content={"state": state, "task_id": uuid_, "error": error}
    )


@app.post("/solve_captcha/clouflare/get_cookie/")
async def get_captcha_solve_task(
    payload: TaskPayload,
):
    content = fetch_cookies(payload.task_id)
    if content and content.get('cookies'):
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=content
        )
    elif content and content.get('state') == "Processing":
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content=content
        )

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=content
    )


async def combined_task(**args):
    task = asyncio.create_task(main_task(**args))
    asyncio.create_task(monitor_timeout(task, 120))  # Start timeout monitor


async def main_task(**args):
    try:
        logger.info("Task started")
        await parse_cf_clearance_cookies(**args)
        logger.info("Task finished")
        return "Success"
    except asyncio.CancelledError:
        set_cookies(
            args.get('task_id'), state="Finished",
            cookies=None, error="Taks Failed")
        logger.warning("Task was cancelled due to timeout")
        return "Cancelled"


async def monitor_timeout(task, timeout):
    await asyncio.sleep(timeout)  # Wait for the timeout duration
    if not task.done():  # If task is still running, cancel it
        logger.warning("Task took too long. Cancelling...")
        task.cancel()
