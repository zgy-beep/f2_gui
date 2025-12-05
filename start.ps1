<#
PowerShell 启动脚本（中文版）for f2_gui
功能：
 - 菜单：启动 GUI / 检查环境 / 配置环境 / 退出
 - 使用 conda 检查/创建环境，优先使用 `conda run` 执行包安装与启动
 - 设计为在 PowerShell 下运行（.ps1）
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# 尝试将 PowerShell 控制台输出编码设置为 UTF-8，避免 conda 打印时出现编码错误
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8

function Write-Info { param($msg) Write-Host $msg -ForegroundColor Cyan }
function Write-Warn { param($msg) Write-Host $msg -ForegroundColor Yellow }
function Write-Err  { param($msg) Write-Host $msg -ForegroundColor Red }

function Check-Conda {
    Write-Info '检查 conda 是否可用...'
    if (-not (Get-Command conda -ErrorAction SilentlyContinue)) {
        Write-Err '错误：未找到 conda，请先安装 Anaconda/Miniconda，并运行 `conda init powershell`（只需一次）。'
        return $false
    }
    return $true
}

function Env-Exists {
    $envs = & conda info --envs 2>&1
    if ($LASTEXITCODE -ne 0) { return $false }
    foreach ($line in $envs) {
        if ($line -match '^\s*f2_gui\s') { return $true }
    }
    return $false
}

function Check-Packages {
    Write-Info '检查 PyQt6 是否已安装（在 f2_gui 环境中）...'
    & conda run -n f2_gui python -c "import PyQt6" > $null 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Warn '必需包缺失: PyQt6'
    } else {
        Write-Info '必需包已安装: PyQt6'
    }
}

function Check-F2Core {
    Write-Info '检查 f2 核心包是否已安装（在 f2_gui 环境中）...'
    & conda run -n f2_gui python -c "import f2" > $null 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Warn 'f2 核心功能未安装'
    } else {
        Write-Info 'f2 核心功能已安装'
    }
}

function Setup-EnvInternal {
    Write-Info '检查 f2_gui 环境是否存在...'
    if (-not (Env-Exists)) {
        Write-Info '创建 f2_gui 环境... (python=3.11)'
        & conda create -n f2_gui python=3.11 -y
        if ($LASTEXITCODE -ne 0) { Write-Err '错误：创建环境失败'; return $false }
    } else {
        Write-Info '环境已存在，跳过创建。'
    }

    Write-Info '检查并安装 PyQt6（使用 conda run 回退）...'
    & conda run -n f2_gui python -c "import PyQt6" > $null 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Info '安装 PyQt6...'
        & conda run -n f2_gui pip install PyQt6
        if ($LASTEXITCODE -ne 0) { Write-Err '错误：PyQt6 安装失败'; return $false }
    } else {
        Write-Info 'PyQt6 已存在'
    }

    Write-Info '检查并安装本地 f2 包（开发模式）...'
    & conda run -n f2_gui python -c "import f2" > $null 2>&1
    if ($LASTEXITCODE -ne 0) {
        $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
        Push-Location $scriptDir
        Write-Info "在 $scriptDir 运行: pip install -e ."
        & conda run -n f2_gui pip install -e .
        $ret = $LASTEXITCODE
        Pop-Location
        if ($ret -ne 0) { Write-Err '错误：f2 核心功能安装失败'; return $false }
    } else {
        Write-Info 'f2 核心功能已存在'
    }

    return $true
}

function Start-AppInternal {
    Write-Info '尝试使用 conda run 在 f2_gui 环境中启动程序...'
    # 设置 Python 使用 UTF-8 模式并禁用 conda 对子进程输出的捕获，
    # 避免 conda 在打印捕获输出时因控制台编码为 GBK 导致 UnicodeEncodeError
    $env:PYTHONUTF8 = '1'
    & conda run -n f2_gui --no-capture-output python -u -m f2.gui
    if ($LASTEXITCODE -ne 0) {
        Write-Err "错误：程序启动失败，退出代码 $LASTEXITCODE"
        return $false
    }
    Write-Info '程序已退出（或成功结束）。'
    return $true
}

function Show-Menu {
    Write-Host "==================== F2 GUI 启动工具 ====================" -ForegroundColor Green
    Write-Host ""
    Write-Host "请选择操作:"
    Write-Host "1. 启动 GUI"
    Write-Host "2. 检查环境"
    Write-Host "3. 配置环境"
    Write-Host "4. 退出"
}

# 主循环
while ($true) {
    Show-Menu
    $choice = Read-Host '请输入选项 (1-4，默认为1)'
    if ([string]::IsNullOrWhiteSpace($choice)) { $choice = '1' }

    switch ($choice) {
        '1' {
            if (-not (Check-Conda)) { break }
            # 直接调用 Start-AppInternal，避免使用 Out-Null 丢弃输出
            Start-AppInternal
            break
        }
        '2' {
            if (-not (Check-Conda)) { break }
            if (Env-Exists) {
                Write-Info '环境 f2_gui 已存在'
                Check-Packages
                Check-F2Core
            } else {
                Write-Warn '环境 f2_gui 不存在'
            }
            Read-Host '按回车返回菜单'
            Clear-Host
            break
        }
        '3' {
            if (-not (Check-Conda)) { break }
            if (Setup-EnvInternal) {
                Write-Info '环境配置完成'
            }
            Read-Host '按回车返回菜单'
            Clear-Host
            break
        }
        '4' {
            Write-Info '再见!'
            break
        }
        Default {
            Write-Warn '无效选项，请重新输入。'
            break
        }
    }

    if ($choice -eq '4') { break }
}

exit 0
