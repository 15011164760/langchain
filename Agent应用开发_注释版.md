# Agent 应用开发（注释版）

> 本文档在原教程基础上为每一段代码补充了详细注释，便于逐行理解 LangChain / LangGraph 的核心概念。
> 标注「★」的是最容易踩坑或最值得记住的点。

Agent 应用开发 = 前端 + 后端 + Agent

- 后端：Java
- Agent：Python

## LangChain

环境要求：

- Python 3.14+
- PyCharm 2025+

---

## 快速上手

### 1、新建项目，配置虚拟环境

```bash
# 创建项目目录并进入
mkdir langchain
```

### 2、创建虚拟环境

```bash
# -m venv 调用 Python 内置的 venv 模块
# .venv 是虚拟环境目录名（约定俗成，也方便 IDE 自动识别）
# 作用：把项目依赖与系统 Python 隔离，避免版本冲突
python -m venv .venv
```

### 3、激活虚拟环境

```bash
# Windows 下激活脚本位于 .venv\Scripts\ 目录
# 激活后命令行前缀会出现 (.venv)，之后的 pip / python 都指向该虚拟环境
.venv\Scripts\activate
```

### 4、安装依赖

```bash
# 核心框架：模型调用、Agent、链式编排
pip install langchain

# LangChain 对 OpenAI 协议的适配层
# ★ 阿里云百炼（DashScope）提供 OpenAI 兼容接口，所以用它来连 Qwen 模型
pip install langchain-openai

# 从 .env 文件读取环境变量，避免把 API Key 硬编码进代码
pip install python-dotenv
```

### 5、创建配置文件，存放 API-KEY 和 URL

```ini
# 文件名必须叫 .env（放在项目根目录，与 notebook / py 文件同级）
# Key 与业务空间要匹配：base_url 是哪个业务空间的，Key 就必须在那个空间里创建
DASHSCOPE_API_KEY=你的apikey
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

> ★ 两个常见坑：
> 1. `load_dotenv()` 默认**不会覆盖系统里已存在的同名环境变量**。如果 Windows 系统环境变量里也设了 `DASHSCOPE_API_KEY`，改 `.env` 是不生效的——要么删掉系统变量，要么写 `load_dotenv(override=True)`。
> 2. 报 401 `invalid_api_key` 时，先用 curl 直接请求接口验证 Key 是否有效，排除是不是代码问题。
> 3. `.env` 不要提交到 Git 仓库。

### 6、写代码连接大模型

```python
# 导入依赖
from dotenv import load_dotenv          # 读取 .env 文件
from langchain.chat_models import init_chat_model   # 统一的大模型初始化工厂
import os

# 加载 .env 中的变量到当前进程的环境变量里（之后用 os.getenv 就能取到）
load_dotenv()

# 创建 model
# init_chat_model：LangChain 的统一入口，换模型只需改参数，不用改业务代码
model = init_chat_model(
    model="qwen-long",                  # 模型名称，必须是百炼控制台里已开通的模型
    model_provider="openai",            # 走 OpenAI 兼容协议（百炼的 compatible-mode）
    api_key=os.getenv("DASHSCOPE_API_KEY"),   # 从环境变量取 Key，避免硬编码
    base_url=os.getenv("DASHSCOPE_BASE_URL")  # 接口地址，末尾要带 /compatible-mode/v1
)

# invoke = 同步调用，一次性拿到完整回复（非流式）
# 传入字符串会被自动包装成一条 HumanMessage
response = model.invoke("你是谁？")

# response 是 AIMessage 对象，正文内容在 .content 里
print(response.content)
```

### 7、设置角色

```python
# 用消息列表来构造多轮对话，每条消息是 {"role": ..., "content": ...}
# role 的取值：
#   system    —— 系统人设，优先级最高，用来约定模型的身份/语气/边界
#   user      —— 用户提问
#   assistant —— 模型的历史回答（多轮对话时回填用）
response = model.invoke([
    {"role": "system", "content": "请你以周杰伦的口吻来回答问题"},
    {"role": "user",   "content": "你是谁？"}
])

print(response.content)
```

### 8、流式输出

```python
# stream = 流式调用，返回一个生成器，模型边生成边吐出内容
# 适合需要「打字机效果」的场景，首字延迟更低
response = model.stream([
    {"role": "system", "content": "请你以周杰伦的口吻来回答问题"},
    {"role": "user",   "content": "你是谁？"}
])

# 每次迭代拿到一个 message 分片（chunk），content 是这一小段文本
for message in response:
    # end="" 不换行，让分片拼成连续的文字
    print(message.content, end="")
```

---

## 智能体中调用

用 `create_agent` 把模型包装成 Agent（本质是一个 LangGraph 图），后续就能挂工具、加记忆、加中间件。

```python
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent     # ★ 创建 Agent 的核心函数
import os

load_dotenv()

# 创建底层大模型（Agent 的「大脑」）
model = init_chat_model(
    model="qwen-long",
    model_provider="openai",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL")
)

# 创建 Agent：把模型包装成一个可循环执行的智能体
# 目前只传了模型，没有工具，等价于一个「带对话协议」的聊天模型
agent = create_agent(model)

# Agent 的输入必须是字典，messages 是消息列表（与上面直接调模型的写法一致）
response = agent.invoke({
    "messages": [
        {"role": "system", "content": "请你以周杰伦的口吻来回答问题"},
        {"role": "user",   "content": "你是谁？"}
    ]
})

# ★ 返回值是「状态字典」而非单纯的 AIMessage：
#   包含 messages（完整对话历史）、可能还有 structured_response、state 等字段
print(response)
```

### 流式输出

```python
# Agent 同样支持 stream
# stream_mode="messages"：按「消息分片」流式输出
# ★ 此时每次迭代拿到的是二元组 (token, metadata)，而不是单个 message
response = agent.stream(
    {
        "messages": [
            {"role": "system", "content": "请你以周星驰的口吻来回答问题"},
            {"role": "user",   "content": "你是谁？"}
        ]
    },
    stream_mode="messages"
)

for token, metadata in response:
    # token 是 AIMessageChunk，content 可能为空（如工具调用分片、元数据分片）
    # metadata 记录了这条分片来自哪个节点、哪个模型等信息
    if token.content:
        print(token.content, end="")
```

---

## 多模态消息

三种核心消息类型的定位：

- `SystemMessage`：系统角色
- `HumanMessage`：用户提问
- `AIMessage`：大模型的回答

> 相对于字典写法 `{"role": ...}`，消息类写法支持更丰富的内容结构（图片、文件、音频等）。

```python
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
import os

load_dotenv()

model = init_chat_model(
    model="qwen3.5-plus",               # ★ 带图片输入时必须用多模态（VL）模型
    model_provider="openai",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL")
)

agent = create_agent(model)

from langchain_core.messages import HumanMessage

# ★ content 传「列表」表示多模态内容，每项通过 type 区分：
#   {"type": "text",  "text": "..."}  —— 文本
#   {"type": "image", "url":  "..."}  —— 图片地址（也可以是 base64）
message = HumanMessage([
    {"type": "text",  "text": "描述一下这张图片中的内容"},
    {"type": "image", "url": "https://inews.gtimg.com/news_bt/Ogw_-rddzOwDnZQN8q5jjefTEK7ZlIEPGAKVCFdISRossAA/641"}
])

# 直接把 HumanMessage 对象放进 messages 列表即可
stream = agent.stream(
    {"messages": [message]},
    stream_mode="messages",
)

for token, metadata in stream:
    if token.content:
        print(token.content, end="")
```

### 设置角色

```python
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
import os

load_dotenv()

model = init_chat_model(
    model="qwen3.5-plus",
    model_provider="openai",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL")
)

agent = create_agent(model)

from langchain_core.messages import HumanMessage, SystemMessage

# 用户消息：多模态内容（文本 + 图片）
human_message = HumanMessage([
    {"type": "text",  "text": "描述一下这张图片中的内容"},
    {"type": "image", "url": "https://inews.gtimg.com/news_bt/Ogw_-rddzOwDnZQN8q5jjefTEK7ZlIEPGAKVCFdISRossAA/641"}
])

# 系统消息：约定模型的人设与语气
system_message = SystemMessage("请以周星驰的口吻来回答问题")

stream = agent.stream(
    {
        # ★ 顺序无所谓：system 消息在组装时会自动排到最前面
        "messages": [human_message, system_message]
    },
    stream_mode="messages",
)

for token, metadata in stream:
    if token.content:
        print(token.content, end="")
```

---

## 系统提示词

除了塞一条 `SystemMessage`，`create_agent` 还提供了 `system_prompt` 参数——**推荐写法**：语义更清晰，且不会被对话历史挤掉。

```python
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
import os

load_dotenv()

model = init_chat_model(
    model="qwen-long",
    model_provider="openai",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL")
)

# ★ system_prompt：Agent 级系统提示词，框架会自动把它注入到每轮对话最前面
agent = create_agent(
    model,
    system_prompt="请以周星驰的口吻来回答问题"
)

# 有了 system_prompt，输入里就只需要用户消息
response = agent.stream(
    {
        "messages": [HumanMessage("你是谁？")]
    },
    stream_mode="messages"
)

for token, metadata in response:
    if token.content:
        print(token.content, end="")
```

### 详细的系统提示词

```python
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
import os

load_dotenv()

model = init_chat_model(
    model="qwen-long",
    model_provider="openai",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL")
)

# ★ 系统提示词写得越具体，输出越稳定
#   推荐结构：角色定位 + 任务目标 + 输出要求（格式/语气/边界）
system_prompt = """
你是一个专业的旅行规划助手。你的任务是根据用户提供的旅行偏好，为其推荐最合适的旅行方案。
"""

agent = create_agent(
    model,
    system_prompt=system_prompt
)

# 用户的具体需求
content = """
我想规划一次旅行，我从深圳出发，我喜欢的目的地类型是海滨城市
"""

response = agent.stream(
    {
        "messages": [HumanMessage(content)]
    },
    stream_mode="messages"
)

for token, metadata in response:
    if token.content:
        print(token.content, end="")
```

---

## 结构化输出

让模型按约定的数据结构返回结果，而不是一段自由文本——**便于后端直接反序列化使用**。

```python
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from pydantic import BaseModel          # ★ 用 Pydantic 模型定义输出结构
import os

load_dotenv()

model = init_chat_model(
    model="qwen-long",
    model_provider="openai",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL")
)

system_prompt = """
你是一个专业的旅行规划助手。你的任务是根据用户提供的旅行偏好，为其推荐最合适的旅行方案。
"""

# 定义输出结构：字段名就是 JSON 的 key，类型决定值的格式
# 框架会把该模型转成 JSON Schema 发给模型，要求它按此结构输出
class TravelData(BaseModel):
    # 目的地
    city: str
    # 推荐理由
    reason: str
    # 费用区间
    cost: str
    # 住宿
    hotel: str
    # 交通
    transport: str
    # 特别提示
    tips: str
    # 最佳旅行季节
    season: str

# ★ response_format 指定输出结构，框架负责解析和校验
agent = create_agent(
    model,
    system_prompt=system_prompt,
    response_format=TravelData
)

content = """
我想规划一次旅行，我从深圳出发，我喜欢的目的地类型是海滨城市
"""

# 结构化输出场景用 invoke 更方便（要拿完整对象来解析）
response = agent.invoke(
    {
        "messages": [HumanMessage(content)]
    }
)

# ★ 结果不在 messages 里，而在 structured_response 键中，是 TravelData 实例
city = response["structured_response"]

# 可以直接按属性访问，也可以 model_dump() 转字典再序列化给前端
print(city)
```

---

## Function Calling

让 Agent 能「调用外部工具」：模型根据工具描述自行判断何时调用、传什么参数。

**步骤：**

1. 注册 Tavily（搜索服务），获取 API_KEY，写进 `.env`
2. 安装 Tavily 依赖
3. 通过 Tavily 查询网页信息并交给 Agent，由 Agent 综合后给出答案

```bash
pip install langchain-tavily
```

```python
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_tavily import TavilySearch        # Tavily 搜索工具的现成封装
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
import os

load_dotenv()

# 自定义方法：创建搜索工具
# TavilySearch 会自动从环境变量 TAVILY_API_KEY 读取密钥
search_tool = TavilySearch()

# 创建 model
model = init_chat_model(
    model="qwen3.5-plus",
    model_provider="openai",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL")
)

# 创建 agent
# ★ tools 传入工具列表；模型会读取工具的 name/description 决定何时调用
#   Agent 内部是「模型 → 判断要不要调工具 → 调工具 → 把结果喂回模型 → 再回答」的循环
agent = create_agent(
    model,
    tools=[search_tool],
    system_prompt="你是一个智能助手，使用工具来回答用户问题"
)

response = agent.invoke(
    {"messages": [HumanMessage("今天深圳天气怎么样？")]}
)

# ★ 打印完整对话轨迹：能看到 HumanMessage → AIMessage(带 tool_calls)
#   → ToolMessage(工具返回) → 最终 AIMessage，便于排查工具是否被正确调用
for message in response["messages"]:
    message.pretty_print()
```

### 结构化输出

```python
from pydantic import BaseModel, Field

# Agent 所引用的网页信息
class Reference(BaseModel):
    # ★ Field(description=...) 会写进 JSON Schema，模型据此理解字段含义
    title: str = Field(description="网页标题")
    url: str = Field(description="网页网址")

# Agent 的回答内容
class AnswerInfo(BaseModel):
    answer: str = Field(description="最终的答案")
    # 嵌套列表：一个问题可以引用多个网页来源
    reference: list[Reference] = Field(description="回答问题的网页信息")

# 在原有 agent 基础上，只需追加 response_format
# 注意：这里的 model、search_tool 来自上一条 cell，需在同一会话中执行
agent = create_agent(
    model,
    tools=[search_tool],
    system_prompt="你是一个智能助手，使用工具来回答用户问题",
    response_format=AnswerInfo
)

response = agent.invoke(
    {"messages": [HumanMessage("梅西是谁？")]}
)

# ★ 结构化结果在 structured_response 中，可直接 answer_info.reference 遍历来源
print(response["structured_response"])
```

---

## 记忆系统

让 Agent 拥有记忆功能，能够记住历史消息。

原理：`checkpointer` 把每轮对话状态存起来，`thread_id` 作为会话标识——**同一 thread_id 的多次调用共享上下文**。

```python
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver   # ★ 内存版检查点存储
import os

load_dotenv()

model = init_chat_model(
    model="qwen-long",
    model_provider="openai",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL")
)

# checkpointer：每执行一步就把 Agent 状态存档
# InMemorySaver 存在进程内存里，重启即丢失；生产环境可换 SqliteSaver / PostgresSaver
agent = create_agent(
    model,
    checkpointer=InMemorySaver()
)

# ★ thread_id 是会话隔离的钥匙：不同用户/不同对话用不同 id
config = {
    "configurable": {"thread_id": "thread_1"}
}

# 第一轮：告诉模型用户信息
response = agent.invoke(
    {
        "messages": [HumanMessage("你好，我叫张三，我喜欢打游戏")]
    },
    config          # 第二个参数传配置，带上 thread_id
)

print(response)
```

```python
# 第二轮：★ 同一个 config（同一个 thread_id），Agent 能拿到上一轮的历史
response = agent.invoke(
    {
        "messages": [HumanMessage("我叫什么？我喜欢干什么？")]
    },
    config
)

print(response)
```

---

## RAG

向量检索原理：

1. 把文本转换为向量数据（Embedding）
2. 通过计算向量相似度找到匹配的文档片段，再拼进提示词交给模型

**代码实现：**

1、安装依赖

```bash
# langchain-community：第三方集成（文档加载器、向量库、DashScope 封装等）
# langchain-text-splitters：文本切分器
# faiss-cpu：Facebook 的向量检索库（CPU 版）
# dashscope：阿里云百炼官方 SDK（做 Embedding 用）
pip install langchain langchain-community langchain-text-splitters faiss-cpu dashscope python-dotenv
```

2、创建知识库文件 `knowledge.md`

```text
2015年欧冠半决赛，梅西在**博阿滕**面前那个著名的“静止变向”，整个过程中足球只触地**三次**。没有踩单车，没有钟摆过人，只有一个**2米**的横向移动和**0.3秒**的爆发加速。这个看似简单的动作，背后是**对重心控制的极致理解**——而这正是梅西足球哲学的终极体现。
```

3、代码实现

```python
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader        # 文本加载器
from langchain_text_splitters import RecursiveCharacterTextSplitter # 递归字符切分器
from langchain_community.chat_models.tongyi import ChatTongyi       # 通义千问原生封装
from langchain_community.embeddings import DashScopeEmbeddings      # 百炼向量化
from langchain_community.vectorstores import FAISS                  # 本地向量库
from langchain_core.prompts import ChatPromptTemplate               # 提示词模板
from langchain_core.runnables import RunnablePassthrough            # 透传组件
from langchain_core.output_parsers import StrOutputParser           # 输出解析器

load_dotenv()

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")

# ---- 1. 加载文档 ----
# ★ TextLoader 默认按系统编码读文件，中文文档必须显式指定 utf-8，否则乱码
loader = TextLoader("./knowledge.md", encoding="utf-8")
docs = loader.load()        # 返回 Document 列表（每个文件一个 Document）

print(docs)

# ---- 2. 切分文本 ----
# 长文档必须切块：模型上下文有限，且切块后检索粒度更精准
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,         # 每块最大字符数
    chunk_overlap=100       # 相邻块重叠字符数，避免语义被硬切断
)

splits = text_splitter.split_documents(docs)

print(splits)

# ---- 3. 向量化 + 建库 ----
# Embedding 模型把文本转成向量；text-embedding-v4 是百炼的向量模型
embeddings = DashScopeEmbeddings(
    model="text-embedding-v4",
    dashscope_api_key=DASHSCOPE_API_KEY
)

# 把切分后的文档逐块向量化并存入 FAISS
vectorstore = FAISS.from_documents(splits, embeddings)

# 检索器：每次查询返回相似度最高的 3 个片段
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# ---- 4. 组装 RAG 提示词 ----
# {context} 和 {question} 是占位符，运行时由链填充
# ★ 明确约束「仅能使用检索到的上下文」，减少模型胡编（幻觉）
rag_prompt = ChatPromptTemplate.from_template(
    """
    你是知识库问答助手，**仅能使用下面检索到的上下文回答问题**。

    上下文： {context}
    用户问题：{question}
    """
)

# 把多个 Document 拼成一段纯文本，作为 {context}
def format_docs(docs):
    return "\n\n".join([d.page_content for d in docs])

# 初始化大模型
# temperature=0 让输出更稳定、更贴近事实（知识问答不需要发散）
model = ChatTongyi(
    model="qwen-long",
    temperature=0,
    dashscope_api_key=DASHSCOPE_API_KEY
)

# ---- 5. 用 LCEL 组装 RAG 链 ----
# ★ 管道符 | 表示数据流：前一步的输出作为后一步的输入
#   第一步把输入问题并行分发给两个分支：
#     context 分支：retriever 检索 → format_docs 拼成文本
#     question 分支：RunnablePassthrough 原样透传用户问题
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | rag_prompt     # 填充模板，得到完整提示词
    | model          # 调用大模型
    | StrOutputParser()   # 把 AIMessage 解析成纯字符串
)

response = rag_chain.invoke("梅西是谁？")
print(response)
```

---

## Context 上下文

把「运行时业务数据」（如当前登录用户）安全地传给工具，**而不是让模型自己编或从提示词里猜**。

```python
from dotenv import load_dotenv
import os

load_dotenv()

# 模拟业务数据：user_a / user_b 是两个角色，各自下面挂了用户
USER_DATA = {
    "user_a": {
        "a1": {"name": "张三", "goods": "电脑"},
        "a2": {"name": "李四", "goods": "电视"}
    },
    "user_b": {
        "b1": {"name": "王五", "goods": "冰箱"},
        "b2": {"name": "赵六", "goods": "空调"}
    }
}

from dataclasses import dataclass

# ★ 上下文结构：用 dataclass 定义，frozen=True 表示不可变（防止工具里被篡改）
@dataclass(frozen=True)
class UserContext:
    user_id: str
    role_id: str

from langchain.tools import tool, ToolRuntime

# @tool 装饰器把普通函数变成 Agent 可调用的工具
# ★ 函数签名带 runtime: ToolRuntime[UserContext]，框架就会在调用时注入上下文
@tool
def get_current_user_data(runtime: ToolRuntime[UserContext]):
    """查询当前登录用户的资源"""
    # ★ 通过 runtime.context 取到 invoke 时传入的 UserContext 实例
    #   这样「当前用户是谁」由后端决定，模型无法伪造，安全
    ctx = runtime.context
    data = USER_DATA.get(ctx.role_id, {}).get(ctx.user_id)
    return f"姓名:{data['name']},商品:{data['goods']}"

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

model = init_chat_model(
    model="qwen3.5-plus",
    model_provider="openai",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL")
)

# ★ context_schema：声明上下文的类型，工具才能正确拿到注入值
agent = create_agent(
    model,
    tools=[get_current_user_data],
    context_schema=UserContext,
    system_prompt="你是购物助手，调用工具来查询用户信息"
)

from langchain_core.messages import HumanMessage

# ★ invoke 时的 context 参数：每次调用动态传入，不同用户互不影响
response = agent.invoke(
    {"messages": [HumanMessage("查询一下我购买的商品")]},
    context=UserContext(user_id="b1", role_id="user_b")
)

for message in response["messages"]:
    message.pretty_print()
```

---

## State

在 Agent 状态里增加**自定义字段**，实现跨轮次的计数、统计等能力。

```python
from langchain.agents import AgentState

# ★ 继承 AgentState（已含 messages 等内置字段），再追加自定义字段
class CallState(AgentState):
    """调用智能体时的智能体状态"""
    model_call_count: int       # 记录模型被调用次数

from langchain.tools import tool, ToolRuntime
from langgraph.types import Command
from langchain.messages import ToolMessage

@tool
def update_model_call_count(runtime: ToolRuntime):
    """记录模型被调用的次数"""
    # runtime.state 是当前状态字典，读取自定义字段
    count = runtime.state.get("model_call_count", 0)
    print("模型被调用次数：", count)

    # ★ 工具返回 Command 表示「要修改状态」，而不是普通的字符串结果
    #   update 里的键会合并进 Agent 状态
    update = {
        "model_call_count": count + 1,
        # 同时补一条 ToolMessage，告诉模型工具执行完毕
        # ★ tool_call_id 必须与模型发起的那次 tool_call 对应，否则会报错
        "messages": [
            ToolMessage(
                content="数据更新成功",
                tool_call_id=runtime.tool_call_id
            )
        ]
    }

    return Command(update=update)
```

```python
from dotenv import load_dotenv
import os

load_dotenv()

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver

model = init_chat_model(
    model="qwen3.5-plus",
    model_provider="openai",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL")
)

# ★ state_schema：把自定义状态结构挂到 Agent 上
# ★ checkpointer：要让状态跨轮次保留，必须配检查点
agent = create_agent(
    model,
    tools=[update_model_call_count],
    state_schema=CallState,
    checkpointer=InMemorySaver(),
    system_prompt="你在回答用户问题的时候调用工具记录模型被调用次数"
)
```

```python
from langchain.messages import HumanMessage

# 会话标识，配合 checkpointer 让状态在同一个 thread 内累积
config = {"configurable": {"thread_id": "1"}}

response = agent.invoke(
    {"messages": [HumanMessage(content="你好，我是张三")]},
    config
)

for message in response["messages"]:
    message.pretty_print()
```

---

## 中间件

Middleware：在 Agent 执行流程中插入横切逻辑（脱敏、审核、限流、日志等），**业务代码零侵入**。

> 信息脱敏

```python
from langchain.agents.middleware import PIIMiddleware

# ★ PIIMiddleware：敏感信息处理中间件
# 第一个参数是内置类型（phone_number / email / credit_card 等）
# detector 也可以传自定义正则
# strategy="mask" 表示把命中的内容打码（其他策略如 block / redact）
pii_middleware_phone = PIIMiddleware(
    "phone_number",
    detector=r"(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,4}\)?[\s.-]?)?\d{3,4}[\s.-]?\d{4}",
    strategy="mask"
)

from dotenv import load_dotenv
import os

load_dotenv()

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage

model = init_chat_model(
    model="qwen-long",
    model_provider="openai",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL")
)

# middleware 传列表，可以叠加多个中间件（按顺序执行）
agent = create_agent(
    model,
    middleware=[pii_middleware_phone]
)

response = agent.invoke({
    "messages": [
        HumanMessage("我的手机号是13112345678，请记住这些信息")
    ]
})

# ★ 观察输出：发给模型 / 存进历史里的手机号应已被打码
for message in response["messages"]:
    message.pretty_print()
```

> 人工审核

关键操作（发邮件、下单、付款）在执行前暂停，等人工确认。

```python
from langchain_core.tools import tool

# 模拟邮箱数据
emails = [
    {
        "subject": "打个招呼",
        "content": """
            你好，张三，
            我们好久没聊天啦，今天突然想起你。
            你最近怎么样？工作和生活一切顺利吗？

            期待你的回信，保重！
        """,
        "from": "lisi@163.com",
        "status": "未读"
    },
    {
        "subject": "工作咨询",
        "content": """
            你好，张三，
            最近还好吗？

            不知道你什么时候有空，能不能一起聊聊。不急，有空再回复就好。

            祝你一切顺心！
        """,
        "from": "wangwu@163.com",
        "status": "已读"
    }
]

@tool
def check_email() -> str:
    """查看邮件"""
    # ★ docstring 会成为工具描述，模型靠它判断「什么时候该用这个工具」
    return str(emails)

@tool
def send_email(to: str, subject: str, content: str):
    """回复邮件"""
    return f"邮件已发送给{to},主题:{subject},内容:{content}"

from langchain.agents.middleware import HumanInTheLoopMiddleware

# ★ 人工介入中间件：interrupt_on 指定哪些工具执行前要暂停
#   description 是展示给审核人的提示文案
#   allowed_decisions 允许的决策类型：approve（通过）/ reject（驳回）/ edit（修改参数）
email_middleware = HumanInTheLoopMiddleware(
    interrupt_on={
        "send_email": {
            "description": "请确认邮件内容",
            "allowed_decisions": ["approve", "reject"]
        }
    }
)

from dotenv import load_dotenv
import os

load_dotenv()

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver

model = init_chat_model(
    model="qwen3.5-plus",
    model_provider="openai",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL")
)

# ★ 人工介入必须配 checkpointer：暂停时的现场需要被保存下来
agent = create_agent(
    model,
    tools=[check_email, send_email],
    middleware=[email_middleware],
    checkpointer=InMemorySaver(),
    system_prompt="你是一个邮件助手"
)

# 同一个 thread_id，保证多轮操作在同一会话内流转
config = {"configurable": {"thread_id": "1"}}

# 第一步：查看邮件
response = agent.invoke(
    {"messages": [HumanMessage("帮我查看邮件")]},
    config
)

for message in response["messages"]:
    message.pretty_print()

# 第二步：让 Agent 起草回复
# ★ 此时会触发中断：返回结果里没有执行 send_email，而是挂起等待人工决策
response = agent.invoke(
    {"messages": [HumanMessage("帮我回复李四，问问他具体时间")]},
    config
)

for message in response["messages"]:
    message.pretty_print()

from langgraph.types import Command

# 第三步：驳回并给出修改意见
# ★ 用 Command(resume=...) 恢复被中断的执行，decisions 对应 interrupt_on 的配置
response = agent.invoke(
    Command(
        resume={
            "decisions": [
                {
                    "type": "reject",
                    "message": "语气太正式了，我和李四是好朋友，用更亲切的语气回复"
                }
            ]
        }
    ),
    config
)

for message in response["messages"]:
    message.pretty_print()

# 第四步：再次中断后选择通过，邮件真正发出
response = agent.invoke(
    Command(
        resume={
            "decisions": [
                {
                    "type": "approve"
                }
            ]
        }
    ),
    config
)

for message in response["messages"]:
    message.pretty_print()
```

---

## MCP

MCP（Model Context Protocol）：用统一协议接入外部工具服务，**不用自己写工具封装**。

1、安装环境

```bash
pip install langchain-mcp-adapters   # 把 MCP 工具适配成 LangChain 工具
pip install uv                       # uvx 命令来自 uv，用于拉起本地 MCP 服务
```

2、查询当前时间

```python
import sys
import asyncio
from dotenv import load_dotenv

load_dotenv()

# ★ Windows 专属兼容处理：stdio 传输需要子进程支持，默认事件循环策略在新版 Python 上会报错
if sys.platform == "win32":
    if not isinstance(asyncio.get_event_loop_policy(), asyncio.WindowsProactorEventLoopPolicy):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    # ★ Jupyter 内核会接管 sys.stderr，MCP 子进程输出可能因此异常，这里恢复原始 stderr
    if "ipykernel" in sys.modules:
        sys.stderr = sys.__stderr__

from langchain_mcp_adapters.client import MultiServerMCPClient

# ★ MultiServerMCPClient：可同时连接多个 MCP 服务，按 key 区分
# transport 支持 stdio（本地进程）/ http（远程服务）/ sse
client = MultiServerMCPClient(
    {
        "time": {
            "transport": "stdio",           # 本地起进程，通过标准输入输出通信
            "command": "uvx",               # 用 uvx 直接运行，无需手动安装
            "args": [
                "mcp-server-time",          # 官方时间 MCP 服务
                "--local-timezone=Asia/Shanghai"
            ]
        }
    }
)

# ★ get_tools 是异步方法，notebook 里可直接 await
#   返回的是 LangChain 工具对象，可直接传给 create_agent
tools = await client.get_tools()
for tool in tools:
    print(tool.name)

from langchain_core.messages import HumanMessage

import os
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

model = init_chat_model(
    model="qwen3.5-plus",
    model_provider="openai",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL")
)

# 把 MCP 拿到的工具集直接交给 Agent
agent = create_agent(
    model,
    tools
)

# 注：原文档此处在同一 cell 内重复定义了一遍 model / agent，保留一份即可
```

3、查询航班

```python
# ★ http 传输：直接连远程 MCP 服务，不需要本地装任何东西
client = MultiServerMCPClient(
    {
        "kiwi-com-flight-search": {
            "transport": "http",
            "url": "https://mcp.kiwi.com"
        }
    }
)

tools = await client.get_tools()
for tool in tools:
    print(tool.name)

model = init_chat_model(
    model="qwen3.5-plus",
    model_provider="openai",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL")
)

agent = create_agent(
    model,
    tools,
    system_prompt="你是一名旅行智能助手，帮用户找到合适的航班"
)

# ★ 异步调用用 ainvoke（与 await get_tools 保持同一事件循环）
response = await agent.ainvoke({
    "messages": [HumanMessage("帮我查询下周一深圳飞北京的航班")]
})

# 打印完整轨迹，确认工具调用参数与返回结果
for message in response["messages"]:
    message.pretty_print()
```

---

## 附：整份文档的核心概念速查

| 概念 | 作用 | 关键参数 |
|---|---|---|
| `init_chat_model` | 统一模型入口，切换厂商只改参数 | `model` / `model_provider` / `api_key` / `base_url` |
| `create_agent` | 把模型包装成可循环执行的 Agent | `tools` / `system_prompt` / `response_format` / `checkpointer` / `middleware` / `context_schema` / `state_schema` |
| `invoke` / `stream` | 一次性返回 / 流式返回 | `stream_mode="messages"` 时返回 `(token, metadata)` |
| `response_format` | 结构化输出 | 传入 Pydantic 模型，结果在 `structured_response` |
| `InMemorySaver` + `thread_id` | 多轮记忆 | 会话隔离靠 `thread_id` |
| `ToolRuntime` | 向工具注入上下文/状态 | `runtime.context` / `runtime.state` / `runtime.tool_call_id` |
| `PIIMiddleware` | 敏感信息脱敏 | `strategy="mask"` |
| `HumanInTheLoopMiddleware` | 关键操作人工审核 | `interrupt_on` + `Command(resume=...)` |
| `MultiServerMCPClient` | 接入 MCP 工具 | `transport`: `stdio` / `http` |
