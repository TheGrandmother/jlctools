import json
from os import path, makedirs
from .models import base_payload, Component, Response
from pathlib import Path
from datetime import datetime, timedelta, UTC
import dataclasses
import requests

list_endpoint = "https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList"

ohm = "Ω"


def body_builder(
    keyword,
    page=1,
    case="",
    base=True,
    extended=True,
    cheap=True,
    min_stock=100,
    page_size=100,
):
    return {
        **base_payload,
        "keyword": keyword.replace("OHM", ohm),
        "preferredComponentFlagCheck": extended,
        "currentPage": page,
        "pageSize": page_size,
        "componentLibraryType": "base" if base else "",
        "preferredComponentFlag": base,
        "startStockNumber": min_stock,
        "componentSpecification": case,
        "sortMode": "PRICE_SORT" if cheap else "",
        "sortASC": "ASC" if cheap else "",
    }


CACHE_PATH = path.join(Path.home(), ".cache")
CACHE_FILE = "jlcparts_cache.json"


class Cache:

    ttl = timedelta(days=1)
    file_path = path.join(CACHE_PATH, CACHE_FILE)

    def __init__(self):
        if not path.exists(CACHE_PATH):
            print("Creating cache folder")
            makedirs(CACHE_PATH)
        if not path.exists(self.file_path):
            open(self.file_path, "w+").close()
        try:
            with open(self.file_path, "r") as f:
                self.dict = json.load(f)
        except json.JSONDecodeError:
            self.dict = {}

    def get(self, key):
        if key not in self.dict:
            return None
        [timestamp, part] = self.dict[key]
        if datetime.now(UTC) - datetime.fromisoformat(timestamp) > self.ttl:
            del self.dict[key]
            return None
        return part

    def write(self, key, part):
        self.dict[key] = [
            datetime.now(UTC).isoformat(),
            dataclasses.asdict(part),
        ]

        with open(self.file_path, "w") as f:
            json.dump(self.dict, f, indent=2)
        return part


cache = Cache()


def get_by_code(code):
    cached = cache.get(code)
    if cached is not None:
        return Component(**cached)
    print(f"Fetching data for {code}")

    mjau = requests.post(
        list_endpoint, json=body_builder(code, base=False, extended=False)
    )
    resp = Response(**mjau.json()["data"]["componentPageInfo"])
    matching = list(filter(lambda c: c.componentCode == code, resp.list))
    if len(matching) != 1:
        raise Exception(f"Got {len(matching)} results with code {code}")
    cache.write(code, matching[0])
    return matching[0]


def search(keyword, case="", base=True, count=1, min_stock=100):
    mjau = requests.post(
        list_endpoint,
        json=body_builder(
            keyword.replace("OHM", ohm),
            base=base,
            extended=base,
            case=case,
            min_stock=min_stock,
        ),
    )
    resp_json = mjau.json()["data"]["componentPageInfo"]
    if resp_json["total"] == 0:
        print(f"No {'basic' if base else ''} parts found for {keyword}")
        quit(1)
    resp = Response(**resp_json)
    separator = "\n" + ("=" * 10) + "\n"
    print(separator.join(map(str, resp.list[:count])))
