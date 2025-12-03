# GUI v02 开发文档

## 架构说明

### 整体架构

GUI v02 采用经典的 MVC (Model-View-Controller) 架构:

```
┌─────────────────────────────────────────────┐
│              Views (视图层)                  │
│  - MainWindow: 主窗口                       │
│  - HomePage: 首页                           │
│  - SettingsPage: 设置页                     │
└──────────────┬──────────────────────────────┘
               │
               │ 用户交互
               ↓
┌─────────────────────────────────────────────┐
│          Controllers (控制器层)              │
│  - DownloadController: 下载控制              │
│  - TaskManager: 任务管理                     │
└──────────────┬──────────────────────────────┘
               │
               │ 数据交互
               ↓
┌─────────────────────────────────────────────┐
│            F2 Core API                       │
│  - DouyinHandler                            │
│  - TiktokHandler                            │
│  - WeiboHandler                             │
│  - TwitterHandler                           │
└─────────────────────────────────────────────┘
```

### 组件说明

#### 1. Components (组件层)

可复用的 UI 组件,遵循单一职责原则:

- **BaseCard**: 基础卡片组件,提供统一的卡片样式
- **StatCard**: 统计卡片,用于显示数值统计
- **DownloadTaskCard**: 下载任务卡片,显示任务进度

#### 2. Views (视图层)

用户界面的主要页面:

- **MainWindow**: 主窗口,包含侧边栏导航和页面堆栈
- **HomePage**: 首页,包含任务创建和任务列表
- **SettingsPage**: 设置页,管理应用配置

#### 3. Controllers (控制器层)

业务逻辑处理和 F2 API 交互:

- **DownloadController**: 管理下载任务的生命周期
- **TaskManager**: 任务状态和队列管理

#### 4. Utils (工具层)

辅助工具类:

- **ConfigManager**: 配置文件的读写
- **GUILogger**: 日志管理和显示

#### 5. Themes (主题层)

主题系统管理:

- **ThemeManager**: 主题切换和样式表生成

## 数据流

### 下载任务流程

```
用户输入
  ↓
HomePage 收集参数
  ↓
DownloadController.start_download()
  ↓
创建 DownloadWorker (QThread)
  ↓
调用 F2 API (异步)
  ↓
发送进度信号
  ↓
更新 DownloadTaskCard
  ↓
任务完成/失败
  ↓
更新统计信息
```

### 配置管理流程

```
应用启动
  ↓
ConfigManager.load()
  ↓
读取 gui_config.json
  ↓
应用配置到各个组件
  ↓
用户修改设置
  ↓
SettingsPage.save_settings()
  ↓
ConfigManager.save()
  ↓
写入 gui_config.json
```

## 信号与槽

### 主要信号

#### ThemeManager
- `theme_changed(str)`: 主题改变时发出

#### DownloadController
- `task_added(str)`: 任务添加
- `task_removed(str)`: 任务移除
- `task_progress(str, int, int)`: 进度更新
- `task_finished(str)`: 任务完成
- `task_error(str, str)`: 任务错误

#### DownloadTaskCard
- `cancel_requested()`: 取消请求
- `pause_requested()`: 暂停请求
- `resume_requested()`: 继续请求

## 与 F2 核心 API 的集成

### 调用示例

```python
# 在 DownloadController 中
async def _download(self):
    """执行下载"""
    if self.platform == "douyin":
        from f2.apps.douyin.handler import DouyinHandler
        
        # 创建处理器
        handler = DouyinHandler()
        
        # 根据模式调用不同方法
        if self.mode == "post":
            await handler.fetch_user_post_videos(
                sec_user_id=self.url,
                max_count=self.config.get("max_counts", 0)
            )
        # ... 其他模式
```

### 需要实现的接口

1. **用户信息获取**: 根据链接解析用户ID
2. **作品列表获取**: 获取用户的作品列表
3. **下载进度回调**: 实时更新下载进度
4. **错误处理**: 处理网络错误、解析错误等

## 样式系统

### Material Design 3 色彩

使用 MD3 的色彩角色系统:

- **Primary**: 主要颜色,用于按钮、重要元素
- **Secondary**: 次要颜色,用于辅助元素
- **Tertiary**: 第三色,用于强调
- **Error**: 错误颜色
- **Surface**: 表面色,用于卡片、对话框
- **Background**: 背景色

### 组件样式

所有组件通过 QSS (Qt Style Sheets) 设置样式,统一管理在 `ThemeManager.generate_stylesheet()` 中。

## 性能优化

### 1. 异步下载

使用 `QThread` 避免阻塞 UI 线程:

```python
worker = DownloadWorker(...)
worker.moveToThread(thread)
thread.started.connect(worker.run)
```

### 2. 虚拟滚动

对于大量任务,考虑使用虚拟滚动(未实现):

```python
# 仅渲染可见区域的任务卡片
visible_tasks = self.get_visible_tasks()
for task in visible_tasks:
    card = DownloadTaskCard(task)
    self.tasks_layout.addWidget(card)
```

### 3. 日志限制

限制日志条目数量,避免内存溢出:

```python
class GUILogger:
    def __init__(self, max_messages: int = 1000):
        self.max_messages = max_messages
```

## 测试

### 单元测试

```bash
# 运行测试
pytest tests/gui_v02/

# 测试覆盖率
pytest --cov=f2.gui_v02 tests/gui_v02/
```

### 手动测试清单

- [ ] 主题切换功能
- [ ] 新建下载任务
- [ ] 暂停/继续/取消下载
- [ ] 设置保存和加载
- [ ] 多任务并发下载
- [ ] 错误处理
- [ ] 日志显示

## 常见问题

### Q: 如何添加新的下载平台?

A: 
1. 在 `config.py` 添加平台配置
2. 在 `DownloadController` 中添加对应的处理逻辑
3. 调用 F2 相应的 Handler

### Q: 如何自定义主题颜色?

A: 编辑 `config.py` 中的 `COLORS` 字典

### Q: 下载进度如何更新?

A: 通过 `DownloadWorker` 的信号机制,实时发送进度

## 未来规划

1. **更多平台支持**: 添加 YouTube、Instagram 等
2. **插件系统**: 允许第三方扩展
3. **云同步**: 配置和历史记录云同步
4. **移动端**: 开发移动端应用
5. **Web 版本**: 提供 Web 界面

---

最后更新: 2025-11-27
