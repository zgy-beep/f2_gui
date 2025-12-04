# F2 GUI v02

> 现代化的 F2 下载工具图形用户界面

## ✨ 特性

- 🌗 **亮色/暗色主题** - 支持主题切换,保护您的眼睛
- 📦 **卡片式布局** - 现代化的卡片布局,信息展示更清晰
- 🔄 **异步下载** - 基于 F2 的异步架构,高效稳定
- 🌐 **多平台支持** - 支持抖音、TikTok、微博、Twitter 等平台
- 📊 **实时统计** - 实时显示下载进度和统计信息
- ⚙️ **灵活配置** - 丰富的配置选项,满足不同需求
- 🔌 **模块化架构** - 清晰的代码结构,易于维护和扩展

## 🏗️ 项目结构

```
gui/
├── __init__.py          # 包初始化
├── __main__.py          # 程序入口
├── config.py            # 配置管理
├── components/          # UI组件
│   ├── base_card.py     # 基础卡片组件
│   ├── stat_card.py     # 统计卡片
│   └── download_task_card.py  # 下载任务卡片
├── controllers/         # 控制器层
│   ├── download_controller.py  # 下载控制器
│   └── task_manager.py         # 任务管理器
├── models/              # 数据模型
├── views/               # 视图层
│   ├── main_window.py   # 主窗口
│   ├── home_page.py     # 首页
│   └── settings_page.py # 设置页面
├── utils/               # 工具类
│   ├── config_manager.py  # 配置管理器
│   └── logger.py          # 日志管理器
├── themes/              # 主题系统
│   └── theme_manager.py   # 主题管理器
└── assets/              # 资源文件
```

## 🚀 快速开始

### 前置要求

- Python 3.11+
- PyQt6
- F2 核心库

### 安装依赖

```bash
# 安装 PyQt6
pip install PyQt6

# 或使用项目的 requirements.txt
pip install -r requirements.txt
```

### 运行程序

```bash
# 方式1: 直接运行模块
python -m f2.gui

# 方式2: 从项目根目录运行
cd f2
python -m gui_v02.__main__
```

## 📖 使用指南

### 新建下载任务

1. 在首页选择要下载的平台(抖音、TikTok等)
2. 选择下载模式(单个作品、用户主页、点赞列表等)
3. 输入链接或用户ID
4. 点击"开始下载"按钮

### 配置设置

在设置页面中,您可以配置:

- **下载设置**

  - 下载路径
  - 文件命名模板
  - 文件名长度限制
  - 最大并发数
  - 最大下载数量
- **代理设置**

  - 启用/禁用代理
  - 代理地址配置
- **高级设置**

  - 日志级别
  - 超时时间
  - 重试次数

### 主题切换

点击侧边栏底部的"切换主题"按钮,即可在亮色和暗色主题之间切换。

## 🎨 设计理念

### Material Design 3

GUI 完全遵循 Material Design 3 设计规范:

- **色彩系统**: 使用 MD3 的动态色彩系统,支持主题色、容器色等
- **圆角设计**: 统一的 12px 圆角,营造柔和的视觉效果
- **阴影效果**: 适度的阴影增强层次感
- **动画交互**: 流畅的过渡动画提升用户体验

### 模块化架构

采用 MVC 架构模式:

- **Models**: 数据模型定义
- **Views**: UI界面和页面
- **Controllers**: 业务逻辑和F2 API交互

## 🔧 开发指南

### 添加新平台

1. 在 `config.py` 的 `PLATFORM_CONFIG` 中添加平台配置
2. 在 `controllers/download_controller.py` 中实现对应的下载逻辑
3. 调用相应的 F2 Handler (如 DouyinHandler, TiktokHandler)

### 自定义主题

编辑 `config.py` 中的 `COLORS` 配置:

```python
COLORS = {
    "light": {
        "primary": "#6750A4",
        "on_primary": "#FFFFFF",
        # ... 其他颜色
    },
    "dark": {
        "primary": "#D0BCFF",
        "on_primary": "#381E72",
        # ... 其他颜色
    }
}
```

### 添加新组件

在 `components/` 目录下创建新组件,继承 `BaseCard`:

```python
from f2.gui.components.base_card import BaseCard

class MyCustomCard(BaseCard):
    def __init__(self, parent=None):
        super().__init__(parent, elevated=True)
        self._setup_content()
  
    def _setup_content(self):
        # 添加您的组件内容
        pass
```

## 📝 待办事项

- [X]  集成 F2 核心 API
- [X]  实现下载历史记录
- [X]  添加下载队列管理
- [X]  支持批量下载
- [X]  添加浏览器 Cookie 导入
- [ ]  支持 微博
- [ ]  支持 TikTok
- [ ]  支持 X
- [X]  添加下载完成通知
- [ ]  实现自动更新检查

## 📄 许可证

本项目采用 Apache-2.0 许可证。详情请见 [LICENSE](../../../LICENSE) 文件。

## 🙏 致谢

- [F2](https://github.com/Johnserf-Seed/f2) - 强大的异步下载核心
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - Qt for Python

## 📮 联系方式

- 项目主页: [https://github.com/Johnserf-Seed/f2](https://github.com/Johnserf-Seed/f2)
- 文档: [https://f2.wiki](https://f2.wiki)
- 问题反馈: [Issues](https://github.com/Johnserf-Seed/f2/issues)

---

**注意**: GUI  仍在开发中,部分功能可能尚未完全实现。欢迎提交 Issue 和 PR!
