---
lab:
  title: 在 AI 代理中使用自定义函数
  description: 了解如何使用函数向代理添加自定义功能。
---

# 在 AI 代理中使用自定义函数

在本练习中，你将探索如何创建可以使用自定义函数作为工具完成任务的代理。

你将生成简单的技术支持代理，以收集技术问题的详细信息并生成支持工单。

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
1. 创建项目后，代理操场将自动打开，以便可以选择或部署模型：

    ![Azure AI Foundry 项目代理操场的屏幕截图。](./Media/ai-foundry-agents-playground.png)

    >**备注**：创建代理和项目时，会自动部署 GPT-4o 基本模型。

1. 在左侧导航窗格中，选择“**概述**”以查看项目的主页；如下所示：

    > **备注**：如果显示“*权限不足*”*错误，请使用“**修复我**”按钮解决此问题。

    ![Azure AI Foundry 项目概述页面的屏幕截图。](./Media/ai-foundry-project.png)

1. 将 **Azure AI Foundry 项目终结点**值复制到记事本，因为你将使用它连接到客户端应用程序中的项目。

## 开发使用函数工具的代理

在 AI Foundry 中创建项目后，让我们开发使用自定义函数工具实现代理的应用。

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
   cd ai-agents/Labfiles/03-ai-agent-functions/Python
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

    >**备注：** 可以忽略库安装过程中显示的任何警告或错误消息。

1. 输入以下命令以编辑已提供的配置文件：

    ```
   code .env
    ```

    该文件已在代码编辑器中打开。

1. 在代码文件中，将 **your_project_endpoint** 占位符替换为项目的终结点（从 Azure AI Foundry 门户中的项目“**概述**”页复制）。
1. 替换占位符后，使用 **Ctrl+S** 命令保存更改，然后使用 **Ctrl+Q** 命令关闭代码编辑器，同时使 Cloud Shell 命令行保持打开状态。

### 定义自定义函数

1. 输入以下命令以编辑为函数代码提供的代码文件：

    ```
   code user_functions.py
    ```

1. 查找注释 **Create a function to submit a support ticket** 并添加以下代码，以生成工单编号并将支持工单另存为文本文件。

    ```python
   # Create a function to submit a support ticket
   def submit_support_ticket(email_address: str, description: str) -> str:
        script_dir = Path(__file__).parent  # Get the directory of the script
        ticket_number = str(uuid.uuid4()).replace('-', '')[:6]
        file_name = f"ticket-{ticket_number}.txt"
        file_path = script_dir / file_name
        text = f"Support ticket: {ticket_number}\nSubmitted by: {email_address}\nDescription:\n{description}"
        file_path.write_text(text)
    
        message_json = json.dumps({"message": f"Support ticket {ticket_number} submitted. The ticket file is saved as {file_name}"})
        return message_json
    ```

1. 查找注释 **Define a set of callable functions** 并添加以下代码，该代码静态定义此代码文件中的一组可调用函数（在本例中，只有一个函数 - 但在实际解决方案中，可能具有多个代理可调用的函数）：

    ```python
   # Define a set of callable functions
   user_functions: Set[Callable[..., Any]] = {
        submit_support_ticket
    }
    ```
1. 保存文件 (*CTRL+S*)。

### 写入代码以实现可以使用函数的代理

1. 输入以下命令以开始编辑代理代码。

    ```
    code agent.py
    ```

    > **提示**：向代码文件添加代码时，请务必保持正确的缩进。

1. 查看现有代码，该代码检索应用程序配置设置并设置循环，用户可在其中为代理输入提示。 该文件的其余部分包括注释，可以在其中添加必要的代码来实现技术支持代理。
1. 查找注释 **Add references** 并添加以下代码，以导入生成将函数代码用作工具的 Azure AI 代理所需的类：

    ```python
   # Add references
   from azure.identity import DefaultAzureCredential
   from azure.ai.agents import AgentsClient
   from azure.ai.agents.models import FunctionTool, ToolSet, ListSortOrder, MessageRole
   from user_functions import user_functions
    ```

1. 查找注释 **Connect to the Agent client**，然后添加以下代码，以使用当前 Azure 凭据连接到 Azure AI 项目。

    > **提示**：注意保持正确缩进级别。

    ```python
   # Connect to the Agent client
   agent_client = AgentsClient(
       endpoint=project_endpoint,
       credential=DefaultAzureCredential
           (exclude_environment_credential=True,
            exclude_managed_identity_credential=True)
   )
    ```
    
1. 查找注释 **Define an agent that can use the custom functions** 部分，并添加以下代码以将函数代码添加到工具集，然后创建可以使用工具集的代理和运行聊天会话的线程。

    ```python
   # Define an agent that can use the custom functions
   with agent_client:

        functions = FunctionTool(user_functions)
        toolset = ToolSet()
        toolset.add(functions)
        agent_client.enable_auto_function_calls(toolset)
            
        agent = agent_client.create_agent(
            model=model_deployment,
            name="support-agent",
            instructions="""You are a technical support agent.
                            When a user has a technical issue, you get their email address and a description of the issue.
                            Then you use those values to submit a support ticket using the function available to you.
                            If a file is saved, tell the user the file name.
                         """,
            toolset=toolset
        )

        thread = agent_client.threads.create()
        print(f"You're chatting with: {agent.name} ({agent.id})")

    ```

1. 查找注释 **Send a prompt to the agent**，并添加以下代码以将用户的提示添加为消息并运行线程。

    ```python
   # Send a prompt to the agent
   message = agent_client.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_prompt
   )
   run = agent_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
    ```

    > **备注**：使用 **create_and_process** 方法运行线程使代理能够自动查找函数，并根据函数名称和参数选择使用它们。 作为替代方法，可以使用 **create_run** 方法，在这种情况下，你将负责编写代码来轮询运行状态以确定何时需要函数调用、调用函数并将结果返回到代理。

1. 查找注释 **Check the run status for failures** 并添加以下代码，以显示发生的任何错误。

    ```python
   # Check the run status for failures
   if run.status == "failed":
        print(f"Run failed: {run.last_error}")
    ```

1. 查找注释 **Show the latest response from the agent** 并添加以下代码，以从已完成的线程中检索消息，并显示代理发送的最后一条消息。

    ```python
   # Show the latest response from the agent
   last_msg = agent_client.messages.get_last_message_text_by_role(
       thread_id=thread.id,
       role=MessageRole.AGENT,
   )
   if last_msg:
        print(f"Last Message: {last_msg.text.value}")
    ```

1. 查找注释 **Get the conversation history**，并添加以下代码以输出对话线程中的消息；反转顺序以按时间顺序显示它们

    ```python
   # Get the conversation history
   print("\nConversation Log:\n")
   messages = agent_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
   for message in messages:
       if message.text_messages:
           last_msg = message.text_messages[-1]
           print(f"{message.role}: {last_msg.text.value}\n")
    ```

1. 查找注释 **Clean up** 并添加以下代码，以在不再需要时删除代理和线程。

    ```python
   # Clean up
   agent_client.delete_agent(agent.id)
   print("Deleted agent")
    ```

1. 使用注释查看代码，了解如何操作：
    - 将自定义函数集添加到工具集
    - 创建使用工具集的代理。
    - 使用来自用户的提示消息运行线程。
    - 检查运行状态，以防出现故障
    - 从已完成的线程中检索消息，并显示代理发送的最后一条消息。
    - 显示对话历史记录
    - 删除不再需要的代理和线程。

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
   python agent.py
    ```
    
    应用程序使用已通过身份验证的 Azure 会话凭据连接到项目，创建并运行代理。

1. 出现提示时，输入提示，例如：

    ```
   I have a technical problem
    ```

    > **提示**：如果应用因超出速率限制而失败。 等待几秒钟，然后重试。 如果订阅配额不足，模型可能无法响应。

1. 查看响应 代理可能会询问你的电子邮件地址和问题说明。 可以使用任何电子邮件地址（例如 `alex@contoso.com`）和任何问题说明（例如 `my computer won't start`）

    当它有足够的信息时，代理应根据需要选择使用函数。

1. 如果需要，可以继续对话。 线程是*有状态的*，因此会保留对话历史记录，这意味着代理具有每个响应的完整上下文。 完成后，请输入`quit`。
1. 查看从线程检索到的对话消息和已生成的工单。
1. 该工具应已将支持工单保存在应用文件夹中。 可以使用 `ls` 命令检查，然后使用 `cat` 命令查看文件内容，如下所示：

    ```
   cat ticket-<ticket_num>.txt
    ```

## 清理

完成练习后，应删除已创建的云资源，以避免不必要的资源使用。

1. 打开 [Azure 门户](https://portal.azure.com)，网址为：`https://portal.azure.com`，并查看在其中部署了本练习中使用的中心资源的资源组内容。
1. 在工具栏中，选择“删除资源组”****。
1. 输入资源组名称，并确认要删除该资源组。
