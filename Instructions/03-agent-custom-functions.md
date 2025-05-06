---
lab:
  title: 在 AI 代理中使用自定义函数
  description: 了解如何使用函数向代理添加自定义功能。
---

# 在 AI 代理中使用自定义函数

在本练习中，你将探索如何创建能使用自定义函数作为工具完成任务的代理。

你将构建一个简单的技术支持代理，用于收集技术问题详细信息并生成支持工单。

完成此练习大约需要 30 分钟。

> **注意**：本练习中使用的一些技术处于预览版或积极开发阶段。 可能会遇到一些意想不到的行为、警告或错误。

## 创建 Azure AI Foundry 项目

让我们首先创建 Azure AI Foundry 项目。

1. 在 Web 浏览器中打开 [Azure AI Foundry 门户](https://ai.azure.com)，网址为：`https://ai.azure.com`，然后使用 Azure 凭据登录。 关闭首次登录时打开的任何使用技巧或快速入门窗格，如有必要，使用左上角的 **Azure AI Foundry** 徽标导航到主页，类似下图所示（若已打开**帮助**面板，请关闭）：

    ![Azure AI Foundry 门户的屏幕截图。](./Media/ai-foundry-home.png)

1. 在主页中，选择“**+ 创建项目**”。
1. 在**创建项目**向导中，输入项目的有效名，如果出现建议使用现有中心的提示，请选择新建中心的选项。 然后查看将自动创建的 Azure 资源以支持中心和项目。
1. 选择“**自定义**”并为中心指定以下设置：
    - **中心名称**：*中心的有效名称*
    - **订阅**：Azure 订阅
    - **资源组**：*创建或选择资源组*
    - **位置**：选择以下任一区域\*：
        - eastus
        - eastus2
        - swedencentral
        - westus
        - westus3
    - **连接 Azure AI 服务或 Azure OpenAI**：*新建 AI 服务资源*
    - **连接 Azure AI 搜索**：跳过连接

    > \*截至本文撰写时，这些区域支持在代理中使用 gpt-4o 模型。 模型可用性受区域配额的约束。 如果稍后在练习中达到配额限制，可能需要在不同的区域中创建另一个资源。

1. 选择“**下一步**”查看配置。 然后，选择“**创建**”并等待该进程完成。
1. 创建项目后，关闭显示的所有使用技巧，并查看 Azure AI Foundry 门户中的项目页面，如下图所示：

    ![Azure AI Foundry 门户中 Azure AI 项目详细信息的屏幕截图。](./Media/ai-foundry-project.png)

## 部署生成式 AI 模型

现在，可随时部署生成式 AI 语言模型以支持代理。

1. 在项目左侧窗格的“**我的资产**”部分中，选择“**模型 + 终结点**”页。
1. 在“**模型 + 终结点**”页的“**模型部署**”选项卡中，在“**+ 部署模型**”菜单中，选择“**部署基础模型**”。
1. 在列表中搜索 **gpt-4o** 模型，然后选择并确认。
1. 在部署详细信息中选择“**自定义**”，并使用以下设置部署模型：
    - **部署名**：*有效的模型部署名*
    - **部署类型**：全局标准
    - **自动版本更新**：启用
    - **模型版本**：*选择最新可用版本*
    - **连接的 AI 资源**：*选择 Azure OpenAI 资源连接*
    - **每分钟令牌限制（千令牌）**：50K *（或如果订阅的可用上限低于 50K，则以其为准）*
    - **内容筛选器**：DefaultV2

    > **注意**：减少 TPM 有助于避免过度使用正在使用的订阅中可用的配额。 50,000 TPM 足以应对本练习所需的数据处理量。 如果可用配额低于上述 50,000 TPM，你仍然可完成本练习，但超过速率限制时可能需要等待并重新提交提示。

1. 等待部署完成。

## 开发一个使用函数工具的代理

你已在 AI Foundry 中创建项目，接下来我们开发一个使用自定义函数工具的代理应用。

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

    > **提示**：在 Cloudshell 中时输入命令时，输出可能会占用大量屏幕缓冲区，导致当前行的光标被遮挡。 可以通过输入 `cls` 命令来清除屏幕，以便更轻松地专注于每项任务。

1. 输入以下命令，将工作目录更改为包含代码文件的文件夹，并列出所有文件。

    ```
   cd ai-agents/Labfiles/03-ai-agent-functions/Python
   ls -a -l
    ```

    提供的文件包括应用程序代码和配置设置文件。

### 配置应用程序设置

1. 在 Cloud Shell 命令行窗格中，输入以下命令以安装将要使用的库：

    ```
   python -m venv labenv
   ./labenv/bin/Activate.ps1
   pip install python-dotenv azure-identity azure-ai-projects
    ```

    >**注意：** 在安装库的过程中，可以忽略显示的任何警告或错误信息。

1. 输入以下命令以编辑已提供的配置文件：

    ```
   code .env
    ```

    该文件已在代码编辑器中打开。

1. 在代码文件中，将 **your_project_connection_string** 占位符替换为项目的连接字符串（从 Azure AI Foundry 门户中的项目“**概述**”页复制），并将 **your_model_deployment** 占位符替换为分配给 gpt-4o 模型部署的名称。
1. 替换占位符后，使用 **Ctrl+S** 命令保存更改，然后使用 **Ctrl+Q** 命令关闭代码编辑器，同时使 Cloud Shell 命令行保持打开状态。

### 定义自定义函数

1. 输入以下命令以编辑已提供的函数代码文件：

    ```
   code user_functions.py
    ```

1. 查找注释：**创建函数以提交支持工单**，并添加以下代码，生成工单编号并将支持工单保存为文本文件。

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

1. 查找注释：**定义一组可调用函数**，并添加以下代码，静态定义此代码文件中的一组可调用函数（本例中只有一个，但在实际解决方案中，代理可能调用多个函数）：

    ```python
   # Define a set of callable functions
   user_functions: Set[Callable[..., Any]] = {
        submit_support_ticket
    }
    ```
1. 保存文件 (*Ctrl + S*)。

### 编写代码以实现可以使用函数的代理

1. 输入以下命令以启动编辑代理代码。

    ```
    code agent.py
    ```

    > **提示**：向代码文件添加代码时，请务必保持正确的缩进。

1. 审阅现有代码，该代码检索应用程序配置设置并设置一个循环，用户可在其中输入代理提示。 该文件的其余部分包括注释，你可以在其中添加必要的代码以实现技术支持代理。
1. 查找注释：**添加引用**，并添加以下代码导入生成 Azure AI 代理所需的类，以便将函数代码用作工具：

    ```python
   # Add references
   from azure.identity import DefaultAzureCredential
   from azure.ai.projects import AIProjectClient
   from azure.ai.projects.models import FunctionTool, ToolSet
   from user_functions import user_functions
    ```

1. 查找注释：**连接到 Azure AI Foundry 项目**，并添加以下代码，使用当前的 Azure 凭据连接到 Azure AI 项目。

    > **提示**：注意保持正确缩进级别。

    ```python
   # Connect to the Azure AI Foundry project
   project_client = AIProjectClient.from_connection_string(
        credential=DefaultAzureCredential
            (exclude_environment_credential=True,
             exclude_managed_identity_credential=True),
        conn_str=PROJECT_CONNECTION_STRING
   )
    ```
    
1. 查找注释：**定义可以使用自定义函数的代理**部分，并添加以下代码将函数代码添加到工具集中，然后创建一个可以使用工具集并运行聊天会话的线程的代理。

    ```python
   # Define an agent that can use the custom functions
   with project_client:

        functions = FunctionTool(user_functions)
        toolset = ToolSet()
        toolset.add(functions)
        project_client.agents.enable_auto_function_calls(toolset=toolset)
            
        agent = project_client.agents.create_agent(
            model=MODEL_DEPLOYMENT,
            name="support-agent",
            instructions="""You are a technical support agent.
                            When a user has a technical issue, you get their email address and a description of the issue.
                            Then you use those values to submit a support ticket using the function available to you.
                            If a file is saved, tell the user the file name.
                         """,
            toolset=toolset
        )

        thread = project_client.agents.create_thread()
        print(f"You're chatting with: {agent.name} ({agent.id})")

    ```

1. 查找注释：**向代理发送提示**，并添加以下代码，将用户的提示添加为消息并运行线程。

    ```python
   # Send a prompt to the agent
   message = project_client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content=user_prompt
   )
   run = project_client.agents.create_and_process_run(thread_id=thread.id, agent_id=agent.id)
    ```

    > **注意**：使用 **create_and_process_run** 方法运行线程，使得代理能够自动查找函数，并根据函数名称和参数选择是否使用它们。 或者，可以使用 **create_run** 方法，在这种情况下，你将负责编写代码来轮询运行状态，以确定何时需要函数调用、调用函数后再将结果返回给代理。

1. 查找注释：**检查运行状态中的失败**，并添加以下代码以显示发生的任何错误。

    ```python
   # Check the run status for failures
   if run.status == "failed":
        print(f"Run failed: {run.last_error}")
    ```

1. 查找注释：**显示代理的最新响应**，并添加以下代码以从已完成的线程中检索消息，并显示代理发送的最后一个消息。

    ```python
   # Show the latest response from the agent
   messages = project_client.agents.list_messages(thread_id=thread.id)
   last_msg = messages.get_last_text_message_by_role("assistant")
   if last_msg:
        print(f"Last Message: {last_msg.text.value}")
    ```

1. 查找注释：**获取对话历史记录**（循环结束后），并添加以下代码以输出对话线程中的消息；按时间顺序反转显示

    ```python
   # Get the conversation history
   print("\nConversation Log:\n")
   messages = project_client.agents.list_messages(thread_id=thread.id)
   for message_data in reversed(messages.data):
        last_message_content = message_data.content[-1]
        print(f"{message_data.role}: {last_message_content.text.value}\n")
    ```

1. 查找注释：**清理**，并添加以下代码，在不再需要时删除代理和线程。

    ```python
   # Clean up
   project_client.agents.delete_agent(agent.id)
   project_client.agents.delete_thread(thread.id)
    ```

1. 使用注释审阅代码，以理解操作方式：
    - 将自定义函数集添加到工具集
    - 创建使用工具集的代理。
    - 使用用户的提示消息运行线程。
    - 检查运行状态，以便在发生故障时处理。
    - 从已完成的线程中检索消息，并显示代理发送的最后一条消息。
    - 显示对话历史记录
    - 不再需要代理和线程时，将其删除。

1. 完成后保存代码文件 (*Ctrl+S*)。 你也可以关闭代码编辑器 (*CTRL+Q*)；但是，如果需要编辑添加的代码，可能需要将其保持打开状态。 无论哪种情况，都请将 cloud shell 命令行窗格保持打开状态。

### 登录 Azure 并运行应用

1. 在 Cloud Shell 命令行窗格中，输入以下命令以登录 Azure。

    ```
    az login
    ```

    **<font color="red">你需要登录到 Azure，即便 cloud shell 会话已通过身份验证。</font>**

    > **注意**：在大多数情况下，使用 *az 登录* 就能满足需求。 但是，如果你的订阅分布在多个租户中，可能需要使用 *--tenant* 参数来指定租户。 有关详细信息，请参阅[使用 Azure CLI 以交互方式登录到 Azure](https://learn.microsoft.com/cli/azure/authenticate-azure-cli-interactively)。
    
1. 出现提示时，请按照说明在新选项卡中打开登录页面，输入提供的身份验证代码和 Azure 凭据。 然后在命令行中完成登录过程，并在出现提示时选择包含 Azure AI Foundry 中心的订阅。
1. 登录后，输入以下命令运行应用程序：

    ```
   python agent.py
    ```
    
    应用程序使用已通过身份验证的 Azure 会话凭据连接到项目，创建并运行代理。

1. 出现提示时，输入如下提示：

    ```
   I have a technical problem
    ```

    > **提示**：如果应用因超出速率限制而失败。 等待几秒钟，然后重试。 如果订阅配额不足，模型可能无法响应。

1. 查看响应 代理可能会询问你的电子邮件地址和问题描述。 你可以使用任何电子邮件地址（如`alex@contoso.com`）和问题说明（如`my computer won't start`）

    在获得足够信息时，代理应根据需要选择使用你的函数。

1. 如果需要，可以继续对话。 线程具有*状态*，因此它会保留对话历史记录，这意味着代理在每次回应时都掌握完整上下文。 完成后，输入`quit`。
1. 审阅从线程检索到的对话消息和已生成的工单。
1. 该工具应已将支持工单保存在应用文件夹中。 你可以使用`ls`命令检查，并使用`cat`命令查看文件内容，示例如下：

    ```
   cat ticket-<ticket_num>.txt
    ```

## 清理

完成练习后，应删除已创建的云资源，以避免不必要的资源使用。

1. 在`https://portal.azure.com`打开 [Azure 门户](https://portal.azure.com)，查看用于本练习的中心资源所部署在资源组的内容。
1. 在工具栏中，选择“删除资源组”****。
1. 输入资源组名称，并确认要删除该资源组。