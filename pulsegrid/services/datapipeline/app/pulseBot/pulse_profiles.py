"""
    this file contains the browser profiles that are gonna used for the crawling and scrapping purpose of pulseBot
"""

from typing import List

from .schema import BrowserProfile

PROFILES : List[BrowserProfile] = [
    BrowserProfile(
        browser="Chrome (Windows)",
        impersonate="chrome",
    ),
    BrowserProfile(
        browser="Safari (macOS)",
        impersonate="safari",  
    )
]