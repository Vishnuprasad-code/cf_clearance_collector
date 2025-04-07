from pydantic import BaseModel
from typing import Optional, List


class BrowserConfig(BaseModel):
    user_data_dir: Optional[str] = None
    headless: bool
    browser_executable_path: Optional[str] = None
    browser_args: Optional[List[str]] = None
    sandbox: bool = True
    lang: str
    host: Optional[str] = None
    port: Optional[int] = None
    expert: Optional[str] = None


class Payload(BaseModel):
    url: str
    browser_config_args: Optional[BrowserConfig] = None


class TaskPayload(BaseModel):
    task_id: str
