---
lab:
  title: 探索 AI 代理开发
  description: 通过探索 Azure AI Foundry 门户中的 Azure AI 代理服务，迈出开发 AI 代理的第一步。
---

# 探索 AI 代理开发

在本练习中，你将使用 Azure AI Foundry 门户中的 Azure AI 代理服务创建用于协助员工费用报销的简单 AI 代理。

此练习大约需要 **30** 分钟。

> **注意**：本练习中使用的一些技术处于预览版或积极开发阶段。 可能会遇到一些意想不到的行为、警告或错误。

## 创建 Azure AI Foundry 项目和代理

让我们首先创建 Azure AI Foundry 项目。

1. 在 Web 浏览器中打开 [Azure AI Foundry 门户](https://ai.azure.com)，网址为：`https://ai.azure.com`，然后使用 Azure 凭据登录。 关闭首次登录时打开的任何使用技巧或快速入门窗格，如有必要，使用左上角的 **Azure AI Foundry** 徽标导航到主页，类似下图所示（若已打开**帮助**面板，请关闭）：

    ![Azure AI Foundry 门户的屏幕截图。](./Media/ai-foundry-home.png)

1. 在主页中，选择“**创建代理**”。
1. 当提示创建项目时，输入项目的有效名称。
1. 展开“**高级选项**”，并指定以下设置：
    - **Azure AI Foundry 资源**：*Azure AI Foundry 资源的有效名称*
    - **订阅**：Azure 订阅
    - **资源组**：*选择你的资源组，或新建一个资源组*
    - 区域****：**选择任何推荐的 AI Foundry****\**

    > \* 某些 Azure AI 资源受区域模型配额约束。 如果稍后在练习中达到配额限制，你可能需要在不同的区域中创建另一个资源。

1. 选择“**创建**”并等待创建项目。
1. 如果出现提示，请使用“全局标准”或“标准”部署类型（具体取决于配额可用性）部署 gpt-4o 模型，并自定义部署详细信息，将“每分钟标记数速率限制”设置为 50,000（如果小于 50,000，则设置为最大可用值）。****************

    > **注意**：减少 TPM 有助于避免过度使用正在使用的订阅中可用的配额。 50,000 TPM 足以应对本练习所需的数据处理量。 如果可用配额低于上述 50,000 TPM，你仍然可完成本练习，但如果超过速率限制，可能会出现错误。

1. 创建项目后，代理操场将自动打开，以便可以选择或部署模型：

    ![Azure AI Foundry 项目代理操场的屏幕截图。](./Media/ai-foundry-agents-playground.png)

    >**备注**：创建代理和项目时，会自动部署 GPT-4o 基本模型。

你将看到已为你创建具有默认名称的代理，以及基础模型部署。

## 创建代理

部署模型后，即可生成 AI 代理。 在本练习中，你将生成用于根据公司费用政策回答问题的简单代理。 你将下载费用政策文档，并将其用作代理的*基础*数据。

1. 打开新的浏览器选项卡，从`https://raw.githubusercontent.com/MicrosoftLearning/mslearn-ai-agents/main/Labfiles/01-agent-fundamentals/Expenses_Policy.docx`下载 [Expenses_policy.docx](https://raw.githubusercontent.com/MicrosoftLearning/mslearn-ai-agents/main/Labfiles/01-agent-fundamentals/Expenses_Policy.docx)，并将其保存在本地。 该文档包含虚构 Contoso 公司的费用政策的详细信息。
1. 返回到包含 Foundry 代理操场的浏览器选项卡，并找到“**设置**”窗格（它可能位于聊天窗口的一侧或下方）。
1. 将“**代理名称**”设置为 `ExpensesAgent`，确保选择之前创建的 gpt-4o 模型部署，并将“**指令**”设置为：

    ```prompt
   You are an AI assistant for corporate expenses.
   You answer questions about expenses based on the expenses policy data.
   If a user wants to submit an expense claim, you get their email address, a description of the claim, and the amount to be claimed and write the claim details to a text file that the user can download.
    ```

    ![Azure AI Foundry 门户中 AI 代理设置页的屏幕截图。](./Media/ai-agent-setup.png)

1. 在“**设置**”窗格的靠下位置，在“**知识**”标题旁边，选择“**+ 添加**”。 然后在“**添加知识**”对话框中，选择“**文件**”。
1. 在“**添加文件**”对话框中，新建名为`Expenses_Vector_Store`的矢量存储，上传并保存之前下载的 **Expenses_policy.docx** 本地文件。
1. 在“**设置**”窗格的“**知识**”部分中，验证是否已列出 **Expenses_Vector_Store**，并显示包含 1 个文件。
1. 在“**知识**”部分的“**操作**”旁边，选择“**+ 添加**”。 然后在“**添加操作**”对话框中，选择“**代码解释器**”，然后选择“**保存**”（无需上传代码解释器的任何文件）。

    代理将使用上传的文档作为其知识源来*设置*其响应 （换句话说，它将根据本文档的内容回答问题）。 它将根据需要使用代码解释器工具，通过生成并运行自己的 Python 代码来执行操作。

## 测试代理

创建代理后，可以在操场聊天中对其进行测试。

1. 在操场聊天项中，输入提示：`What's the maximum I can claim for meals?` 并查看代理的响应 - 这应基于费用政策文档中作为知识添加到代理设置的信息。

    > **备注**：如果代理因超出速率限制而无法响应。 等待几秒钟，然后重试。 如果订阅配额不足，模型可能无法响应。 如果问题仍然存在，请尝试在“**模型 + 终结点**”页上增加模型的配额。

1. 尝试以下跟进提示：`I'd like to submit a claim for a meal.` 并查看响应。 代理应要求你提供提交报销所需的信息。
1. 向代理提供电子邮件地址；例如， `fred@contoso.com`。 代理应确认响应并请求费用报销所需的剩余信息（说明和金额）
1. 提交描述报销和金额的提示；例如， `Breakfast cost me $20`。
1. 代理应使用代码解释器来准备费用报销文本文件，并提供一个链接供你下载。

    ![Azure AI Foundry 门户中代理操场的屏幕截图。](./Media/ai-agent-playground.png)

1. 下载并打开文本文档以查看费用报销详细信息。

## 清理

完成练习后，应删除已创建的云资源，以避免不必要的资源使用。

1. 打开 [Azure 门户](https://portal.azure.com)，网址为：`https://portal.azure.com`，并查看在其中部署了本练习中使用的中心资源的资源组内容。
1. 在工具栏中，选择“删除资源组”****。
1. 输入资源组名称，并确认要删除该资源组。
