from typing import Dict, List

_sessions: Dict[str, List[Dict[str, str]]] = {}


def add_message(session_id: str, role: str, content: str) -> None:
    if session_id not in _sessions:
        _sessions[session_id] = []
    _sessions[session_id].append({"role": role, "content": content})


def get_messages(session_id: str) -> List[Dict[str, str]]:
    return _sessions.get(session_id, [])
