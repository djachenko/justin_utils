# justin_utils — Project Guide

## Что это

Общие утилиты Python-экосистемы. Библиотека без зависимостей, которую можно установить отдельно и использовать в любом проекте экосистемы.

---

## Место в экосистеме

```
justin ──→ justin_utils
pyvko  ──→ justin_utils (планируется)
```

Цель: вобрать весь переиспользуемый код из `justin` и `pyvko`, чтобы шарить между проектами без лишних зависимостей.

---

## Текущие модули

| Модуль | Содержимое |
|--------|------------|
| `filesystem.py` | `Folder`, `File` — обёртки над `Path` с удобным доступом к подпапкам |
| `parts.py` | CLI-утилита `parts` |
| `subfolder.py` | CLI-утилита `sf` |
| `transfer.py` | `TransferSpeedMeter`, `TransferTimeEstimator` |
| `time_formatter.py` | Форматирование времени |
| `data.py` | `DataSize` |
| `dictable.py` | `Dictable`, `DictableDataclass`, `fromdict` — десериализация JSON в датаклассы |
| `exif.py` | EXIF-утилиты |
| `singleton.py` | Singleton паттерн |
| `joins.py`, `pylinq.py` | LINQ-подобные операции над коллекциями |
| `json_migration.py` | Утилиты для JSON-миграций |

---

## Git

Semantic commits: `feat:`, `fix:`, `refactor:`, `chore:`
