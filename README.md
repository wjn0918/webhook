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

### 环境要求

- Python 3.12+
- pip (Python 包管理器)

### 安装步骤

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd webhook
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **配置环境变量**
   ```bash
   cp .env.template .env
   ```

   编辑 `.env` 文件，配置以下参数：
   ```env
   # 钉钉机器人 webhook URL
   DINGTALK_WEBHOOK_URL=https://oapi.dingtalk.com/robot/send?access_token=YOUR_ACCESS_TOKEN

   # 钉钉机器人 secret（用于加签安全模式）
   DINGTALK_SECRET=YOUR_SECRET

   # 服务器配置
   HOST=0.0.0.0
   PORT=8000
   ```

5. **启动服务**
   ```bash
   python main.py
   ```

服务将在 `http://localhost:8000` 启动。

## 📖 使用方法

### 1. 配置 Prometheus Alertmanager

在 Alertmanager 配置文件中添加 webhook 接收器：

```yaml
route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'webhook'

receivers:
- name: 'webhook'
  webhook_configs:
  - url: 'http://your-server:8000/webhook'
    send_resolved: true
```

### 2. 配置钉钉机器人

1. 在钉钉群中添加机器人
2. 设置安全模式为 "加签"
3. 复制 webhook URL 和 secret 到 `.env` 文件

### 3. 测试告警

发送测试请求到 webhook 端点：

```bash
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "alerts": [{
      "status": "firing",
      "labels": {
        "alertname": "Test Alert",
        "severity": "warning"
      },
      "annotations": {
        "summary": "This is a test alert",
        "description": "Test description"
      }
    }]
  }'
```

## 🎨 模板系统

服务支持智能模板选择，根据告警内容自动选择合适的模板：

### 模板类型

1. **证书过期模板** (`certificate_expiry_template.j2`)
   - 适用于 TLS/SSL 证书即将过期告警
   - 关键词：`tls`, `证书`, `ssl`, `certificate`, `过期`, `expiry`

2. **服务宕机模板** (`service_down_template.j2`)
   - 适用于服务不可用告警
   - 关键词：`down`, `宕机`, `unreachable`, `unavailable`, `故障`, `failed`

3. **通用告警模板** (`alert_template.j2`)
   - 默认模板，用于其他类型告警

### 自定义模板

在 `templates/` 目录下创建新的 `.j2` 文件，然后修改 `main.py` 中的 `select_template()` 函数添加新的模板选择逻辑。

## 📋 API 接口

### GET /

健康检查端点

**响应：**
```json
{
  "message": "Webhook service is running",
  "status": "healthy"
}
```

### POST /webhook

接收 Alertmanager 告警的主端点

**请求体：** Alertmanager webhook 格式

**响应：**
```json
{
  "status": "success",
  "message": "Alert notification sent to DingTalk"
}
```

### GET /health

详细健康检查

**响应：**
```json
{
  "status": "healthy"
}
```

## 🔧 配置说明

### 环境变量

| 变量名 | 必需 | 默认值 | 描述 |
|--------|------|--------|------|
| `DINGTALK_WEBHOOK_URL` | 是 | - | 钉钉机器人 webhook URL |
| `DINGTALK_SECRET` | 否 | - | 钉钉机器人 secret（加签模式） |
| `HOST` | 否 | `0.0.0.0` | 服务器监听地址 |
| `PORT` | 否 | `8000` | 服务器监听端口 |

### 钉钉配置

1. 访问 [钉钉开发者后台](https://open.dingtalk.com/)
2. 创建机器人应用
3. 配置 webhook URL
4. 启用 "加签" 安全模式
5. 获取 access_token 和 secret

## 🐳 Docker 部署

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main.py"]
```

```bash
docker build -t alertmanager-webhook .
docker run -p 8000:8000 --env-file .env alertmanager-webhook
```

## 📝 开发

### 项目结构

```
webhook/
├── main.py                 # 主应用文件
├── requirements.txt        # Python 依赖
├── .env.template          # 环境变量模板
├── templates/             # Jinja2 模板目录
│   ├── alert_template.j2
│   ├── certificate_expiry_template.j2
│   └── service_down_template.j2
└── README.md
```

### 本地开发

```bash
# 安装开发依赖
pip install -r requirements.txt

# 运行测试
python -m pytest

# 代码格式化
pip install black
black .
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙋‍♂️ 支持

如果您遇到问题或有建议，请：

- 提交 [GitHub Issue](https://github.com/your-repo/issues)
- 查看 [文档](https://github.com/your-repo/wiki)
- 发送邮件至 maintainer@example.com

---

⭐ 如果这个项目对你有帮助，请给它一个星标！
