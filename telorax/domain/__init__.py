"""

Telorax Domain Glossary

-----------------------

Account          : real Telegram user account with a session

Operation        : batch action request (e.g. 500 views)

OperationType    : action type (VIEW=1, SUBSCRIBE=2, REACTION=4, ...)

OperationDispatch: record of an operation run on one account (dedup)

Membership       : account membership in a channel/group

PeerSnapshot     : cached peer metadata to reduce API calls

"""
