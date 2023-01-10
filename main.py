from fastapi import Depends, FastAPI, Header, HTTPException
from datetime import datetime
from enum import Enum
from typing import Union

from fastapi import (Body, Cookie, Depends, FastAPI, File, Form, Header,
                     HTTPException, Path, Query, UploadFile, status)
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr, Field, HttpUrl

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
    include_in_schema=True)
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


@app.post("/res/", response_model=Res, summary="aaabbb", description="Create an item with all the information, name, description, price, tax and a set of unique tags", response_description="The created item",)
# response_model定义响应模型，summary、description、response_description定义docs中接口的信息
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


class UserBase(BaseModel):
    # 抽象共同的属性
    username: str
    email: EmailStr
    full_name: str | None = None


class UserIncome(UserBase):
    # 模型继承
    password: str


class UserOutcome(UserBase):
    pass


class UserInDB(UserBase):
    hashed_password: str


def fake_password_hasher(raw_password: str):
    return "supersecret" + raw_password


def fake_save_user(user_income: UserIncome):
    hashed_password = fake_password_hasher(user_income.password)
    # Pydantic models .dict()方法将模型转换成python字典
    user_in_db = UserInDB(**user_income.dict(),
                          hashed_password=hashed_password)
    print("User saved! ..not really")
    return user_in_db


@app.post("/userincome/", response_model=UserOutcome)
async def create_user(user_income: UserIncome):
    user_saved = fake_save_user(user_income)
    return user_saved


class BaseItem(BaseModel):
    description: str
    type: str


class CarItem(BaseItem):
    type = "car"


class PlaneItem(BaseItem):
    type = "plane"
    size: int


items = {
    "item1": {"description": "All my friends drive a low rider", "type": "car"},
    "item2": {
        "description": "Music is my aeroplane, it's my aeroplane",
        "type": "plane",
        "size": 5,
    },
}


@app.get("/carplas/{item_id}", response_model=Union[PlaneItem, CarItem])
# Union：多个模型的集合
async def read_item(item_id: str):
    return items[item_id]


class Listmodel(BaseModel):
    name: str
    description: str


listModels = [
    {"name": "Foo", "description": "There comes my hero"},
    {"name": "Red", "description": "It's my aeroplane"},
]


@app.get("/listmodels/", response_model=list[Listmodel], status_code=status.HTTP_201_CREATED)
# 返回list
# status
async def read_items():
    return listModels


@app.get("/keyword-weights/", response_model=dict[str, float], status_code=201)
# 返回任意字典，但是key和value类型确定
# status_code指定返回码
async def read_keyword_weights():
    return {"foo": 2.3, "bar": 3.4}


class Tags(Enum):
    root = "root"
    login = "login"


@app.post("/login/", tags=[Tags.login])
async def login(username: str = Form(), password: str = Form()):
    # http Form
    return {"username": username}


@app.post("/files/", tags=["files"])
async def create_file(file: bytes = File()):
    # File将所有的文件内容存储在内存中，适合小文件
    return {"file_size": len(file)}


@app.post("/uploadfile/", tags=["files"])
async def create_upload_file(file: UploadFile):
    # UploadFile对比File有如下优势：
    # 1.如果文件超过指定大小，则存储在磁盘上，适合大文件
    # 2.可以从上传文件获取元数据（filename，content_type，file）
    # 3.有一个file-like async接口（write(data)，read(size)，seek(offset)，close()）
    return {"filename": file.filename}


@app.post("/files2/", tags=["files"])
async def create_file(file: bytes | None = File(default=None, description="A file read as bytes")):
    # default=None表示可选
    if not file:
        return {"message": "No file sent"}
    else:
        return {"file_size": len(file)}


@app.post("/uploadfile2/", tags=["files"])
async def create_upload_file(file: UploadFile | None = File(description="A file read as UploadFile")):
    if not file:
        return {"message": "No upload file sent"}
    else:
        return {"filename": file.filename}


@app.post("/files3/", tags=["files"])
# 上传多文件
async def create_files(files: list[bytes] = File(description="Multiple files as bytes")):
    return {"file_sizes": [len(file) for file in files]}


@app.post("/uploadfiles3/", tags=["files"])
# 上传多文件
async def create_upload_files(files: list[UploadFile] = File(description="Multiple files as UploadFile"),):
    return {"filenames": [file.filename for file in files]}


@app.get("/", tags=[Tags.root])
async def main():
    content = """
<body>
<form action="/files3/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
<form action="/uploadfiles3/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)


@app.post("/files4/", tags=["files"])
# File和Form同时声明
# docstring会出现在docs中的description
async def create_file(
    file: bytes = File(), fileb: UploadFile = File(), token: str = Form()
):
    """
    Create an item with all the information:

    - **name**: each item must have a name
    - **description**: a long description
    - **price**: required
    - **tax**: if the item doesn't have tax, you can omit this
    - **tags**: a set of unique tag strings for this item
    """
    return {
        "file_size": len(file),
        "token": token,
        "fileb_content_type": fileb.content_type,
    }


projects = {"foo": "The Foo Wrestlers"}


@app.get("/projs/{item_id}", deprecated=True)
async def read_item(item_id: str):
    if item_id not in projects:
        # HTTPException抛异常，detail接受str、dict、list等，并转成json，headers添加响应头
        raise HTTPException(status_code=404, detail="Item not found", headers={
                            "X-Error": "There goes my error"},)
    return {"item": projects[item_id]}


fake_db = {}


class Ab(BaseModel):
    title: str
    timestamp: datetime
    description: str | None = None


@app.put("/abs/{id}")
# jsonable_encoder转换Pydantic model为json
def update_item(id: str, ab: Ab):
    json_compatible_item_data = jsonable_encoder(ab)
    fake_db[id] = json_compatible_item_data


# 依赖注入
async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}


@app.get("/coms/", tags=["Depends"])
async def read_items(commons: dict = Depends(common_parameters)):
    return commons


@app.get("/users/", tags=["Depends"])
async def read_users(commons: dict = Depends(common_parameters)):
    return commons


fake_items_db2 = [{"item_name": "Foo"}, {
    "item_name": "Bar"}, {"item_name": "Baz"}]


class CommonQueryParams:
    def __init__(self, q: str | None = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit


@app.get("/fines/", tags=["Depends"])
# Depends依赖注入只需要参数为一个callable，而class也是callable，故可以直接注入class，Depends没有参数则默认采用声明的class，即Depends()=Depends(CommonQueryParams)
async def read_items(commons: CommonQueryParams = Depends()):
    response = {}
    if commons.q:
        response.update({"q": commons.q})
    items = fake_items_db2[commons.skip: commons.skip + commons.limit]
    response.update({"items": items})
    return response


def query_extractor(q: str | None = None):
    return q


# 依赖嵌套
def query_or_cookie_extractor(
    q: str = Depends(query_extractor), last_query: str | None = Cookie(default=None)
):
    if not q:
        return last_query
    return q


@app.get("/read_query/", tags=["Depends"])
async def read_query(query_or_default: str = Depends(query_or_cookie_extractor)):
    return {"q_or_cookie": query_or_default}


async def verify_token(x_token: str = Header()):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


async def verify_key(x_key: str = Header()):
    if x_key != "fake-super-secret-key":
        raise HTTPException(status_code=400, detail="X-Key header invalid")
    return x_key


@app.get("/deps/", dependencies=[Depends(verify_token), Depends(verify_key)], tags=["Depends"])
# 依赖需要执行，但不需要依赖返回值
async def deps():
    return [{"item": "Foo"}, {"item": "Bar"}]

# 整个app都注入依赖
# app = FastAPI(dependencies=[Depends(verify_token), Depends(verify_key)])
