from typing import Optional, Dict, Annotated

from pydantic import BaseModel

#this class is used for the brower profile handlings
class BrowserProfile(BaseModel):
    browser: str
    impersonate : str