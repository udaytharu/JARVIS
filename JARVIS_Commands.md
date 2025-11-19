# JARVIS AI – Command Reference & Control

This guide explains everything you can say or type—and exactly how backend navigation/automation is mapped in the latest JARVIS-AI.

---

## 🧭 Universal Navigation (via Navigator)
All navigation is routed via the `Navigator` class (`nav`) in `Backend/Navigation.py`. To add or extend commands, simply update the mapping in `Navigator.run()`.

### Core Navigation Commands
| Command                | Description              | Example                 |
|------------------------|--------------------------|-------------------------|
| `scroll up [n]`        | Scroll up n steps        | `scroll up 10`          |
| `scroll down [n]`      | Scroll down n steps      | `scroll down 20`        |
| `swipe left [n]`       | Drag left n pixels       | `swipe left 200`        |
| `swipe right [n]`      | Drag right n pixels      | `swipe right 50`        |
| `swipe up [n]`         | Drag up n pixels         | `swipe up 120`          |
| `swipe down [n]`       | Drag down n pixels       | `swipe down 80`         |
| `zoom in`              | Zoom in (Ctrl/Cmd+"+")  | `zoom in`               |
| `zoom out`             | Zoom out                 | `zoom out`              |
| `zoom reset`           | Reset zoom (Ctrl+0)      | `zoom reset`            |
| `page up`              | Page up                  | `page up`               |
| `page down`            | Page down                | `page down`             |
| `home`                 | Go to beginning          | `home`                  |
| `end`                  | Go to end                | `end`                   |
| `left`/`right`/`up`/`down` | Arrow keys           | `left`                  |
| `enter`                | Enter key                | `enter`                 |
| `escape`               | Escape                   | `escape`                |
| `tab`                  | Tab key                  | `tab`                   |
| `backspace`            | Backspace                | `backspace`             |
| `select all`           | Ctrl+A/Cmd+A             | `select all`            |
| `copy`/`paste`/`cut`   | Clipboard ops            | `copy`                  |
| `undo`/`redo`          | Undo/Redo                | `undo`, `redo`          |
| `save`                 | Save file                | `save`                  |
| `refresh`              | Refresh                  | `refresh`               |
| `fullscreen`           | Toggle fullscreen        | `fullscreen`            |
| `go to page [n]`       | Go to page NUM (PDF)     | `go to page 7`          |

---

## 🔀 Command Normalization (Best Practice)

> If a phrase does not match exactly, normalize it in code before calling `nav.run()`, or add it to the mapping. For example:
>
> ```python
> normalized = q.replace("scrollup", "scroll up").replace("zoomin", "zoom in")
> nav.run(normalized)
> ```
>
> Or add an alias in the `mapping` dictionary in `Backend/Navigation.py`.

---

## 🚀 Automation & System Control

Automation commands (handled via `Backend/Automation.py`) use natural phrases:
| Command                   | Description                | Example                  |
|---------------------------|----------------------------|--------------------------|
| `open [application]`      | Open app/site              | `open chrome`            |
| `close [application]`     | Close app/process          | `close notepad`          |
| `play [song]`             | Play on YouTube            | `play let her go`        |
| `content [topic]`         | Generate text              | `content email template`  |
| `create presentation ...` | Generate PPTX via Groq     | `create presentation ai` |
| `google search ...`       | Google search              | `google search python`   |
| `youtube search ...`      | YouTube search             | `youtube search cooking` |
| `generate image ...`      | SDXL image generation      | `generate image dog`     |
| `system mute`             | Mute/unmute                | `system mute`            |
| `system shutdown`         | Shutdown PC                | `system shutdown`        |

---

## 🤖 Model Selection (.env Power)

- Choose your Cohere model for intent routing in `.env`:

  ```
  CohereModel=command-light
  ```
  > Change to any currently free/supported model from Cohere if deprecated!

---

## Troubleshooting & Pro Tips
- **Navigation doesn’t work?**
  - Check GUI for unknown command error.
  - Expand or normalize phrases as above.
- **Silent or missing function?**
  - All backend commands return and display errors—watch the UI/chat window.
  - Check `[Navigator] Unknown command:` or `[Navigator] Action failed: ...` in logs.
- **Model error?**
  - If Cohere returns a 404 for your model, update `.env` with a new one (`command-light`, etc.)
- **Focus the app/window**: Navigation/automation requires the right target window to be focused!
- **Expand/extend as open source:** All command vocabularies are easy to update by editing the relevant backend helpers.

---

## Example Session
```
you: scroll down 10
jarvis: [works, page scrolls]
you: open chrome
jarvis: [chrome opens]
you: zoom in
jarvis: [ctrl/cmd +, window zooms]
you: play let her go
jarvis: [YouTube opens, starts the song]
```
--- 