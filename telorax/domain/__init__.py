"""
Telorax Domain Glossary
-----------------------
TelegramAccount  : یک user account واقعی Telegram با session
Campaign         : درخواست batch engagement (مثلاً 500 view)
EngagementKind   : نوع تعامل (VIEW, SUBSCRIBE, REACTION, ...)
CampaignDispatch : ثبت اجرای campaign روی یک account (dedup)
ChannelMembership: عضویت account در channel/group
PeerSnapshot     : cache اطلاعات peer برای کاهش API call
"""
