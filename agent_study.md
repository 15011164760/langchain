# Agent 应用开发（初学者带注释版）

> 说明：本文在原笔记基础上，给**每一行代码**都加了中文注释，帮助初学者理解每个语句在做什么。代码逻辑保持原样，仅补充注释。

Agent 应用开发 = 前端 + 后端 + Agent

- 后端用 Java
- Agent 用 Python

---

## LangChain

**环境要求**

- Python 3.14+
- PyCharm 2025+

---

## 快速上手

### 1、新建项目，配置虚拟环境

```bash
mkdir langchain
```

> `mkdir langchain`：在当前目录创建一个名为 `langchain` 的文件夹（项目目录）。

### 2、创建虚拟环境

```bash
python -m venv .venv
```

> `python -m venv .venv`：用 Python 自带的 `venv` 模块，在 `.venv` 目录下创建一个独立的虚拟环境（隔离项目依赖，避免污染全局 Python）。

### 3、激活虚拟环境

```bash
.venv\Scripts\activate
```

> `.venv\Scripts\activate`：Windows 下激活虚拟环境。激活后命令行前面会出现 `(.venv)`，表示当前用的就是虚拟环境的 Python。
> （macOS/Linux 用 `source .venv/bin/activate`）

### 4、安装依赖

```bash
pip install langchain
pip install langchain-openai
pip install python-dotenv
```

> - `pip install langchain`：安装 LangChain 核心库（Agent、链、消息等）。
> - `pip install langchain-openai`：安装 OpenAI 兼容接口的适配器（阿里通义千问也走 OpenAI 兼容协议，所以用它）。
> - `pip install python-dotenv`：安装读取 `.env` 配置文件的库（用来安全存放 API Key）。

### 5、创建配置文件，存放 API-KEY 和 URL

```bash
DASHSCOPE_API_KEY=你的apikey
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

> 这两行写在项目根目录的 `.env` 文件里：
>
> - `DASHSCOPE_API_KEY`：阿里云百炼（通义千问）的 API 密钥。
> - `DASHSCOPE_BASE_URL`：通义千问的 OpenAI 兼容接口地址。

### 6、写代码连接大模型

```python
# 导入依赖
from dotenv import load_dotenv                       # 从 dotenv 库导入 load_dotenv，用于读取 .env 文件
from langchain.chat_models import init_chat_model    # 导入 init_chat_model，用于初始化聊天模型
import os                                            # 导入 os，用于读取环境变量

load_dotenv()                                        # 加载 .env 文件，把里面的键值对读进环境变量

# 创建 model
model = init_chat_model(                             # 初始化一个聊天模型对象
    model="qwen-long",                               # 指定使用的模型名称：qwen-long
    model_provider="openai",                         # 指定模型提供方为 openai（走 OpenAI 兼容协议）
    api_key=os.getenv("DASHSCOPE_API_KEY"),          # 从环境变量读取 API Key
    base_url=os.getenv("DASHSCOPE_BASE_URL")         # 从环境变量读取接口地址
)

response = model.invoke("你是谁？")                   # invoke 表示"同步调用一次"，传入字符串问题，返回模型回复对象
print(response.content)                              # 打印回复对象里的 content（文本内容）
```

### 7、设置角色（system / user 消息）

```python
response = model.invoke([                            # invoke 也可以传入"消息列表"
    {"role": "system", "content": "请你以周杰伦的口吻来回答问题"},  # system：设定模型的身份/语气
    {"role": "user",   "content": "你是谁？"}         # user：用户真正的提问
])
print(response.content)                              # 打印回答文本
```

### 8、流式输出（一个字一个字往外蹦）

```python
response = model.stream([                            # stream 表示"流式调用"，逐块返回结果
    {"role": "system", "content": "请你以周杰伦的口吻来回答问题"},  # 系统角色设定
    {"role": "user",   "content": "你是谁？"}         # 用户提问
])

for message in response:                             # 遍历流式返回的每一个消息块
    print(message.content, end="")                   # 打印当前块的内容，end="" 表示不换行（像打字机效果）
```

---

## 智能体中调用

```python
from dotenv import load_dotenv                       # 导入 load_dotenv 读取 .env
from langchain.chat_models import init_chat_model    # 导入模型初始化函数
from langchain.agents import create_agent            # 导入 create_agent，用于创建智能体
import os                                            # 导入 os 读取环境变量

load_dotenv()                                        # 加载 .env 配置

model = init_chat_model(                             # 初始化聊天模型
    model="qwen-long",                               # 模型名称
    model_provider="openai",                         # 走 OpenAI 兼容协议
    api_key=os.getenv("DASHSCOPE_API_KEY"),          # API Key
    base_url=os.getenv("DASHSCOPE_BASE_URL")         # 接口地址
)

agent = create_agent(model)                          # 创建一个智能体，只传模型（此时还没有工具）

response = agent.invoke({                            # 调用智能体，传入一个字典
    "messages": [                                    # messages 键存放消息列表
        {"role": "system", "content": "请你以周杰伦的口吻来回答问题"},  # 系统角色
        {"role": "user",   "content": "你是谁？"}     # 用户问题
    ]
})

print(response)                                      # 打印智能体返回的完整结果（包含所有消息）
```

**流式输出**

```python
response = agent.stream(                             # 流式调用智能体
    {
        "messages": [                                # 消息列表
            {"role": "system", "content": "请你以周星驰的口吻来回答问题"},  # 系统角色设定
            {"role": "user",   "content": "你是谁？"} # 用户问题
        ]
    },
    stream_mode="messages"                           # 流式模式设为 "messages"，即按消息块输出
)

for token, metadata in response:                     # 每次迭代得到 (消息块 token, 元数据 metadata)
    if token.content:                                # 如果该消息块有文本内容
        print(token.content, end="")                 # 打印出来，不换行
```

---

## 多模态消息

**三种消息类型说明：**

- `SystemMessage`：系统角色消息（设定 AI 身份）
- `HumanMessage`：用户提问消息
- `AIMessage`：大模型的回答消息

```python
from dotenv import load_dotenv                       # 读取 .env
from langchain.chat_models import init_chat_model    # 初始化模型
from langchain.agents import create_agent            # 创建智能体
import os                                            # 读环境变量

load_dotenv()                                        # 加载配置

model = init_chat_model(                             # 初始化模型
    model="qwen3.5-plus",                            # 这里换成多模态模型 qwen3.5-plus
    model_provider="openai",                         # OpenAI 兼容协议
    api_key=os.getenv("DASHSCOPE_API_KEY"),          # API Key
    base_url=os.getenv("DASHSCOPE_BASE_URL")         # 接口地址
)

agent = create_agent(model)                          # 创建智能体

from langchain_core.messages import HumanMessage     # 导入 HumanMessage（用户消息类）

message = HumanMessage([                             # 构造一条用户消息，内容是"列表"形式（多模态）
    {"type": "text",  "text": "描述一下这张图片中的内容"},  # 文本部分
    {"type": "image", "url": "https://inews.gtimg.com/news_bt/Ogw_-rddzOwDnZQN8q5jjefTEK7ZlIEPGAKVCFdISRossAA/641"}  # 图片部分（URL 形式）
])

stream = agent.stream(                               # 流式调用智能体
    {"messages": [message]},                         # 把上面那条多模态消息放进 messages
    stream_mode="messages",                          # 按消息块流式输出
)

for token, metadata in stream:                       # 遍历每个流式块
    if token.content:                                # 若有文本内容
        print(token.content, end="")                 # 打印，不换行
```

**设置角色（SystemMessage + HumanMessage 多模态）**

```python
from dotenv import load_dotenv                       # 读取 .env
from langchain.chat_models import init_chat_model    # 初始化模型
from langchain.agents import create_agent            # 创建智能体
import os                                            # 读环境变量

load_dotenv()                                        # 加载配置

model = init_chat_model(                             # 初始化多模态模型
    model="qwen3.5-plus",                            # 模型名称
    model_provider="openai",                         # OpenAI 兼容协议
    api_key=os.getenv("DASHSCOPE_API_KEY"),          # API Key
    base_url=os.getenv("DASHSCOPE_BASE_URL")         # 接口地址
)

agent = create_agent(model)                          # 创建智能体

from langchain_core.messages import HumanMessage, SystemMessage  # 导入用户消息、系统消息两个类

human_message = HumanMessage([                       # 构造用户多模态消息
    {"type": "text",  "text": "描述一下这张图片中的内容"},  # 文本部分
    {"type": "image", "url": "https://inews.gtimg.com/news_bt/Ogw_-rddzOwDnZQN8q5jjefTEK7ZlIEPGAKVCFdISRossAA/641"}  # 图片 URL
])

system_message = SystemMessage("请以周星驰的口吻来回答问题")  # 构造系统消息，设定角色语气

stream = agent.stream(                               # 流式调用智能体
    {"messages": [human_message, system_message]},   # 消息列表里放用户消息 + 系统消息
    stream_mode="messages",                          # 流式输出模式
)

for token, metadata in stream:                       # 遍历流式块
    if token.content:                                # 有文本才打印
        print(token.content, end="")                 # 逐字打印
```

---

## 系统提示词

> 用 `create_agent` 的 `system_prompt` 参数直接设定系统提示词，比在 messages 里塞 system 消息更简洁。

```python
from dotenv import load_dotenv                       # 读取 .env
from langchain.chat_models import init_chat_model    # 初始化模型
from langchain.agents import create_agent            # 创建智能体
from langchain_core.messages import HumanMessage     # 用户消息类
import os                                            # 读环境变量

load_dotenv()                                        # 加载配置

model = init_chat_model(                             # 初始化模型
    model="qwen-long",                               # 模型名称
    model_provider="openai",                         # OpenAI 兼容协议
    api_key=os.getenv("DASHSCOPE_API_KEY"),          # API Key
    base_url=os.getenv("DASHSCOPE_BASE_URL")         # 接口地址
)

agent = create_agent(
    model,                                           # 传入模型
    system_prompt="请以周星驰的口吻来回答问题"         # 直接传系统提示词，设定角色
)

response = agent.stream(                             # 流式调用智能体
    {
        "messages": [HumanMessage("你是谁？")]         # 只传一条用户消息即可
    },
    stream_mode="messages"                           # 流式输出
)

for token, metadata in response:                     # 遍历流式块
    if token.content:                                # 有文本
        print(token.content, end="")                 # 逐字打印
```

**更详细的系统提示词**

```python
from dotenv import load_dotenv                       # 读取 .env
from langchain.chat_models import init_chat_model    # 初始化模型
from langchain.agents import create_agent            # 创建智能体
from langchain_core.messages import HumanMessage     # 用户消息类
import os                                            # 读环境变量

load_dotenv()                                        # 加载配置

model = init_chat_model(                             # 初始化模型
    model="qwen-long",                               # 模型名称
    model_provider="openai",                         # OpenAI 兼容协议
    api_key=os.getenv("DASHSCOPE_API_KEY"),          # API Key
    base_url=os.getenv("DASHSCOPE_BASE_URL")         # 接口地址
)

system_prompt = """
你是一个专业的旅行规划助手。你的任务是根据用户提供的旅行偏好，为其推荐最合适的旅行方案。
"""                                                  # 用三引号写多行系统提示词，交代角色和任务

agent = create_agent(
    model,                                           # 传入模型
    system_prompt=system_prompt                      # 传入上面定义的系统提示词
)

content = """
我想规划一次旅行，我从深圳出发，我喜欢的目的地类型是海滨城市
"""                                                  # 用户的提问内容

response = agent.stream(                             # 流式调用智能体
    {
        "messages": [HumanMessage(content)]          # 把用户内容包装成 HumanMessage
    },
    stream_mode="messages"                           # 流式输出
)

for token, metadata in response:                     # 遍历流式块
    if token.content:                                # 有文本
        print(token.content, end="")                 # 逐字打印
```

---

## 结构化输出

> 让模型按我们定义的"数据结构"（Pydantic 模型）返回结果，方便程序后续处理。

```python
from dotenv import load_dotenv                       # 读取 .env
from langchain.chat_models import init_chat_model    # 初始化模型
from langchain.agents import create_agent            # 创建智能体
from langchain_core.messages import HumanMessage     # 用户消息类
from pydantic import BaseModel                       # 导入 BaseModel，用于定义数据结构
import os                                            # 读环境变量

load_dotenv()                                        # 加载配置

model = init_chat_model(                             # 初始化模型
    model="qwen-long",                               # 模型名称
    model_provider="openai",                         # OpenAI 兼容协议
    api_key=os.getenv("DASHSCOPE_API_KEY"),          # API Key
    base_url=os.getenv("DASHSCOPE_BASE_URL")         # 接口地址
)

system_prompt = """
你是一个专业的旅行规划助手。你的任务是根据用户提供的旅行偏好，为其推荐最合适的旅行方案。
"""                                                  # 系统提示词

class TravelData(BaseModel):                         # 定义一个数据结构类，继承 BaseModel
    city: str                                        # 目的地（字符串）
    reason: str                                      # 推荐理由
    cost: str                                        # 费用区间
    hotel: str                                       # 住宿
    transport: str                                   # 交通
    tips: str                                        # 特别提示
    season: str                                      # 最佳旅行季节

agent = create_agent(
    model,                                           # 传入模型
    system_prompt=system_prompt,                     # 系统提示词
    response_format=TravelData                       # 指定结构化输出格式为 TravelData
)

content = """
我想规划一次旅行，我从深圳出发，我喜欢的目的地类型是海滨城市
"""                                                  # 用户提问

response = agent.invoke(                             # 同步调用一次智能体
    {
        "messages": [HumanMessage(content)]          # 用户消息
    }
)

city = response['structured_response']               # 从返回结果里取出结构化数据
print(city)                                          # 打印结构化对象（字段符合 TravelData）
```

---

## Function Calling（工具调用）

1. 注册 Tavily，获取 API_KEY
2. 安装 Tavily 依赖

```bash
pip install langchain-tavily
```

> 安装 Tavily 搜索工具库（让 Agent 能联网搜索）。

3. 通过 Tavily 查询网页信息，提供给 Agent，再由 Agent 给出答案

```python
from dotenv import load_dotenv                       # 读取 .env
from langchain_core.messages import HumanMessage     # 用户消息类
from langchain_tavily import TavilySearch            # 导入 Tavily 搜索工具
from langchain.agents import create_agent            # 创建智能体
from langchain.chat_models import init_chat_model    # 初始化模型
import os                                            # 读环境变量

load_dotenv()                                        # 加载配置

search_tool = TavilySearch()                         # 创建 Tavily 搜索工具实例（会自动读 TAVILY_API_KEY）

model = init_chat_model(                             # 初始化模型
    model="qwen3.5-plus",                            # 模型名称
    model_provider="openai",                         # OpenAI 兼容协议
    api_key=os.getenv("DASHSCOPE_API_KEY"),          # API Key
    base_url=os.getenv("DASHSCOPE_BASE_URL")         # 接口地址
)

agent = create_agent(
    model,                                           # 传入模型
    tools=[search_tool],                             # 传入工具列表（这里只有搜索工具）
    system_prompt="你是一个智能助手，使用工具来回答用户问题"  # 系统提示词
)

response = agent.invoke(                             # 同步调用智能体
    {"messages": [HumanMessage("今天深圳天气怎么样？")]}  # 用户问题（会触发搜索工具）
)

for message in response["messages"]:                 # 遍历返回的所有消息（含 AI 调用工具的过程）
    message.pretty_print()                           # 美化打印每条消息
```

**结构化输出（工具 + 结构化答案）**

```python
from pydantic import BaseModel, Field                # 导入 BaseModel 和 Field（Field 可加描述）

class Reference(BaseModel):                          # 定义"引用网页"数据结构
    title: str = Field(description="网页标题")        # 网页标题
    url: str   = Field(description="网页网址")        # 网页网址

class AnswerInfo(BaseModel):                         # 定义"最终答案"数据结构
    answer: str = Field(description="最终的答案")      # 答案文本
    reference: list[Reference] = Field(description="回答问题的网页信息")  # 引用的网页列表

agent = create_agent(
    model,                                           # 模型
    tools=[search_tool],                             # 工具
    system_prompt="你是一个智能助手，使用工具来回答用户问题",  # 系统提示词
    response_format=AnswerInfo                       # 指定结构化输出格式
)

response = agent.invoke(                             # 同步调用
    {"messages": [HumanMessage("梅西是谁？")]}          # 用户问题
)

print(response["structured_response"])               # 打印结构化答案（answer + reference 列表）
```

---

## 记忆系统

> 让 Agent 拥有记忆功能，能够记住历史对话。用 `checkpointer`（检查点）+ `thread_id`（会话线程 ID）实现。

```python
from dotenv import load_dotenv                       # 读取 .env
from langchain_core.messages import HumanMessage     # 用户消息类
from langchain.agents import create_agent            # 创建智能体
from langchain.chat_models import init_chat_model    # 初始化模型
from langgraph.checkpoint.memory import InMemorySaver # 内存保存器（把对话状态存在内存里）
import os                                            # 读环境变量

load_dotenv()                                        # 加载配置

model = init_chat_model(                             # 初始化模型
    model="qwen-long",                               # 模型名称
    model_provider="openai",                         # OpenAI 兼容协议
    api_key=os.getenv("DASHSCOPE_API_KEY"),          # API Key
    base_url=os.getenv("DASHSCOPE_BASE_URL")         # 接口地址
)

agent = create_agent(
    model,                                           # 模型
    checkpointer=InMemorySaver()                     # 传入内存保存器，使智能体有记忆
)

config = {
    "configurable": {"thread_id": "thread_1"}        # 指定会话 ID；同一 ID 共享历史记忆
}

response = agent.invoke(                             # 第一次调用
    {
        "messages": [HumanMessage("你好，我叫张三，我喜欢打游戏")]  # 告诉智能体信息
    },
    config                                           # 传入会话配置
)

print(response)                                      # 打印第一次结果（会记住"张三""打游戏"）
```

```python
response = agent.invoke(                             # 第二次调用（同一个 thread_id，能回忆上文）
    {
        "messages": [HumanMessage("我叫什么？我喜欢干什么？")]  # 询问之前说过的信息
    },
    config                                           # 同一会话配置
)

print(response)                                      # 智能体能答出"张三""打游戏"
```

---

## RAG（检索增强生成）

**向量检索原理**

1. 把文本转换为向量数据（embedding）
2. 通过计算向量相似度，找到匹配的文档片段

**代码实现**

1、安装依赖

```bash
pip install langchain langchain-community langchain-text-splitters faiss-cpu dashscope python-dotenv
```

> - `langchain` / `langchain-community`：LangChain 核心与社区扩展
> - `langchain-text-splitters`：文本切分工具
> - `faiss-cpu`：Facebook 的向量检索库（CPU 版）
> - `dashscope`：阿里云百炼 SDK（用于 Embedding）
> - `python-dotenv`：读取 `.env`

2、创建知识库文件 `knowledge.md`

```markdown
2015年欧冠半决赛，梅西在**博阿滕**面前那个著名的"静止变向"，整个过程中足球只触地**三次**。没有踩单车，没有钟摆过人，只有一个**2米**的横向移动和**0.3秒**的爆发加速。这个看似简单的动作，背后是**对重心控制的极致理解**——而这正是梅西足球哲学的终极体现。
```

> 这就是我们要让模型"查资料"的知识库文件。

3、代码实现

```python
import os                                            # 操作系统接口
from dotenv import load_dotenv                       # 读取 .env
from langchain_community.document_loaders import TextLoader   # 文本加载器（读 md 文件）
from langchain_text_splitters import RecursiveCharacterTextSplitter  # 递归字符文本切分器
from langchain_community.chat_models.tongyi import ChatTongyi        # 通义千问聊天模型（社区版）
from langchain_community.embeddings import DashScopeEmbeddings       # DashScope 向量化模型
from langchain_community.vectorstores import FAISS                   # FAISS 向量数据库
from langchain_core.prompts import ChatPromptTemplate                # 聊天提示词模板
from langchain_core.runnables import RunnablePassthrough             # 透传组件（原样传递输入）
from langchain_core.output_parsers import StrOutputParser            # 把模型输出解析成字符串

load_dotenv()                                        # 加载配置

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")   # 读取 API Key 到变量

loader = TextLoader("./knowledge.md", encoding="utf-8")  # 创建文本加载器，指定 utf-8 编码
docs = loader.load()                                 # 加载文档，返回 Document 对象列表

print(docs)                                          # 打印加载的文档

text_splitter = RecursiveCharacterTextSplitter(      # 创建文本切分器
    chunk_size=800,                                  # 每个文本块最多 800 字符
    chunk_overlap=100                                # 相邻块重叠 100 字符（避免切断语义）
)

splits = text_splitter.split_documents(docs)         # 把文档切分成多个小块

print(splits)                                        # 打印切分后的块

embeddings = DashScopeEmbeddings(                    # 创建 Embedding 模型
    model="text-embedding-v4",                       # 向量模型名
    dashscope_api_key=DASHSCOPE_API_KEY              # API Key
)

vectorstore = FAISS.from_documents(splits, embeddings)  # 把切分块向量化后存入 FAISS 向量库
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})  # 创建检索器，每次返回最相似的 3 个块

rag_prompt = ChatPromptTemplate.from_template(       # 定义 RAG 提示词模板
    """
    你是知识库问答助手，**仅能使用下面检索到的上下文回答问题**。

    上下文： {context}
    用户问题：{question}
    """
)

def format_docs(docs):                               # 定义函数：把检索到的多个文档块拼成一个字符串
    return "\n\n".join([d.page_content for d in docs])  # 取出每块的 page_content，用两个换行连接

model = ChatTongyi(                                  # 初始化通义千问聊天模型
    model="qwen-long",                               # 模型名称
    temperature=0,                                   # 温度 0，输出更稳定
    dashscope_api_key=DASHSCOPE_API_KEY              # API Key
)

rag_chain = (                                        # 用管道符 | 组装 RAG 链
    {"context": retriever | format_docs, "question": RunnablePassthrough()}  # context：检索并格式化；question：原样透传用户问题
    | rag_prompt                                     # 把 context 和 question 填入提示词模板
    | model                                          # 交给模型生成回答
    | StrOutputParser()                              # 把模型输出解析成纯字符串
)

response = rag_chain.invoke("梅西是谁？")              # 执行整条 RAG 链，传入用户问题
print(response)                                      # 打印回答
```

---

## Context 上下文

> 把"当前用户信息"等上下文安全地传给工具使用（而不是写死在提示词里）。

```python
from dotenv import load_dotenv                       # 读取 .env
import os                                            # 读环境变量

load_dotenv()                                        # 加载配置

USER_DATA = {
    "user_a": {                                      # 用户组 A
        "a1": {"name": "张三", "goods": "电脑"},       # A 组第 1 个用户的数据
        "a2": {"name": "李四", "goods": "电视"}        # A 组第 2 个用户的数据
    },
    "user_b": {                                      # 用户组 B
        "b1": {"name": "王五", "goods": "冰箱"},       # B 组第 1 个用户的数据
        "b2": {"name": "赵六", "goods": "空调"}        # B 组第 2 个用户的数据
    }
}

from dataclasses import dataclass                    # 导入 dataclass 装饰器（简化类定义）

@dataclass(frozen=True)                              # frozen=True：实例创建后不可修改（只读）
class UserContext:                                   # 定义上下文数据结构
    user_id: str                                     # 用户 ID
    role_id: str                                     # 用户组 ID

from langchain.tools import tool, ToolRuntime        # 导入 tool 装饰器和 ToolRuntime（运行时信息）

@tool                                                # 把函数注册为一个工具
def get_current_user_data(runtime: ToolRuntime[UserContext]):
    """查询当前登录用户的资源"""                        # 工具说明（模型据此判断何时调用）
    ctx = runtime.context                            # 从运行时取出上下文（即传入的 UserContext）
    data = USER_DATA.get(ctx.role_id, {}).get(ctx.user_id)  # 用 role_id + user_id 查出对应用户数据
    return f"姓名:{data['name']},商品:{data['goods']}"  # 返回格式化字符串

from langchain.agents import create_agent            # 创建智能体
from langchain.chat_models import init_chat_model    # 初始化模型

model = init_chat_model(                             # 初始化模型
    model="qwen3.5-plus",                            # 模型名称
    model_provider="openai",                         # OpenAI 兼容协议
    api_key=os.getenv("DASHSCOPE_API_KEY"),          # API Key
    base_url=os.getenv("DASHSCOPE_BASE_URL")         # 接口地址
)

agent = create_agent(
    model,                                           # 模型
    tools=[get_current_user_data],                   # 注册工具
    context_schema=UserContext,                      # 声明上下文结构（类型安全）
    system_prompt="你是购物助手，调用工具来查询用户信息"  # 系统提示词
)

from langchain_core.messages import HumanMessage     # 用户消息类

response = agent.invoke(                             # 同步调用智能体
    {"messages": [HumanMessage("查询一下我购买的商品")]},  # 用户问题
    context=UserContext(user_id="b1", role_id="user_b")  # 传入具体上下文（当前用户是 b1）
)

for message in response['messages']:                 # 遍历所有消息
    message.pretty_print()                           # 美化打印
```

---

## State（状态）

> 给智能体增加自定义状态字段，工具可以读写这些状态（通过返回 `Command` 更新）。

```python
from langchain.agents import AgentState              # 导入 AgentState（智能体的基础状态类）

class CallState(AgentState):                         # 自定义状态类，继承 AgentState
    """调用智能体时的智能体状态"""
    model_call_count: int                            # 新增字段：模型被调用的次数

from langchain.tools import tool, ToolRuntime        # 导入工具装饰器、运行时
from langgraph.types import Command                  # 导入 Command（用于更新状态/跳转）
from langchain.messages import ToolMessage           # 导入 ToolMessage（工具返回的消息）

@tool                                                # 注册为工具
def update_model_call_count(runtime: ToolRuntime):
    """记录模型被调用的次数"""                        # 工具说明
    count = runtime.state.get("model_call_count", 0) # 从状态里读取当前计数（默认 0）
    print("模型被调用次数：", count)                   # 打印当前计数

    update = {                                       # 构造要更新的状态字典
        "model_call_count": count + 1,               # 计数 +1
        "messages": [                                # 同时要往消息列表里追加一条 ToolMessage
            ToolMessage(
                content="数据更新成功",                # 工具消息内容
                tool_call_id=runtime.tool_call_id    # 关联本次工具调用的 ID
            )
        ]
    }

    return Command(update=update)                    # 返回 Command，让框架把 update 合并进状态
```

```python
from dotenv import load_dotenv                       # 读取 .env
import os                                            # 读环境变量
load_dotenv()                                        # 加载配置

from langchain.agents import create_agent            # 创建智能体
from langchain.chat_models import init_chat_model    # 初始化模型
from langgraph.checkpoint.memory import InMemorySaver  # 内存保存器

model = init_chat_model(                             # 初始化模型
    model="qwen3.5-plus",                            # 模型名称
    model_provider="openai",                         # OpenAI 兼容协议
    api_key=os.getenv("DASHSCOPE_API_KEY"),          # API Key
    base_url=os.getenv("DASHSCOPE_BASE_URL")         # 接口地址
)

agent = create_agent(
    model,                                           # 模型
    tools=[update_model_call_count],                 # 注册"更新计数"工具
    state_schema=CallState,                          # 使用自定义状态结构 CallState
    checkpointer=InMemorySaver(),                    # 保存状态（记忆）
    system_prompt="你在回答用户问题的时候调用工具记录模型被调用次数"  # 系统提示词
)
```

```python
from langchain.messages import HumanMessage          # 用户消息类

config = {"configurable": {"thread_id": "1"}}        # 会话 ID（决定状态存哪个线程）

response = agent.invoke(                             # 同步调用智能体
    {"messages": [HumanMessage(content="你好，我是张三")]},  # 用户消息
    config                                           # 会话配置
)

for message in response['messages']:                 # 遍历返回的所有消息
    message.pretty_print()                           # 美化打印
```

---

## 中间件（Middleware）

> 中间件可以在请求前后"插手"处理，比如脱敏、人工审核。

### 信息脱敏

```python
from langchain.agents.middleware import PIIMiddleware # 导入 PII（个人隐私信息）中间件

pii_middleware_phone = PIIMiddleware(                # 创建手机号脱敏中间件
    "phone_number",                                  # 要处理的敏感信息类型：手机号
    detector=r"(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?)?\d{3,4}[\s.-]?\d{4}",  # 正则：匹配各种手机号格式
    strategy="mask"                                  # 策略：mask（打码遮蔽）
)

from dotenv import load_dotenv                       # 读取 .env
import os                                            # 读环境变量
load_dotenv()                                        # 加载配置

from langchain.agents import create_agent            # 创建智能体
from langchain.chat_models import init_chat_model    # 初始化模型
from langchain_core.messages import HumanMessage     # 用户消息类

model = init_chat_model(                             # 初始化模型
    model="qwen-long",                               # 模型名称
    model_provider="openai",                         # OpenAI 兼容协议
    api_key=os.getenv("DASHSCOPE_API_KEY"),          # API Key
    base_url=os.getenv("DASHSCOPE_BASE_URL")         # 接口地址
)

agent = create_agent(
    model,                                           # 模型
    middleware=[pii_middleware_phone]                # 挂载脱敏中间件
)

response = agent.invoke({                            # 同步调用
    "messages": [
        HumanMessage("我的手机号是13112345678，请记住这些信息")  # 用户输入含手机号
    ]
})

for message in response['messages']:                 # 遍历消息
    message.pretty_print()                           # 打印（能看到手机号被脱敏）
```

### 人工审核（Human-in-the-Loop）

```python
from langchain_core.tools import tool                # 工具装饰器

emails = [                                           # 模拟邮箱里的邮件数据
    {
        "subject": "打个招呼",                        # 邮件主题
        "content": """
            你好，张三，
            我们好久没聊天啦，今天突然想起你。
            你最近怎么样？工作和生活一切顺利吗？

            期待你的回信，保重！
        """,                                         # 邮件内容
        "from": "lisi@163.com",                      # 发件人
        "status": "未读"                              # 状态
    },
    {
        "subject": "工作咨询",                        # 邮件主题
        "content": """
            你好，张三，
            最近还好吗？

            不知道你什么时候有空，能不能一起聊聊。不急，有空再回复就好。

            祝你一切顺心！
        """,                                         # 邮件内容
        "from": "wangwu@163.com",                    # 发件人
        "status": "已读"                              # 状态
    }
]

@tool                                                # 注册为工具
def check_email() -> str:
    """查看邮件"""                                    # 工具说明
    return str(emails)                               # 返回邮件列表的字符串形式

@tool                                                # 注册为工具
def send_email(to: str, subject: str, content: str):
    """回复邮件"""                                    # 工具说明
    return f"邮件已发送给{to},主题:{subject},内容:{content}"  # 返回"发送成功"的模拟结果

from langchain.agents.middleware import HumanInTheLoopMiddleware  # 导入人工审核中间件

email_middleware = HumanInTheLoopMiddleware(         # 创建人工审核中间件
    interrupt_on={                                   # 指定"在哪些工具调用时中断等待人工"
        "send_email": {                              # 对 send_email 工具中断
            "description": "请确认邮件内容",           # 中断提示语
            "allowed_decisions": ["approve", "reject"]  # 允许的决定：批准 / 拒绝
        }
    }
)

from dotenv import load_dotenv                       # 读取 .env
import os                                            # 读环境变量
load_dotenv()                                        # 加载配置

from langchain.agents import create_agent            # 创建智能体
from langchain.chat_models import init_chat_model    # 初始化模型
from langgraph.checkpoint.memory import InMemorySaver  # 内存保存器

model = init_chat_model(                             # 初始化模型
    model="qwen3.5-plus",                            # 模型名称
    model_provider="openai",                         # OpenAI 兼容协议
    api_key=os.getenv("DASHSCOPE_API_KEY"),          # API Key
    base_url=os.getenv("DASHSCOPE_BASE_URL")         # 接口地址
)

agent = create_agent(
    model,                                           # 模型
    tools=[check_email, send_email],                 # 注册两个工具
    middleware=[email_middleware],                   # 挂载人工审核中间件
    checkpointer=InMemorySaver(),                    # 保存状态（中断后可继续）
    system_prompt="你是一个邮件助手"                    # 系统提示词
)

config = {"configurable": {"thread_id": "1"}}        # 会话 ID

response = agent.invoke(                             # 第一次调用：查看邮件
    {"messages": [HumanMessage("帮我查看邮件")]},       # 用户请求
    config                                           # 会话配置
)

for message in response['messages']:                 # 遍历消息
    message.pretty_print()                           # 打印

response = agent.invoke(                             # 第二次调用：回复邮件（会触发人工审核中断）
    {"messages": [HumanMessage("帮我回复李四，问问他具体时间")]},  # 用户请求
    config                                           # 会话配置
)

for message in response['messages']:                 # 遍历消息
    message.pretty_print()                           # 打印（此时停在 send_email 等待审核）

from langgraph.types import Command                  # 导入 Command（用于恢复中断）

response = agent.invoke(                             # 恢复中断：拒绝并给出修改意见
    Command(
        resume={
            "decisions": [                           # 决定列表
                {
                    "type": "reject",                # 拒绝
                    "message": "语气太正式了，我和李四是好朋友，用更亲切的语气回复"  # 给模型的修改建议
                }
            ]
        }
    ),
    config                                           # 会话配置
)

for message in response['messages']:                 # 遍历消息
    message.pretty_print()                           # 打印（模型按建议重写）

response = agent.invoke(                             # 再次恢复中断：批准发送
    Command(
        resume={
            "decisions": [
                {
                    "type": "approve"                # 批准
                }
            ]
        }
    ),
    config                                           # 会话配置
)

for message in response['messages']:                 # 遍历消息
    message.pretty_print()                           # 打印（邮件"发送"成功）
```

---

## MCP（模型上下文协议）

> MCP 让 Agent 能以统一方式接入外部工具服务（本地进程或远程 HTTP 服务）。

1、安装环境

```bash
pip install langchain-mcp-adapters
pip install uv
```

> - `langchain-mcp-adapters`：把 MCP 工具接入 LangChain 的适配器。
> - `uv`：超快的 Python 包/工具运行器，`uvx` 可直接运行 MCP 服务器。

2、查询当前时间

```python
import sys                                           # 系统模块
import asyncio                                       # 异步 IO 模块
from dotenv import load_dotenv                       # 读取 .env
load_dotenv()                                        # 加载配置

if sys.platform == "win32":                          # 如果是 Windows 平台
    if not isinstance(asyncio.get_event_loop_policy(), asyncio.WindowsProactorEventLoopPolicy):  # 若当前不是 Proactor 事件循环策略
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())  # 设为 Proactor（Windows 子进程需要）

    if "ipykernel" in sys.modules:                   # 如果运行在 Jupyter 内核里
        sys.stderr = sys.__stderr__                  # 恢复标准错误输出（避免某些显示问题）

from langchain_mcp_adapters.client import MultiServerMCPClient  # 导入多服务器 MCP 客户端

client = MultiServerMCPClient(                       # 创建 MCP 客户端，可配置多个服务
    {
        "time": {                                    # 服务名：time
            "transport": "stdio",                    # 传输方式：stdio（本地子进程标准输入输出）
            "command": "uvx",                        # 启动命令：uvx
            "args": [                                # 命令参数
                "mcp-server-time",                   # 要运行的 MCP 服务器包
                "--local-timezone=Asia/Shanghai",    # 指定本地时区为上海
            ]
        }
    }
)

tools = await client.get_tools()                     # 异步获取该客户端下所有工具
for tool in tools:                                   # 遍历工具
    print(tool.name)                                 # 打印工具名称

from langchain_core.messages import HumanMessage     # 用户消息类

import os                                            # 读环境变量
from langchain.agents import create_agent            # 创建智能体
from langchain.chat_models import init_chat_model    # 初始化模型

model = init_chat_model(                             # 初始化模型
    model="qwen3.5-plus",                            # 模型名称
    model_provider="openai",                         # OpenAI 兼容协议
    api_key=os.getenv("DASHSCOPE_API_KEY"),          # API Key
    base_url=os.getenv("DASHSCOPE_BASE_URL")         # 接口地址
)

agent = create_agent(
    model,                                           # 模型
    tools                                            # 把 MCP 工具列表传进去
)
response = await agent.ainvoke(
    {
        "messages": [HumanMessage("现在几点了？")]
    }
)

for message in response['messages']:
    message.pretty_print()
from langchain_core.messages import HumanMessage     # 用户消息类（原笔记此处重复导入）
import os                                            # 读环境变量（原笔记此处重复导入）
from langchain.agents import create_agent            # 创建智能体（原笔记此处重复导入）
from langchain.chat_models import init_chat_model    # 初始化模型（原笔记此处重复导入）

model = init_chat_model(                             # 再次初始化模型（原笔记重复代码）
    model="qwen3.5-plus",                            # 模型名称
    model_provider="openai",                         # OpenAI 兼容协议
    api_key=os.getenv("DASHSCOPE_API_KEY"),          # API Key
    base_url=os.getenv("DASHSCOPE_BASE_URL")         # 接口地址
)

agent = create_agent(
    model,                                           # 模型
    tools                                            # 工具
)
```

3、查询航班（HTTP 远程 MCP 服务）

```python
client = MultiServerMCPClient(                       # 新建 MCP 客户端
    {
        "kiwi-com-flight-search": {                  # 服务名：kiwi 航班搜索
            "transport": "http",                     # 传输方式：HTTP（远程服务）
            "url": "https://mcp.kiwi.com"            # 服务地址
        }
    }
)

tools = await client.get_tools()                     # 异步获取所有工具
for tool in tools:                                   # 遍历工具
    print(tool.name)                                 # 打印工具名称

model = init_chat_model(                             # 初始化模型
    model="qwen3.5-plus",                            # 模型名称
    model_provider="openai",                         # OpenAI 兼容协议
    api_key=os.getenv("DASHSCOPE_API_KEY"),          # API Key
    base_url=os.getenv("DASHSCOPE_BASE_URL")         # 接口地址
)

agent = create_agent(
    model,                                           # 模型
    tools,                                           # 传入 MCP 工具
    system_prompt="你是一名旅行智能助手，帮用户找到合适的航班"  # 系统提示词
)

response = await agent.ainvoke({                     # 异步调用智能体（ainvoke）
    "messages": [HumanMessage("帮我查询下周一深圳飞北京的航班")]  # 用户问题
})

for message in response['messages']:                 # 遍历消息
    message.pretty_print()                           # 美化打印
```

---

## 小结（给初学者的学习路线建议）

1. **先跑通最基础的模型连接**（快速上手 6~8 步），理解 `invoke` 和 `stream`。
2. **理解三种消息角色**：`system` / `user` / `assistant`。
3. **学会 `create_agent` + `system_prompt`**，这是后面一切功能的基础。
4. **结构化输出**（Pydantic）→ 让结果可编程使用。
5. **工具调用（Function Calling）** → 让 Agent 能"动手"。
6. **记忆（checkpointer + thread_id）** → 多轮对话。
7. **RAG** → 让 Agent 基于私有知识回答。
8. **Context / State** → 把业务上下文与状态传入 Agent。
9. **中间件** → 脱敏、人工审核等安全控制。
10. **MCP** → 接入标准化外部工具生态。

> 提示：原笔记中 MCP 部分有一段 `model` / `agent` 的重复代码，学习时可以直接忽略第二段重复的初始化。
