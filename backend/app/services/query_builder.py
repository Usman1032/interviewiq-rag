"""
Turns (role, resume profile, interview history) into a retrieval query.

Design decision: rather than a single static query per session, we build
a fresh query for every question -- seeded by an unexplored skill/domain
from the resume so consecutive questions don't retrieve the same chunks
and the interview naturally tours the candidate's stated background.
"""
import random
from typing import Dict, Any, List


def build_query(
    role_label: str,
    profile: Dict[str, Any],
    asked_topics: List[str],
) -> str:
    candidates = list(
        dict.fromkeys(
            (profile.get("skills") or [])
            + (profile.get("technologies") or [])
            + (profile.get("domains") or [])
        )
    )
    unexplored = [c for c in candidates if c not in asked_topics]
    pool = unexplored or candidates

    if pool:
        topic = random.choice(pool)
        return f"{role_label} technical interview concepts related to {topic}"
    return f"core {role_label} technical interview concepts"


def pick_topic(profile: Dict[str, Any], asked_topics: List[str]) -> str:
    candidates = list(
        dict.fromkeys(
            (profile.get("skills") or [])
            + (profile.get("technologies") or [])
            + (profile.get("domains") or [])
        )
    )
    unexplored = [c for c in candidates if c not in asked_topics]
    pool = unexplored or candidates
    return random.choice(pool) if pool else "general"
