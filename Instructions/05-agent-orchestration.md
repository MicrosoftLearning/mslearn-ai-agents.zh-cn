---
lab:
  title: 使用 Microsoft Agent Framework 开发多智能体解决方案
  description: 了解如何使用 Microsoft Agent Framework SDK 配置多个智能体进行协作
---

# 开发多代理解决方案

在本练习中，你将练习在 Microsoft Agent Framework SDK 中使用顺序业务流程模式。 你将创建一个简单的管道，其中包含三个代理，共同处理客户反馈并建议后续步骤。 你将创建以下代理：

- “摘要生成器”代理会将原始反馈浓缩为简短、中立的语句。
- “分类器”代理会将反馈归类为“正面”、“负面”或“功能”请求。
- 最后，“建议的操作”代理会推荐适当的后续步骤。

你将了解如何使用 Microsoft Agent Framework SDK 分解问题、通过正确的智能体路由问题并生成可操作的结果。 现在就开始吧！

完成此练习大约需要 30 分钟。

> **注意**：本练习中使用的一些技术处于预览版或积极开发阶段。 可能会遇到一些意想不到的行为、警告或错误。

## 在 Microsoft Foundry 项目中部署模型

首先，在 Foundry 项目中部署一个模型。

1. 在 Web 浏览器中，打开 [Foundry 门户](https://ai.azure.com) (`https://ai.azure.com`)，然后使用你的 Azure 凭据登录。 关闭首次登录时打开的任何使用技巧或快速入门窗格，如有必要，使用左上角的 Foundry**** 徽标导航到主页，类似下图所示（如果已打开“帮助”**** 面板，请关闭它）：

    ![Foundry 门户的屏幕截图。](./Media/ai-foundry-home.png)

    > **重要说明**：确保此实验室的 “新建 Foundry”切换开关为“关闭”状态。******

1. 在主页的“**浏览模型和功能**”部分中，搜索 `gpt-4o` 模型；我们将在项目中使用它。
1. 在搜索结果中，选择 **gpt-4o** 模型以查看其详细信息，然后在模型的页面顶部，选择“**使用此模型**”。
1. 当提示创建项目时，输入项目的有效名称并展开“**高级选项**”。
1. 为项目确认以下设置：
    - Foundry 资源****：Foundry 资源的有效名称**
    - **订阅**：Azure 订阅
    - **资源组**：*创建或选择资源组*
    - **区域**：选择推荐的任何 AI Foundry******\*

    > \* 某些 Azure AI 资源受区域模型配额约束。 如果稍后在练习中达到配额限制，你可能需要在不同的区域中创建另一个资源。

1. 选择“**创建**”并等待项目（包括所选的 gpt-4 模型部署）创建。

1. 创建项目后，将自动打开聊天操场。

1. 在左侧导航窗格中，选择“**模型和终结点**”，然后选择 **gpt-4o** 部署。

1. 在“**设置**”窗格中，记下模型部署的名称；应为 **gpt-4o**。 可以通过在“**模型和终结点**”页中查看部署来确认这一点（只需在左侧导航窗格中打开该页）。
1. 在左侧导航窗格中，选择“**概述**”以查看项目的主页；如下所示：

    ![Foundry 门户中 Azure AI 项目详细信息的屏幕截图。](./Media/ai-foundry-project.png)

## 创建 AI 代理客户端应用

现在，你已准备好创建定义代理和自定义函数的客户端应用。 GitHub 存储库中提供了一些代码。

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
   cd ai-agents/Labfiles/05-agent-orchestration/Python
   ls -a -l
    ```

    提供的文件包含应用程序代码和配置设置文件。

### 配置应用程序设置

1. 在 Cloud Shell 命令行窗格中，输入以下命令以安装将要使用的库：

    ```
   python -m venv labenv
   ./labenv/bin/Activate.ps1
   pip install azure-identity agent-framework
    ```

1. 输入以下命令以编辑所提供的配置文件：

    ```
   code .env
    ```

    该文件已在代码编辑器中打开。

1. 在代码文件中，将 your_openai_endpoint 占位符替换为项目的终结点（从 Foundry 门户中的项目“概述”页复制）。******** 将 your_model_deployment 占位符替换为分配给 gpt-4o 模型部署的名称。****

1. 替换占位符后，使用 **Ctrl+S** 命令保存更改，然后使用 **Ctrl+Q** 命令关闭代码编辑器，同时使 Cloud Shell 命令行保持打开状态。

### 创建 AI 代理

现在，你已准备好为多代理解决方案创建代理！ 现在就开始吧！

1. 输入以下命令以编辑 agents.py**** 文件：

    ```
   code agents.py
    ```

1. 在文件顶部的注释“添加首选项”**** 下，添加以下代码，以引用实现代理所需的库中的命名空间：

    ```python
   # Add references
   import asyncio
   from typing import cast
   from agent_framework import ChatMessage, Role, SequentialBuilder, WorkflowOutputEvent
   from agent_framework.azure import AzureAIAgentClient
   from azure.identity import AzureCliCredential
    ```

1. 在 main 函数中，花点时间查看智能体说明。**** 这些说明定义业务流程中每个智能体的行为。

1. 在注释“Create the chat client”下添加以下代码****：

    ```python
   # Create the chat client
   credential = AzureCliCredential()
   async with (
       AzureAIAgentClient(async_credential=credential) as chat_client,
   ):
    ```

    请注意，AzureCliCredential 对象将允许你的代码向 Azure 帐户进行身份验证。**** AzureAIAgentClient 对象将自动包含来自 .env 配置的 Foundry 项目设置。****

1. 在注释“Create agents”下添加以下代码：****

    （请务必保持缩进级别）

    ```python
   # Create agents
   summarizer = chat_client.create_agent(
       instructions=summarizer_instructions,
       name="summarizer",
   )

   classifier = chat_client.create_agent(
       instructions=classifier_instructions,
       name="classifier",
   )

   action = chat_client.create_agent(
       instructions=action_instructions,
       name="action",
   )
    ```

## 创建顺序式业务流程

1. 在 main 函数中，找到注释“Initialize the current feedback”并添加以下代码：********
    
    （请务必保持缩进级别）

    ```python
   # Initialize the current feedback
   feedback="""
   I use the dashboard every day to monitor metrics, and it works well overall. 
   But when I'm working late at night, the bright screen is really harsh on my eyes. 
   If you added a dark mode option, it would make the experience much more comfortable.
   """
    ```

1. 在注释“Build a sequential orchestration”下，添加以下代码以使用定义的智能体定义顺序业务流程：****

    ```python
   # Build sequential orchestration
   workflow = SequentialBuilder().participants([summarizer, classifier, action]).build()
    ```

    智能体将按照将反馈添加到业务流程的顺序进行处理。

1. 在注释“Run and collect outputs”下添加以下代码****：

    ```python
   # Run and collect outputs
   outputs: list[list[ChatMessage]] = []
   async for event in workflow.run_stream(f"Customer feedback: {feedback}"):
       if isinstance(event, WorkflowOutputEvent):
           outputs.append(cast(list[ChatMessage], event.data))
    ```

    此代码将运行业务流程，并从每个参与智能体收集输出。

1. 在注释“Display outputs”下添加以下代码：****

    ```python
   # Display outputs
   if outputs:
       for i, msg in enumerate(outputs[-1], start=1):
           name = msg.author_name or ("assistant" if msg.role == Role.ASSISTANT else "user")
           print(f"{'-' * 60}\n{i:02d} [{name}]\n{msg.text}")
    ```

    此代码会格式化并显示从业务流程收集的工作流输出中的消息。

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
   python agents.py
    ```

    应会看到类似于下面的信息：

    ```output
    ------------------------------------------------------------
    01 [user]
    Customer feedback:
        I use the dashboard every day to monitor metrics, and it works well overall.
        But when I'm working late at night, the bright screen is really harsh on my eyes.
        If you added a dark mode option, it would make the experience much more comfortable.

    ------------------------------------------------------------
    02 [summarizer]
    User requests a dark mode for better nighttime usability.
    ------------------------------------------------------------
    03 [classifier]
    Feature request
    ------------------------------------------------------------
    04 [action]
    Log as enhancement request for product backlog.
    ```

1. （可选）可以尝试使用不同的反馈输入来运行代码，例如：

    ```output
    I use the dashboard every day to monitor metrics, and it works well overall. But when I'm working late at night, the bright screen is really harsh on my eyes. If you added a dark mode option, it would make the experience much more comfortable.
    ```
    ```output
    I reached out to your customer support yesterday because I couldn't access my account. The representative responded almost immediately, was polite and professional, and fixed the issue within minutes. Honestly, it was one of the best support experiences I've ever had.
    ```

## 总结

在本练习中，你练习了使用 Microsoft Agent Framework SDK 的顺序业务流程，将多个智能体组合成一个简化的工作流。 干得漂亮!

## 清理

如果已完成对 Azure AI 代理服务的探索，则应删除在本练习中创建的资源，以避免产生不必要的 Azure 成本。

1. 返回到包含 Azure 门户的浏览器选项卡（或在新的浏览器选项卡中重新打开 [Azure 门户](https://portal.azure.com)，网址为：`https://portal.azure.com`），查看已在其中部署本练习中使用的资源的资源组内容。

1. 在工具栏中，选择“删除资源组”****。

1. 输入资源组名称，并确认要删除该资源组。
