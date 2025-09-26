---
lab:
  title: 使用语义内核开发多代理解决方案
  description: 了解如何配置多代理以使用语义内核 SDK 进行协作
---

# 开发多代理解决方案

在本练习中，你将在语义内核 SDK 中练习使用顺序式业务流程模式。 你将创建一个简单的管道，其中包含三个代理，共同处理客户反馈并建议后续步骤。 你将创建以下代理：

- “摘要生成器”代理会将原始反馈浓缩为简短、中立的语句。
- “分类器”代理会将反馈归类为“正面”、“负面”或“功能”请求。
- 最后，“建议的操作”代理会推荐适当的后续步骤。

你将了解如何使用语义内核 SDK 将问题拆解，分配给合适的代理，并生成可执行的结果。 现在就开始吧！

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
    - **区域**：选择推荐的任何 AI Foundry******\*

    > \* 某些 Azure AI 资源受区域模型配额约束。 如果稍后在练习中达到配额限制，你可能需要在不同的区域中创建另一个资源。

1. 选择“**创建**”并等待项目（包括所选的 gpt-4 模型部署）创建。

1. 创建项目后，将自动打开聊天操场。

1. 在左侧导航窗格中，选择“**模型和终结点**”，然后选择 **gpt-4o** 部署。

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

1. 在代码文件中，将 your_openai_endpoint**** 占位符替换为项目的 Azure Open AI 终结点（从 Azure AI Foundry 门户中的项目“概述”**** 页的 Azure OpenAI**** 下复制）。 将 your_openai_api_key**** 替换为项目的 API 密钥，并确保 MODEL_DEPLOYMENT_NAME 变量设置为模型部署名称（应为 gpt-4o**）。

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
   from semantic_kernel.agents import Agent, ChatCompletionAgent, SequentialOrchestration
   from semantic_kernel.agents.runtime import InProcessRuntime
   from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
   from semantic_kernel.contents import ChatMessageContent
    ```


1. 在 get_agents**** 函数中，在注释“创建摘要生成器代理”**** 下添加以下代码：

    ```python
   # Create a summarizer agent
   summarizer_agent = ChatCompletionAgent(
       name="SummarizerAgent",
       instructions="""
       Summarize the customer's feedback in one short sentence. Keep it neutral and concise.
       Example output:
       App crashes during photo upload.
       User praises dark mode feature.
       """,
       service=AzureChatCompletion(),
   )
    ```

1. 在注释“创建分类器代理”**** 下添加以下代码：

    ```python
   # Create a classifier agent
   classifier_agent = ChatCompletionAgent(
       name="ClassifierAgent",
       instructions="""
       Classify the feedback as one of the following: Positive, Negative, or Feature request.
       """,
       service=AzureChatCompletion(),
   )
    ```

1. 在注释“创建建议的操作代理”**** 下添加以下代码：

    ```python
   # Create a recommended action agent
   action_agent = ChatCompletionAgent(
       name="ActionAgent",
       instructions="""
       Based on the summary and classification, suggest the next action in one short sentence.
       Example output:
       Escalate as a high-priority bug for the mobile team.
       Log as positive feedback to share with design and marketing.
       Log as enhancement request for product backlog.
       """,
       service=AzureChatCompletion(),
   )
    ```

1. 在注释“返回代理列表”**** 下添加以下代码：

    ```python
   # Return a list of agents
   return [summarizer_agent, classifier_agent, action_agent]
    ```

    在此列表中的代理顺序，就是它们在业务流程期间被依次选择执行的顺序。

## 创建顺序式业务流程

1. 在 main**** 函数中，找到注释“初始化输入任务”**** 并添加以下代码：
    
    ```python
   # Initialize the input task
   task="""
   I tried updating my profile picture several times today, but the app kept freezing halfway through the process. 
   I had to restart it three times, and in the end, the picture still wouldn't upload. 
   It's really frustrating and makes the app feel unreliable.
   """
    ```

1. 在注释“创建顺序式业务流程”**** 下，添加以下代码以使用响应回叫定义顺序式业务流程：

    ```python
   # Create a sequential orchestration
   sequential_orchestration = SequentialOrchestration(
       members=get_agents(),
       agent_response_callback=agent_response_callback,
   )
    ```

    通过 `agent_response_callback`，可以在业务流程期间查看来自每个代理的响应。

1. 在注释“创建运行时并启动”**** 下添加以下代码：

    ```python
   # Create a runtime and start it
   runtime = InProcessRuntime()
   runtime.start()
    ```

1. 在注释“通过任务和运行时调用业务流程”**** 下添加以下代码：

    ```python
   # Invoke the orchestration with a task and the runtime
   orchestration_result = await sequential_orchestration.invoke(
       task=task,
       runtime=runtime,
   )
    ```

1. 在注释“等待结果”**** 下添加以下代码：

    ```python
   # Wait for the results
   value = await orchestration_result.get(timeout=20)
   print(f"\n****** Task Input ******{task}")
   print(f"***** Final Result *****\n{value}")
    ```

    在此代码中，你将检索并显示业务流程的结果。 如果业务流程未在指定的超时范围内完成，将引发超时异常。

1. 找到注释“空闲时停止运行时”****，并添加以下代码：

    ```python
   # Stop the runtime when idle
   await runtime.stop_when_idle()
    ```

    处理完成后，停止运行时以清理资源。

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
   python agents.py
    ```

    应会看到类似于下面的信息：

    ```output
    # SummarizerAgent
    App freezes during profile picture upload, preventing completion.
    # ClassifierAgent
    Negative
    # ActionAgent
    Escalate as a high-priority bug for the development team.

    ****** Task Input ******
    I tried updating my profile picture several times today, but the app kept freezing halfway through the process.
    I had to restart it three times, and in the end, the picture still wouldn't upload.
    It's really frustrating and makes the app feel unreliable.

    ***** Final Result *****
    Escalate as a high-priority bug for the development team.
    ```

1. （可选）你可以尝试使用不同的任务输入运行代码，例如：

    ```output
    I use the dashboard every day to monitor metrics, and it works well overall. But when I'm working late at night, the bright screen is really harsh on my eyes. If you added a dark mode option, it would make the experience much more comfortable.
    ```
    ```output
    I reached out to your customer support yesterday because I couldn't access my account. The representative responded almost immediately, was polite and professional, and fixed the issue within minutes. Honestly, it was one of the best support experiences I've ever had.
    ```

## 总结

在本练习中，你通过语义内核 SDK 练习了顺序式业务流程，将多个代理组合成一个简化的工作流。 干得漂亮!

## 清理

如果已完成对 Azure AI 代理服务的探索，则应删除在本练习中创建的资源，以避免产生不必要的 Azure 成本。

1. 返回到包含 Azure 门户的浏览器选项卡（或在新的浏览器选项卡中重新打开 [Azure 门户](https://portal.azure.com)，网址为：`https://portal.azure.com`），查看已在其中部署本练习中使用的资源的资源组内容。

1. 在工具栏中，选择“删除资源组”****。

1. 输入资源组名称，并确认要删除该资源组。
