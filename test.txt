# Python 调大模型 · 从零学习指南

> 目标：从「没怎么写过 Python」到「能看懂、能改、能自己写出调用大模型的代码」。
> 原则：**不系统学 Python，只学调用大模型真正用得到的那部分**。
> 配套项目：`D:\pro\langchain`（本目录已有 `.venv`、`.env`、`agent.ipynb` 和 `Agent应用开发_注释版.md`）

---

## 0. 先破除一个误解：调用大模型到底在做什么

很多人以为「用 Python 调大模型」是在本地跑一个 AI，其实不是。

**本质只有三步：**

```
① 组装一个 JSON（问题 + 参数）
② 通过 HTTP 发给云端接口
③ 收到 JSON，把里面的回答取出来
```

一次最原始的调用长这样（先看个大概，不用现在就懂）：

```python
import os
import requests

response = requests.post(
    "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
    headers={"Authorization": f"Bearer {os.environ['DASHSCOPE_API_KEY']}"},
    json={
        "model": "qwen-long",
        "messages": [{"role": "user", "content": "你好"}]
    }
)

print(response.json()["choices"][0]["message"]["content"])
```

就这十几行。**LangChain、Agent、RAG 全都是在这十几行上面加的封装**，帮你少写重复代码而已。

所以你真正要学的 Python 语法，其实只是一张很短的清单：

| 知识点 | 为什么必须学 | 用在哪 |
|---|---|---|
| 变量、字符串、f-string | 拼 URL、拼提示词 | 到处都是 |
| **字典 dict** ★ | 消息格式、请求体、返回结果全是字典 | 最重要的一个 |
| 列表 list | 多条消息、多个工具、多个文档 | 消息列表 `messages` |
| import / 函数调用 | 调 SDK | `model.invoke(...)` |
| for 循环 | 遍历流式输出、遍历消息 | `for token in stream:` |
| 环境变量 os.getenv | 安全地放 API Key | `.env` |
| 异常 try/except | 处理 401、网络错误 | 报错不崩 |
| 类 class | Pydantic 结构化输出 | `class TravelData(BaseModel)` |
| 生成器 / async | 流式输出、异步调用 | `stream` / `ainvoke` |

> ★ 如果只挑一个最重要的：把 **字典 dict** 学透，你就已经能看懂一半 LangChain 代码了。

---

## 1. 学习路线总览

| 阶段 | 学什么 | 目标 | 优先级 |
|---|---|---|---|
| ① Python 最小语法集 | 变量 / 字符串 / 列表 / 字典 / 函数 / import | 能读懂代码 | **必须** |
| ② 工程基础 | venv、pip、`.env`、环境变量 | 不踩环境坑 | **必须** |
| ③ HTTP 与 JSON | 请求 / 响应 / JSON 解析 | 理解底层 | 必须（理解即可） |
| ④ SDK 裸调 | `openai` 库直连百炼兼容接口 | 跑通第一次调用 | **必须** |
| ⑤ LangChain 层 | `init_chat_model` / `invoke` / `stream` | 会写业务代码 | **必须** |
| ⑥ Agent 进阶 | 工具 / 记忆 / 结构化输出 / RAG / MCP | 做完整应用 | 用到再学 |

**建议节奏**：① ② 花一两个小时速览 → 直接做 ④ 跑通第一次调用（正反馈最快）→ 回头补 ③ ⑤ → 再看 ⑥。

---

## 2. 环境准备（你项目里已经做好了，但要理解每一步）

```bash
# 1. 建虚拟环境：把依赖隔离在项目内，不污染系统 Python
python -m venv .venv

# 2. 激活（Windows）——激活后 pip / python 都指向虚拟环境
.venv\Scripts\activate

# 3. 装依赖
pip install langchain langchain-openai python-dotenv openai
```

`.env` 文件（放在项目根目录，和代码同级）：

```ini
DASHSCOPE_API_KEY=你的apikey
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

> ★ 两个真实踩过的坑：
> 1. `load_dotenv()` **默认不覆盖系统里已有的同名环境变量**。如果 Windows 系统环境变量也设了 `DASHSCOPE_API_KEY`，改 `.env` 完全不生效 → 要么删掉系统变量，要么写 `load_dotenv(override=True)`。
> 2. 报 401 `invalid_api_key` 时，先用一个最简单的请求（或 curl）验证 Key 本身是否有效，别一上来怀疑代码。
> 3. `.env` 别提交到 Git。

---

## 3. Python 基础语法（只讲调用大模型用得到的）

### 3.1 变量与基本类型

```python
# Python 不需要声明类型，直接赋值即可
model_name = "qwen-long"        # str   字符串
temperature = 0.7               # float 浮点数
max_tokens = 500                # int   整数
streaming = True                # bool  布尔（注意首字母大写）
result = None                   # NoneType（相当于 JS 的 null）

# 打印
print(model_name)
```

> 对照 JS：`let a = 1` → Python 直接 `a = 1`，没有 `let/const/var`。

### 3.2 字符串与 f-string ★

```python
name = "张三"

# f-string：字符串前加 f，用 {} 嵌变量 —— 拼提示词最常用
prompt = f"请以{name}的口吻回答，温度是{temperature}"
print(prompt)

# 三引号：写多行长文本（系统提示词、长 prompt 都用这个）
system_prompt = """
你是一个专业的旅行规划助手。
请根据用户的偏好推荐旅行方案。
"""
```

> ★ 调模型时：`f"Bearer {api_key}"`、拼用户输入、拼检索到的上下文，全靠 f-string / 三引号。

### 3.3 列表 list

```python
# 列表 = 有序集合，用方括号
messages = [
    {"role": "system", "content": "你是助手"},
    {"role": "user",   "content": "你是谁？"}
]

messages.append({"role": "user", "content": "再问一个"})  # 追加
print(len(messages))        # 长度
print(messages[0])          # 取第一个（下标从 0 开始）
```

> ★ `messages` 永远是列表，这是调用大模型最核心的数据结构。

### 3.4 字典 dict ★★★ 最重要

```python
# 字典 = 键值对，用花括号；相当于 JS 的对象 / JSON
message = {
    "role": "user",
    "content": "你是谁？"
}

print(message["role"])                  # 用 key 取值 → "user"
print(message.get("role"))              # 更安全的写法：key 不存在返回 None，不报错
print(message.get("xxx", "默认值"))      # 还可以给默认值

message["content"] = "换个问题"          # 修改
message["new_key"] = "新值"             # 新增

# 遍历字典
for key, value in message.items():
    print(key, value)
```

> ★ 为什么它最重要：
> - 一条消息 = 一个字典 `{"role": ..., "content": ...}`
> - 请求体 = 一个字典
> - Agent 的返回值 = 一个字典，所以你写 `response["messages"]`、`response["structured_response"]`
> - 多模态图片消息里的每一项也是一个字典
>
> 一句话：**看到 `{}` 就想到「一个东西的若干属性」，看到 `[]` 就想到「一串东西」。**

### 3.5 条件与循环

```python
# 条件：注意冒号 + 缩进（Python 用缩进代替大括号，通常是 4 个空格）
if token.content:               # 空字符串/None 会被当成 False
    print(token.content, end="")
else:
    pass                        # pass = 什么都不做，占位用

# for 循环：遍历列表
for message in response["messages"]:
    message.pretty_print()
```

> ★ 缩进是 Python 最容易报错的地方：**同一个代码块必须对齐**，混用 Tab 和空格会直接 `IndentationError`。

### 3.6 函数

```python
# def 定义函数，参数不用写类型；return 返回结果
def format_docs(docs):
    return "\n\n".join([d.page_content for d in docs])

# 带默认值的参数
def build_message(role="user", content=""):
    return {"role": role, "content": content}

msg = build_message(content="你好")
```

> 上面第一行里的 `[d.page_content for d in docs]` 叫**列表推导式**，等价于循环 append，RAG 代码里很常见，看到别慌。

### 3.7 模块导入 import

```python
import os                                       # 导入整个模块 → os.getenv(...)
from dotenv import load_dotenv                  # 只导入某个函数 → 直接 load_dotenv()
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

# as 起别名（约定俗成）
import pandas as pd
```

> ★ `ModuleNotFoundError: No module named 'xxx'` = 没装依赖 → `pip install xxx`（注意要在激活的虚拟环境里装）。

### 3.8 异常 try / except

```python
try:
    response = model.invoke("你好")
except Exception as e:
    print("调用失败：", e)
```

> 调外部接口一定会遇到 401、超时、限流，包一层 try/except 程序才不会直接崩。

### 3.9 类 class 与对象（结构化输出会用到）

```python
from pydantic import BaseModel, Field

# class 定义一个「数据模板」：继承 BaseModel 后，框架会自动按这个结构解析模型输出
class TravelData(BaseModel):
    city: str = Field(description="目的地")       # 字段名: 类型
    reason: str = Field(description="推荐理由")
    cost: str

# 创建对象
data = TravelData(city="三亚", reason="海滨城市", cost="3000-5000")
print(data.city)            # 用点号取属性
print(data.model_dump())    # 转回字典，方便给前端
```

> ★ 对比「字典取值用 `["key"]`」，**对象取属性用 `.key`**。LangChain 里两种都会碰到：
> `response["messages"]`（字典） vs `response.content`（对象）。

### 3.10 生成器与流式输出

```python
# stream() 返回的不是一次性结果，而是「边生成边给」的迭代器
for token, metadata in agent.stream({"messages": [...]}, stream_mode="messages"):
    if token.content:
        print(token.content, end="")    # end="" 不换行，拼成连续文字
```

> ★ 这里每次循环拿到的是**两个值组成的元组**，所以写 `for a, b in ...`（叫「解包」）。
> 与普通 `model.stream()` 只给一个 message 不同，`stream_mode="messages"` 会额外给元数据。

### 3.11 异步 async / await（进阶，用到再学）

```python
# 函数前加 async，调用前加 await；用于 IO 密集场景（MCP、并发请求）
tools = await client.get_tools()
response = await agent.ainvoke({"messages": [...]})
```

> 记住一条：**看到 `await` 就说明这行代码必须在异步环境里跑**。Jupyter notebook 里可以直接 `await`；普通 `.py` 脚本要用 `asyncio.run(main())` 包起来。

### 3.12 文件与 JSON

```python
import json

# 读文件：中文必须显式写 encoding="utf-8"，否则可能乱码
with open("knowledge.md", "r", encoding="utf-8") as f:
    text = f.read()

# JSON 与 Python 互转
data = json.loads('{"role": "user"}')     # JSON 字符串 → 字典
text = json.dumps(data, ensure_ascii=False)  # 字典 → JSON 字符串
```

---

## 4. 逐行拆解：把上面的语法串成真实代码

下面这段就是你 `agent.ipynb` 里的代码，我在右边标出每行用到的语法点：

```python
from dotenv import load_dotenv                    # 3.7 import
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
import os

load_dotenv()                                     # 3.7 函数调用：读 .env

model = init_chat_model(                          # 3.6 函数调用 + 关键字参数
    model="qwen-long",                           # 3.1 变量值（字符串）
    model_provider="openai",
    api_key=os.getenv("DASHSCOPE_API_KEY"),      # 环境变量读取
    base_url=os.getenv("DASHSCOPE_BASE_URL")
)

agent = create_agent(model)                       # 返回值赋给变量

from langchain_core.messages import HumanMessage

# 3.4 列表里套字典 —— 多模态消息
message = HumanMessage([
    {"type": "text",  "text": "描述一下这张图片中的内容"},
    {"type": "image", "url": "https://..."}
])

stream = agent.stream(                            # 3.10 生成器
    {"messages": [message]},                      # 3.4 字典 + 3.3 列表
    stream_mode="messages",
)

for token, metadata in stream:                    # 3.5 for + 元组解包
    if token.content:                             # 3.5 if + 3.9 对象属性
        print(token.content, end="")              # 3.2 print 的 end 参数
```

**看明白了吗**：整段代码里真正用到的 Python 语法，就是「变量 + 字符串 + 列表 + 字典 + 函数 + import + for + if」。剩下的都是别人写好的库。

---

## 5. 从零跑通第一次调用（照着做）

### Step 1：确认环境

```bash
.venv\Scripts\activate
python --version
pip list | findstr langchain
```

### Step 2：放好 `.env`

按第 2 节写好 Key 和 Base URL，然后**验证它真的被读到了**：

```python
import os
from dotenv import load_dotenv

load_dotenv(override=True)                       # ★ 强制覆盖系统环境变量，避免踩坑
key = os.getenv("DASHSCOPE_API_KEY")
print("Key 前缀:", key[:12] if key else "没读到！")
```

### Step 3：先用 `openai` 库裸调（最贴近本质）

```python
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
)

resp = client.chat.completions.create(
    model="qwen-long",
    messages=[{"role": "user", "content": "用一句话介绍你自己"}],
)

print(resp.choices[0].message.content)
```

> 这一步跑通了，说明 **Key、网络、base_url 全都没问题**。以后再报错就好定位了。

### Step 4：换成 LangChain（少写样板代码）

```python
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
import os

load_dotenv(override=True)

model = init_chat_model(
    model="qwen-long",
    model_provider="openai",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
)

print(model.invoke("用一句话介绍你自己").content)
```

### Step 5：换成流式输出

```python
for chunk in model.stream("讲个冷笑话"):
    print(chunk.content, end="")
```

### Step 6：升级成 Agent

```python
from langchain.agents import create_agent

agent = create_agent(model, system_prompt="请以周星驰的口吻回答问题")

for token, meta in agent.stream(
    {"messages": [{"role": "user", "content": "你是谁？"}]},
    stream_mode="messages",
):
    if token.content:
        print(token.content, end="")
```

---

## 6. 常见报错速查

| 报错 | 含义 | 怎么修 |
|---|---|---|
| `IndentationError` | 缩进不对 | 统一用 4 个空格，别混 Tab |
| `ModuleNotFoundError: No module named 'xxx'` | 没装依赖 | `pip install xxx`，确认虚拟环境已激活 |
| `KeyError: 'messages'` | 字典里没这个 key | 先 `print(response)` 看结构，或改用 `.get()` |
| `TypeError: ... is not subscriptable` | 把对象当字典用了 | 对象用 `.属性`，字典用 `["key"]` |
| `'NoneType' object has no attribute ...` | 变量是 None | 多半是环境变量没读到，打印出来看 |
| `401 invalid_api_key` | Key 无效 / 不匹配业务空间 | 用 Step 3 的最小请求验证；检查 base_url 与 Key 是否同一业务空间 |
| 中文乱码 | 文件编码 | 读文件加 `encoding="utf-8"` |
| 改了 `.env` 不生效 | 系统环境变量优先 | `load_dotenv(override=True)` 或删系统变量 |

---

## 7. 练习清单（按顺序做）

1. 打印一个 f-string，把自己的名字和模型名拼进去
2. 手工构造一个 `messages` 列表（含 system + user 两条消息）并打印
3. 用 `.get()` 安全地从字典里取一个不存在的 key
4. 跑通本文 Step 3（裸调），把回答打印出来
5. 跑通 Step 4，对比两种写法的差异
6. 改成 Step 5 流式输出，观察打字机效果
7. 用 `try/except` 包住调用，故意把 Key 改错，看程序是否不崩
8. 写一个 `build_message(role, content)` 函数，用它生成消息列表
9. 定义一个 `class Answer(BaseModel)`，配 `response_format` 拿结构化输出
10. 阅读本目录 `Agent应用开发_注释版.md`，逐节对照注释，看不懂的语法回来查本文第 3 节

---

## 8. 学完基础之后往哪走

按你现有教程的顺序推进即可，全部都建立在本文的 8 个语法点上：

```
消息与角色 → 系统提示词 → 结构化输出 → 工具调用(Function Calling)
→ 记忆(checkpointer + thread_id) → RAG → Context / State → 中间件 → MCP
```

对应的 Python 进阶点（用到再学，不用提前啃）：
- **装饰器 `@tool`**：理解成「给函数加个标记」，把普通函数变成工具
- **类型注解 `str` / `list[Reference]`**：Pydantic 靠它生成输出结构
- **继承 `class Xxx(BaseModel)`**：结构化输出、自定义 State 都靠它
- **异步 `async / await`**：MCP、批量并发
- **生成器**：流式输出的底层

---

## 附录：如果你熟悉 JS，这样对照最快

| JavaScript | Python | 备注 |
|---|---|---|
| `const a = 1` | `a = 1` | 不用声明关键字 |
| `` `hi ${name}` `` | `f"hi {name}"` | f-string |
| `{ a: 1 }` | `{"a": 1}` | Python 的 key 要加引号 |
| `[1, 2, 3]` | `[1, 2, 3]` | 一样（叫 list 不叫 array） |
| `obj.a` | `d["a"]` | 字典用方括号 |
| `arr.push(x)` | `arr.append(x)` | |
| `arr.length` | `len(arr)` | |
| `for (const x of arr)` | `for x in arr:` | 冒号 + 缩进 |
| `function f(a) {}` | `def f(a):` | 冒号 + 缩进 |
| `try { } catch(e) { }` | `try: ... except Exception as e:` | |
| `import x from 'y'` | `from y import x` | |
| `null` | `None` | |
| `true / false` | `True / False` | **首字母大写** |
| `console.log()` | `print()` | |
| `JSON.parse()` | `json.loads()` | 需 `import json` |

> 最大的思维切换只有两个：**① 用缩进代替 `{}`；② 字典取值用 `["key"]` 而不是 `.key`**（`.key` 是对象属性）。
