from pydantic import BaseModel, EmailStr
from fastapi import FastAPI, Header
from enum import Enum

from fastapi import Body, Cookie, FastAPI, Path, Query
from pydantic import BaseModel, Field, HttpUrl

app = FastAPI()

# path 数据类型检测


@app.get("/items/{item_id}")
async def root(item_id: int):
    return {"item_id": item_id}


class ModelName(str, Enum):
    # path 变量枚举
    alexnet = 'alexnet'
    resnet = 'resnet'
    lenet = 'lenet'


@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    # 获取枚举值 model_name.value
    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}


# path包含路径的路径参数
@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}


fake_items_db = [{"item_name": "Foo"}, {
    "item_name": "Bar"}, {"item_name": "Baz"}]


@app.get("/temp/")
# 查询参数默认值 http://127.0.0.1:8000/temp/?skip=0&limit=10
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip: skip + limit]


@app.get("/ta/{item_id}")
# 可选查询参数，设置可以为None，默认为None
async def read_item(item_id: str, q: str | None = None):
    if q:
        return {"item_id": item_id, "q": q}
    return {"item_id": item_id}


@app.get("/it/{item_id}")
# bool类型参数
async def read_item(item_id: str, q: str | None = None, short: bool = False):
    item = {"item_id": item_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item


@app.get("/weather/{item_id}")
# 必须参数：不指定默认值
async def read_user_item(item_id: str, needy: str):
    item = {"item_id": item_id, "needy": needy}
    return item


class Item(BaseModel):
    # Pydantic models 构建post请求体模型
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


@app.post("/items/")
async def create_item(item: Item):
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict


@app.put("/items/{item_id}")
# 请求体+path参数+query参数
async def create_item(item_id: int, item: Item, q: str | None = None):
    result = {"item_id": item_id, **item.dict()}
    if q:
        result.update({"q": q})
    return result


@app.get("/teacher/")
# Query变量，对str 支持min_length，max_length，regex
# default=...或default=Required或者没有default表示此查询参数必选
async def read_items(q: str | None = Query(default=None, max_length=50)):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


@app.get("/page/")
# 查询参数list
# http://localhost:8000/items/?q=foo&q=bar
async def read_items(q: list[str] | None = Query(default=None)):
    query_items = {"q": q}
    return query_items


@app.get("/word/")
# 查询参数添加元数据和数据验证
async def read_items(q: str | None = Query(
    alias="item-query",
    title="Query string",
    description="Query string for the items to search in the database that have a good match",
    min_length=3,
    max_length=50,
    regex="^fixedquery$",
    deprecated=True,
    include_in_schema=False)
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


@app.get("/noodle/{item_id}")
# Path参数添加元数据（支持所有Query元数据）和数据验证
# 第一个参数为 * 让python将后续参数视为 kwargs
async def read_items(
    *,
    item_id: int = Path(title="The ID of the item to get", ge=0, le=1000),
    q: str,
    size: float = Query(gt=0, lt=10.5)
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results


class User(BaseModel):
    username: str
    full_name: str | None = None


@app.put("/user/{item_id}")
# 多个请求体
# {
#   "item": {
#       "name": "Foo",
#       "description": "The pretender",
#       "price": 42.0,
#       "tax": 3.2
#   },
#   "user": {
#       "username": "dave",
#       "full_name": "Dave Grohl"
#   }
# }
async def update_item(item_id: int, item: Item, user: User):
    results = {"item_id": item_id, "item": item, "user": user}
    return results


@app.put("/fire/{item_id}")
# 使用Body参数定义请求体，另外支持Query元数据和数据验证
async def update_item(item_id: int,  importance: int = Body(embed=True)):
    results = {"item_id": item_id, "importance": importance}
    return results


@app.put("/fire2/{item_id}")
# 使用Body参数定义请求体，混合Pydantic models
async def update_item(item_id: int, item: Item, user: User, importance: int = Body()):
    results = {"item_id": item_id, "item": item,
               "user": user, "importance": importance}
    return results


class Goods(BaseModel):
    # 在Pydantic models中使用Field定义元数据和数据验证
    name: str
    description: str | None = Field(
        default=None, title="The description of the item", max_length=300)
    price: float = Field(
        gt=0, description="The price must be greater than zero")
    tax: float | None = None


@app.put("/goods/{item_id}")
async def update_item(item_id: int, item: Goods = Body(embed=True)):
    results = {"item_id": item_id, "item": item}
    return results


class Iters(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: list[str] = []  # list类型
    tags2: set[str] = set()  # set类型，自动去重


@app.put("/iters/{item_id}")
async def update_item(item_id: int, item: Iters):
    results = {"item_id": item_id, "item": item}
    return results


class Image(BaseModel):
    url: HttpUrl  # 特殊类型
    name: str


class School(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()
    image: Image | None = None  # 嵌套模型


@app.put("/schools/{item_id}")
async def update_item(item_id: int, item: School):
    results = {"item_id": item_id, "item": item}
    return results


class Image2(BaseModel):
    url: HttpUrl
    name: str


class Item2(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()
    images: list[Image2] | None = None


class Offer(BaseModel):
    name: str
    description: str | None = None
    price: float
    items: list[Item2]


@app.post("/offers/")
# 多重嵌套
async def create_offer(offer: Offer):
    return offer


@app.post("/index-weights/")
# 只指定键和值类型，不指定键名
async def create_index_weights(weights: dict[int, float]):
    return weights


class Kick(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

# 添加example，只影响docs
    class Config:
        schema_extra = {
            "example": {
                "name": "Foo",
                "description": "A very nice Item",
                "price": 35.4,
                "tax": 3.2,
            }
        }


@app.put("/kick/{item_id}")
async def update_item(item_id: int, item: Kick):
    results = {"item_id": item_id, "item": item}
    return results


# Path() Query() Header() Cookie() Body() Form() File() 都可以使用example、examples来添加说明
@app.put("/exs/{item_id}")
async def update_item(
    item_id: int,
    item: Item = Body(
        example={
            "name": "Foo",
            "description": "A very nice Item",
            "price": 35.4,
            "tax": 3.2,
        },
    ),
):
    results = {"item_id": item_id, "item": item}
    return results


@app.get("/cooks/")
# cookie参数
async def read_items(ads_id: str | None = Cookie(default=None)):
    return {"ads_id": ads_id}


@app.get("/pubs/")
# header参数
async def read_items(token: str | None = Header(default=None)):
    return {"token": token}


@app.get("/pubs2/")
async def read_items(x_token: list[str] | None = Header(default=None)):
    return {"X-Token values": x_token}


class Res(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: list[str] = []


@app.post("/res/", response_model=Res)
# response_model定义响应模型
async def create_item(item: Res):
    return item


class UserIn(BaseModel):
    username: str
    password: str
    email: EmailStr
    full_name: str | None = None


class UserOut(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None


@app.post("/useres/", response_model=UserOut)
# 通过不同模型过滤password
async def create_user(user: UserIn):
    return user


class Meti(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float = 10.5
    tags: list[str] = []


metis = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The bartenders", "price": 62, "tax": 20.2},
    "baz": {"name": "Baz", "description": None, "price": 50.2, "tax": 10.5, "tags": []},
}


@app.get("/metis/{item_id}", response_model=Meti, response_model_exclude_unset=True)
# response_model_exclude_unset排除未设置值的属性
async def read_item(item_id: str):
    return metis[item_id]


@app.get("/metis/{item_id}/name", response_model=Meti, response_model_include={"name", "description"},)
# response_model_include只返回指定属性
async def read_item_name(item_id: str):
    return metis[item_id]


@app.get("/metis/{item_id}/public", response_model=Meti, response_model_exclude={"tax"})
# response_model_exclude排除指定属性
async def read_item_public_data(item_id: str):
    return metis[item_id]

# dfdf
