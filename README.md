# add-principles

为项目 AGENTS.md 添加通用原则的 Kimi Skill。

## 安装

```bash
# 进入 Kimi skills 目录
cd ~/.kimi/skills

# 克隆本仓库
git clone <repository-url> add-principles
```

## 使用方法

在 Kimi 对话中说出：

```
添加原则
```

或

```
给项目加原则
```

## 功能特点

- **自动初始化**：如果项目没有 AGENTS.md，自动执行 `/init` 创建
- **原则库管理**：从 `principles.md` 读取你维护的原则集合
- **智能去重**：自动检测重复原则，避免冗余添加
- **计划预览**：执行前展示完整添加计划，确认后再写入
- **安全备份**：修改前自动创建备份文件

## 自定义原则库

编辑 `add-principles/principles.md` 文件，添加你常用的原则：

```markdown
## Git工作流
- main 分支受保护
- 使用 Conventional Commits

## 测试规范
- 覆盖率 ≥ 80%
- 边界条件必须覆盖
```

## 交互流程

```
📂 当前目录：/path/to/project
诊断结果：✗ AGENTS.md 不存在
正在执行 /init 创建 AGENTS.md...
✓ AGENTS.md 创建成功

可用原则：
   [1] Git工作流
   [2] 测试规范
   [3] 代码审查

请选择要添加的原则：1 2

🔍 正在检查重复...
[1] Git工作流   状态：✅ 无冲突
[2] 测试规范    状态：✅ 无冲突

📋 添加计划
   ➕ [新增] Git工作流
   ➕ [新增] 测试规范

请选择：[y] 确认执行 [p] 预览 [q] 取消
```

## License

MIT
