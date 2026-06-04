from nicegui import ui


def apply_theme() -> None:
    ui.colors(
        primary="#2563eb",
        secondary="#15803d",
        accent="#0f766e",
        positive="#15803d",
        negative="#b91c1c",
        warning="#b45309",
    )
    ui.add_css(
        """
        :root {
          --fm-bg: #f6f8fb;
          --fm-surface: #ffffff;
          --fm-muted: #64748b;
          --fm-border: #d9e2ec;
          --fm-text: #17202a;
        }
        body {
          background: var(--fm-bg);
          color: var(--fm-text);
        }
        .fm-page {
          width: 100%;
          max-width: 1440px;
          margin: 0 auto;
          padding: 20px;
        }
        .fm-panel {
          background: var(--fm-surface);
          border: 1px solid var(--fm-border);
          border-radius: 8px;
          box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
        }
        .fm-stat {
          min-height: 92px;
        }
        .fm-muted {
          color: var(--fm-muted);
        }
        .fm-grid {
          height: 520px;
          width: 100%;
        }
        .fm-small-grid {
          height: 340px;
          width: 100%;
        }
        .fm-link-active {
          background: rgba(37, 99, 235, 0.12);
          color: #1d4ed8;
          font-weight: 700;
        }
        .q-dark .fm-panel {
          background: #111827;
          border-color: #263244;
        }
        .q-dark body {
          background: #0b1120;
        }
        """
    )
