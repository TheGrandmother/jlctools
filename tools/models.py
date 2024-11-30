from dataclasses import dataclass, fields
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

    _out_of_date = False

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
    minImageAccessId: None
    dataManualOfficialLink: str
    productBigImageAccessId: None

    def __post_init__(self):
        super(Component).__init__()

        def defaff(l):
            field_names = [f.name for f in fields(Price)]
            d = {k: v for (k, v) in cast(dict, l).items() if k in field_names}
            return d

        self.componentPrices = sorted(
            [Price(**defaff(l)) for l in self.componentPrices],
            key=lambda p: p.productPrice,
        )

    def is_basic(self):
        return (
            self.preferredComponentFlag or self.componentLibraryType == "base"
        )

    def __str__(self):
        def format_attr(attributes):
            if type(attributes) == str:
                return attributes
            longest = max(
                len(a.get("attribute_name_en", "")) for a in attributes
            )
            return "\n".join(
                [
                    f'  {(a["attribute_name_en"]+":").ljust(longest + 1, " ")} {a["attribute_value_name"]}'
                    for a in attributes
                    if "attribute_name_en" in a
                ]
            )

        something = [
            f"Comp\t{self.componentModelEn}",
            f"Type\t{self.componentTypeEn}",
            f"Name\t{self.componentName}",
            f"Spec\t{self.componentSpecificationEn}",
            f"LCSC\t{self.componentCode}",
            f"Price\t{self.componentPrices[0].productPrice}",
            f"Count\t{self.stockCount}",
            f"Link\thttps://jlcpcb.com/partdetail/{self.urlSuffix}",
        ]
        if self.attributes is not None:
            something += [f"Attr\t\n{format_attr(self.attributes)}"]
        else:
            something += [f"Desc\t{self.describe}"]

        if self.preferredComponentFlag:
            something += ["  Is preffered"]
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

        # dataclasses are the best thing ever....
        def defaff(l):
            field_names = [f.name for f in fields(Component)]
            raw_dict = cast(dict, l)
            d = {k: v for (k, v) in raw_dict.items() if k in field_names}
            diff = set(raw_dict.keys()) - set(field_names)
            if len(diff) != 0 and not Component._out_of_date:
                Component._out_of_date = True
                diff_types = [(n, type(raw_dict[n])) for n in diff]
                print(
                    f"WARNING: Component schema out of date. Additional fields: \n{diff_types}"
                )
            return d

        self.list = [Component(**defaff(l)) for l in self.list]
