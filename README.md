# FDE 学习项目：城市天气数据应用

![tests](https://github.com/dadaguai19405-art/fde-learning/actions/workflows/tests.yml/badge.svg)

这是一个从零开始学习 Forward Deployed Engineer（FDE）的实践项目，覆盖 Python 基础、数据处理、SQLite、外部 API、Streamlit 网页和云端部署。

## 在线演示

[打开城市天气应用](https://fde-learning-bwfhebreaterkqtryda9co.streamlit.app/)

## 功能

- 选择上海、北京、深圳三个城市
- 调用 Open-Meteo 公开天气 API 获取实时温度和风速
- 将每次观测写入 SQLite 数据库
- 展示当前天气、最近记录和温度趋势图
- 网页和命令行共用同一份任务/天气数据

## 技术栈

- Python 3.x
- requests
- SQLite
- pandas
- Streamlit
- Git / GitHub
- Streamlit Community Cloud

## 质量检查

- pytest：34 个测试
- 覆盖率：84.62%，最低门槛 70%
- ruff：代码检查通过
- GitHub Actions：每次 push 自动运行 lint 和测试

本地运行：

```powershell
ruff check .
python -m pytest -q
```

## 数据链路

```text
Open-Meteo API
      ↓
requests 获取 JSON
      ↓
解析天气字段
      ↓
SQLite 保存历史记录
      ↓
Streamlit 页面展示
      ↓
浏览器访问
```

## 运行方法

安装依赖：

```powershell
pip install -r requirements.txt
```

启动天气网页：

```powershell
streamlit run day04/weather_web.py
```

启动任务清单网页：

```powershell
streamlit run day03/task_manager_web_sql.py
```

运行任务清单命令行版：

```powershell
python day03/task_manager_sql.py
```

## 项目结构

```text
day01/   Python 基础、密码检查器
day02/   列表、字典、JSON、任务清单
day03/   SQLite、任务清单网页版
day04/   天气 API、城市选择、趋势图
```

## 学习记录

### 2026-10-19

- 安装并验证 Python、VS Code、Git
- 完成第一个 Python 脚本
- 学会变量、输入输出、条件判断、异常处理

### 2026-10-20

- 完成密码检查器和任务清单
- 学习列表、字典、JSON、SQLite
- 完成天气 API 取数和 Streamlit 页面
- 将项目推送到 GitHub 并部署到 Streamlit Community Cloud

### 2026-10-21

- 增加多城市选择和温度趋势图
- 修复 Streamlit 弃用警告
- 完成线上部署和访问地址确认

## 说明

云端 SQLite 数据是临时的，应用重启后历史记录可能被清空。真实交付场景应使用 Supabase、PostgreSQL 或其他托管数据库。
