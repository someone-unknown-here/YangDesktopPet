# 一款基于羊羊不吃草的桌宠

一个基于羊羊不吃草的 Python 桌宠项目，支持角色动画、对话气泡、状态管理等功能。

The English version of the README can be found below the Mandarin version.

---

## 项目简介

本项目实现了一个设定源于羊羊不吃草的桌宠，具备以下能力：

* 动态角色展示（不同动作与状态）
* 对话气泡
* 行为状态管理
* 基于配置文件的行为控制
* 用户交互支持（点击、拖动等）

程序运行后，会在桌面上显示一个可交互的角色窗口。

桌宠具体使用教程和介绍请看抖音视频。

## 环境要求

* Python 3.11
* 项目依赖的第三方库（如 `PySide6` 等）。见 `requirements.txt`。

可使用以下命令搭建环境：
```bash
pip install -r requirements.txt
```

建议使用 **Python 3.11** 运行本项目。
使用其他 Python 版本可能会导致兼容性问题，例如类型注解或第三方库行为不一致，从而引发运行错误。

## 运行方式

请注意：程序的入口文件为 `main.py`。

在命令行中运行：

```bash
py -3.11 main.py
```

**请确保在包含 `main.py` 的目录下运行程序。**

这样可以保证资源文件夹（如 `assets/`、`states/`）能够被正确加载。

## 程序运行流程（简要）

1. 通过 `main.py` 启动程序
2. 初始化主窗口（MainWindow）
3. 加载配置、资源与对话系统
4. 创建运行时状态（RuntimeState）
5. 进入主循环：

   * 更新动画
   * 处理用户交互
   * 更新状态
   * 显示对话

## License

本项目仅供学习和个人使用。

---

# A Desktop Pet Based on “羊羊不吃草”

A Python-based desktop pet project inspired by “羊羊不吃草”, featuring character animations, dialogue bubbles, and state management.

---

## Overview

This project implements a desktop companion character inspired by “羊羊不吃草”, with the following features:

* Animated character with multiple actions and states
* Dialogue bubble display
* Behavior and state management
* Configurable behavior via configuration files
* User interaction support (clicking, dragging, etc.)

After launching the program, an interactive character window will appear on the desktop.

---

## Requirements

* Python 3.11
* Required third-party libraries (e.g., `PySide6`). See `requirements.txt` for details.

The library environment can be built with the following command:
```bash
pip install -r requirements.txt
```

This project is developed with **Python 3.11** and is intended to be run using this version.

Using other Python versions may lead to compatibility issues, such as differences in type hint handling or third-party library behavior.

---

## Usage

The entry point of the program is `main.py`.

Run the following command in your terminal:

```bash
py -3.11 main.py
```

**Make sure to run the program from the directory containing `main.py`.**

This ensures that resource folders (such as `assets/` and `states/`) are correctly located and loaded.

---

## Program Flow (Simplified)

1. Start the program via `main.py`
2. Initialize the main window (`MainWindow`)
3. Load configuration, assets, and dialogue system
4. Create the runtime state (`RuntimeState`)
5. Enter the main loop:

   * Update animations
   * Handle user interactions
   * Update state
   * Display dialogue

---

## License

This project is for learning and personal use only.