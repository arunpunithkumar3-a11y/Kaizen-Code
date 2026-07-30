def resume():
    import questionary
    from questionary import Choice
    from kaizen.cli.ui import panels
    from kaizen.cli.ui.styles import QUESTIONARY_STYLE
    from kaizen.storage.db.session_manager import session_service

    # Display elegant header containing active environment details
    panels.show_banner()

    sessions = session_service.list_sessions()
    if not sessions:
        panels.info("No active chat sessions found to resume.")
        return

    sorted_sessions = sorted(
        sessions.items(), key=lambda item: item[1].get("created_at", ""), reverse=True
    )

    from datetime import datetime

    max_title_len = min(
        40, max((len(y.get("title", "")) for y in sessions.values()), default=20)
    )

    choice_data = []
    for x, y in sorted_sessions:
        title = y.get("title", "Untitled")
        if len(title) > max_title_len:
            title_display = title[: max_title_len - 3] + "..."
        else:
            title_display = title.ljust(max_title_len)

        created_at_str = y.get("created_at")
        if created_at_str:
            try:
                dt_utc = datetime.fromisoformat(created_at_str)
                dt_local = dt_utc.astimezone()
                time_str = dt_local.strftime("%Y-%m-%d %H:%M")
            except Exception:
                time_str = "Unknown Date"
        else:
            time_str = "Unknown Date"

        display_name = f"{title_display}  ({time_str})"
        choice_data.append(Choice(display_name, value=x))

    thread_id = questionary.select(
        "Select a chat session to resume:",
        choices=choice_data,
        style=QUESTIONARY_STYLE,
        qmark="  ❖",
        pointer="❯",
    ).ask()
    
    if thread_id is None:
        return

    panels.console.print()

    while True:
        try:
            query = panels.custom_input().strip()
        except KeyboardInterrupt:
            break

        if not query:
            continue
        if query == "exit":
            break

        panels.console.print()
        panels.execute_agent(thread_id, query)
