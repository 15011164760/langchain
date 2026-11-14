# Agent 应用开发

Agent 应用开发=前端+后端+Agent

后端 Java

Agent Python

## LangChain

环境要求

python 3.14+

pycharm 2025+

## 快速上手

1、新建项目，配置虚拟环境

```
mkdir langchain
```

2、创建虚拟环境

```
python -m venv .venv
```

3、激活虚拟环境

```
.venv\Scripts\activate
```

4、安装依赖

```
pip install langchain
pip install langchain-openai
pip install python-dotenv
```

5、创建配置文件，存放 API-KEY  和 URL

```
DASHSCOPE_API_KEY=你的apikey
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

6、写代码连接大模型

```python
# 导入依赖
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
import os
load_dotenv()

# 创建model
model=init_chat_model(
    model="qwen-long",
    model_provider="openai",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL")
)

response=model.invoke("你是谁？");
print(response.content)
```

7、设置角色

```pyhon
response=model.invoke([
    {"role":"system","content":"请你以周杰伦的口吻来回答问题"},
    {"role":"user","content":"你是谁？"}
]);
print(response.content)
```

8、流式输出

```python
response=model.stream([
    {"role":"system","content":"请你以周杰伦的口吻来回答问题"},
    {"role":"user","content":"你是谁？"}
]);

for message in response:
    print(message.content,end="")
```

## 智能体中调用

```python
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
import os
load_dotenv()

model=init_chat_model(
    model="qwen-long",
    model_provider="openai",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL")
)

agent = create_agent(model)

response = agent.invoke({
    "messages":[
        {"role":"system","content":"请你以周杰伦的口吻来回答问题"},
        {"role":"user","content":"你是谁？"}
    ]
})

print(response)
```

流式输出

```python
response = agent.stream(
    {
    "messages":[
        {"role":"system","content":"请你以周星驰的口吻来回答问题"},
        {"role":"user","content":"你是谁？"}
    ]},
    stream_mode="messages"
)

for token,metadata in response:
    if token.content:
        print(token.content,end="")
```

## 多模态消息

SystemMessage：系统角色

HumanMessage：用户提问

AIMessage：大模型的回答

```python
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
import os

load_dotenv()

model=init_chat_model(
    model="qwen3.5-plus",
    model_provider="openai",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL")
)

agent = create_agent(model)

from langchain_core.messages import HumanMessage
message = HumanMessage([
    {"type":"text","text":"描述一下这张图片中的内容"},
    {"type":"image","url":"https://inews.gtimg.com/news_bt/Ogw_-rddzOwDnZQN8q5jjefTEK7ZlIEPGAKVCFdISRossAA/641"}
])

stream = agent.stream(
    {"messages":[message]},
    stream_mode = "messages",
)

for token,metadata in stream:
    if token.content:
        print(token.content,end="")
```

设置角色

```python
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
import os

load_dotenv()

model=init_chat_model(
    model="qwen3.5-plus",
    model_provider="openai",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL")
)

agent = create_agent(model)

from langchain_core.messages import HumanMessage, SystemMessage

human_message = HumanMessage([
    {"type":"text","text":"描述一下这张图片中的内容"},
    {"type":"image","url":"https://inews.gtimg.com/news_bt/Ogw_-rddzOwDnZQN8q5jjefTEK7ZlIEPGAKVCFdISRossAA/641"}
])

system_message = SystemMessage("请以周星驰的口吻来回答问题")

stream = agent.stream(
    {"messages":[human_message,system_message]},
    stream_mode = "messages",
)

for token,metadata in stream:
    if token.content:
        print(token.content,end="")
```

## 系统提示词

```python
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
import os

load_dotenv()

model=init_chat_model(
    model="qwen-long",
    model_provider="openai",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL")
)

agent = create_agent(
    model,
    system_prompt="请以周星驰的口吻来回答问题"
)

response = agent.stream(
    {
        "messages":[HumanMessage("你是谁？")]
    },
    stream_mode="messages"
)

for token,metadata in response:
    if token.content:
        print(token.content,end="")
```

详细的系统提示词

```python
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
import os

load_dotenv()

model=init_chat_model(
    model="qwen-long",
    model_provider="openai",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL")
)

system_prompt="""
你是一个专业的旅行规划助手。你的任务是根据用户提供的旅行偏好，为其推荐最合适的旅行方案。
"""

agent = create_agent(
    model,
    system_prompt=system_prompt
)

content="""
我想规划一次旅行，我从深圳出发，我喜欢的目的地类型是海滨城市
"""

response = agent.stream(
    {
        "messages":[HumanMessage(content)]
    },
    stream_mode="messages"
)

for token,metadata in response:
    if token.content:
        print(token.content,end="")
```

## 结构化输出

```python
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from pydantic import BaseModel
import os

load_dotenv()

model=init_chat_model(
    model="qwen-long",
    model_provider="openai",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL")
)

system_prompt="""
你是一个专业的旅行规划助手。你的任务是根据用户提供的旅行偏好，为其推荐最合适的旅行方案。
"""

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

agent = create_agent(
    model,
    system_prompt=system_prompt,
    response_format=TravelData
)

content="""
我想规划一次旅行，我从深圳出发，我喜欢的目的地类型是海滨城市
"""

response = agent.invoke(
    {
        "messages":[HumanMessage(content)]
    }
)

city = response['structured_response']
print(city)
```

## Function Calling

1、注册 Tavily，获取 API_KEY

2、安装 Tavily 依赖

```
pip install langchain-tavily
```

3、通过 Tavily 查询相关网页信息，提供给 Agent，再由 Agent 给出答案

```python
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_tavily import TavilySearch
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
import os
load_dotenv()

# 自定义方法
search_tool = TavilySearch()

# 创建model
model = init_chat_model(
    model="qwen3.5-plus",
    model_provider="openai",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL")
)

# 创建agent
agent = create_agent(
    model,
    tools=[search_tool],
    system_prompt="你是一个智能助手，使用工具来回答用户问题"
)

response = agent.invoke(
    {"messages":[HumanMessage("今天深圳天气怎么样？")]}
)

for message in response["messages"]:
    message.pretty_print()
```

结构化输出

```python
from pydantic import BaseModel,Field

# Agent所引用的网页信息
class Reference(BaseModel):
    title: str = Field(description="网页标题")
    url: str = Field(description="网页网址")

# Agent的回答内容
class AnswerInfo(BaseModel):
    answer: str = Field(description="最终的答案")
    reference: list[Reference] = Field(description="回答问题的网页信息")

agent = create_agent(
    model,
    tools=[search_tool],
    system_prompt="你是一个智能助手，使用工具来回答用户问题",
    response_format=AnswerInfo
)

response = agent.invoke(
    {"messages":[HumanMessage("梅西是谁？")]}
)

print(response["structured_response"])
```

## 记忆系统

让 Agent 拥有记忆功能，能够记住历史消息

```ptyhon
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver
import os
load_dotenv()

model = init_chat_model(
    model="qwen-long",
    model_provider="openai",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL")
)

agent = create_agent(
    model,
    checkpointer=InMemorySaver()
)

config = {
    "configurable":{"thread_id":"thread_1"}
}

response = agent.invoke(
    {
        "messages":[HumanMessage("你好，我叫张三，我喜欢打游戏")]
    },
    config
)

print(response)
```

```python
response = agent.invoke(
    {
        "messages":[HumanMessage("我叫什么？我喜欢干什么？")]
    },
    config
)

print(response)
```

## RAG

向量检索

1、把文本转换为向量数据

2、通过计算向量数据来判断相似度，从而找到匹配的文档片段

代码实现

1、安装依赖

```
pip install langchain langchain-community langchain-text-splitters faiss-cpu dashscope python-dotenv
```

2、创建知识库文件 knowledge.md

```
2015年欧冠半决赛，梅西在**博阿滕**面前那个著名的“静止变向”，整个过程中足球只触地**三次**。没有踩单车，没有钟摆过人，只有一个**2米**的横向移动和**0.3秒**的爆发加速。这个看似简单的动作，背后是**对重心控制的极致理解**——而这正是梅西足球哲学的终极体现。
```

3、代码实现

```python
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")

# 加载文档
loader = TextLoader("./knowledge.md",encoding="utf-8")
docs = loader.load()

print(docs)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100
)

splits = text_splitter.split_documents(docs)

print(splits)

embeddings = DashScopeEmbeddings(
    model="text-embedding-v4",
    dashscope_api_key=DASHSCOPE_API_KEY
)

vectorstore = FAISS.from_documents(splits,embeddings)
retriever = vectorstore.as_retriever(search_kwargs = {"k":3})

rag_prompt = ChatPromptTemplate.from_template(
    """
    你是知识库问答助手，**仅能使用下面检索到的上下文回答问题**。

    上下文： {context}
    用户问题：{question}
    """
)

def format_docs(docs):
    return "\n\n".join([d.page_content for d in docs])

# 初始化大模型
model = ChatTongyi(
    model="qwen-long",
    temperature=0,
    dashscope_api_key=DASHSCOPE_API_KEY
)

rag_chain = (
    {"context":retriever | format_docs,"question":RunnablePassthrough()}
    | rag_prompt
    | model
    | StrOutputParser()
)

response = rag_chain.invoke("梅西是谁？")
print(response)
```

## Context 上下文

```python
from dotenv import load_dotenv
import os

load_dotenv()

USER_DATA = {
    "user_a":{
        "a1":{"name":"张三","goods":"电脑"},
        "a2":{"name":"李四","goods":"电视"}
    },
    "user_b":{
        "b1":{"name":"王五","goods":"冰箱"},
        "b2":{"name":"赵六","goods":"空调"}
    }
}

from dataclasses import dataclass

@dataclass(frozen=True)
class UserContext:
    user_id: str
    role_id: str

from langchain.tools import tool,ToolRuntime

@tool
def get_current_user_data(runtime: ToolRuntime[UserContext]):
    """查询当前登录用户的资源"""
    ctx = runtime.context
    data = USER_DATA.get(ctx.role_id,{}).get(ctx.user_id)
    return f"姓名:{data['name']},商品:{data['goods']}"

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

model = init_chat_model(
    model="qwen3.5-plus",
    model_provider="openai",
    api_key = os.getenv("DASHSCOPE_API_KEY"),
    base_url = os.getenv("DASHSCOPE_BASE_URL")
)

agent = create_agent(
    model,
    tools=[get_current_user_data],
    context_schema=UserContext,
    system_prompt="你是购物助手，调用工具来查询用户信息"
)

from langchain_core.messages import HumanMessage

response = agent.invoke(
    {"messages":[HumanMessage("查询一下我购买的商品")]},
    context=UserContext(user_id="b1",role_id="user_b")
)

for message in response['messages']:
    message.pretty_print()
```

## State

```python
from langchain.agents import AgentState

class CallState(AgentState):
    """调用智能体时的智能体状态"""
    model_call_count: int

from langchain.tools import tool,ToolRuntime
from langgraph.types import Command
from langchain.messages import ToolMessage

@tool
def update_model_call_count(runtime:ToolRuntime):
    """记录模型被调用的次数"""
    count = runtime.state.get("model_call_count",0)
    print("模型被调用次数：",count)

    update = {
        "model_call_count":count+1,
        "messages":[
            ToolMessage(
                content="数据更新成功",
                tool_call_id = runtime.tool_call_id
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
    api_key = os.getenv("DASHSCOPE_API_KEY"),
    base_url = os.getenv("DASHSCOPE_BASE_URL")
)

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

config = {"configurable":{"thread_id":"1"}}

response = agent.invoke(
    {"messages":[HumanMessage(content="你好，我是张三")]},
    config
)

for message in response['messages']:
    message.pretty_print()
```

## 中间件

Middleware

> 信息脱敏

```python
from langchain.agents.middleware import PIIMiddleware

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
    api_key = os.getenv("DASHSCOPE_API_KEY"),
    base_url = os.getenv("DASHSCOPE_BASE_URL")
)

agent = create_agent(
    model,
    middleware=[pii_middleware_phone]
)

response = agent.invoke({
    "messages":[
        HumanMessage("我的手机号是13112345678，请记住这些信息")
    ]
})

for message in response['messages']:
    message.pretty_print()
```

> 人工审核

```python
from langchain_core.tools import tool

emails = [
    {
        "subject":"打个招呼",
        "content":"""
            你好，张三，
            我们好久没聊天啦，今天突然想起你。
            你最近怎么样？工作和生活一切顺利吗？

            期待你的回信，保重！
        """,
        "from":"lisi@163.com",
        "status":"未读"
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
def check_email()->str:
    """查看邮件"""
    return str(emails)

@tool
def send_email(to: str,subject: str,content: str):
    """回复邮件"""
    return f"邮件已发送给{to},主题:{subject},内容:{content}"

from langchain.agents.middleware import HumanInTheLoopMiddleware

email_middleware = HumanInTheLoopMiddleware(
    interrupt_on={
        "send_email":{
            "description":"请确认邮件内容",
            "allowed_decisions":["approve","reject"]
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
    api_key = os.getenv("DASHSCOPE_API_KEY"),
    base_url = os.getenv("DASHSCOPE_BASE_URL")
)

agent = create_agent(
    model,
    tools=[check_email,send_email],
    middleware=[email_middleware],
    checkpointer=InMemorySaver(),
    system_prompt="你是一个邮件助手"
)

config = {"configurable":{"thread_id":"1"}}

response = agent.invoke(
    {"messages":[HumanMessage("帮我查看邮件")]},
    config
)

for message in response['messages']:
    message.pretty_print()
    
response = agent.invoke(
    {"messages":[HumanMessage("帮我回复李四，问问他具体时间")]},
    config
)

for message in response['messages']:
    message.pretty_print()
    
from langgraph.types import Command

response = agent.invoke(
    Command(
        resume={
            "decisions":[
                {
                    "type":"reject",
                    "message":"语气太正式了，我和李四是好朋友，用更亲切的语气回复"
                }
            ]
        }
    ),
    config
)

for message in response['messages']:
    message.pretty_print()
    
    response = agent.invoke(
    Command(
        resume={
            "decisions":[
                {
                    "type":"approve"
                }
            ]
        }
    ),
    config
)

for message in response['messages']:
    message.pretty_print()
```

## MCP

1、安装环境

```
pip install langchain-mcp-adapters
pip install uv
```

2、查询当前时间

```python
import sys
import asyncio
from dotenv import load_dotenv
load_dotenv()

if sys.platform == "win32":
    if not isinstance(asyncio.get_event_loop_policy(),asyncio.WindowsProactorEventLoopPolicy):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    if "ipykernel" in sys.modules:
        sys.stderr = sys.__stderr__
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient(
    {
        "time":{
            "transport":"stdio",
            "command":"uvx",
            "args":[
                "mcp-server-time",
                "--local-timezone=Asia/Shanghai",
            ]
        }
    }
)

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
    api_key = os.getenv("DASHSCOPE_API_KEY"),
    base_url = os.getenv("DASHSCOPE_BASE_URL")
)

agent = create_agent(
    model,
    tools
)

from langchain_core.messages import HumanMessage

import os
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

model = init_chat_model(
    model="qwen3.5-plus",
    model_provider="openai",
    api_key = os.getenv("DASHSCOPE_API_KEY"),
    base_url = os.getenv("DASHSCOPE_BASE_URL")
)

agent = create_agent(
    model,
    tools
)
```

3、查询航班

```python
client = MultiServerMCPClient(
    {
        "kiwi-com-flight-search":{
            "transport":"http",
            "url":"https://mcp.kiwi.com"
        }
    }
)

tools = await client.get_tools()
for tool in tools:
    print(tool.name)
    
    model = init_chat_model(
    model="qwen3.5-plus",
    model_provider="openai",
    api_key = os.getenv("DASHSCOPE_API_KEY"),
    base_url = os.getenv("DASHSCOPE_BASE_URL")
)

agent = create_agent(
    model,
    tools,
    system_prompt="你是一名旅行智能助手，帮用户找到合适的航班"
)

response = await agent.ainvoke({
    "messages":[HumanMessage("帮我查询下周一深圳飞北京的航班")]
})

for message in response['messages']:
    message.pretty_print()
```