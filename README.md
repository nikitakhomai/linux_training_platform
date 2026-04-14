# 🛡️ Linux Security Training Platform

## Платформа практико-ориентированного обучения безопасности операционных систем на базе ядра Linux

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Kubernetes](https://img.shields.io/badge/kubernetes-%23326ce5.svg?style=for-the-badge&logo=kubernetes&logoColor=white)](https://kubernetes.io)
[![PostgreSQL](https://img.shields.io/badge/postgresql-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)](https://reactjs.org)

---

## 📋 Оглавление
- [О проекте](#о-проекте)
- [Архитектура](#архитектура)
- [Технологический стек](#технологический-стек)
- [Микросервисы](#микросервисы)
- [Текущий статус](#текущий-статус)
- [План разработки](#план-разработки)
- [Быстрый старт](#быстрый-старт)
- [API Документация](#api-документация)
- [Структура проекта](#структура-проекта)
- [Команда](#команда)
- [Лицензия](#лицензия)

---

## 🎯 О проекте

**Linux Security Training Platform** — это специализированная образовательная платформа для практико-ориентированного обучения навыкам обеспечения безопасности операционных систем на базе ядра Linux.

### 🚨 Проблематика

| Проблема | Решение |
|----------|---------|
| ❌ Разрыв между академическими знаниями и требованиями работодателей | ✅ Реалистичные лабораторные среды с реальными сценариями |
| ❌ Отсутствие автоматизированной проверки сложных конфигураций | ✅ Продвинутая система валидации состояния системы |
| ❌ Сложность масштабирования лабораторных работ | ✅ Kubernetes-нативная архитектура |
| ❌ Нет единого стандарта обучения безопасности Linux | ✅ Соответствие CIS Benchmarks, NIST CSF, STIG |

### 🎓 Целевая аудитория

- **Студенты** технических специальностей (Информационная безопасность, Прикладная информатика)
- **Начинающие специалисты** по безопасности Linux
- **Преподаватели** вузов и центров дополнительного образования
- **Корпоративные учебные центры**

---

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────────────────────┐
│                         API Gateway (NGINX)                         │
│                      http://platform.local/api/*                    │
└─────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────┐         ┌───────────────┐         ┌───────────────┐
│  Auth Service │         │  Task Service │         │  Check Service│
│    :8000      │◄────────┤    :8001      │◄────────┤    :8002      │
│  FastAPI      │         │  FastAPI      │         │  FastAPI      │
└───────────────┘         └───────────────┘         └───────────────┘
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────┐         ┌───────────────┐         ┌───────────────┐
│  PostgreSQL   │         │  PostgreSQL   │         │   Redis       │
│   auth_db     │         │   task_db     │         │   cache       │
└───────────────┘         └───────────────┘         └───────────────┘
                                    │
                                    ▼
                          ┌─────────────────┐
                          │   Kubernetes    │
                          │   Cluster       │
                          └─────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
            ┌───────────────┐               ┌───────────────┐
            │   Task Pods   │               │  Validation   │
            │   Containers  │               │   Scripts     │
            └───────────────┘               └───────────────┘
```

### 🔬 Ключевые архитектурные решения

| Решение | Обоснование |
|---------|-------------|
| **Микросервисная архитектура** | Независимое масштабирование, изоляция отказов, разделение ответственности |
| **Kubernetes оркестрация** | Промышленный стандарт, автоскейлинг, самовосстановление, продвинутые сетевые политики |
| **FastAPI** | Асинхронность, высокая производительность, автодокументация, интеграция с K8s API |
| **PostgreSQL + Redis** | ACID транзакции для прогресса студентов, in-memory кэш для токенов и сессий |
| **GitOps (ArgoCD)** | Декларативное управление, контроль версий конфигураций, быстрый откат |

---

## 🛠️ Технологический стек

### Бэкенд
| Технология | Версия | Назначение |
|------------|--------|------------|
| Python | 3.11+ | Основной язык разработки |
| FastAPI | 0.104+ | REST API фреймворк |
| SQLAlchemy | 2.0+ | ORM для работы с БД |
| Alembic | 1.12+ | Миграции баз данных |
| Pydantic | 2.5+ | Валидация данных |
| python-jose | 3.3+ | JWT токены |
| bcrypt | 4.1+ | Хэширование паролей |
| httpx | 0.25+ | HTTP клиент для межсервисного взаимодействия |

### Инфраструктура
| Технология | Версия | Назначение |
|------------|--------|------------|
| Kubernetes | 1.28+ | Оркестрация контейнеров |
| Docker | 24.0+ | Контейнеризация |
| PostgreSQL | 15+ | Реляционная база данных |
| Redis | 7+ | Кэширование, сессии |
| Nginx | 1.25+ | API Gateway, reverse proxy |
| Prometheus | 2.45+ | Сбор метрик |
| Grafana | 10+ | Визуализация метрик |
| ArgoCD | 2.8+ | GitOps непрерывная доставка |

### Фронтенд (планируется)
| Технология | Версия | Назначение |
|------------|--------|------------|
| React | 18+ | UI библиотека |
| TypeScript | 5+ | Типизированный JavaScript |
| Vite | 5+ | Сборщик проекта |
| TailwindCSS | 3+ | Стилизация |
| xterm.js | 5+ | Веб-терминал |
| WebSocket | - | Реальное время |

---

## 🧩 Микросервисы

### ✅ **Auth Service** (Порт: 8000) — **ГОТОВО**

Сервис аутентификации и управления пользователями.

**Функционал:**
- ✅ Регистрация пользователей
- ✅ JWT аутентификация (access + refresh токены)
- ✅ Ролевая модель (student, teacher, admin)
- ✅ Интеграция с PostgreSQL
- ✅ Интеграция с Redis (кэш, blacklist токенов)
- ✅ Swagger документация (/docs)

**Модели данных:**
```python
User:
  - id: int
  - email: str (unique)
  - username: str (unique)
  - full_name: str
  - hashed_password: str
  - role: enum(STUDENT, TEACHER, ADMIN)
  - is_active: bool
  - is_verified: bool
  - timestamps: created_at, updated_at, last_login
```

**API Endpoints:**
| Метод | Endpoint | Описание | Доступ |
|-------|----------|----------|--------|
| POST | `/auth/register` | Регистрация | public |
| POST | `/auth/login` | Вход | public |
| POST | `/auth/refresh` | Обновление токена | public |
| POST | `/auth/logout` | Выход | auth |
| GET | `/users/me` | Информация о себе | auth |
| GET | `/users/` | Список пользователей | admin |
| GET | `/users/{id}` | Пользователь по ID | admin |

---

### 🚧 **Task Service** (Порт: 8001) — **В РАЗРАБОТКЕ**

Сервис управления заданиями и курсами.

**Функционал:**
- ✅ Базовая структура проекта
- ✅ Модели данных (Task, Course, Category)
- ✅ Pydantic схемы
- ✅ CRUD операции
- ✅ Интеграция с Auth Service (проверка токенов)
- 🔄 Dockerfile
- 🔄 docker-compose
- 🔄 API эндпоинты

**Модели данных:**
```python
Category:
  - id: int
  - name: str
  - description: str
  - icon: str

Course:
  - id: int
  - title: str
  - description: str
  - difficulty: str (beginner, intermediate, advanced)
  - category_id: int (FK)
  - order: int
  - is_published: bool
  - estimated_time_minutes: int

Task:
  - id: int
  - title: str
  - description: str
  - task_type: str (hardening, audit, penetration, configuration, monitoring)
  - course_id: int (FK)
  - order_in_course: int
  - docker_image: str
  - docker_command: str
  - config: JSON
  - validation_script: str
  - hint_script: str
  - points: int
  - difficulty: str (easy, medium, hard)
  - estimated_time_minutes: int
  - is_published: bool
  - is_template: bool
```

**Планируемые API Endpoints:**
| Метод | Endpoint | Описание | Доступ |
|-------|----------|----------|--------|
| GET | `/tasks/` | Список заданий | auth |
| GET | `/tasks/{id}` | Задание по ID | auth |
| POST | `/tasks/` | Создать задание | admin |
| PUT | `/tasks/{id}` | Обновить задание | admin |
| DELETE | `/tasks/{id}` | Удалить задание | admin |
| GET | `/courses/` | Список курсов | auth |
| GET | `/categories/` | Список категорий | auth |

---

### ⏳ **Check Service** (Порт: 8002) — **ПЛАНИРУЕТСЯ**

Сервис проверки решений студентов. **Ключевая инновация платформы!**

**Функционал:**
- ⏳ Валидация конфигурационных файлов (SSH, PAM, sudoers, auditd)
- ⏳ Проверка системных состояний (процессы, порты, модули ядра)
- ⏳ Сравнение с эталонными конфигурациями (CIS Benchmarks, STIG)
- ⏳ Динамические проверочные скрипты внутри контейнеров
- ⏳ Детальная обратная связь с анализом ошибок

**Отличия от CTF-платформ:**
| Платформа | Тип проверки | Обратная связь |
|-----------|--------------|----------------|
| CTFd/GZCTF | Статические флаги | ✅/❌ |
| TryHackMe | Флаги + скрипты | ❌ Минимальная |
| HackTheBox | Только флаги | ❌ |
| **Наша платформа** | **Анализ состояния системы** | **✅ Детальный анализ ошибок** |

---

### ⏳ **Progress Service** (Порт: 8003) — **ПЛАНИРУЕТСЯ**

Сервис отслеживания прогресса и аналитики.

**Функционал:**
- ⏳ Матрица компетенций по категориям навыков
- ⏳ Отслеживание выполнения заданий
- ⏳ Визуализация прогресса
- ⏳ Персонализированные рекомендации
- ⏳ Анализ типичных ошибок

---

### ⏳ **Orchestration Service** (Порт: 8004) — **ПЛАНИРУЕТСЯ**

Сервис управления лабораторными средами в Kubernetes.

**Функционал:**
- ⏳ Динамическое создание/удаление Kubernetes namespaces
- ⏳ Запуск контейнеров с заданиями
- ⏳ Управление ресурсами (CPU, RAM, Storage)
- ⏳ Сетевая изоляция (Network Policies)
- ⏳ Мониторинг состояния

---

### ⏳ **Frontend** (Порт: 3000) — **ПЛАНИРУЕТСЯ**

Веб-интерфейс платформы.

**Функционал:**
- ⏳ Страница входа/регистрации
- ⏳ Каталог заданий и курсов
- ⏳ Встроенный веб-терминал (xterm.js)
- ⏳ Личный кабинет с прогрессом
- ⏳ Панель администратора
- ⏳ Панель преподавателя

---

## 📊 Текущий статус

### ✅ **Завершено (Этап 1):**
- [x] Исследование 9 существующих платформ (CmdChallenge, OverTheWire, Linux Journey, Cyber SecLab, CTFd, GZCTF, Metasploit, TryHackMe, HackTheBox)
- [x] Разработка системы критериев оценки (12 критериев, 3 группы)
- [x] Сравнительный анализ и выявление лучших практик
- [x] Формирование технических и функциональных требований
- [x] Проектирование микросервисной архитектуры на Kubernetes
- [x] UML диаграммы компонентов и потоков данных
- [x] **Auth Service** - полностью рабочий микросервис
- [x] Интеграция с PostgreSQL и Redis
- [x] JWT аутентификация с ролевой моделью

### 🚧 **В работе (Этап 2):**
- [ ] **Task Service** - разработка (70% готовности)
- [ ] Dockerfile и docker-compose для Task Service
- [ ] Интеграция с Auth Service
- [ ] Создание тестовых заданий (Docker-образы)

### ⏳ **Планируется (Этап 3-5):**
- [ ] **Check Service** - разработка системы валидации
- [ ] **Orchestration Service** - интеграция с Kubernetes
- [ ] **Progress Service** - трекинг прогресса и аналитика
- [ ] **Frontend** на React + TypeScript
- [ ] **API Gateway** на Nginx/Traefik
- [ ] **Мониторинг** (Prometheus + Grafana)
- [ ] **GitOps** (ArgoCD)
- [ ] **Наполнение контентом** (20+ заданий по безопасности Linux)

---

## 📅 План разработки

### **Спринт 1 (Текущий) - Завершение Task Service**
```yaml
Цель: Полностью рабочий Task Service с CRUD операциями
Задачи:
  - Завершить Dockerfile и docker-compose
  - Реализовать все API endpoints
  - Написать тесты (pytest)
  - Добавить миграции Alembic
  - Протестировать интеграцию с Auth Service
Дедлайн: 2 недели
```

### **Спринт 2 - Check Service (MVP)**
```yaml
Цель: Базовая система проверки решений
Задачи:
  - Разработать архитектуру валидации
  - Создать простые валидаторы (SSH конфигурация)
  - Интеграция с Task Service
  - Тестирование на Docker-контейнерах
Дедлайн: 3 недели
```

### **Спринт 3 - Kubernetes интеграция**
```yaml
Цель: Запуск лабораторных сред в K8s
Задачи:
  - Настройка локального K8s кластера (kind/minikube)
  - Разработка Orchestration Service
  - Создание манифестов для заданий
  - Network Policies и Resource Quotas
Дедлайн: 3 недели
```

### **Спринт 4 - Фронтенд MVP**
```yaml
Цель: Базовый веб-интерфейс
Задачи:
  - Настройка React + TypeScript проекта
  - Компонент авторизации
  - Каталог заданий
  - Веб-терминал (xterm.js)
Дедлайн: 3 недели
```

### **Спринт 5 - Продакшен подготовка**
```yaml
Цель: Промышленная эксплуатация
Задачи:
  - Настройка мониторинга (Prometheus + Grafana)
  - CI/CD пайплайны (GitHub Actions)
  - GitOps с ArgoCD
  - Документация и онбординг
Дедлайн: 2 недели
```

---

## 🚀 Быстрый старт

### Предварительные требования
- Docker 24.0+
- Docker Compose 2.20+
- Python 3.11+
- Git

### 1️⃣ Клонирование репозитория
```bash
git clone https://github.com/your-org/linux-security-training-platform.git
cd linux-security-training-platform
```

### 2️⃣ Запуск Auth Service
```bash
cd services/auth-service
cp .env.example .env
docker-compose up --build
```

Проверка:
```bash
curl http://localhost:8000/health
# {"status":"healthy","service":"auth-service"}
```

Откройте браузер: http://localhost:8000/docs

### 3️⃣ Тестирование Auth Service
```bash
# Регистрация
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "username": "student1",
    "password": "password123",
    "full_name": "Иван Иванов",
    "role": "student"
  }'

# Вход
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=student1&password=password123"

# Получение информации о себе (с токеном)
curl -X GET "http://localhost:8000/users/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4️⃣ Запуск Task Service (в разработке)
```bash
cd services/task-service
cp .env.example .env
docker-compose up --build
```

---

## 📚 API Документация

| Сервис | Swagger UI | ReDoc |
|--------|------------|-------|
| Auth Service | http://localhost:8000/docs | http://localhost:8000/redoc |
| Task Service | http://localhost:8001/docs | http://localhost:8001/redoc |

---

## 📁 Структура проекта

```
linux-security-training-platform/
│
├── services/                    # Микросервисы
│   ├── auth-service/           # ✅ Готово
│   │   ├── src/
│   │   │   ├── api/
│   │   │   ├── core/
│   │   │   ├── models/
│   │   │   ├── schemas/
│   │   │   └── crud/
│   │   ├── Dockerfile
│   │   ├── docker-compose.yml
│   │   ├── requirements.txt
│   │   └── .env.example
│   │
│   ├── task-service/           # 🚧 В разработке
│   │   ├── src/
│   │   ├── Dockerfile
│   │   ├── docker-compose.yml
│   │   └── requirements.txt
│   │
│   ├── check-service/          # ⏳ Планируется
│   ├── progress-service/       # ⏳ Планируется
│   └── orchestration-service/  # ⏳ Планируется
│
├── frontend/                   # ⏳ Планируется
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
│
├── infrastructure/             # ⏳ Планируется
│   ├── k8s/                   # Kubernetes манифесты
│   ├── monitoring/            # Prometheus + Grafana
│   └── gitops/               # ArgoCD конфигурация
│
├── docs/                      # Документация
│   ├── architecture/         # Диаграммы архитектуры
│   ├── api/                 # API спецификации
│   └── guides/              # Руководства
│
├── tasks/                    # Docker-образы заданий
│   ├── ssh-hardening/
│   ├── iptables-config/
│   ├── selinux-policies/
│   └── ...
│
├── docker-compose.yml       # Общий compose для всех сервисов
├── README.md               # Этот файл
└── LICENSE
```

---

## 🧪 Примеры заданий (планируются)

### Уровень 1: Базовый (easy)
| Задание | Навык | Docker-образ | Время |
|---------|-------|--------------|-------|
| Настройка прав доступа | chmod, chown, umask | `ubuntu:22.04` | 15 мин |
| Базовая настройка SSH | sshd_config, ключи | `ubuntu:22.04` | 20 мин |
| Работа с журналами | journalctl, syslog | `ubuntu:22.04` | 15 мин |

### Уровень 2: Средний (medium)
| Задание | Навык | Docker-образ | Время |
|---------|-------|--------------|-------|
| Настройка iptables | Межсетевой экран | `ubuntu:22.04` | 30 мин |
| Аудит с auditd | Мониторинг событий | `ubuntu:22.04` | 30 мин |
| Настройка sudoers | Привилегии | `ubuntu:22.04` | 25 мин |

### Уровень 3: Продвинутый (hard)
| Задание | Навык | Docker-образ | Время |
|---------|-------|--------------|-------|
| Политики SELinux | Мандатный доступ | `centos:8` | 45 мин |
| Обнаружение руткитов | rkhunter, chkrootkit | `ubuntu:22.04` | 40 мин |
| Контроль целостности | AIDE/Tripwire | `ubuntu:22.04` | 45 мин |

---

## 🔬 Ключевые инновации

### 1️⃣ **Проверка состояния системы, а не флагов**
В отличие от CTF-платформ, где достаточно найти строку-флаг, наша платформа анализирует **реальное состояние системы**:
- Корректность конфигурационных файлов
- Права доступа на критичные файлы
- Запущенные процессы и открытые порты
- Загруженные модули ядра
- Политики SELinux/AppArmor

### 2️⃣ **Соответствие промышленным стандартам**
Все задания базируются на:
- **CIS Benchmarks** for Linux
- **NIST Cybersecurity Framework** (CSF)
- **DISA STIG** (Security Technical Implementation Guides)
- **PCI DSS** требования к безопасности

### 3️⃣ **Детальная обратная связь**
```json
{
  "task_id": 1,
  "status": "failed",
  "errors": [
    {
      "file": "/etc/ssh/sshd_config",
      "line": 32,
      "issue": "PermitRootLogin yes",
      "severity": "critical",
      "recommendation": "Set PermitRootLogin to 'no' or 'prohibit-password'",
      "cis_benchmark": "CIS 5.2.10",
      "reference": "https://www.cisecurity.org/benchmark/16592"
    }
  ]
}
```

### 4️⃣ **Масштабируемая Kubernetes-инфраструктура**
- Каждый студент получает **изолированный namespace**
- Автоматическое масштабирование под нагрузкой
- Self-healing (самовосстановление)
- Resource quotas для защиты от DoS

---

## 🎯 Roadmap 2026

```
Q1 2026
├── ✅ Завершение анализа и проектирования
├── ✅ Auth Service
├── 🚧 Task Service
└── 🚧 Начало Check Service

Q2 2026
├── ✅ Check Service MVP
├── ✅ Kubernetes интеграция
├── 🚧 Frontend MVP
└── 🚧 10 базовых заданий

Q3 2026
├── ✅ Полноценный фронтенд
├── ✅ Progress Service
├── 🚧 20+ заданий
└── 🚧 Пилотное тестирование в вузах

Q4 2026
├── ✅ Промышленная эксплуатация
├── ✅ Интеграция с LMS
├── 🚧 Корпоративные версии
└── 📦 Релиз 1.0
```

---

## 👥 Команда

| Роль | Имя | Ответственность |
|------|-----|-----------------|
| **Руководитель** | Карапетьянц Николай | Научное руководство |
| **Разработчик** | Хомяков Н.С. | Архитектура, бэкенд, инфраструктура |
| **Консультант** | Кафедра Криптология и Кибербезопасность, НИЯУ МИФИ | Экспертиза |

---

## 📚 Источники и стандарты

1. NIST Cybersecurity Framework 2.0
2. CIS Benchmarks for Linux
3. DISA Security Technical Implementation Guides
4. ISO/IEC 27001:2022
5. PCI DSS v4.0
6. MITRE ATT&CK Framework
7. Федеральный закон №187-ФЗ "О безопасности КИИ"
8. Национальная программа "Цифровая экономика РФ"

---

## 📄 Лицензия

© 2026 НИЯУ МИФИ, Кафедра Криптология и Кибербезопасность

Данный проект разрабатывается в рамках научно-исследовательской работы. Все права защищены.

---

---

**Статус проекта:** 🚧 Активная разработка (Этап 2 из 5)

[![Open in VSCode](https://img.shields.io/badge/Open%20in-VSCode-blue?style=for-the-badge&logo=visualstudiocode)](https://open.vscode.dev/your-org/linux-security-training-platform)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=for-the-badge)](http://makeapullrequest.com)

---

*Последнее обновление: 9 февраля 2026*
