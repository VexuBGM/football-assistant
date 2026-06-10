from nicegui import ui


def apply_theme() -> None:
    ui.add_head_html(
        """
        <script>
          (() => {
            const storageKey = 'football-manager-theme';

            function normalize(theme) {
              return theme === 'dark' ? 'dark' : 'light';
            }

            function apply(theme) {
              const value = normalize(theme);
              document.documentElement.dataset.theme = value;
              document.documentElement.classList.toggle('body--dark', value === 'dark');
              if (document.body) {
                document.body.dataset.theme = value;
                document.body.classList.toggle('body--dark', value === 'dark');
              }
              localStorage.setItem(storageKey, value);
              window.dispatchEvent(new CustomEvent('fm-theme-change', {detail: {theme: value}}));
            }

            window.FMTheme = {
              apply,
              toggle() {
                apply(document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark');
              },
              current() {
                return normalize(document.documentElement.dataset.theme);
              },
            };

            apply(localStorage.getItem(storageKey));
            document.addEventListener('DOMContentLoaded', () => apply(window.FMTheme.current()));
          })();
        </script>
        """
    )
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
          --fm-surface-raised: #ffffff;
          --fm-muted: #64748b;
          --fm-border: #d9e2ec;
          --fm-text: #17202a;
          --fm-link: #334155;
          --fm-chat-user-bg: #dbeafe;
          --fm-chat-bot-bg: #f1f5f9;
          --fm-goal: #15803d;
          --fm-card: #b45309;
        }
        html[data-theme="dark"] {
          --fm-bg: #0b1120;
          --fm-surface: #111827;
          --fm-surface-raised: #182235;
          --fm-muted: #a7b4c8;
          --fm-border: #263244;
          --fm-text: #e5edf7;
          --fm-link: #d7e1ef;
          --fm-chat-user-bg: #1e3a5f;
          --fm-chat-bot-bg: #243044;
          --fm-goal: #4ade80;
          --fm-card: #fbbf24;
        }
        html,
        body,
        #app,
        .q-layout,
        .q-page-container,
        .q-page,
        .nicegui-content {
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
          color: var(--fm-text);
        }
        .fm-shell {
          background: var(--fm-surface);
          border-color: var(--fm-border);
          color: var(--fm-text);
        }
        .fm-nav-link {
          color: var(--fm-link);
        }
        .fm-card,
        .q-dialog .q-card {
          background: var(--fm-surface-raised);
          color: var(--fm-text);
        }
        .q-menu,
        .q-list,
        .q-item,
        .q-field--outlined .q-field__control,
        .q-textarea .q-field__control {
          background: var(--fm-surface-raised);
          color: var(--fm-text);
        }
        .q-separator {
          background: var(--fm-border);
        }
        .fm-chat-user {
          background: var(--fm-chat-user-bg);
          color: var(--fm-text);
        }
        .fm-chat-bot {
          background: var(--fm-chat-bot-bg);
          color: var(--fm-text);
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
          min-width: 0;
        }
        .fm-small-grid {
          height: 340px;
          width: 100%;
          min-width: 0;
        }
        .fm-grid,
        .fm-small-grid {
          --ag-background-color: var(--fm-surface-raised);
          --ag-foreground-color: var(--fm-text);
          --ag-header-background-color: var(--fm-surface);
          --ag-header-foreground-color: var(--fm-text);
          --ag-border-color: var(--fm-border);
          --ag-row-border-color: var(--fm-border);
          --ag-odd-row-background-color: var(--fm-surface-raised);
          --ag-row-hover-color: rgba(37, 99, 235, 0.10);
          --ag-selected-row-background-color: rgba(37, 99, 235, 0.16);
          --ag-input-background-color: var(--fm-surface);
          --ag-input-text-color: var(--fm-text);
        }
        .fm-grid .ag-root-wrapper,
        .fm-small-grid .ag-root-wrapper,
        .fm-grid .ag-root,
        .fm-small-grid .ag-root,
        .fm-grid .ag-body-viewport,
        .fm-small-grid .ag-body-viewport,
        .fm-grid .ag-center-cols-viewport,
        .fm-small-grid .ag-center-cols-viewport {
          background: var(--fm-surface-raised);
          color: var(--fm-text);
        }
        .fm-grid .ag-root-wrapper,
        .fm-small-grid .ag-root-wrapper {
          width: 100%;
        }
        .fm-grid .ag-cell,
        .fm-small-grid .ag-cell,
        .fm-grid .ag-header-cell-text,
        .fm-small-grid .ag-header-cell-text {
          overflow: hidden;
          text-overflow: ellipsis;
        }
        .fm-grid .ag-header,
        .fm-small-grid .ag-header,
        .fm-grid .ag-header-cell,
        .fm-small-grid .ag-header-cell {
          background: var(--fm-surface);
          color: var(--fm-text);
          border-color: var(--fm-border);
        }
        .fm-grid .ag-row,
        .fm-small-grid .ag-row,
        .fm-grid .ag-cell,
        .fm-small-grid .ag-cell {
          background: var(--fm-surface-raised);
          color: var(--fm-text);
          border-color: var(--fm-border);
        }
        html[data-theme="dark"] .fm-grid,
        html[data-theme="dark"] .fm-small-grid {
          --ag-row-hover-color: rgba(96, 165, 250, 0.14);
          --ag-selected-row-background-color: rgba(96, 165, 250, 0.22);
        }
        .fm-link-active {
          background: rgba(37, 99, 235, 0.12);
          color: #1d4ed8;
          font-weight: 700;
        }
        html[data-theme="dark"] .fm-link-active {
          background: rgba(96, 165, 250, 0.18);
          color: #bfdbfe;
        }
        .fm-goal {
          color: var(--fm-goal);
        }
        .fm-card-event {
          color: var(--fm-card);
        }
        .q-field--outlined .q-field__control::before {
          border-color: var(--fm-border);
        }
        .q-field__native,
        .q-field__input,
        .q-field__label,
        .q-field__prefix,
        .q-field__suffix {
          color: var(--fm-text);
        }
        .q-menu {
          min-width: min(22rem, calc(100vw - 2rem));
        }
        .fm-toolbar {
          width: 100%;
          min-width: 0;
        }
        .fm-toolbar .q-field {
          flex-shrink: 0;
        }
        """
    )
