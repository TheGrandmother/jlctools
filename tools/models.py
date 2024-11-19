from dataclasses import dataclass, field
import json
from typing import Any, List, cast

base_payload = {
    "keyword": "Operational",
    "preferredComponentFlagCheck": False,
    "componentLibraryTypeCheck": True,
    "currentPage": 1,
    "pageSize": 25,
    "searchSource": "search",
    "componentAttributes": [],
    "componentLibraryType": "base",
    "preferredComponentFlag": False,
    "stockFlag": None,
    "stockSort": None,
    "componentBrand": None,
    "componentSpecification": None,
}


class BaseModel:
    @classmethod
    def from_json(cls, string: str):
        data: dict = json.loads(string)
        return cls(**data)

    def json(self):
        return json.dumps(self, default=lambda o: o.__dict__)


@dataclass
class Price(BaseModel):
    endNumber: int
    productPrice: float
    startNumber: int


@dataclass
class Component(BaseModel):
    allowPostFlag: bool
    attributes: None
    canPresaleNumber: int
    componentAlternativesCode: None
    componentBrandEn: str
    componentBrandHigh: str
    componentModelHigh: str
    componentCode: str
    componentId: int
    componentImageUrl: str
    componentLibraryType: str
    componentModelEn: str
    componentName: str
    componentNameEn: None
    componentPrices: List[Price]
    componentProductType: int
    componentSource: str
    componentSpecificationEn: str
    componentTypeEn: str
    dataManualFileAccessId: str
    dataManualUrl: str
    describe: str
    erpComponentName: str
    encapsulationNumber: str
    estimateDate: str
    fullReelPrice: str
    firstSortAccessId: str
    firstSortName: None
    idleFlag: bool
    initialPrice: str
    imageList: list
    isBuyComponent: str
    lcscGoodsUrl: str
    leastPatchNumber: int
    lossNumber: int
    manufacturerBlackFlag: None
    mergedComponentCode: None
    minImage: str
    minPurchaseNum: int
    preMinPurchaseNum: int
    noBuyReason: None | str
    preferredComponentFlag: bool
    rankScore: int
    remarkHigh: str
    replaceUrlSuffix: None
    score: float
    shopCostPrice: float
    secondSortAccessId: str
    secondSortName: None
    stockCount: int
    urlSuffix: str

    def __post_init__(self):
        super(Component).__init__()
        self.componentPrices = sorted(
            [Price(**cast(dict, l)) for l in self.componentPrices],
            key=lambda p: p.productPrice,
        )

    def is_basic(self):
        return (
            self.preferredComponentFlag or self.componentLibraryType == "base"
        )

    def __str__(self):
        something = [
            f"Comp\t{self.componentModelEn}",
            f"Name\t{self.componentName}",
            f"Desc\t{self.describe}",
            f"Spec\t{self.componentSpecificationEn}",
            f"LCSC\t{self.componentCode}",
            f"Price\t{self.componentPrices[0].productPrice}",
            f"Count\t{self.stockCount}",
            f"Attr\t{self.attributes}",
            f"Link\thttps://jlcpcb.com/partdetail/{self.urlSuffix}",
        ]
        if self.preferredComponentFlag:
            something += ["Is preffered"]
        if self.noBuyReason is not None:
            something += [self.noBuyReason]
        return "\n".join(something)


@dataclass
class Response:
    endRow: int
    hasNextPage: bool
    hasPreviousPage: bool
    isFirstPage: bool
    isLastPage: bool
    navigateFirstPage: int
    navigateLastPage: int
    navigatePages: int
    navigatepageNums: Any
    nextPage: int
    pageNum: int
    pageSize: int
    pages: int
    prePage: int
    size: int
    startRow: int
    total: int
    list: List[Component]

    def __post_init__(self):
        super(Response).__init__()
        self.list = [Component(**cast(dict, l)) for l in self.list]
