# Contributing

Thank you for your interest in Termimato. Bug reports, ideas, documentation fixes and code are all welcome.

## Where to start

- Question about usage or an idea: [Discussions](https://github.com/Juic3-me/Termimato/discussions).
- Bug: [Issues](https://github.com/Juic3-me/Termimato/issues/new/choose). Fill in the template: version, Python, terminal and a minimal example.
- Larger change: open an issue or a discussion first, so the direction can be agreed before you spend time on code.

## Setting up

```
git clone https://github.com/<your-name>/Termimato
cd Termimato
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e .
```

The library has no runtime dependencies.

## Running the tests

```
python -m unittest discover -s tests -t . -v
```

The same command runs in CI on Linux, macOS and Windows. A change that adds or fixes behavior needs a test next to the existing ones in `tests/`. Tests capture standard output, so they do not need a real terminal.

## Preparing a change

1. Fork the repository and create a branch from `main`: `git checkout -b fix-scanner-width`.
2. Keep the change focused. One pull request should do one thing.
3. Follow the style of the surrounding code: type hints on public functions, no comments that repeat the code, no unused imports.
4. Update `README.md`, `README.ru.md` and `CHANGELOG.md` if the public behavior changed.
5. Run the tests and push the branch.
6. Open a pull request and fill in the template.

New effects should be `async` functions in `termimato/effects.py`, use `get_config()` for defaults that make sense as settings, restore the line or screen they changed (also on cancellation) and be exported from `termimato/__init__.py`.

## Commit messages

A short summary in the imperative mood, up to about 70 characters: `Fix scanner window for even widths`. Details go into the body of the message.

## Code of conduct

Everyone who takes part follows the [code of conduct](CODE_OF_CONDUCT.md).

---

# Участие в разработке

Спасибо за интерес к Termimato. Приветствуются сообщения об ошибках, идеи, правки документации и код.

## С чего начать

- Вопрос по использованию или идея: [Discussions](https://github.com/Juic3-me/Termimato/discussions).
- Ошибка: [Issues](https://github.com/Juic3-me/Termimato/issues/new/choose). Заполните шаблон: версия, Python, терминал и минимальный пример.
- Крупное изменение: сначала создайте issue или обсуждение, чтобы согласовать направление до того, как вы потратите время на код.

## Подготовка окружения

```
git clone https://github.com/<ваш-ник>/Termimato
cd Termimato
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e .
```

У библиотеки нет зависимостей времени выполнения.

## Запуск тестов

```
python -m unittest discover -s tests -t . -v
```

Та же команда выполняется в CI на Linux, macOS и Windows. Изменение, которое добавляет или исправляет поведение, должно сопровождаться тестом рядом с существующими в `tests/`. Тесты перехватывают стандартный вывод, поэтому настоящий терминал им не нужен.

## Подготовка изменения

1. Сделайте форк и создайте ветку от `main`: `git checkout -b fix-scanner-width`.
2. Не расширяйте изменение. Один пул-реквест решает одну задачу.
3. Следуйте стилю окружающего кода: аннотации типов у публичных функций, никаких комментариев, повторяющих код, никаких неиспользуемых импортов.
4. Обновите `README.md`, `README.ru.md` и `CHANGELOG.md`, если изменилось публичное поведение.
5. Запустите тесты и отправьте ветку.
6. Откройте пул-реквест и заполните шаблон.

Новые эффекты это `async`-функции в `termimato/effects.py`. Они берут через `get_config()` умолчания, которые имеет смысл настраивать, восстанавливают изменённую строку или экран (в том числе при отмене) и экспортируются из `termimato/__init__.py`.

## Сообщения коммитов

Краткое описание в повелительном наклонении, примерно до 70 символов: `Fix scanner window for even widths`. Подробности идут в тело сообщения.

## Кодекс поведения

Все участники соблюдают [кодекс поведения](CODE_OF_CONDUCT.md).
