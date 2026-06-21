# 宠物服务管理平台

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Django](https://img.shields.io/badge/Django-4.2-green)
![Database](https://img.shields.io/badge/Database-MySQL%208.0-orange)

## 项目介绍

本项目是一个基于 Python Django 开发的宠物服务管理平台，面向数据库课程设计与作品集展示场景。系统围绕宠物主人、商家和平台管理员三类角色，完成宠物服务浏览、商家入驻审核、服务发布审核、订单预约、评价管理、疫苗记录与提醒等核心业务流程。

项目重点放在关系型数据库建模与 Web 业务闭环上：通过自定义用户模型、外键关联、唯一约束、索引、订单状态流转和评分重算逻辑，展示一个较完整的 Django + MySQL 管理系统。

## 技术栈

| 模块 | 技术 |
| --- | --- |
| 后端框架 | Python 3.12、Django 4.2 |
| 数据库 | MySQL 8.0、PyMySQL |
| 前端页面 | Django Templates、Bootstrap 5 |
| 数据采集 | 高德地图 Web API、Python requests |
| 开发工具 | Git、pip、virtualenv |

## 环境要求

- Windows、Linux 或 macOS
- Python 3.12
- MySQL 8.0 或兼容版本
- pip 20.0+

## 安装与运行

### 1. 克隆项目

```bash
git clone <your-repository-url>
cd project
```

### 2. 创建并激活虚拟环境

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source .venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置数据库

复制 `.env.example` 为 `.env`，或在终端中设置同名环境变量。默认数据库配置如下：

```text
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_DATABASE=pet_service_db
MYSQL_USER=root
MYSQL_PASSWORD=
```

在 MySQL 中创建数据库：

```sql
CREATE DATABASE pet_service_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. 初始化数据表

```bash
python manage.py migrate
```

### 6. 启动开发服务器

```bash
python manage.py runserver
```

启动后访问 `http://127.0.0.1:8000/`。

## 核心功能

| 功能模块 | 说明 |
| --- | --- |
| 用户与角色 | 支持宠物主人、商家、管理员三类角色，不同角色进入不同工作台 |
| 商家管理 | 商家注册、资料维护、平台审核、服务状态管理 |
| 服务管理 | 服务分类、服务发布、启用/停用、列表筛选与详情展示 |
| 订单流程 | 宠物主人预约服务，商家确认，订单支付/完成/取消 |
| 评价体系 | 用户评价服务，系统自动维护商家平均评分 |
| 宠物档案 | 维护宠物基础信息、疫苗记录和疫苗到期提醒 |
| 收藏功能 | 宠物主人可收藏常用商家，便于再次访问 |

## 项目目录结构

```text
project/
|-- manage.py                         # Django 命令入口
|-- requirements.txt                  # Python 依赖清单
|-- README.md                         # 项目说明文档
|-- .env.example                      # 环境变量示例
|-- pet_service_project/              # Django 项目配置目录
|   |-- settings.py                   # 全局配置、数据库、模板、静态资源
|   |-- urls.py                       # 全局 URL 路由
|   |-- asgi.py                       # ASGI 部署入口
|   |-- wsgi.py                       # WSGI 部署入口
|-- pet_core/                         # 核心业务应用
|   |-- models.py                     # 数据模型与约束定义
|   |-- urls.py                       # 应用路由
|   |-- forms.py                      # 表单校验
|   |-- auth_views.py                 # 登录、注册、退出
|   |-- owner_views.py                # 宠物主人相关页面
|   |-- merchant_views.py             # 商家相关页面
|   |-- admin_views.py                # 平台管理员相关页面
|   |-- public_views.py               # 首页、列表、详情等公开页面
|   |-- ratings.py                    # 评分重算逻辑
|   |-- vaccine_logic.py              # 疫苗提醒逻辑
|   |-- templates/pet_core/           # 页面模板
|   |-- static/pet_core/              # 应用静态资源
|   |-- migrations/                   # 数据库迁移文件
|-- scripts/                          # 数据采集与辅助脚本
|   |-- pet_service_crawler.py        # 高德地图宠物服务数据采集脚本
|   |-- README.md                     # 爬虫脚本说明
|-- data/
|   |-- final_data/                   # 本地 CSV/ZIP 数据集，默认不提交到 Git
|-- docs/                             # 课程设计、复盘和补充文档
```

## 数据库设计说明

核心数据表围绕以下实体展开：

- `User`、`PetOwner`、`Merchant`、`Administrator`
- `Pet`、`Vaccine`、`VaccineRecord`
- `ServiceCategory`、`Service`
- `Order`、`VaccineOrderDetail`
- `Review`、`FavoriteStore`

项目通过迁移文件维护表结构，并为常见查询场景添加索引，例如商家地区与分类筛选、服务状态筛选、订单查询、疫苗提醒查询等。

## 常用开发命令

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py test pet_core
python manage.py createsuperuser
```

查看迁移生成的 SQL：

```bash
python manage.py sqlmigrate pet_core 0001
```

## 数据采集说明

`scripts/pet_service_crawler.py` 用于通过高德地图 API 采集宠物服务商家数据。使用前需要申请高德地图 Key，并按照 `scripts/README.md` 中的说明配置脚本。

采集生成的原始数据、导出的 CSV/ZIP 和本地数据库文件属于运行时数据，默认不提交到 Git 仓库。

## 可扩展方向

- [ ] 增加后台图表看板，展示订单量、商家评分、服务分类占比等统计数据
- [ ] 增加 CSV/Excel 数据导入导出功能
- [ ] 接入在线支付或模拟支付流水
- [ ] 增加更细粒度的权限控制和操作日志
- [ ] 补充 Docker 部署与生产环境配置文档

## GitHub 发布注意事项

发布到 GitHub 前，请确认没有提交以下内容：

- `.env`、数据库密码、API Key 等敏感配置
- `db.sqlite3`、MySQL 导出文件等本地数据库
- `*.log`、`*.err`、`*.pid` 等运行日志
- `data/final_data/` 下的大体积数据文件
