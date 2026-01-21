# Prometheus Alertmanager Webhook Service

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

一个基于 FastAPI 的 webhook 服务，用于接收 Prometheus Alertmanager 的告警通知，并通过钉钉机器人推送格式化的告警消息。支持智能模板选择，提供多种告警类型的专用模板。

## ✨ 功能特性

- 🚀 **高性能**：基于 FastAPI 的异步 Web 服务
- 📱 **钉钉集成**：支持钉钉机器人 webhook，包含安全加签验证
- 🎨 **智能模板**：根据告警类型自动选择合适的 Jinja2 模板
- 🔧 **灵活配置**：环境变量配置，支持多种部署方式
- 📊 **丰富模板**：
  - 通用告警模板
  - SSL 证书过期提醒模板
  - 服务宕机告警模板
- 🛡️ **安全可靠**：支持 HTTPS、请求验证和错误处理
- 📝 **详细日志**：完整的请求和响应日志记录

## 🚀 快速开始

### 打包

```
make install
```

```
make build-linux
```