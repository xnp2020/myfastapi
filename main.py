
from fastapi import FastAPI, Path, Query
from fastapi import FastAPI, Path
from enum import Enum

from fastapi import FastAPI, Query, Path
from pydantic import BaseModel

app = FastAPI()

# path 数据类型检测


@app.get("/items/{item_id}")
async def root(item_id: int):
    return {"item_id": item_id}

# path 变量枚举


class ModelName(str, Enum):
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
# 可选查询参数，设置可以为None
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

# 构建post请求体模型


class Item(BaseModel):
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
