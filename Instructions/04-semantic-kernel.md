---
lab:
  title: 使用语义内核 SDK 开发 Azure AI 代理
  description: 了解如何使用语义内核 SDK 创建并使用 Azure AI 代理服务的代理。
---

# 使用语义内核 SDK 开发 Azure AI 代理

在本练习中，你将使用 Azure AI 代理服务和语义内核创建一个处理报销申请的 AI 代理。

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
1. 在“**设置**”窗格中，记下模型部署的名称；应为 **gpt-4o**。 可以通过在“**模型和终结点**”页中查看部署来确认这一点（只需在左侧导航窗格中打开该页）。
1. 在左侧导航窗格中，选择“**概述**”以查看项目的主页；如下所示：

    ![Azure AI Foundry 门户中 Azure AI 项目详细信息的屏幕截图。](./Media/ai-foundry-project.png)

## 创建代理客户端应用

现在，你已准备好创建定义代理和自定义函数的客户端应用。 GitHub 存储库中已经提供了部分代码。

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

1. 克隆存储库后，输入以下命令切换到代码文件所在的目录，并查看其中的所有文件。

    ```
   cd ai-agents/Labfiles/04-semantic-kernel/python
   ls -a -l
    ```

    提供的文件包含应用程序代码、配置设置文件以及费用数据文件。

### 配置应用程序设置

1. 在 Cloud Shell 命令行窗格中，输入以下命令以安装将要使用的库：

    ```
   python -m venv labenv
   ./labenv/bin/Activate.ps1
   pip install python-dotenv azure-identity semantic-kernel --upgrade 
    ```

    > **注意**：安装语义内核时，会自动安装与语义内核兼容的 azure-ai-projects 版本。****

1. 输入以下命令以编辑已提供的配置文件：

    ```
   code .env
    ```

    该文件已在代码编辑器中打开。

1. 在代码文件中，将 **your_project_endpoint** 占位符替换为项目的终结点（从 Azure AI Foundry 门户中的项目“**概述**”页复制而来），并将 **your_model_deployment** 占位符替换为 分配给 gpt-4 模型部署的名称。
1. 替换占位符后，使用 **Ctrl+S** 命令保存更改，然后使用 **Ctrl+Q** 命令关闭代码编辑器，同时使 Cloud Shell 命令行保持打开状态。

### 为代理应用编写代码

> **提示**：添加代码时，请务必保持正确的缩进。 使用现有的注释作为指南，并保持相同的缩进级别输入新代码。

1. 输入以下命令以编辑已提供的代理代码文件：

    ```
   code semantic-kernel.py
    ```

1. 查看文件中的代码。 该结构包含：
    - 一些**导入**语句，用于添加对常用命名空间的引用
    - 一个 *main* 函数，用于加载包含支出数据的文件，向用户询问指令，然后调用...
    - 必须在 **process_expenses_data** 函数中添加创建和使用代理的代码
    - 包含一个名为 **send_email** 的内核函数的 **EmailPlugin** 类；该函数将被代理用来模拟发送电子邮件的功能。

1. 在文件顶部，现有 **import** 语句之后，查找注释“**Add references**”，并添加以下代码，以引用实现代理所需的库中的命名空间：

    ```python
   # Add references
   from dotenv import load_dotenv
   from azure.identity.aio import DefaultAzureCredential
   from semantic_kernel.agents import AzureAIAgent, AzureAIAgentSettings, AzureAIAgentThread
   from semantic_kernel.functions import kernel_function
   from typing import Annotated
    ```

1. 在文件底部附近，查找注释 **Create a Plugin for the email functionality** 并添加以下代码，定义一个插件类，该类包含代理用于发送电子邮件的函数（插件是向语义内核代理添加自定义功能的方式）。

    ```python
   # Create a Plugin for the email functionality
   class EmailPlugin:
       """A Plugin to simulate email functionality."""
    
       @kernel_function(description="Sends an email.")
       def send_email(self,
                      to: Annotated[str, "Who to send the email to"],
                      subject: Annotated[str, "The subject of the email."],
                      body: Annotated[str, "The text body of the email."]):
           print("\nTo:", to)
           print("Subject:", subject)
           print(body, "\n")
    ```

    > **备注**：该函数*模拟*发送电子邮件，其方式是将其打印到控制台。 在实际应用程序中，你将使用 SMTP 服务或类似方式实际发送电子邮件！

1. 将备份移到新的 EmailPlugin**** 类代码上方，在 process_expenses_data**** 函数中，找到注释“获取配置设置”****，并添加以下代码来加载配置文件并创建一个 AzureAIAgentSettings**** 对象（它将自动从配置中包含 Azure AI 代理设置）。

    （请务必保持缩进级别）

    ```python
   # Get configuration settings
   load_dotenv()
   ai_agent_settings = AzureAIAgentSettings()
    ```

1. 查找注释 **Connect to the Azure AI Foundry project**，并添加以下代码，使用当前登录所使用的 Azure 凭据连接到 Azure AI Foundry 项目。

    （请务必保持缩进级别）

    ```python
   # Connect to the Azure AI Foundry project
   async with (
        DefaultAzureCredential(
            exclude_environment_credential=True,
            exclude_managed_identity_credential=True) as creds,
        AzureAIAgent.create_client(
            credential=creds
        ) as project_client,
   ):
    ```

1. 查找注释 **Define an Azure AI agent that sends an expense claim email**，并添加以下代码，为代理创建 Azure AI 代理定义。

    （请务必保持缩进级别）

    ```python
   # Define an Azure AI agent that sends an expense claim email
   expenses_agent_def = await project_client.agents.create_agent(
        model= ai_agent_settings.model_deployment_name,
        name="expenses_agent",
        instructions="""You are an AI assistant for expense claim submission.
                        When a user submits expenses data and requests an expense claim, use the plug-in function to send an email to expenses@contoso.com with the subject 'Expense Claim`and a body that contains itemized expenses with a total.
                        Then confirm to the user that you've done so."""
   )
    ```

1. 查找注释 **Create a semantic kernel agent**，并添加以下代码以创建 Azure AI 代理的语义内核代理对象，并包含对 **EmailPlugin** 插件的引用。

    （请确认保持缩进级别）

    ```python
   # Create a semantic kernel agent
   expenses_agent = AzureAIAgent(
        client=project_client,
        definition=expenses_agent_def,
        plugins=[EmailPlugin()]
   )
    ```

1. 查找注释：**使用代理处理报销申请**，并添加以下代码以创建一个线程供代理运行，然后使用聊天消息调用它。

    （请确认保持缩进级别）：

    ```python
   # Use the agent to process the expenses data
   # If no thread is provided, a new thread will be
   # created and returned with the initial response
   thread: AzureAIAgentThread | None = None
   try:
        # Add the input prompt to a list of messages to be submitted
        prompt_messages = [f"{prompt}: {expenses_data}"]
        # Invoke the agent for the specified thread with the messages
        response = await expenses_agent.get_response(prompt_messages, thread=thread)
        # Display the response
        print(f"\n# {response.name}:\n{response}")
   except Exception as e:
        # Something went wrong
        print (e)
   finally:
        # Cleanup: Delete the thread and agent
        await thread.delete() if thread else None
        await project_client.agents.delete_agent(expenses_agent.id)
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
    
1. 出现提示时，请按照说明在新选项卡中打开登录页，并输入提供的验证码和 Azure 凭据。 然后在命令行中完成登录过程，并在出现提示时选择包含 Azure AI Foundry 中心的订阅。
1. 登录后，输入以下命令来运行应用程序：

    ```
   python semantic-kernel.py
    ```
    
    应用程序使用已通过身份验证的 Azure 会话凭据连接到项目，创建并运行代理。

1. 当系统询问如何处理报销数据时，请输入以下提示：

    ```
   Submit an expense claim
    ```

1. 应用程序完成后，审阅输出。 代理应根据所提供的数据撰写报销申请的电子邮件。

    > **提示**：如果应用因超出速率限制而失败。 等待几秒钟，然后重试。 如果订阅配额不足，模型可能无法响应。

## 总结

在本练习中，你使用了 Azure AI 代理服务 SDK 和语义内核来创建代理。

## 清理

如果已完成对 Azure AI 代理服务的探索，则应删除在本练习中创建的资源，以避免产生不必要的 Azure 成本。

1. 返回到包含 Azure 门户的浏览器选项卡（或在新的浏览器选项卡中重新打开 [Azure 门户](https://portal.azure.com)，网址为：`https://portal.azure.com`），查看已在其中部署本练习中使用的资源的资源组内容。
1. 在工具栏中，选择“删除资源组”****。
1. 输入资源组名称，并确认要删除该资源组。
