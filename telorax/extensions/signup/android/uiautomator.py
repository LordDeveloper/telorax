from __future__ import annotations

from telorax.extensions.signup.protocol import SignupAutomation, SignupContext


class UiautomatorSignupAutomation:
    """Android signup automation using uiautomator2 on a connected device.

    Requires:
    - Official Telegram app installed on the device
    - ADB access to the device
    - SMS verification handled externally (metadata['sms_code'] or hook override)
    """

    def __init__(self, device_serial: str | None = None) -> None:
        self._device_serial = device_serial

    async def signup(self, context: SignupContext) -> bytes:
        try:
            import uiautomator2 as u2
        except ImportError as exc:
            msg = 'Install signup extras: pip install telorax[signup]'
            raise RuntimeError(msg) from exc

        device = u2.connect(self._device_serial)
        await self._run_signup_flow(device, context)
        return await self._export_session(device, context)

    async def _run_signup_flow(self, device: object, context: SignupContext) -> None:
        app = device.app_start('org.telegram.messenger')  # type: ignore[attr-defined]
        if not app:
            msg = 'Unable to start official Telegram app'
            raise RuntimeError(msg)

        phone = f'+{context.msisdn}'
        self._tap_text(device, 'Start Messaging')
        self._tap_text(device, 'Continue')
        self._fill_phone(device, phone)
        self._tap_text(device, 'Next')

        sms_code = str(context.metadata.get('sms_code') or '')
        if not sms_code:
            msg = 'sms_code must be provided in job metadata until SMS provider hook is wired'
            raise RuntimeError(msg)
        self._fill_code(device, sms_code)

        self._fill_name(device, context.first_name, context.last_name)
        if context.two_factor_password:
            self._configure_2fa(device, context.two_factor_password)

    def _tap_text(self, device: object, label: str) -> None:
        clicked = device(text=label).click_exists(timeout=10.0)  # type: ignore[attr-defined]
        if not clicked:
            msg = f'UI element not found: {label}'
            raise RuntimeError(msg)

    def _fill_phone(self, device: object, phone: str) -> None:
        field = device(className='android.widget.EditText')  # type: ignore[attr-defined]
        field.set_text(phone)

    def _fill_code(self, device: object, code: str) -> None:
        field = device(className='android.widget.EditText')  # type: ignore[attr-defined]
        field.set_text(code)

    def _fill_name(self, device: object, first_name: str, last_name: str) -> None:
        fields = device(className='android.widget.EditText')  # type: ignore[attr-defined]
        fields[0].set_text(first_name)
        if fields.count > 1:
            fields[1].set_text(last_name)
        self._tap_text(device, 'Done')

    def _configure_2fa(self, device: object, password: str) -> None:
        _ = password
        msg = '2FA automation hook is not implemented yet'
        raise RuntimeError(msg)

    async def _export_session(self, device: object, context: SignupContext) -> bytes:
        exported_path = str(context.metadata.get('session_export_path') or '')
        if exported_path:
            content = device.pull(exported_path)  # type: ignore[attr-defined]
            if isinstance(content, bytes):
                return content
        msg = (
            'Session export requires rooted device access or session_export_path in metadata. '
            'Typical path: /data/data/org.telegram.messenger/files/tgnet.dat or exported .session file.'
        )
        raise RuntimeError(msg)
