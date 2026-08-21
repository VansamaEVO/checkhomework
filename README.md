# 学生作业智能检查系统（Streamlit）

> 面向教师的作业提交统计与人工阅卷平台 —— 上传花名册和作业包，一键生成提交统计、逐个阅卷打分、导出成绩单。

基于 **Streamlit** 构建的 Web 应用，帮助老师从繁琐的作业收集中解放出来：自动比对花名册与作业提交情况，可视化展示提交率，并支持在网页上直接阅读学生代码、人工打分、一键导出成绩。

## ✨ 功能特性

- 📊 **提交统计**：自动识别作业包中的提交文件（按 9 位学号命名），与花名册比对，展示应交 / 已交 / 未交人数与提交率环形图
- 📋 **学生明细**：全量学生列表，已交 / 未交状态用绿 / 红色高亮区分
- 📝 **作业评分（核心）**：逐个学生展开查看代码（可滚动），右侧评分控制台人工打分，分数实时保存
- 📥 **导出成绩单**：一键下载 CSV 成绩单（UTF-8 BOM，Excel 直接打开不乱码）
- 🎨 清爽的渐变 Banner 与卡片式 UI，支持「一键展开所有作业」快速浏览

## 🚀 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 启动应用
streamlit run check_homework_End.py
```

浏览器访问 `http://localhost:8501`。

> 也支持 **GitHub Codespaces** 一键运行（已配置 `.devcontainer`），打开即自动安装依赖并启动服务。

## 📦 使用流程

1. **上传花名册**：Excel（`.xlsx`），需包含「学号」「姓名」列（表头位置自动识别）
2. **上传作业包**：ZIP 压缩包，内含以学生学号命名的 `.py` 文件（支持子文件夹递归查找）
3. **查看统计**：Tab1 看提交概况，Tab2 看学生明细
4. **阅卷打分**：Tab3 阅读代码并输入分数
5. **导出结果**：底部下载 CSV 成绩单

## 🛠 技术栈

- Python 3 · Streamlit
- pandas / openpyxl（Excel 解析）
- Altair（统计图表）

## 📁 项目结构

```
checkhomework/
├── check_homework_End.py   # 主程序（单文件应用）
├── requirements.txt        # 依赖列表
└── .devcontainer/          # GitHub Codespaces 配置
```

## License

MIT
