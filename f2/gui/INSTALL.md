# GUI v02 启动脚本

## Windows 启动脚本

创建一个 `run_gui.bat` 文件:

```batch
@echo off
cd /d %~dp0
python -m f2.gui_v02
pause
```

## Linux/Mac 启动脚本

创建一个 `run_gui.sh` 文件:

```bash
#!/bin/bash
cd "$(dirname "$0")"
python3 -m f2.gui_v02
```

然后添加执行权限:
```bash
chmod +x run_gui.sh
```

## 使用说明

1. 将对应的启动脚本放在 `f2` 项目根目录
2. 双击运行即可启动 GUI
