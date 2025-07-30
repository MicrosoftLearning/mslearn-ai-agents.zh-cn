---
lab:
  title: 使用 MCP 将 AI 智能体连接到工具
  description: 了解如何将模型上下文协议与 AI 智能体集成
---

# 使用模型上下文协议 (MCP) 将 AI 智能体连接到工具

在本练习中，你将创建一个智能体，该智能体可以连接到 MCP 服务器，并自动发现可调用的函数。

你将为一家化妆品零售商构建一个简单的库存评估智能体。 通过使用 MCP 服务器，智能体将能够检索库存相关信息，并提供补货或清货建议。

> **提示**：本练习中使用的代码基于适用于 Python 的 Azure AI Foundry 和 MCP SDK。 可以使用适用于 Microsoft .NET 的 SDK 开发类似解决方案。 有关详细信息，请参阅 [Azure AI Foundry SDK 客户端库](https://learn.microsoft.com/azure/ai-foundry/how-to/develop/sdk-overview)和 [MCP C# SDK](https://modelcontextprotocol.github.io/csharp-sdk/api/ModelContextProtocol.html)。

完成此练习大约需要 30 分钟。

> **注意**：本练习中使用的一些技术处于预览版或积极开发阶段。 可能会遇到一些意想不到的行为、警告或错误。

## 创建 Azure AI Foundry 项目

让我们首先创建 Azure AI Foundry 项目。

1. 在 Web 浏览器中打开 [Azure AI Foundry 门户](https://ai.azure.com)，网址为：`https://ai.azure.com`，然后使用 Azure 凭据登录。 关闭首次登录时打开的任何使用技巧或快速入门窗格，如有必要，使用左上角的 **Azure AI Foundry** 徽标导航到主页，类似下图所示（若已打开**帮助**面板，请关闭）：

    ![Azure AI Foundry 门户的屏幕截图。](./Media/ai-foundry-home.png)

1. 在主页中，选择“**创建代理**”。
1. 当提示创建项目时，输入项目的有效名称并展开“**高级选项**”。
1. 为项目确认以下设置：
    - **Azure AI Foundry 资源**：*Azure AI Foundry 资源的有效名称*
    - **订阅**：Azure 订阅
    - **资源组**：*创建或选择资源组*
    - **区域**：*选择任何**支持 AI 服务的位置***\*

    > \* 某些 Azure AI 资源受区域模型配额约束。 如果稍后在练习中达到配额限制，你可能需要在不同的区域中创建另一个资源。

1. 选择“**创建**”并等待创建项目。
1. 如果出现提示，请使用“全局标准”或“标准”部署选项（具体取决于配额可用性）部署 gpt-4o 模型。********

    >**注意**：如果配额可用，则在创建智能体和项目时，可能会自动部署 GPT-4o 基础模型。

1. 项目创建完成后，会打开“智能体”操场。

1. 在左侧导航窗格中，选择“**概述**”以查看项目的主页；如下所示：

    ![Azure AI Foundry 项目概述页面的屏幕截图。](./Media/ai-foundry-project.png)

1. 将 **Azure AI Foundry 项目终结点**值复制到记事本，因为你将使用它连接到客户端应用程序中的项目。

## 开发使用 MCP 函数工具的智能体

现在你已经在 AI Foundry 中创建了项目，接下来我们将开发一个应用，将 AI 智能体与 MCP 服务器集成起来。

### 克隆包含应用程序代码的存储库

1. 打开新的浏览器选项卡（使 Azure AI Foundry 门户在现有选项卡中保持打开状态）。 然后在新选项卡中，浏览到 [Azure 门户](https://portal.azure.com)，网址为：`https://portal.azure.com`；如果出现提示，请使用 Azure 凭据登录。

    关闭任何欢迎通知以查看 Azure 门户主页。

1. 使用页面顶部搜索栏右侧的 **[\>_]** 按钮在 Azure 门户中新建 Cloud Shell，选择订阅中不含存储的 ***PowerShell*** 环境。

    在 Azure 门户底部的窗格中，Cloud Shell 提供命令行接口。 可以调整此窗格的大小或最大化此窗格，以便更易于使用。

    > **备注**：如果以前创建了使用 *Bash* 环境的 Cloud Shell，请将其切换到 ***PowerShell***。

1. 在 Cloud Shell 工具栏的“**设置**”菜单中，选择“**转到经典版本**”（这是使用代码编辑器所必需的）。

    **<font color="red">在继续作之前，请确保已切换到 Cloud Shell 的经典版本。</font>**

1. 在 Cloud Shell 窗格中，输入以下命令以克隆包含此练习代码文件的 GitHub 存储库（键入命令，或将其复制到剪贴板后，在命令行中右键单击并粘贴为纯文本）：

    ```
   rm -r ai-agents -f
   git clone https://github.com/MicrosoftLearning/mslearn-ai-agents ai-agents
    ```

    > **提示**：在 Cloudshell 中时输入命令时，输出可能会占用大量屏幕缓冲区，当前行的光标可能会被遮挡。 可以通过输入 `cls` 命令来清除屏幕，以便更轻松地专注于每项任务。

1. 输入以下命令，将工作目录更改为包含代码文件的文件夹，并列出所有文件。

    ```
   cd ai-agents/Labfiles/07-use-agent-tools-with-mcp/Python
   ls -a -l
    ```

    提供的文件包括客户端和服务器应用程序代码。 模型上下文协议提供了一种将 AI 模型连接到不同数据源和工具的标准化方式。 我们将 `client.py` 和 `server.py` 分开，以保持智能体逻辑与工具定义的模块化，并模拟真实的体系结构。 
    
    `server.py` 定义了智能体可使用的工具，模拟后端服务或业务逻辑。 
    `client.py` 负责设置 AI 智能体、处理用户提示，并在需要时调用这些工具。

### 配置应用程序设置

1. 在 Cloud Shell 命令行窗格中，输入以下命令以安装将要使用的库：

    ```
   python -m venv labenv
   ./labenv/bin/Activate.ps1
   pip install -r requirements.txt azure-ai-projects mcp
    ```

    >**备注：** 可以忽略库安装过程中显示的任何警告或错误消息。

1. 输入以下命令以编辑已提供的配置文件：

    ```
   code .env
    ```

    该文件已在代码编辑器中打开。

1. 在代码文件中，将 your_project_endpoint**** 占位符替换为项目的终结点（从 Azure AI Foundry 门户的项目“概述”**** 页复制），并确保将 MODEL_DEPLOYMENT_NAME 变量设置为模型部署名称（应为 gpt-4o**）。

1. 替换占位符后，使用 **Ctrl+S** 命令保存更改，然后使用 **Ctrl+Q** 命令关闭代码编辑器，同时使 Cloud Shell 命令行保持打开状态。

### 定义函数工具

1. 输入以下命令以编辑为函数代码提供的代码文件：

    ```
   code server.py
    ```

    在此代码文件中，你将定义一些工具，供智能体用于模拟零售商店的后端服务。 

1. 找到注释“添加库存检查工具”**** 并添加以下代码：

    ```python
   # Add an inventory check tool
   @mcp.tool()
   def get_inventory_levels() -> dict:
        """Returns current inventory for all products."""
        return {
            "Moisturizer": 6,
            "Shampoo": 8,
            "Body Spray": 28,
            "Hair Gel": 5, 
            "Lip Balm": 12,
            "Skin Serum": 9,
            "Cleanser": 30,
            "Conditioner": 3,
            "Setting Powder": 17,
            "Dry Shampoo": 45
        }
    ```

    此字典表示一个示例库存。 `@mcp.tool()` 批注使 LLM 能够发现你的函数。 

1. 找到注释“添加每周销量工具”**** 并添加以下代码：

    ```python
   # Add a weekly sales tool
   @mcp.tool()
   def get_weekly_sales() -> dict:
        """Returns number of units sold last week."""
        return {
            "Moisturizer": 22,
            "Shampoo": 18,
            "Body Spray": 3,
            "Hair Gel": 2,
            "Lip Balm": 14,
            "Skin Serum": 19,
            "Cleanser": 4,
            "Conditioner": 1,
            "Setting Powder": 13,
            "Dry Shampoo": 17
        }
    ```

1. 保存文件 (*CTRL+S*)。

### 将 MCP 工具连接到智能体

1. 输入以下命令以开始编辑代理代码。

    ```
   code client.py
    ```

    在此文件中，你将准备 AI 智能体、接受用户提示并调用函数工具。

    > **提示**：向代码文件添加代码时，请务必保持正确的缩进。

1. 查看现有函数 `connect_to_server`。 此函数用于启动服务器并检索可用的工具。 文件的其余部分包含了注释，用于提示你在相应位置添加必要的代码来实现库存智能体。

1. 找到注释“添加引用”****，并添加以下代码以导入类：

    ```python
   # Add references
   from mcp import ClientSession, StdioServerParameters
   from mcp.client.stdio import stdio_client
   from azure.ai.agents import AgentsClient
   from azure.ai.agents.models import FunctionTool, MessageRole, ListSortOrder
   from azure.identity import DefaultAzureCredential
    ```

1. 找到注释“连接到智能体客户端”****，并添加以下代码，通过当前的 Azure 凭据连接到 Azure AI 项目。

    ```python
   # Connect to the agents client
   agents_client = AgentsClient(
        endpoint=project_endpoint,
        credential=DefaultAzureCredential(
            exclude_environment_credential=True,
            exclude_managed_identity_credential=True
        )
   )
    ```

1. 在注释“列出服务器上可用的工具”**** 下，添加以下代码：

    ```python
   # List tools available on the server
   response = await session.list_tools()
   tools = response.tools
    ```

1. 在注释“为每个工具生成一个函数”**** 下，添加以下代码：

    ```python
   # Build a function for each tool
   def make_tool_func(tool_name):
        async def tool_func(**kwargs):
            result = await session.call_tool(tool_name, kwargs)
            return result
        
        tool_func.__name__ = tool_name
        return tool_func

   functions_dict = {tool.name: make_tool_func(tool.name) for tool in tools}
   mcp_function_tool = FunctionTool(functions=list(functions_dict.values()))
    ```

    这段代码会动态包装 MCP 服务器中可用的工具，使 AI 智能体能够调用它们。 每个工具都会被转换为一个异步函数，然后打包进一个 `FunctionTool`，供智能体使用。

1. 找到注释“创建智能体”**** 并添加以下代码：

    ```python
   # Create the agent
   agent = agents_client.create_agent(
        model=model_deployment,
        name="inventory-agent",
        instructions="""
        You are an inventory assistant. Here are some general guidelines:
        - Recommend restock if item inventory < 10  and weekly sales > 15
        - Recommend clearance if item inventory > 20 and weekly sales < 5
        """,
        tools=mcp_function_tool.definitions
   )
    ```

1. 找到注释“启用自动函数调用”**** 并添加以下代码：

    ```python
   # Enable auto function calling
   agents_client.enable_auto_function_calls(tools=mcp_function_tool)
    ```

1. 在注释“为聊天会话创建线程”**** 下，添加以下代码：

    ```python
   # Create a thread for the chat session
   thread = agents_client.threads.create()
    ```

1. 找到注释“调用提示”**** 并添加以下代码：

    ```python
   # Invoke the prompt
   message = agents_client.messages.create(
        thread_id=thread.id,
        role=MessageRole.USER,
        content=user_input,
   )
   run = agents_client.runs.create(thread_id=thread.id, agent_id=agent.id)
    ```

1. 找到注释“检索匹配的函数工具”**** 并添加以下代码：

    ```python
   # Retrieve the matching function tool
   function_name = tool_call.function.name
   args_json = tool_call.function.arguments
   kwargs = json.loads(args_json)
   required_function = functions_dict.get(function_name)

   # Invoke the function
   output = await required_function(**kwargs)
    ```

    这段代码利用来自智能体线程中工具调用的信息。 它会提取函数名称和参数，并用于调用匹配的函数。

1. 在注释“追加输出文本”**** 下，添加以下代码：

    ```python
   # Append the output text
   tool_outputs.append({
        "tool_call_id": tool_call.id,
        "output": output.content[0].text,
   })
    ```

1. 在注释“提交工具调用输出”**** 下，添加以下代码：

    ```python
   # Submit the tool call output
   agents_client.runs.submit_tool_outputs(thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs)
    ```

    这段代码会向智能体线程发出信号，指出所需操作已完成，并更新工具调用输出。

1. 找到注释“显示响应”**** 并添加以下代码：

    ```python
   # Display the response
   messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
   for message in messages:
        if message.text_messages:
            last_msg = message.text_messages[-1]
            print(f"{message.role}:\n{last_msg.text.value}\n")
    ```

1. 完成后保存代码文件 (*CTRL+S*)。 还可以关闭代码编辑器 (*CTRL+Q*)；不过，在需要对添加的代码进行任何编辑时，可能需要将其保持打开状态。 在任一情况下，将 Cloud Shell 命令行窗格保持打开状态。

### 登录到 Azure 并运行应用

1. 在 Cloud Shell 命令行窗格中，输入以下命令以登录到 Azure。

    ```
   az login
    ```

    **<font color="red">必须登录到 Azure - 即使 Cloud Shell 会话已经过身份验证。</font>**

    > **备注**：在大多数情况下，仅使用 *az login* 就足够了。 但是，如果在多个租户中有订阅，则可能需要使用 *--tenant* 参数指定租户。 有关详细信息，请参阅[使用 Azure CLI 以交互方式登录到 Azure](https://learn.microsoft.com/cli/azure/authenticate-azure-cli-interactively)。
    
1. 出现提示时，请按照说明在新选项卡中打开登录页，并输入提供的验证码和 Azure 凭据。 然后在命令行中完成登录过程，并在出现提示时选择包含 Azure AI Foundry 中心的订阅。

1. 登录后，输入以下命令来运行应用程序：

    ```
   python client.py
    ```

1. 出现提示时，输入查询，例如：

    ```
   What are the current inventory levels?
    ```

    > **提示**：如果应用因超出速率限制而失败。 等待几秒钟，然后重试。 如果订阅配额不足，模型可能无法响应。

    部分输出如下所示：

    ```
    MessageRole.AGENT:
    Here are the current inventory levels:

    - Moisturizer: 6
    - Shampoo: 8
    - Body Spray: 28
    - Hair Gel: 5
    - Lip Balm: 12
    - Skin Serum: 9
    - Cleanser: 30
    - Conditioner: 3
    - Setting Powder: 17
    - Dry Shampoo: 45
    ```

1. 如果需要，可以继续对话。 线程是*有状态的*，因此会保留对话历史记录，这意味着代理具有每个响应的完整上下文。 

    尝试输入提示，例如：

    ```
   Are there any products that should be restocked?
    ```

    ```
   Which products would you recommend for clearance?
    ```

    ```
   What are the best sellers this week?
    ```

    完成后，请输入`quit`。

## 清理

完成练习后，应删除已创建的云资源，以避免不必要的资源使用。

1. 打开 [Azure 门户](https://portal.azure.com)，网址为：`https://portal.azure.com`，并查看在其中部署了本练习中使用的中心资源的资源组内容。
1. 在工具栏中，选择“删除资源组”****。
1. 输入资源组名称，并确认要删除该资源组。
