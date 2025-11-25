---
lab:
  title: 使用 Microsoft Agent Framework SDK 开发 Azure AI 智能体
  description: 了解如何使用 Microsoft Agent Framework SDK 创建和使用 Azure AI 聊天智能体。
---

# 使用 Microsoft Agent Framework SDK 开发 Azure AI 聊天智能体

在本练习中，你将使用 Azure AI 智能体服务和 Microsoft Agent Framework 创建处理报销申请的 AI 智能体。

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
1. 在“**设置**”窗格中，记下模型部署的名称；应为 **gpt-4o**。 可以通过在“**模型和终结点**”页中查看部署来确认这一点（只需在左侧导航窗格中打开该页）。
1. 在左侧导航窗格中，选择“**概述**”以查看项目的主页；如下所示：

    ![Foundry 门户中 Azure AI 项目详细信息的屏幕截图。](./Media/ai-foundry-project.png)

## 创建代理客户端应用

现在，你已准备好创建定义代理和自定义函数的客户端应用。 GitHub 存储库中已经提供了部分代码。

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

1. 克隆存储库后，输入以下命令切换到代码文件所在的目录，并查看其中的所有文件。

    ```
   cd ai-agents/Labfiles/04-agent-framework/python
   ls -a -l
    ```

    提供的文件包含应用程序代码、配置设置文件以及费用数据文件。

### 配置应用程序设置

1. 在 Cloud Shell 命令行窗格中，输入以下命令以安装将要使用的库：

    ```
   python -m venv labenv
   ./labenv/bin/Activate.ps1
   pip install azure-identity agent-framework
    ```

1. 输入以下命令以编辑已提供的配置文件：

    ```
   code .env
    ```

    该文件已在代码编辑器中打开。

1. 在代码文件中，将 your_project_endpoint**** 占位符替换为项目的终结点（从 Foundry 门户中的项目“概述”**** 页复制），并将 your_model_deployment**** 占位符替换为分配给 gpt-4o 模型部署的名称。
1. 替换占位符后，使用 **Ctrl+S** 命令保存更改，然后使用 **Ctrl+Q** 命令关闭代码编辑器，同时使 Cloud Shell 命令行保持打开状态。

### 为代理应用编写代码

> **提示**：添加代码时，请务必保持正确的缩进。 使用现有的注释作为指南，并保持相同的缩进级别输入新代码。

1. 输入以下命令以编辑已提供的代理代码文件：

    ```
   code agent-framework.py
    ```

1. 查看文件中的代码。 该结构包含：
    - 一些**导入**语句，用于添加对常用命名空间的引用
    - 一个 *main* 函数，用于加载包含支出数据的文件，向用户询问指令，然后调用...
    - 必须在 **process_expenses_data** 函数中添加创建和使用代理的代码

1. 在文件顶部，现有 **import** 语句之后，查找注释“**Add references**”，并添加以下代码，以引用实现代理所需的库中的命名空间：

    ```python
   # Add references
   from agent_framework import AgentThread, ChatAgent
   from agent_framework.azure import AzureAIAgentClient
   from azure.identity.aio import AzureCliCredential
   from pydantic import Field
   from typing import Annotated
    ```

1. 在文件底部附近，找到注释“Create a tool function for the email functionality”，并添加以下代码以定义智能体将用于发送电子邮件的函数（工具是向智能体添加自定义功能的方法）****

    ```python
   # Create a tool function for the email functionality
   def send_email(
    to: Annotated[str, Field(description="Who to send the email to")],
    subject: Annotated[str, Field(description="The subject of the email.")],
    body: Annotated[str, Field(description="The text body of the email.")]):
        print("\nTo:", to)
        print("Subject:", subject)
        print(body, "\n")
    ```

    > **备注**：该函数*模拟*发送电子邮件，其方式是将其打印到控制台。 在实际应用程序中，你将使用 SMTP 服务或类似方式实际发送电子邮件！

1. 在 send_email 代码上方进行备份，在 process_expenses_data 函数中，找到注释“Create a chat agent”，并添加以下代码以使用工具和说明创建 ChatAgent 对象。****************

    （请务必保持缩进级别）

    ```python
   # Create a chat agent
   async with (
       AzureCliCredential() as credential,
       ChatAgent(
           chat_client=AzureAIAgentClient(async_credential=credential),
           name="expenses_agent",
           instructions="""You are an AI assistant for expense claim submission.
                           When a user submits expenses data and requests an expense claim, use the plug-in function to send an email to expenses@contoso.com with the subject 'Expense Claim`and a body that contains itemized expenses with a total.
                           Then confirm to the user that you've done so.""",
           tools=send_email,
       ) as agent,
   ):
    ```

    请注意，AzureCliCredential 对象将允许你的代码向 Azure 帐户进行身份验证。**** AzureAIAgentClient 对象将自动包含来自 .env 配置的 Foundry 项目设置。****

1. 查找注释：**使用代理处理报销申请**，并添加以下代码以创建一个线程供代理运行，然后使用聊天消息调用它。

    （请确认保持缩进级别）：

    ```python
   # Use the agent to process the expenses data
   try:
       # Add the input prompt to a list of messages to be submitted
       prompt_messages = [f"{prompt}: {expenses_data}"]
       # Invoke the agent for the specified thread with the messages
       response = await agent.run(prompt_messages)
       # Display the response
       print(f"\n# Agent:\n{response}")
   except Exception as e:
       # Something went wrong
       print (e)
    ```

1. 审阅代理的完整代码，使用注释帮助你理解每个代码块的作用，然后保存代码更改 （**CTRL+S**)。
1. 如果需要更正代码中的任何拼写错误，请保持代码编辑器为打开状态，但调整窗格大小，以便可以查看更多命令行控制台。

### 登录 Azure 并运行应用

1. 在代码编辑器下方的 Cloud Shell 命令行窗格中，输入以下命令以登录 Azure。

    ```
    az login
    ```

    **<font color="red">必须登录到 Azure - 即使已对 Cloud Shell 会话进行身份验证。</font>**

    > **备注**：在大多数情况下，仅使用 *az login* 就足够了。 但是，如果在多个租户中有订阅，则可能需要使用 *--tenant* 参数指定租户。 有关详细信息，请参阅[使用 Azure CLI 以交互方式登录到 Azure](https://learn.microsoft.com/cli/azure/authenticate-azure-cli-interactively)。
    
1. 出现提示时，请按照说明在新选项卡中打开登录页，并输入提供的验证码和 Azure 凭据。 然后在命令行中完成登录过程，并在出现提示时选择包含 Foundry 中心的订阅。
1. 登录后，输入以下命令来运行应用程序：

    ```
   python agent-framework.py
    ```
    
    应用程序使用已通过身份验证的 Azure 会话凭据连接到项目，创建并运行代理。

1. 当系统询问如何处理报销数据时，请输入以下提示：

    ```
   Submit an expense claim
    ```

1. 应用程序完成后，审阅输出。 代理应根据所提供的数据撰写报销申请的电子邮件。

    > **提示**：如果应用因超出速率限制而失败。 等待几秒钟，然后重试。 如果订阅配额不足，模型可能无法响应。

## 总结

在本练习中，你使用了 Microsoft Agent Framework SDK 通过自定义工具创建智能体。

## 清理

如果已完成对 Azure AI 代理服务的探索，则应删除在本练习中创建的资源，以避免产生不必要的 Azure 成本。

1. 返回到包含 Azure 门户的浏览器选项卡（或在新的浏览器选项卡中重新打开 [Azure 门户](https://portal.azure.com)，网址为：`https://portal.azure.com`），查看已在其中部署本练习中使用的资源的资源组内容。
1. 在工具栏中，选择“删除资源组”****。
1. 输入资源组名称，并确认要删除该资源组。
