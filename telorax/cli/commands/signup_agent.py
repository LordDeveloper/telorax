from __future__ import annotations

import asyncio

import typer

signup_agent_app = typer.Typer(help='Automatic Telegram signup agent (Android extension)')


@signup_agent_app.command('run')
def run_signup_agent(
    agent_id: str = typer.Option(..., help='Unique identifier for this Android worker'),
    device: str | None = typer.Option(None, help='ADB device serial'),
    base_url: str | None = typer.Option(None, help='Telorax API base URL'),
) -> None:
    """Poll telorax for signup jobs and automate registration on Android."""
    from telorax.bootstrap.container import Container
    from telorax.extensions.signup.android.uiautomator import UiautomatorSignupAutomation
    from telorax.extensions.signup.android_agent import (
        AndroidSignupRunner,
        TeloraxSignupAgentClient,
        build_agent_config,
    )

    settings = Container().config()
    config = build_agent_config(settings, agent_id=agent_id, base_url=base_url)
    client = TeloraxSignupAgentClient(config)
    runner = AndroidSignupRunner(client, UiautomatorSignupAutomation(device_serial=device))
    try:
        asyncio.run(runner.run_forever())
    except KeyboardInterrupt:
        raise typer.Exit(code=130) from None
