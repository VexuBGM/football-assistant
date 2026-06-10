from nicegui import ui

from ...chatbot import Chatbot
from ...utils.logger import log_command
from ..layout import page_shell, section


@ui.page("/chatbot")
def chatbot_page() -> None:
    bot = Chatbot()
    messages: list[tuple[str, str]] = []

    def content() -> None:
        @ui.refreshable
        def history() -> None:
            if not messages:
                ui.label("Type a command to use the original staged chatbot workflow.").classes("fm-muted")
                return
            for role, text in messages[-20:]:
                align = "items-end" if role == "You" else "items-start"
                color = "fm-chat-user" if role == "You" else "fm-chat-bot"
                with ui.column().classes(f"{align} w-full"):
                    ui.label(role).classes("text-xs fm-muted")
                    ui.label(text).classes(f"{color} rounded-md px-3 py-2 whitespace-pre-wrap max-w-3xl")

        def send() -> None:
            text = command.value.strip()
            if not text:
                return
            parsed = bot.parse(text)
            result = bot.handle(parsed)
            log_command(text, parsed.intent, parsed.entities, "EXIT" if result == "EXIT" else result)
            messages.append(("You", text))
            messages.append(("Bot", "Goodbye!" if result == "EXIT" else result))
            command.value = ""
            history.refresh()

        with section("Chatbot", "The original command interface remains available for demos and testing"):
            with ui.row().classes("gap-2 w-full items-end"):
                command = ui.input("Command").props("outlined").classes("flex-1")
                command.on("keydown.enter", lambda _: send())
                ui.button("Send", icon="send", on_click=send)
            history()

    page_shell("/chatbot", "Chatbot", "Run the same regex-based commands from the browser.", content)
