---
lab:
  title: 使用 Azure AI Foundry 开发多代理解决方案
  description: 了解如何配置多个代理以使用 Azure AI Foundry 代理服务协同工作
---

# 开发多代理解决方案

在本练习中，你将创建一个项目，利用 Azure AI Foundry 代理服务来编排多个 AI 代理的协作与执行。 在本练习中，你将创建一个任务主代理，负责引导一组角色穿越地牢。 这个小队由代表战士、治疗者和侦察兵的互联 AI 代理组成。 Quest master 代理接收用户提供的应用场景，并将任务相应地分配给小队成员。 现在就开始吧！

完成此练习大约需要 30 分钟。

## 在 Azure AI Foundry 项目中部署模型

让我们首先在 Azure AI Foundry 项目中部署模型。

1. 在 Web 浏览器中打开 [Azure AI Foundry 门户](https://ai.azure.com)，网址为：`https://ai.azure.com`，然后使用 Azure 凭据登录。 关闭首次登录时打开的任何使用技巧或快速入门窗格，如有必要，使用左上角的 **Azure AI Foundry** 徽标导航到主页，类似下图所示（若已打开**帮助**面板，请关闭）：

    ![Azure AI Foundry 门户的屏幕截图。](./Media/ai-foundry-home.png)

1. 在主页的“**浏览模型和功能**”部分中，搜索 `gpt-4o` 模型；我们将在项目中使用它。
1. 在搜索结果中，选择 **gpt-4o** 模型以查看其详细信息，然后在模型的页面顶部，选择“**使用此模型**”。
1. 当提示创建项目时，输入项目的有效名称并展开“**高级选项**”。
1. 为项目确认以下设置：
    - **Azure AI Foundry 资源**：*Azure AI Foundry 资源的有效名称*
    - **订阅**：Azure 订阅
    - **资源组**：*创建或选择资源组*
    - **区域**：*选择任何**支持 AI 服务的位置***\*

    > \* 某些 Azure AI 资源受区域模型配额约束。 如果稍后在练习中达到配额限制，你可能需要在不同的区域中创建另一个资源。

1. 选择“**创建**”并等待项目（包括所选的 gpt-4 模型部署）创建。
1. 创建项目后，将自动打开聊天操场。

    > **备注**：对于本练习，此模型的默认 TPM 设置可能太低。 减少 TPM 有助于避免过度使用正在使用的订阅中可用的配额。 

1. 在左侧导航窗格中，选择“**模型和终结点**”，然后选择 **gpt-4o** 部署。

1. 选择“**编辑**”，然后增加“**每分钟令牌速率限制**”

   > **备注**：40,000 TPM 足以应对本练习使用的数据。 如果可用配额低于上述 50,000 TPM，你仍然可完成本练习，但超过速率限制时可能需要等待并重新提交提示。

1. 在左侧导航窗格中，选择“**概述**”以查看项目的主页；如下所示：

    > **备注**：如果显示“*权限不足*”*错误，请使用“**修复我**”按钮解决此问题。

    ![Azure AI Foundry 项目概述页面的屏幕截图。](./Media/ai-foundry-project.png)

1. 将 **Azure AI Foundry 项目终结点**值复制到记事本，因为你将使用它连接到客户端应用程序中的项目。

## 创建 AI 代理客户端应用

现在，你已准备好创建一个用于定义代理和指令的客户端应用。 GitHub 存储库中提供了一些代码。

### 准备环境

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

1. 克隆完成后，输入以下命令，将工作目录更改为包含代码文件的文件夹，并列出所有代码文件。

    ```
   cd ai-agents/Labfiles/06-build-multi-agent-solution/Python
   ls -a -l
    ```

    提供的文件包含应用程序代码和配置设置文件。

### 配置应用程序设置

1. 在 Cloud Shell 命令行窗格中，输入以下命令以安装将要使用的库：

    ```
   python -m venv labenv
   ./labenv/bin/Activate.ps1
   pip install -r requirements.txt azure-ai-projects
    ```

1. 输入以下命令以编辑所提供的配置文件：

    ```
   code .env
    ```

    该文件已在代码编辑器中打开。

1. 在代码文件中，将 **your_project_endpoint** 占位符替换为项目的终结点（从 Azure AI Foundry 门户中的项目“**概述**”页复制而来），并将 **your_model_deployment** 占位符替换为 分配给 gpt-4 模型部署的名称。

1. 替换占位符后，使用 **Ctrl+S** 命令保存更改，然后使用 **Ctrl+Q** 命令关闭代码编辑器，同时使 Cloud Shell 命令行保持打开状态。

### 创建 AI 代理

现在，你已准备好为多代理解决方案创建代理！ 现在就开始吧！

1. 输入以下命令以编辑 **agent_quest.py** 文件：

    ```
   code agent_quest.py
    ```

1. 查看文件中的代码，注意其中包含每个代理的名称和指令字符串。

1. 查找注释 **Add references**，并添加以下代码，以导入你将需要的类：

    ```python
    # Add references
    from azure.ai.agents import AgentsClient
    from azure.ai.agents.models import ConnectedAgentTool, MessageRole, ListSortOrder
    from azure.identity import DefaultAzureCredential
    ```

1. 查找注释 **创建 Azure AI 代理服务上的治疗者代理**，并添加以下代码以创建 Azure AI 代理。

    ```python
    # Create the healer agent on the Azure AI agent service
    healer_agent = agents_client.create_agent(
        model=model_deployment,
        name=healer_agent_name,
        instructions=healer_instructions
    )
    ```

    此代码在 Azure AI 代理客户端中创建代理定义。

1. 找到注释**为治疗者代理创建连接的代理工具**，并添加以下代码：

    ```python
    # Create a connected agent tool for the healer agent
    healer_agent_tool = ConnectedAgentTool(
        id=healer_agent.id, 
        name=healer_agent_name, 
        description="Responsible for healing party members and addressing injuries."
    )
    ```

    现在，创建其他队成员代理。

1. 在注释**创建侦察兵代理和连接工具**下，添加以下代码：
    
    ```python
    # Create the scout agent and connected tool
    scout_agent = agents_client.create_agent(
        model=model_deployment,
        name=scout_agent_name,
        instructions=scout_instructions
    )
    scout_agent_tool = ConnectedAgentTool(
        id=scout_agent.id, 
        name=scout_agent_name, 
        description="Goes ahead of the main party to perform reconnaissance."
    )
    ```

1. 在注释**创建战士代理和连接工具**下，添加以下代码：
    
    ```python
    # Create the warrior agent and connected tool
    warrior_agent = agents_client.create_agent(
        model=model_deployment,
        name=warrior_agent_name,
        instructions=warrior_instructions
    )
    warrior_agent_tool = ConnectedAgentTool(
        id=warrior_agent.id, 
        name=warrior_agent_name, 
        description="Responds to combat or physical challenges."
    )
    ```


1. 在注释**使用连接代理工具创建主代理**，添加以下代码：
    
    ```python
    # Create a main agent with the Connected Agent tools
    agent = agents_client.create_agent(
        model=model_deployment,
        name="quest_master",
        instructions="""
            You are the Questmaster, the intelligent guide of a three-member adventuring party exploring a short dungeon. 
            Based on the scenario, delegate tasks to the appropriate party member. The current party members are: Warrior, Scout, Healer.
            Only include the party member's response, do not provide an analysis or summary.
        """,
        tools=[
            healer_agent_tool.definitions[0],
            scout_agent_tool.definitions[0],
            warrior_agent_tool.definitions[0]
        ]
    )
    ```

1. 查找注释**创建聊天会话线程**，并添加以下代码：
    
    ```python
    # Create thread for the chat session
    print("Creating agent thread.")
    thread = agents_client.threads.create()
    ```


1. 在注释**创建任务提示**下，添加以下代码：
    
    ```python
    prompt = "We find a locked door with strange symbols, and the warrior is limping."
    ```

1. 在注释**发送提示到代理**下，添加以下代码：
    
    ```python
    # Send a prompt to the agent
    message = agents_client.messages.create(
        thread_id=thread.id,
        role=MessageRole.USER,
        content=prompt,
    )
    ```

1. 在注释**创建并使用工具在线程中运行创建和处理代理**下，添加以下代码：
    
    ```python
    # Create and process Agent run in thread with tools
    print("Processing agent thread. Please wait.")
    run = agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
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

1. 出现提示时，请按照说明在新选项卡中打开登录页，并输入提供的验证码和 Azure 凭据。 然后在命令行中完成登录过程，并在出现提示时选择包含 Azure AI Foundry 中心的订阅。

1. 登录后，输入以下命令来运行应用程序：

    ```
   python agent_quest.py
    ```

    应会看到类似于下面的信息：

    ```output
    Creating agent thread.
    Processing agent thread. Please wait.

    MessageRole.USER:
    We find a locked door with strange symbols, and the warrior is limping.

    MessageRole.AGENT:
    - **Scout:** Decipher the celestial patterns of the strange symbols and determine the sequence to unlock the door. 
    - **Healer:** The warrior's injury has been addressed; moderate strain is relieved through healing magic and restorative salve.
    - **Warrior:** Recovered and ready to assist physically or guard the party as we proceed.

    Cleaning up agents:
    Deleted quest master agent.
    Deleted healer agent.
    Deleted scout agent.
    Deleted warrior agent.
    ```

    你可以用不同的应用场景修改提示，以查看代理们是如何协作的。

## 清理

如果已完成对 Azure AI 代理服务的探索，则应删除在本练习中创建的资源，以避免产生不必要的 Azure 成本。

1. 返回到包含 Azure 门户的浏览器选项卡（或在新的浏览器选项卡中重新打开 [Azure 门户](https://portal.azure.com)，网址为：`https://portal.azure.com`），查看已在其中部署本练习中使用的资源的资源组内容。

1. 在工具栏中，选择“删除资源组”****。

1. 输入资源组名称，并确认要删除该资源组。
