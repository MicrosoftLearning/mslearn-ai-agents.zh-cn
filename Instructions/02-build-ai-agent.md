---
lab:
  title: 部署 AI 代理
  description: 使用 Azure AI 代理服务开发使用内置工具的代理。
---

# 部署 AI 代理

在本练习中，你将使用 Azure AI 代理服务创建一个简单的代理来分析数据和创建图表。 代理使用内置 *代码解释器* 工具动态生成创建图表所需的代码作为图像，然后保存生成的图表图像。

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

1. 将 **Azure AI Foundry 项目终结点**值复制到记事本，因为你将使用它们连接到客户端应用程序中的项目。

## 创建代理客户端应用

现在，你已准备好创建使用代理的客户端应用。 GitHub 存储库中已经提供了部分代码。

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
   cd ai-agents/Labfiles/02-build-ai-agent/Python
   ls -a -l
    ```

    提供的文件包含应用程序代码、配置设置和数据。

### 配置应用程序设置

1. 在 Cloud Shell 命令行窗格中，输入以下命令以安装将要使用的库：

    ```
   python -m venv labenv
   ./labenv/bin/Activate.ps1
   pip install -r requirements.txt azure-ai-projects
    ```

1. 输入以下命令以编辑已提供的配置文件：

    ```
   code .env
    ```

    该文件已在代码编辑器中打开。

1. 在代码文件中，将 **your_project_endpoint** 占位符替换为项目的终结点（从 Azure AI Foundry 门户中的项目“**概述**”页复制）。
1. 替换占位符后，使用 **Ctrl+S** 命令保存更改，然后使用 **Ctrl+Q** 命令关闭代码编辑器，同时使 Cloud Shell 命令行保持打开状态。

### 为代理应用编写代码

> **提示**：添加代码时，请务必保持正确的缩进。 使用注释缩进级别作为指南。

1. 输入以下命令以编辑已提供的代码文件：

    ```
   code agent.py
    ```

1. 查看现有代码，该代码检索应用程序配置设置并从要分析的 *data.txt* 加载数据。 该文件的其余部分包含注释，可以在其中添加必要的代码来实现数据分析代理。
1. 查找注释 **Add references** 并添加以下代码，以导入需要使用内置代码解释器工具的 Azure AI 代理的类：

    ```python
   # Add references
   from azure.identity import DefaultAzureCredential
   from azure.ai.agents import AgentsClient
   from azure.ai.agents.models import FilePurpose, CodeInterpreterTool, ListSortOrder, MessageRole
    ```

1. 查找注释 **Connect to the Agent client** 并添加以下代码，以连接到 Azure AI 项目。

    > **提示**：注意保持正确缩进级别。

    ```python
   # Connect to the Agent client
   agent_client = AgentsClient(
       endpoint=project_endpoint,
       credential=DefaultAzureCredential
           (exclude_environment_credential=True,
            exclude_managed_identity_credential=True)
   )
   with agent_client:
    ```

    该代码使用当前的 Azure 凭据连接到 Azure AI Foundry 项目。 最后的 *with project_client* 语句启动一个代码块，该代码块定义客户端的范围，确保在块中的代码完成时将其清理干净。

1. 在 *with project_client* 块内，查找注释 **Upload the data file and create a CodeInterpreterTool**，并添加以下代码，以将数据文件上传到项目，并创建可访问其中数据的 CodeInterpreterTool：

    ```python
   # Upload the data file and create a CodeInterpreterTool
   file = agent_client.files.upload_and_poll(
        file_path=file_path, purpose=FilePurpose.AGENTS
   )
   print(f"Uploaded {file.filename}")

   code_interpreter = CodeInterpreterTool(file_ids=[file.id])
    ```
    
1. 查找注释 **Define an agent that uses the CodeInterpreterTool** 并添加以下代码，以定义用于分析数据的 AI 代理，并可以使用前面定义的代码解释器工具：

    ```python
   # Define an agent that uses the CodeInterpreterTool
   agent = agent_client.create_agent(
        model=model_deployment,
        name="data-agent",
        instructions="You are an AI agent that analyzes the data in the file that has been uploaded. If the user requests a chart, create it and save it as a .png file.",
        tools=code_interpreter.definitions,
        tool_resources=code_interpreter.resources,
   )
   print(f"Using agent: {agent.name}")
    ```

1. 查找注释 **Create a thread for the conversation**并添加以下代码，以启动与代理的聊天会话将在其中运行的线程：

    ```python
   # Create a thread for the conversation
   thread = agent_client.threads.create()
    ```
    
1. 请注意，下一部分代码设置一个循环，以便用户输入提示，当用户输入“退出”时结束。

1. 查找注释 **Send a prompt to the agent** 并添加以下代码，将用户消息添加到提示（以及之前加载的文件中的数据），然后使用代理运行线程。

    ```python
   # Send a prompt to the agent
   message = agent_client.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_prompt,
    )

   run = agent_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
    ```

1. 查找注释 **Check the run status for failures**，并添加以下代码，以显示发生的任何错误。

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

1. 查找注释 **Get the conversation history** （循环结束后），并添加以下代码以输出对话线程中的消息；反转顺序以按时间顺序显示它们

    ```python
   # Get the conversation history
   print("\nConversation Log:\n")
   messages = agent_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
   for message in messages:
       if message.text_messages:
           last_msg = message.text_messages[-1]
           print(f"{message.role}: {last_msg.text.value}\n")
    ```

1. 查找注释 **Get any generated files** 并添加以下代码，以便从消息（这指示代理在其内部存储中保存了文件）获取任何文件路径批注，并将文件复制到应用文件夹。 _备注_：当前图像内容不可供系统使用。

    ```python
   # Get any generated files
   for msg in messages:
       # Save every image file in the message
       for img in msg.image_contents:
           file_id = img.image_file.file_id
           file_name = f"{file_id}_image_file.png"
           agent_client.files.save(file_id=file_id, file_name=file_name)
           print(f"Saved image file to: {Path.cwd() / file_name}")
    ```

1. 查找注释 **Clean up** 并添加以下代码，以在不再需要时删除代理和线程。

    ```python
   # Clean up
   agent_client.delete_agent(agent.id)
    ```

1. 使用注释查看代码，了解如何操作：
    - 连接到 AI Foundry 项目。
    - 上传数据文件并创建可访问它的代码解释器工具。
    - 创建使用代码解释器工具的新代理，并有显式指令，用于分析数据并将图表创建为 .png 文件。
    - 运行一个线程，其中包含来自用户的提示消息以及要分析的数据。
    - 检查运行状态，以防出现故障
    - 从已完成的线程中检索消息，并显示代理发送的最后一条消息。
    - 显示对话历史记录
    - 保存生成的每个文件。
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

1. 出现提示时，查看应用从 *data.txt* 文本文件加载的数据。 然后输入提示，例如：

    ```
   What's the category with the highest cost?
    ```

    > **提示**：如果应用因超出速率限制而失败。 等待几秒钟，然后重试。 如果订阅配额不足，模型可能无法响应。

1. 查看响应 然后输入另一个提示，此次请求图表：

    ```
   Create a pie chart showing cost by category
    ```

    在这种情况下，代理应根据需要选择性地使用代码解释器工具，以基于请求创建图表。

1. 如果需要，可以继续对话。 线程是*有状态的*，因此会保留对话历史记录，这意味着代理具有每个响应的完整上下文。 完成后，请输入`quit`。
1. 查看从线程检索到的对话消息以及生成的文件。

1. 应用程序完成后，使用 Cloud Shell **下载**命令下载保存在应用文件夹中的每个 .png 文件。 例如：

    ```
   download ./<file_name>.png
    ```

    下载命令会在浏览器右下角创建弹出链接，可以选择此链接下载并打开文件。

## 总结

在本练习中，已使用 Azure AI 代理服务 SDK 创建使用 AI 代理的客户端应用程序。 代理使用内置的代码解释器工具运行创建映像的动态代码。

## 清理

如果已完成对 Azure AI 代理服务的探索，则应删除在本练习中创建的资源，以避免产生不必要的 Azure 成本。

1. 返回到包含 Azure 门户的浏览器选项卡（或在新的浏览器选项卡中重新打开 [Azure 门户](https://portal.azure.com)，网址为：`https://portal.azure.com`），查看已在其中部署本练习中使用的资源的资源组内容。
1. 在工具栏中，选择“删除资源组”****。
1. 输入资源组名称，并确认要删除该资源组。
