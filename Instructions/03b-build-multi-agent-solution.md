---
lab:
  title: 使用 Microsoft Foundry 开发多智能体解决方案
  description: 了解如何配置多个智能体以使用 Microsoft Foundry 智能体服务协同工作
---

# 开发多代理解决方案

在本练习中，你将创建一个项目，利用 Microsoft Foundry 智能体服务来编排多个 AI 智能体。 你将设计一个 AI 解决方案，用于协助处理票证会审。 连接的智能体将评估票证的优先级，为团队分配提出建议，并确定完成票证所需的工作量级别。 现在就开始吧！

> **提示**：本练习中使用的代码基于适用于 Python 的 Foundry SDK。 可以使用适用于 Microsoft .NET、JavaScript 和 Java 的 SDK 开发类似的解决方案。 有关详细信息，请参阅 [Foundry SDK 客户端库](https://learn.microsoft.com/azure/ai-foundry/how-to/develop/sdk-overview)。

完成此练习大约需要 30 分钟。

> **注意**：本练习中使用的一些技术处于预览版或积极开发阶段。 可能会遇到一些意想不到的行为、警告或错误。

## 创建 Foundry 项目

首先创建一个 Foundry 项目。

1. 在 Web 浏览器中，打开 [Foundry 门户](https://ai.azure.com) (`https://ai.azure.com`)，然后使用你的 Azure 凭据登录。 关闭首次登录时打开的任何使用技巧或快速入门窗格，如有必要，使用左上角的 Foundry**** 徽标导航到主页，类似下图所示（如果已打开“帮助”**** 面板，请关闭它）：

    ![Foundry 门户的屏幕截图。](./Media/ai-foundry-home.png)

    > **重要说明**：确保此实验室的 “新建 Foundry”切换开关为“关闭”状态。******

1. 在主页中，选择“**创建代理**”。
1. 当提示创建项目时，输入项目的有效名称并展开“**高级选项**”。
1. 为项目确认以下设置：
    - Foundry 资源****：Foundry 资源的有效名称**
    - **订阅**：Azure 订阅
    - **资源组**：*创建或选择资源组*
    - **区域**：选择推荐的任何 AI Foundry******\*

    > \* 某些 Azure AI 资源受区域模型配额约束。 如果稍后在练习中达到配额限制，你可能需要在不同的区域中创建另一个资源。

1. 选择“**创建**”并等待创建项目。
1. 如果出现提示，请使用“全局标准”或“标准”部署选项（具体取决于配额可用性）部署 gpt-4o 模型。********

    >**注意**：如果配额可用，则在创建智能体和项目时，可能会自动部署 GPT-4o 基础模型。

1. 项目创建完成后，会打开“智能体”操场。

1. 在左侧导航窗格中，选择“**概述**”以查看项目的主页；如下所示：

    ![Foundry 项目概述页面的屏幕截图。](./Media/ai-foundry-project.png)

1. 将 Foundry 项目终结点的值复制到记事本，因为你将使用这些值连接到客户端应用程序中的项目。****

## 创建 AI 代理客户端应用

现在，你已准备好创建一个用于定义代理和指令的客户端应用。 GitHub 存储库中提供了一些代码。

### 准备环境

1. 打开一个新的浏览器标签页（Foundry 门户在现有标签页中保持打开状态）。 然后在新选项卡中，浏览到 [Azure 门户](https://portal.azure.com)，网址为：`https://portal.azure.com`；如果出现提示，请使用 Azure 凭据登录。

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

1. 克隆完成后，输入以下命令，将工作目录更改为包含代码文件的文件夹，并列出所有代码文件。

    ```
   cd ai-agents/Labfiles/03b-build-multi-agent-solution/Python
   ls -a -l
    ```

    提供的文件包含应用程序代码和配置设置文件。

### 配置应用程序设置

1. 在 Cloud Shell 命令行窗格中，输入以下命令以安装将要使用的库：

    ```
   python -m venv labenv
   ./labenv/bin/Activate.ps1
   pip install -r requirements.txt azure-ai-projects azure-ai-agents
    ```

1. 输入以下命令以编辑所提供的配置文件：

    ```
   code .env
    ```

    该文件已在代码编辑器中打开。

1. 在代码文件中，将 your_project_endpoint**** 占位符替换为项目的终结点（从 Foundry 门户中的项目“概述”**** 页复制），并将 your_model_deployment**** 占位符替换为分配给 gpt-4o 模型部署的名称（默认为 `gpt-4o`）。

1. 替换占位符后，使用 **Ctrl+S** 命令保存更改，然后使用 **Ctrl+Q** 命令关闭代码编辑器，同时使 Cloud Shell 命令行保持打开状态。

### 创建 AI 代理

现在，你已准备好为多代理解决方案创建代理！ 现在就开始吧！

1. 输入以下命令以编辑 agent_triage.py**** 文件：

    ```
   code agent_triage.py
    ```

1. 查看文件中的代码，注意其中包含每个代理的名称和指令字符串。

1. 查找注释 **Add references**，并添加以下代码，以导入你将需要的类：

    ```python
   # Add references
   from azure.ai.agents import AgentsClient
   from azure.ai.agents.models import ConnectedAgentTool, MessageRole, ListSortOrder, ToolSet, FunctionTool
   from azure.identity import DefaultAzureCredential
    ```

1. 请注意，已提供用于从环境变量加载项目终结点和模型名称的代码。

1. 找到注释“连接到代理客户端”**** 并添加以下代码，创建一个连接到项目的 AgentsClient：

    ```python
   # Connect to the agents client
   agents_client = AgentsClient(
        endpoint=project_endpoint,
        credential=DefaultAzureCredential(
            exclude_environment_credential=True, 
            exclude_managed_identity_credential=True
        ),
   )
    ```

    现在，你将添加代码以使用 AgentsClient 创建多个代理，每个代理都具有在处理支持工单时要扮演的特定角色。

    > **提示**：添加后续代码时，请务必在 `using agents_client:` 语句下保持正确的缩进级别。

1. 找到注释“创建代理以确定支持工单的优先级”****，并输入以下代码（注意保留正确的缩进级别）：

    ```python
   # Create an agent to prioritize support tickets
   priority_agent_name = "priority_agent"
   priority_agent_instructions = """
   Assess how urgent a ticket is based on its description.

   Respond with one of the following levels:
   - High: User-facing or blocking issues
   - Medium: Time-sensitive but not breaking anything
   - Low: Cosmetic or non-urgent tasks

   Only output the urgency level and a very brief explanation.
   """

   priority_agent = agents_client.create_agent(
        model=model_deployment,
        name=priority_agent_name,
        instructions=priority_agent_instructions
   )
    ```

1. 找到注释“创建代理以将工单分配给相应的团队”****，并输入以下代码：

    ```python
   # Create an agent to assign tickets to the appropriate team
   team_agent_name = "team_agent"
   team_agent_instructions = """
   Decide which team should own each ticket.

   Choose from the following teams:
   - Frontend
   - Backend
   - Infrastructure
   - Marketing

   Base your answer on the content of the ticket. Respond with the team name and a very brief explanation.
   """

   team_agent = agents_client.create_agent(
        model=model_deployment,
        name=team_agent_name,
        instructions=team_agent_instructions
   )
    ```

1. 找到注释“创建代理以估算支持工单的工作量”****，并输入以下代码：

    ```python
   # Create an agent to estimate effort for a support ticket
   effort_agent_name = "effort_agent"
   effort_agent_instructions = """
   Estimate how much work each ticket will require.

   Use the following scale:
   - Small: Can be completed in a day
   - Medium: 2-3 days of work
   - Large: Multi-day or cross-team effort

   Base your estimate on the complexity implied by the ticket. Respond with the effort level and a brief justification.
   """

   effort_agent = agents_client.create_agent(
        model=model_deployment,
        name=effort_agent_name,
        instructions=effort_agent_instructions
   )
    ```

    到目前为止，你已经创建了三个代理；每个代理在会审支持工单时都扮演着特定的角色。 现在，我们为每个代理创建 ConnectedAgentTool 对象，以便其他代理可以使用它们。

1. 找到注释“为支持代理创建连接的代理工具”****，并输入以下代码：

    ```python
   # Create connected agent tools for the support agents
   priority_agent_tool = ConnectedAgentTool(
        id=priority_agent.id, 
        name=priority_agent_name, 
        description="Assess the priority of a ticket"
   )
    
   team_agent_tool = ConnectedAgentTool(
        id=team_agent.id, 
        name=team_agent_name, 
        description="Determines which team should take the ticket"
   )
    
   effort_agent_tool = ConnectedAgentTool(
        id=effort_agent.id, 
        name=effort_agent_name, 
        description="Determines the effort required to complete the ticket"
   )
    ```

    现在，你已准备好创建一个主代理，它将根据需要使用连接的代理协调工单会审过程。

1. 找到注释“创建代理以使用连接的代理对支持工单处理进行会审”****，并输入以下代码：

    ```python
   # Create an agent to triage support ticket processing by using connected agents
   triage_agent_name = "triage-agent"
   triage_agent_instructions = """
   Triage the given ticket. Use the connected tools to determine the ticket's priority, 
   which team it should be assigned to, and how much effort it may take.
   """

   triage_agent = agents_client.create_agent(
        model=model_deployment,
        name=triage_agent_name,
        instructions=triage_agent_instructions,
        tools=[
            priority_agent_tool.definitions[0],
            team_agent_tool.definitions[0],
            effort_agent_tool.definitions[0]
        ]
   )
    ```

    现在，你已经定义了一个主代理，可以向它提交提示，让它使用其他代理来会审支持问题。

1. 找到注释“使用代理会审支持问题”****，并输入以下代码：

    ```python
   # Use the agents to triage a support issue
   print("Creating agent thread.")
   thread = agents_client.threads.create()  

   # Create the ticket prompt
   prompt = input("\nWhat's the support problem you need to resolve?: ")
    
   # Send a prompt to the agent
   message = agents_client.messages.create(
        thread_id=thread.id,
        role=MessageRole.USER,
        content=prompt,
   )   
    
   # Run the thread usng the primary agent
   print("\nProcessing agent thread. Please wait.")
   run = agents_client.runs.create_and_process(thread_id=thread.id, agent_id=triage_agent.id)
        
   if run.status == "failed":
        print(f"Run failed: {run.last_error}")

   # Fetch and display messages
   messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
   for message in messages:
        if message.text_messages:
            last_msg = message.text_messages[-1]
            print(f"{message.role}:\n{last_msg.text.value}\n")
   
    ```

1. 找到注释“清理”****，并输入以下代码以删除不再需要的代理：

    ```python
   # Clean up
   print("Cleaning up agents:")
   agents_client.delete_agent(triage_agent.id)
   print("Deleted triage agent.")
   agents_client.delete_agent(priority_agent.id)
   print("Deleted priority agent.")
   agents_client.delete_agent(team_agent.id)
   print("Deleted team agent.")
   agents_client.delete_agent(effort_agent.id)
   print("Deleted effort agent.")
    ```
    

1. 使用 **Ctrl+S** 命令保存对代码文件的更改。 可以保持打开状态（如果需要编辑代码以修复任何错误），或使用 **CTRL+Q** 命令关闭代码编辑器，同时保持 Cloud shell 命令行打开状态。

### 登录到 Azure 并运行应用

现在，可随时运行代码并观看 AI 代理进行协作。

1. 在 Cloud Shell 命令行窗格中，输入以下命令以登录到 Azure。

    ```
   az login
    ```

    **<font color="red">必须登录到 Azure - 即使 Cloud Shell 会话已经过身份验证。</font>**

    > **备注**：在大多数情况下，仅使用 *az login* 就足够了。 但是，如果在多个租户中有订阅，则可能需要使用 *--tenant* 参数指定租户。 有关详细信息，请参阅[使用 Azure CLI 以交互方式登录到 Azure](https://learn.microsoft.com/cli/azure/authenticate-azure-cli-interactively)。

1. 出现提示时，请按照说明在新选项卡中打开登录页，并输入提供的验证码和 Azure 凭据。 然后在命令行中完成登录过程，并在出现提示时选择包含 Foundry 中心的订阅。

1. 登录后，输入以下命令来运行应用程序：

    ```
   python agent_triage.py
    ```

1. 输入提示，例如 `Users can't reset their password from the mobile app.`

    代理处理提示后，你应会看到类似于以下内容的一些输出：

    ```output
    Creating agent thread.
    Processing agent thread. Please wait.

    MessageRole.USER:
    Users can't reset their password from the mobile app.

    MessageRole.AGENT:
    ### Ticket Assessment

    - **Priority:** High — This issue blocks users from resetting their passwords, limiting access to their accounts.
    - **Assigned Team:** Frontend Team — The problem lies in the mobile app's user interface or functionality.
    - **Effort Required:** Medium — Resolving this problem involves identifying the root cause, potentially updating the mobile app functionality, reviewing API/backend integration, and testing to ensure compatibility across Android/iOS platforms.

    Cleaning up agents:
    Deleted triage agent.
    Deleted priority agent.
    Deleted team agent.
    Deleted effort agent.
    ```

    可以尝试使用其他票证方案来修改提示，以观察智能体的协作方式。 例如，“调查搜索终结点偶发性的 502 错误”。

## 清理

如果已完成对 Azure AI 代理服务的探索，则应删除在本练习中创建的资源，以避免产生不必要的 Azure 成本。

1. 返回到包含 Azure 门户的浏览器选项卡（或在新的浏览器选项卡中重新打开 [Azure 门户](https://portal.azure.com)，网址为：`https://portal.azure.com`），查看已在其中部署本练习中使用的资源的资源组内容。

1. 在工具栏中，选择“删除资源组”****。

1. 输入资源组名称，并确认要删除该资源组。
