# Minimal Agent Handoff Example / Минимальный пример Agent Handoff

This example shows the smallest useful Agent Handoff structure for a repository.
Этот пример показывает минимальную полезную структуру Agent Handoff для репозитория.

## File tree / Дерево файлов

```text
AGENTS.md
AGENT_HANDOFF_STANDARD.md
.github/
  ISSUE_TEMPLATE/
  pull_request_template.md
ai/
  README.md
  PROJECT_STATE.md
  DECISIONS.md
  GITHUB_WORKFLOW.md
  HANDOFF_PROTOCOL.md
  AGENT_IDENTITY.md
  WORK_CLAIM_PROTOCOL.md
  TASK_REPORT_PROTOCOL.md
  REVIEW_PROTOCOL.md
  handoffs/
    INDEX.md
```

## Minimal workflow / Минимальный workflow

1. Create or select an Issue. / Создайте или выберите Issue.
2. Claim the work. / Зафиксируйте claim работы.
3. Create a meaningful branch. / Создайте осмысленную branch.
4. Open a Draft PR early. / Рано откройте Draft PR.
5. Run checks. / Запустите проверки.
6. Leave a handoff when work is done or paused. / Оставьте handoff при завершении или паузе.

## Minimal prompt / Минимальный prompt

```text
Add the minimal Agent Handoff structure to this repository.
Use GitHub Issues and Pull Requests as the source of work truth.
Keep ai/ compact.
Use meaningful branch names without issue numbers by default.
```

```text
Добавь минимальную структуру Agent Handoff в этот репозиторий.
Используй GitHub Issues и Pull Requests как источник правды по работе.
Держи ai/ компактным.
Используй осмысленные имена веток без номеров Issue по умолчанию.
```
