# Changelog

All notable changes to this project are listed here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), versions follow [Semantic Versioning](https://semver.org/).

Все заметные изменения проекта перечислены здесь. Формат основан на Keep a Changelog, версии нумеруются по Semantic Versioning.

## [2.0.1] - 2026-11-15

### Fixed / Исправлено

- The package could not be imported: `__init__.py` referenced a missing `animator` module. / Пакет не импортировался: `__init__.py` ссылался на несуществующий модуль `animator`.
- `Termimato` and `AnimationController` from the README did not exist. Both are implemented now (`termimato/core.py`). / Классов `Termimato` и `AnimationController` из README не было. Теперь они реализованы (`termimato/core.py`).
- `ColorNotSupportedError` was imported but never defined. / `ColorNotSupportedError` импортировался, но нигде не был определён.
- The import name in the README is `termimato`, while the package folder was `Termimato`, which fails on case-sensitive file systems. The folder is now lowercase. / В README импорт `termimato`, а папка пакета называлась `Termimato`, что не работает в файловых системах с учётом регистра. Папка теперь в нижнем регистре.
- `rainbow_text` drew almost black text because of a wrong hue formula. It now uses `colorsys`. / `rainbow_text` рисовал почти чёрный текст из-за неверной формулы оттенка. Теперь используется `colorsys`.
- `rainbow_text` swallowed task cancellation and left no clean line on a normal finish. / `rainbow_text` подавлял отмену задачи и не оставлял чистую строку при обычном завершении.
- `scanner` highlighted the wrong number of characters for even `width` values. / `scanner` подсвечивал неверное число символов при чётной `width`.
- `fade_out(effect="fade")` never changed the color. An unknown effect name was ignored silently. / `fade_out(effect="fade")` не менял цвет. Неизвестное имя эффекта молча игнорировалось.
- `progress_bar(0)` raised `ZeroDivisionError`. It raises `ValueError` now. / `progress_bar(0)` вызывал `ZeroDivisionError`. Теперь вызывает `ValueError`.
- `particle_explosion` cleared the whole terminal and ignored its real size. It draws on the alternate screen now. / `particle_explosion` стирал весь терминал и не учитывал его реальный размер. Теперь рисует на альтернативном экране.
- `CountdownAnimator` showed the last number for no time at all, and `minutes` and `hours` were wrong above one hour. / `CountdownAnimator` не задерживал последнее число на экране, а `minutes` и `hours` были неверны после первого часа.
- A stopped animator raised `CancelledError` into the caller; finished animators stayed in the `RUNNING` state; stopping an idle animator marked it as cancelled. / Остановленный аниматор бросал `CancelledError` вызывающему коду; завершённые аниматоры оставались в состоянии `RUNNING`; остановка неактивного аниматора помечала его отменённым.
- `SpinnerAnimator` left its last frame on the screen. / `SpinnerAnimator` оставлял на экране последний кадр.
- `Termimato.play` could not pass an `effect=` argument to an effect. / `Termimato.play` не мог передать эффекту аргумент `effect=`.
- `asyncio.get_event_loop()` inside coroutines replaced with `get_running_loop()`. / `asyncio.get_event_loop()` внутри корутин заменён на `get_running_loop()`.

### Changed / Изменено

- Python 3.9 or newer is required. / Требуется Python 3.9 или новее.
- Effects now read their defaults from the configuration (`default_speed`, `type_writer_jitter`, `scanner_width`, `glitch_charset`, `fade_out_effect`). `Colors.rgb`, `Colors.bg_rgb` and `Colors.gradient` follow `enable_true_color` and `fallback_to_8bit`. / Эффекты берут умолчания из конфигурации. `Colors.rgb`, `Colors.bg_rgb` и `Colors.gradient` учитывают `enable_true_color` и `fallback_to_8bit`.
- Configuration options that nothing used were removed: `buffer_output`, `flush_threshold`, `enable_sound_effects`, `enable_signal_handlers`, `debug_mode`, `log_file`, `custom_themes`. Old config files that contain them still load. / Удалены параметры конфигурации, которые нигде не использовались. Старые файлы конфигурации с ними продолжают загружаться.
- Unused exceptions `AnimationInterruptedError` and `ValidationError` were removed. `TermimatoError`, `ConfigurationError`, `EffectNotFoundError` and `ColorError` are exported from the package. / Удалены неиспользуемые исключения `AnimationInterruptedError` и `ValidationError`. Из пакета экспортируются `TermimatoError`, `ConfigurationError`, `EffectNotFoundError` и `ColorError`.
- `CountdownAnimator` no longer passes `total_seconds`; use `seconds`. `AnimationMetrics.avg_fps` was removed. / `CountdownAnimator` больше не передаёт `total_seconds`, используйте `seconds`. Удалено поле `AnimationMetrics.avg_fps`.

### Added / Добавлено

- `speed` parameter of `progress_bar`. / Параметр `speed` у `progress_bar`.
- `ColorTheme.named()`, `save_config` returns the written path. / `ColorTheme.named()`, `save_config` возвращает путь записанного файла.
- Tests, examples, packaging metadata, CI, issue and pull request templates, documentation in English and Russian. / Тесты, примеры, метаданные пакета, CI, шаблоны issue и pull request, документация на английском и русском.

## [2.0.0]

First public release. / Первый публичный выпуск.
