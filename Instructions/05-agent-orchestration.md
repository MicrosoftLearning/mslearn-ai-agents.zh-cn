---
lab:
  title: 使用语义内核开发多代理解决方案
  description: 了解如何配置多代理以使用语义内核 SDK 进行协作
---

# 开发多代理解决方案

在本练习中，你将创建一个项目，使用语义内核 SDK 协调两个 AI 代理。 *事件管理器*代理将分析服务日志文件中的问题。 如果发现问题，事件管理器将推荐解决方案操作，*DevOps 助手*代理将收到建议并调用纠正函数并执行解决方法。 然后，事件管理器代理将查看更新的日志，以确保解决方案成功。

在本练习中，提供了四个示例日志文件。 “DevOps 助手”代理代码仅使用一些示例日志消息更新示例日志文件。

> **提示**：本练习中使用的代码基于适用于 Python 的 Semantic Kernel SDK。 可以使用适用于 Microsoft .NET 和 Java 的 SDK 开发类似解决方案。 有关详细信息，请参阅[支持的语义内核语言](https://learn.microsoft.com/semantic-kernel/get-started/supported-languages)。

完成此练习大约需要 30 分钟。

> **注意**：本练习中使用的一些技术处于预览版或积极开发阶段。 可能会遇到一些意想不到的行为、警告或错误。

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

1. 在“**设置**”窗格中，记下模型部署的名称；应为 **gpt-4o**。 可以通过在“**模型和终结点**”页中查看部署来确认这一点（只需在左侧导航窗格中打开该页）。
1. 在左侧导航窗格中，选择“**概述**”以查看项目的主页；如下所示：

    ![Azure AI Foundry 门户中 Azure AI 项目详细信息的屏幕截图。](./Media/ai-foundry-project.png)

## 创建 AI 代理客户端应用

现在，你已准备好创建定义代理和自定义函数的客户端应用。 GitHub 存储库中提供了一些代码。

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
   cd ai-agents/Labfiles/05-agent-orchestration/Python
   ls -a -l
    ```

    提供的文件包含应用程序代码和配置设置文件。

### 配置应用程序设置

1. 在 Cloud Shell 命令行窗格中，输入以下命令以安装将要使用的库：

    ```
   python -m venv labenv
   ./labenv/bin/Activate.ps1
   pip install python-dotenv azure-identity semantic-kernel --upgrade
    ```

    > **注意**：安装语义内核时，会自动安装与语义内核兼容的 azure-ai-projects 版本。****

1. 输入以下命令以编辑所提供的配置文件：

    ```
   code .env
    ```

    该文件已在代码编辑器中打开。

1. 在代码文件中，将 **your_project_endpoint** 占位符替换为项目的终结点（从 Azure AI Foundry 门户中的项目“**概述**”页复制而来），并将 **your_model_deployment** 占位符替换为 分配给 gpt-4 模型部署的名称。

1. 替换占位符后，使用 **Ctrl+S** 命令保存更改，然后使用 **Ctrl+Q** 命令关闭代码编辑器，同时使 Cloud Shell 命令行保持打开状态。

### 创建 AI 代理

现在，你已准备好为多代理解决方案创建代理！ 现在就开始吧！

1. 输入以下命令以编辑 **agent_chat.py** 文件：

    ```
   code agent_chat.py
    ```

1. 查看文件中的代码，注意其中包含：
    - 定义两个代理的名称和指令的常量。
    - **main** 函数，用于添加实现多代理解决方案的大部分代码。
    - **SelectionStrategy** 类，用于实现确定每个回合对话中应选择哪个代理所需的逻辑。
    - **ApprovalTerminationStrategy** 类，用于实现确定会话结束时间所需的逻辑。
    - **DevopsPlugin** 类，包含用于执行 DevOps 操作的函数。
    - **LogFilePlugin** 类，包含用于读取和写入日志文件的函数。

    首先，你将创建 *事件管理器* 代理，该代理将分析服务日志文件、识别潜在问题，并在必要时建议解决操作或升级问题。

1. 记下 **INCIDENT_MANAGER_INSTRUCTIONS** 字符串。 这些是代理的说明。

1. 在 **main** 函数中，查找注释 **Create the incident manager agent on the Azure AI agent service**，并添加以下代码以创建 Azure AI 代理。

    ```python
   # Create the incident manager agent on the Azure AI agent service
   incident_agent_definition = await client.agents.create_agent(
        model=ai_agent_settings.model_deployment_name,
        name=INCIDENT_MANAGER,
        instructions=INCIDENT_MANAGER_INSTRUCTIONS
   )
    ```

    此代码在 Azure AI 项目客户端上创建代理定义。

1. 查找注释 **Create a Semantic Kernel agent for the Azure AI incident manager agent**，并添加以下代码，以基于 Azure AI 代理定义创建语义内核代理。

    ```python
   # Create a Semantic Kernel agent for the Azure AI incident manager agent
   agent_incident = AzureAIAgent(
        client=client,
        definition=incident_agent_definition,
        plugins=[LogFilePlugin()]
   )
    ```

    此代码创建具有 **LogFilePlugin** 访问权限的语义内核代理。 此插件允许代理读取日志文件内容。

    现在让我们创建第二个代理，它将响应问题并执行 DevOps 操作来解决这些问题。

1. 在代码文件的顶部，花点时间观察 **DEVOPS_ASSISTANT_INSTRUCTIONS** 字符串。 这些指令将提供给新的 DevOps 助手代理。

1. 查找注释 **Create the devops agent on the Azure AI agent service**，并添加以下代码以创建 Azure AI 代理定义：
    
    ```python
   # Create the devops agent on the Azure AI agent service
   devops_agent_definition = await client.agents.create_agent(
        model=ai_agent_settings.model_deployment_name,
        name=DEVOPS_ASSISTANT,
        instructions=DEVOPS_ASSISTANT_INSTRUCTIONS,
   )
    ```

1. 查找注释 **Create a Semantic Kernel agent for the devops Azure AI agent**，并添加以下代码以基于 Azure AI 代理定义创建语义内核代理。
    
    ```python
   # Create a Semantic Kernel agent for the devops Azure AI agent
   agent_devops = AzureAIAgent(
        client=client,
        definition=devops_agent_definition,
        plugins=[DevopsPlugin()]
   )
    ```

    **DevopsPlugin** 允许代理模拟 DevOps 任务，例如重启服务或回滚事务。

### 定义群组聊天策略

现在，需要提供用于确定应选择哪个代理来轮次对话，以及何时应结束对话的逻辑。

让我们从 **SelectionStrategy** 开始，它确定哪个代理应该进行下一个轮次。

1. 在 **SelectionStrategy** 类（位于 **main** 函数下方）中，查找注释 **Select the next agent that should take the next turn in the chat**，并添加以下代码以定义选择函数：

    ```python
   # Select the next agent that should take the next turn in the chat
   async def select_agent(self, agents, history):
        """"Check which agent should take the next turn in the chat."""

        # The Incident Manager should go after the User or the Devops Assistant
        if (history[-1].name == DEVOPS_ASSISTANT or history[-1].role == AuthorRole.USER):
            agent_name = INCIDENT_MANAGER
            return next((agent for agent in agents if agent.name == agent_name), None)
        
        # Otherwise it is the Devops Assistant's turn
        return next((agent for agent in agents if agent.name == DEVOPS_ASSISTANT), None)
    ```

    此代码按每个轮次运行以确定哪个代理应做出响应，并检查聊天历史记录以查看上次响应的人员。

    现在，让我们实现 **ApprovalTerminationStrategy** 类，以帮助在目标完成且对话可以结束时发出信号。

1. 在 **ApprovalTerminationStrategy** 类中，查找注释 **End the chat if the agent has indicated there is no action needed**，并添加以下代码来定义终止函数：

    ```python
   # End the chat if the agent has indicated there is no action needed
   async def should_agent_terminate(self, agent, history):
        """Check if the agent should terminate."""
        return "no action needed" in history[-1].content.lower()
    ```

    内核在代理响应后调用此函数，以确定是否满足完成条件。 在这种情况下，当事件管理器响应“无需执行任何操作”时，即达到目标。 此短语在事件管理器代理指令中定义。

### 实现群组聊天

现在有两个代理和可帮助其轮次和结束聊天的策略，你可以实现群组聊天。

1. 在 main 函数中备份，查找注释 **Add the agents to a group chat with a custom termination and selection strategy**，并添加以下代码以创建群组聊天：

    ```python
   # Add the agents to a group chat with a custom termination and selection strategy
   chat = AgentGroupChat(
        agents=[agent_incident, agent_devops],
        termination_strategy=ApprovalTerminationStrategy(
            agents=[agent_incident], 
            maximum_iterations=10, 
            automatic_reset=True
        ),
        selection_strategy=SelectionStrategy(agents=[agent_incident,agent_devops]),      
   )
    ```

    在此代码中，你将使用事件管理器和 DevOps 代理创建代理群组聊天对象。 还可以定义聊天的终止和选择策略。 请注意，**ApprovalTerminationStrategy** 仅与事件管理器代理关联，不与 DevOps 代理关联。 这使得事件管理器代理负责发出聊天结束的信号。 **SelectionStrategy** 包括所有应轮次聊天的代理。

    请注意，自动重置标志将在聊天结束时自动清除聊天。 这样，代理就可以继续分析文件，无需使用过多不必要令牌的聊天历史记录对象。 

1. 查找注释 **Append the current log file to the chat**，并添加以下代码以将最近读取的日志文件文本添加到聊天：

    ```python
   # Append the current log file to the chat
   await chat.add_chat_message(logfile_msg)
   print()
    ```

1. 查找注释 **Invoke a response from the agents**，并添加以下代码以调用群组聊天：

    ```python
   # Invoke a response from the agents
   async for response in chat.invoke():
        if response is None or not response.name:
            continue
        print(f"{response.content}")
    ```

    这是触发聊天的代码。 由于已将日志文件文本添加为消息，因此选择策略将确定哪个代理应读取和响应此消息，然后代理之间的对话将继续，直到满足终止策略的条件或达到最大迭代次数。

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
   python agent_chat.py
    ```

    应会看到类似于下面的信息：

    ```output
    
    INCIDENT_MANAGER > /home/.../logs/log1.log | Restart service ServiceX
    DEVOPS_ASSISTANT > Service ServiceX restarted successfully.
    INCIDENT_MANAGER > No action needed.

    INCIDENT_MANAGER > /home/.../logs/log2.log | Rollback transaction for transaction ID 987654.
    DEVOPS_ASSISTANT > Transaction rolled back successfully.
    INCIDENT_MANAGER > No action needed.

    INCIDENT_MANAGER > /home/.../logs/log3.log | Increase quota.
    DEVOPS_ASSISTANT > Successfully increased quota.
    (continued)
    ```

    > **备注**：应用包含一些在处理每个日志文件间等待的代码，以尝试降低超出 TPM 速率限制的风险，还包括异常处理代码（以防出现此类情况） 如果订阅配额不足，模型可能无法响应。

1. 验证**日志**文件夹中的日志文件是否已使用来自 DevopsAssistant 的解析操作消息进行更新。

    例如，log1.log 应追加以下日志消息：

    ```log
    [2025-02-27 12:43:38] ALERT  DevopsAssistant: Multiple failures detected in ServiceX. Restarting service.
    [2025-02-27 12:43:38] INFO  ServiceX: Restart initiated.
    [2025-02-27 12:43:38] INFO  ServiceX: Service restarted successfully.
    ```

## 总结

在本练习中，已使用 Azure AI 代理服务和语义内核 SDK 创建可以自动检测问题并应用解决方案的 AI 事件和 DevOps 代理。 干得漂亮!

## 清理

如果已完成对 Azure AI 代理服务的探索，则应删除在本练习中创建的资源，以避免产生不必要的 Azure 成本。

1. 返回到包含 Azure 门户的浏览器选项卡（或在新的浏览器选项卡中重新打开 [Azure 门户](https://portal.azure.com)，网址为：`https://portal.azure.com`），查看已在其中部署本练习中使用的资源的资源组内容。

1. 在工具栏中，选择“删除资源组”****。

1. 输入资源组名称，并确认要删除该资源组。
