def chat():
    import questionary
    from kaizen.cli.ui import panels
    from kaizen.cli.ui.styles import QUESTIONARY_STYLE
    from kaizen.storage.db.session_manager import session_service

    # Display elegant header containing active environment details
    panels.show_banner()

    title = questionary.text(
        "Enter title for this chat session (leave blank for auto-title):",
        style=QUESTIONARY_STYLE,
        qmark="  ❖",
    ).ask()

    if title is None:
        return

    title = title.strip()
    if not title:
        from datetime import datetime
        title = f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
    thread_id = session_service.create(title=title)
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
