---
lab:
  title: 探索 AI 代理开发
  description: 通过探索 Azure AI Foundry 门户中的 Azure AI 代理服务工具，迈出开发 AI 代理的第一步。
---

# 探索 AI 代理开发

在本练习中，你将使用 Azure AI Foundry 门户中的 Azure AI 代理服务工具创建用于回答费用报销问题的简单 AI 代理。

此练习大约需要 **30** 分钟。

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
    - **位置**：选择以下任一区域：\*
        - eastus
        - eastus2
        - swedencentral
        - westus
        - westus3
    - **连接 Azure AI 服务或 Azure OpenAI**：*新建 AI 服务资源*
    - **连接 Azure AI 搜索**：跳过连接

    > \* 编写时，这些区域支持 gpt-4o 模型用于代理。 模型可用性受区域配额的约束。 如果稍后在练习中达到配额限制，可能需要在不同的区域中创建另一个资源。

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

## 创建 AI 代理

部署模型后，即可生成 AI 代理。 在本练习中，你将生成用于根据公司费用政策回答问题的简单代理。 你将下载费用政策文档，并将其用作代理的*基础*数据。

1. 打开新的浏览器选项卡，从`https://raw.githubusercontent.com/MicrosoftLearning/mslearn-ai-agents/main/Labfiles/01-agent-fundamentals/Expenses_Policy.docx`下载 [Expenses_policy.docx](https://raw.githubusercontent.com/MicrosoftLearning/mslearn-ai-agents/main/Labfiles/01-agent-fundamentals/Expenses_Policy.docx)，并将其保存在本地。 该文档包含虚构 Contoso 公司的费用政策的详细信息。
1. 返回到包含 Azure AI Foundry 门户的浏览器选项卡，然后在左侧的导航窗格中，在“**生成和自定义**”部分中，选择“**代理**”页。
1. 如果出现提示，请选择 Azure OpenAI 服务资源并转到。

    此时，应自动新建名称类似于 *Agent123* 的代理（如果没有，请使用“**+ 新建代理**”按钮创建一个代理）。

1. 选择新建的代理。 然后，在新建代理的“**设置**”窗格中，将“**代理名称**”设置为`ExpensesAgent`，确保选择之前创建的 GPT-4o 模型部署，并将“**指令**”设置为`Answer questions related to expense claims`。

    ![Azure AI Foundry 门户中 AI 代理设置页的屏幕截图。](./Media/ai-agent-setup.png)

1. 在“**设置**”窗格的靠下位置，在“**知识**”标题旁边，选择“**+ 添加**”。 然后在“**添加知识**”对话框中，选择“**文件**”。
1. 在“**添加文件**”对话框中，新建名为`Expenses_Vector_Store`的矢量存储，上传并保存之前下载的 **Expenses_policy.docx** 本地文件。

    ![Azure AI Foundry 门户中“添加文件”对话框的屏幕截图。](./Media/ai-agent-add-files.png)

1. 在“**设置**”窗格的“**知识**”部分中，验证是否已列出 **Expenses_Vector_Store**，并显示包含 1 个文件。

    > **备注**：还可以将**操作**添加到代理以自动执行任务。 在此简单的信息检索代理示例中，无需执行任何操作。

## 测试代理

创建代理后，可以在 Azure AI Foundry 门户操场中对其进行测试。

1. 在代理的“**设置**”窗格顶部，选择“**在操场中试用**”。
1. 在操场中，输入提示`What's the maximum I can claim for meals?`并查看代理的响应 - 这应基于费用政策文档中作为知识添加到代理设置的信息。

    ![Azure AI Foundry 门户中代理操场的屏幕截图。](./Media/ai-agent-playground.png)

    > **备注**：如果代理因超出速率限制而无法响应。 等待几秒钟，然后重试。 如果订阅配额不足，模型可能无法响应。

1. 尝试跟进问题，例如`What about accommodation?`并查看回复。

## 清理

完成练习后，应删除已创建的云资源，以避免不必要的资源使用。

1. 打开 [Azure 门户](https://portal.azure.com)，网址为：`https://portal.azure.com`，并查看在其中部署了本练习中使用的中心资源的资源组内容。
1. 在工具栏中，选择“删除资源组”****。
1. 输入资源组名称，并确认要删除该资源组。
