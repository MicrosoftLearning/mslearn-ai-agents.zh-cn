---
lab:
  title: 将 AI 智能体连接到远程 MCP 服务器
  description: 了解如何将模型上下文协议工具与 AI 智能体集成
---

# 使用模型上下文协议 (MCP) 将 AI 智能体连接到工具

在本练习中，你将生成连接到云托管 MCP 服务器的智能体。 该智能体将利用 AI 支持的搜索，帮助开发人员从 Microsoft 官方文档中获取准确、实时的答案。 这对于构建能够为开发人员提供关于 Azure、.NET 和 Microsoft 365 等工具的最新指导的助手非常有用。 该智能体将使用提供的 `microsoft_docs_search` 工具查询文档，并返回相关结果。

> **提示**：本练习中使用的代码基于 Azure AI 代理服务 MCP 支持示例存储库。 如需了解更多信息，请参阅 [Azure OpenAI 演示](https://github.com/retkowsky/Azure-OpenAI-demos/blob/main/Azure%20Agent%20Service/9%20Azure%20AI%20Agent%20service%20-%20MCP%20support.ipynb)或访问[连接模型上下文协议服务器](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/model-context-protocol)页面。

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

### 将 Azure AI 智能体连接到远程 MCP 服务器

在此任务中，你将连接到远程 MCP 服务器、准备 AI 智能体，并运行用户提示。

1. 找到注释“添加引用”****，并添加以下代码以导入类：

    ```python
   # Add references
   from azure.identity import DefaultAzureCredential
   from azure.ai.agents import AgentsClient
   from azure.ai.agents.models import McpTool
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

1. 在注释“初始化智能体 MCP 工具”下方，添加以下代码****：

    ```python
   # Initialize agent MCP tool
   mcp_tool = McpTool(
       server_label=mcp_server_label,
       server_url=mcp_server_url,
   )
    ```

    此代码将连接到 Microsft Learn Docs 远程 MCP 服务器。 这是一项云托管服务，使客户端能够直接从 Microsoft 官方文档中获取可信且最新的信息。

1. 在注释“使用 MCP 工具定义创建新智能体”下方，添加以下代码****：

    ```python
   # Create a new agent with the mcp tool definitions
   agent = agents_client.create_agent(
       model=model_deployment,
       name="my-mcp-agent",
       instructions="""
        You have access to an MCP server called `microsoft.docs.mcp` - this tool allows you to 
        search through Microsoft's latest official documentation. Use the available MCP tools 
        to answer questions and perform tasks.""",
       tools=mcp_tool.definitions,
   )
    ```

    在这段代码中，你需要为智能体提供指令和 MCO 工具定义。

1. 找到注释“创建通信线程”，并添加以下代码****：

    ```python
   # Create thread for communication
   thread = agents_client.threads.create()
   print(f"Created thread, ID: {thread.id}")
    ```

1. 找到注释“在该线程上创建消息”，并添加以下代码****：

    ```python
   # Create a message on the thread
   message = agents_client.messages.create(
       thread_id=thread.id,
       role="user",
       content="Give me the Azure CLI commands to create an Azure Container App with a managed identity.",
   )
   print(f"Created message, ID: {message.id}")
    ```

1. 在注释“更新 MCP 工具标头”下方，添加以下代码****：

    ```python
   # Update mcp tool headers
   mcp_tool.update_headers("SuperSecret", "123456")
    ```

1. 找到注释“设置审批模式”并添加以下代码****：

    ```python
   # Set approval mode
   mcp_tool.set_approval_mode("never")
    ```

1. 找到注释“使用 MCP 工具在线程中创建和处理智能体运行”****，并添加以下代码：

    ```python
   # Create and process agent run in thread with MCP tools
   run = agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id, tool_resources=mcp_tool.resources)
   print(f"Created run, ID: {run.id}")
    ```
    
    AI 智能体会自动调用连接的 MCP 工具来处理提示请求。 为了说明此过程，注释“显示运行步骤和工具调用”下的代码将输出来自 MCP 服务器的任何调用工具信息****。

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

    部分输出如下所示：

    ```
    Created agent, ID: <<agent-id>>
    MCP Server: mslearn at https://learn.microsoft.com/api/mcp
    Created thread, ID: <<thread-id>>
    Created message, ID: <<message-id>>
    Created run, ID: <<run-id>>
    Run completed with status: RunStatus.COMPLETED
    Step <<step1-id>> status: completed

    Step <<step2-id>> status: completed
    MCP Tool calls:
        Tool Call ID: <<tool-call-id>>
        Type: mcp
        Type: microsoft_docs_search


    Conversation:
    --------------------------------------------------
    ASSISTANT: You can use Azure CLI to create an Azure Container App with a managed identity (either system-assigned or user-assigned). Below are the relevant commands and workflow:

    ---

    ### **1. Create a Resource Group**
    ```azurecli
    az group create --name myResourceGroup --location eastus
    ```

    {{continued...}}

    通过遵循这些步骤，你可以部署一个带有系统分配或用户分配的托管标识的 Azure 容器应用，实现与其他 Azure 服务的无缝集成。
    --------------------------------------------------
    用户：向我提供 Azure CLI 命令，以创建具有托管标识的 Azure 容器应用。
    --------------------------------------------------
    已删除的智能体
    ```

    Notice that the agent was able to invoke the MCP tool `microsoft_docs_search` automatically to fulfill the request.

## Clean up

Now that you've finished the exercise, you should delete the cloud resources you've created to avoid unnecessary resource usage.

1. Open the [Azure portal](https://portal.azure.com) at `https://portal.azure.com` and view the contents of the resource group where you deployed the hub resources used in this exercise.
1. On the toolbar, select **Delete resource group**.
1. Enter the resource group name and confirm that you want to delete it.
