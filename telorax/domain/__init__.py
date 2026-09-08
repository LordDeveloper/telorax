"""
Telorax Domain Glossary
-----------------------
Account          : real Telegram user account with a session
Operation        : batch engagement request (e.g. 500 views)
EngagementKind   : engagement type (VIEW, SUBSCRIBE, REACTION, ...)
OperationDispatch: record of an operation run on one account (dedup)
Membership       : account membership in a channel/group
PeerSnapshot     : cached peer metadata to reduce API calls
"""
