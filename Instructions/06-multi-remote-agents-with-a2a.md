---
lab:
  title: 使用 A2A 协议连接到远程智能体
  description: 使用 A2A 协议与远程智能体协作。
---

# 使用 A2A 协议连接到远程智能体

在本练习中，你将使用 Azure AI 智能体服务和 A2A 协议创建可相互交互的简单远程智能体。 这些智能体将协助技术作者准备其开发人员博客文章。 标题智能体将生成标题，大纲智能体将利用标题为文章制定简明大纲。 让我们开始吧

> **提示**：本练习中使用的代码基于适用于 Python 的 Azure AI Foundry SDK。 可以使用适用于 Microsoft .NET、JavaScript 和 Java 的 SDK 开发类似的解决方案。 有关详细信息，请参阅 [Azure AI Foundry SDK 客户端库](https://learn.microsoft.com/azure/ai-foundry/how-to/develop/sdk-overview)。

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
    - **区域**：选择推荐的任何 AI Foundry******\*

    > \* 某些 Azure AI 资源受区域模型配额约束。 如果稍后在练习中达到配额限制，你可能需要在不同的区域中创建另一个资源。

1. 选择“**创建**”并等待创建项目。
1. 如果出现提示，请使用“全局标准”或“标准”部署选项（具体取决于配额可用性）部署 gpt-4o 模型。********

    >**注意**：如果配额可用，则在创建智能体和项目时，可能会自动部署 GPT-4o 基础模型。

1. 项目创建完成后，会打开“智能体”操场。

1. 在左侧导航窗格中，选择“**概述**”以查看项目的主页；如下所示：

    ![Azure AI Foundry 项目概述页面的屏幕截图。](./Media/ai-foundry-project.png)

1. 将 **Azure AI Foundry 项目终结点**值复制到记事本，因为你将使用它们连接到客户端应用程序中的项目。

## 创建 A2A 应用程序

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
   cd ai-agents/Labfiles/06-build-remote-agents-with-a2a/python
   ls -a -l
    ```

    提供的文件包括：
    ```output
    python
    ├── outline_agent/
    │   ├── agent.py
    │   ├── agent_executor.py
    │   └── server.py
    ├── routing_agent/
    │   ├── agent.py
    │   └── server.py
    ├── title_agent/
    │   ├── agent.py
    |   ├── agent_executor.py
    │   └── server.py
    ├── client.py
    └── run_all.py
    ```

    每个智能体文件夹都包含 Azure AI 智能体代码和用于托管智能体的服务器。 路由智能体负责发现标题智能体和大纲智能体并与之通信************。 客户端**** 允许用户向路由智能体提交提示。 `run_all.py` 启动所有服务器并运行客户端。

### 配置应用程序设置

1. 在 Cloud Shell 命令行窗格中，输入以下命令以安装将要使用的库：

    ```
   python -m venv labenv
   ./labenv/bin/Activate.ps1
   pip install -r requirements.txt azure-ai-projects a2a-sdk
    ```

1. 输入以下命令以编辑已提供的配置文件：

    ```
   code .env
    ```

    该文件已在代码编辑器中打开。

1. 在代码文件中，将 your_project_endpoint**** 占位符替换为项目的终结点（从 Azure AI Foundry 门户的项目“概述”**** 页复制），并确保将 MODEL_DEPLOYMENT_NAME 变量设置为模型部署名称（应为 gpt-4o**）。
1. 替换占位符后，使用 **Ctrl+S** 命令保存更改，然后使用 **Ctrl+Q** 命令关闭代码编辑器，同时使 Cloud Shell 命令行保持打开状态。

### 创建可发现的智能体

在这项任务中，你要创建标题智能体，帮助作者为文章创建流行的标题。 还可以定义 A2A 协议所需的智能体技能和卡片，使智能体可被发现。

1. 导航到 `title_agent` 目录：

    ```
   cd title_agent
    ```

> **提示**：添加代码时，请务必保持正确的缩进。 使用注释缩进级别作为指南。

1. 输入以下命令以编辑已提供的代码文件：

    ```
   code agent.py
    ```

1. 查找注释“创建智能体客户端”并添加以下代码，以连接到 Azure AI 项目****：

    > **提示**：注意保持正确缩进级别。

    ```python
   # Create the agents client
   self.client = AgentsClient(
       endpoint=os.environ['PROJECT_ENDPOINT'],
       credential=DefaultAzureCredential(
           exclude_environment_credential=True,
           exclude_managed_identity_credential=True
       )
   )
    ```

1. 查找注释“创建标题智能体”并添加以下代码，以创建智能体****：

    ```python
   # Create the title agent
   self.agent = self.client.create_agent(
       model=os.environ['MODEL_DEPLOYMENT_NAME'],
       name='title-agent',
       instructions="""
       You are a helpful writing assistant.
       Given a topic the user wants to write about, suggest a single clear and catchy blog post title.
       """,
   )
    ```

1. 查找注释“创建聊天会话线程”并添加以下代码，以创建聊天线程****：

    ```python
   # Create a thread for the chat session
   thread = self.client.threads.create()
    ```

1. 查找注释“发送用户消息”并添加以下代码，以提交用户提示****：

    ```python
   # Send user message
   self.client.messages.create(thread_id=thread.id, role=MessageRole.USER, content=user_message)
    ```

1. 在注释“创建并运行智能体”下添加以下代码，以启动智能体的响应生成****：

    ```python
   # Create and run the agent
   run = self.client.runs.create_and_process(thread_id=thread.id, agent_id=self.agent.id)
    ```

    文件其余部分提供的代码将处理并返回智能体的响应。 

1. 保存代码文件 (CTRL+S)**。 现在，你已准备好使用 A2A 协议共享智能体的技能和卡片。 

1. 输入以下命令编辑标题智能体的 `server.py` 文件  

    ```
   code server.py
    ```

1. 查找注释“定义智能体技能”并添加以下代码，以指定智能体的功能****：

    ```python
   # Define agent skills
   skills = [
       AgentSkill(
           id='generate_blog_title',
           name='Generate Blog Title',
           description='Generates a blog title based on a topic',
           tags=['title'],
           examples=[
               'Can you give me a title for this article?',
           ],
       ),
   ]
    ```

1. 查找注释“创建智能体卡片”并添加以下代码，以定义使智能体可被发现的元数据****：

    ```python
   # Create agent card
   agent_card = AgentCard(
       name='AI Foundry Title Agent',
       description='An intelligent title generator agent powered by Azure AI Foundry. '
       'I can help you generate catchy titles for your articles.',
       url=f'http://{host}:{port}/',
       version='1.0.0',
       default_input_modes=['text'],
       default_output_modes=['text'],
       capabilities=AgentCapabilities(),
       skills=skills,
   )
    ```

1. 查找注释“创建智能体执行程序”并添加以下代码，以使用智能体卡片初始化智能体执行程序****：

    ```python
   # Create agent executor
   agent_executor = create_foundry_agent_executor(agent_card)
    ```

    智能体执行程序将充当所创建标题智能体的包装器。

1. 查找注释“创建请求处理器”并添加以下内容，以使用执行程序处理传入的请求****：

    ```python
   # Create request handler
   request_handler = DefaultRequestHandler(
       agent_executor=agent_executor, task_store=InMemoryTaskStore()
   )
    ```

1. 在注释“创建 A2A 应用程序”下添加以下代码，以创建与 A2A 兼容的应用程序实例****：

    ```python
   # Create A2A application
   a2a_app = A2AStarletteApplication(
       agent_card=agent_card, http_handler=request_handler
   )
    ```
    
    此代码创建一个 A2A 服务器，该服务器会使用标题智能体执行程序共享标题智能体的信息并处理此智能体的传入请求。

1. 完成后保存代码文件 (*CTRL+S*)。

### 启用智能体之间的消息

在此任务中，使用 A2A 协议使路由智能体能够将消息发送到其他智能体。 还可以通过实现智能体执行程序类来允许标题智能体接收消息。

1. 导航到 `routing_agent` 目录：

    ```
   cd ../routing_agent
    ```

1. 输入以下命令以编辑已提供的代码文件：

    ```
   code agent.py
    ```

    路由智能体充当业务流程协调程序，用于处理用户消息并确定应由哪个远程智能体来处理请求。

    收到用户消息时，路由智能体：
    - 启动会话线程。
    - 使用 `create_and_process` 方法评估与用户消息最匹配的智能体。
    - 使用 `send_message` 函数通过 HTTP 将消息路由到适当的智能体。
    - 远程智能体处理消息并返回响应。

    路由智能体最终捕获响应，并通过线程将其返回给用户。

    请注意，`send_message` 方法是异步的，必须等待智能体运行成功完成。

1. 在注释“使用智能体名称检索远程智能体的 A2A 客户端”下添加以下代码****：

    ```python
   # Retrieve the remote agent's A2A client using the agent name 
   client = self.remote_agent_connections[agent_name]
    ```

1. 查找注释“构造要发送到远程智能体”的有效负载并添加以下代码****：

    ```python
   # Construct the payload to send to the remote agent
   payload: dict[str, Any] = {
       'message': {
           'role': 'user',
           'parts': [{'kind': 'text', 'text': task}],
           'messageId': message_id,
       },
   }
    ```

1. 查找注释“在 SendMessageRequest 对象中包装有效负载”并添加以下代码****：

    ```python
   # Wrap the payload in a SendMessageRequest object
   message_request = SendMessageRequest(id=message_id, params=MessageSendParams.model_validate(payload))
    ```

1. 在注释“将消息发送到远程智能体客户端并等待响应”下添加以下代码****：

    ```python
   # Send the message to the remote agent client and await the response
   send_response: SendMessageResponse = await client.send_message(message_request=message_request)
    ```


1. 完成后保存代码文件 (*CTRL+S*)。 现在，路由智能体能够发现消息并将其发送到标题智能体。 让我们创建智能体执行程序代码来处理来自路由智能体的传入消息。

1. 导航到 `title_agent` 目录：

    ```
   cd ../title_agent
    ```

1. 输入以下命令以编辑已提供的代码文件：

    ```
   code agent_executor.py
    ```

    `AgentExecutor` 类实现必须包含 `execute` 和 `cancel` 方法。 已为你提供 cancel 方法。 `execute` 方法包含一个 `TaskUpdater` 对象，该对象用于管理事件并在任务完成时向调用方发出信号。 让我们添加任务执行逻辑。

1. 在 `execute` 方法中，在注释“处理请求”**** 下添加以下代码：

    ```python
   # Process the request
   await self._process_request(context.message.parts, context.context_id, updater)
    ```

1. 在 `_process_request` 方法中，在注释“获取标题智能体”**** 下添加以下代码：

    ```python
   # Get the title agent
   agent = await self._get_or_create_agent()
    ```

1. 在注释“更新任务状态”下添加以下代码****：

    ```python
   # Update the task status
   await task_updater.update_status(
       TaskState.working,
       message=new_agent_text_message('Title Agent is processing your request...', context_id=context_id),
   )
    ```

1. 查找注释“运行智能体对话”**** 并添加以下代码：

    ```python
   # Run the agent conversation
   responses = await agent.run_conversation(user_message)
    ```

1. 查找注释“使用响应更新任务”**** 并添加以下代码：

    ```python
   # Update the task with the responses
   for response in responses:
       await task_updater.update_status(
           TaskState.working,
           message=new_agent_text_message(response, context_id=context_id),
       )
    ```

1. 查找注释“将任务标记为完成”**** 并添加以下代码：

    ```python
   # Mark the task as complete
   final_message = responses[-1] if responses else 'Task completed.'
   await task_updater.complete(
       message=new_agent_text_message(final_message, context_id=context_id)
   )
    ```

    现在，已使用智能体执行程序包装标题智能体，A2A 协议将使用该执行程序来处理消息。 干得漂亮!

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
    cd ..
    python run_all.py
    ```
    
    应用程序使用已通过身份验证的 Azure 会话凭据连接到项目，创建并运行代理。 当每个服务器启动时，你应该会看到它们的一些输出。

1. 等到输入提示出现，然后输入如下提示：

    ```
   Create a title and outline for an article about React programming.
    ```

    片刻后，应会看到来自智能体的响应和结果。

1. 输入 `quit` 以退出程序并停止服务器。
    
## 总结

在本练习中，你使用了 Azure AI 智能体服务 SDK 和 A2A Python SDK 来创建远程多智能体解决方案。 你创建了一个可发现的 A2A 兼容智能体，并设置了一个路由智能体来访问智能体的技能。 你还实现了智能体执行程序来处理传入的 A2A 消息和管理任务。 干得漂亮!

## 清理

如果已完成对 Azure AI 代理服务的探索，则应删除在本练习中创建的资源，以避免产生不必要的 Azure 成本。

1. 返回到包含 Azure 门户的浏览器选项卡（或在新的浏览器选项卡中重新打开 [Azure 门户](https://portal.azure.com)，网址为：`https://portal.azure.com`），查看已在其中部署本练习中使用的资源的资源组内容。
1. 在工具栏中，选择“删除资源组”****。
1. 输入资源组名称，并确认要删除该资源组。
