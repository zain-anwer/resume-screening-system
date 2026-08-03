"""
Registry for evaluating the freeform `other_policies` entries HR can add
from the frontend's "Additional Policies" section.

Each entry only has a name, a description, and optional labeled
sub-fields — there's no fixed schema, because HR can type anything
("Gender Diversity", "Disability Quota", "Preferred Skills", ...). That
means the backend genuinely cannot auto-evaluate an arbitrary new policy
against candidate data without someone writing the matching logic.

The safe default for an *unregistered* policy name is to report it as
informational / needs-manual-review, and to leave it out of the
pass/fail `overall_status` decision entirely — so adding a new policy
on the frontend can never silently start rejecting or accepting people
based on logic that doesn't exist yet.

To wire up real logic for a specific policy, register a handler:

    from policy_engine.policy_registry import register_policy

    @register_policy("Preferred Skills")
    def check_preferred_skills(candidate, policy):
        skills = [sf.get("label", "") for sf in policy.get("sub_fields", [])]
        ...
        return {"status": True, "reason": "...", "automated": True}

Handler name matching is case/punctuation-insensitive ("Preferred
Skills", "preferred-skills", "preferred_skills" all match the same
registration), so HR renaming a policy slightly on the frontend doesn't
silently drop the handler.
"""

import re

_HANDLERS = {}


def _slugify(name):
    return re.sub(r"[^a-z0-9]+", "_", str(name or "").strip().lower()).strip("_")


def register_policy(*names):
    """Decorator: register a handler under one or more policy names."""
    slugs = {_slugify(n) for n in names}

    def decorator(fn):
        for slug in slugs:
            _HANDLERS[slug] = fn
        return fn

    return decorator


def get_handler(policy_name):
    return _HANDLERS.get(_slugify(policy_name))


def registered_policy_names():
    """Mostly useful for debugging/tests."""
    return sorted(_HANDLERS.keys())


def evaluate_other_policies(candidate, other_policies):
    """Evaluate every other_policies entry from a policy YAML against a
    candidate. Returns a list of per-policy results; never raises on
    unregistered or malformed entries.
    """
    results = []

    for policy in other_policies or []:
        if not isinstance(policy, dict):
            continue

        name = (policy.get("name") or "").strip() or "Unnamed Policy"
        handler = get_handler(name)

        if handler:
            try:
                outcome = handler(candidate, policy)
            except Exception as exc:  # a bad handler shouldn't crash evaluation
                outcome = {
                    "status": False,
                    "reason": f"Policy handler error: {exc}",
                    "automated": True,
                }
        else:
            outcome = {
                "status": True,
                "reason": (
                    "No automated check registered for this policy — "
                    "recorded for manual review only."
                ),
                "automated": False,
            }

        results.append({"name": name, **outcome})

    return results


# ---------------------------------------------------------
# Built-in handlers for known conventions
# ---------------------------------------------------------
# HR can name a policy "Preferred Skills" from the frontend's Additional
# Policies section, add one sub-field per skill (label = skill name),
# and it'll be checked against the candidate's parsed skills list.

@register_policy("Preferred Skills")
def _check_preferred_skills(candidate, policy):
    skills = [str(s).lower() for s in candidate.get("skills", [])]
    haystack = " ".join(skills)

    wanted = [
        sf.get("label", "").strip()
        for sf in policy.get("sub_fields", [])
        if sf.get("label", "").strip()
    ]

    if not wanted:
        return {
            "status": True,
            "reason": "No skills listed under this policy",
            "matched": [],
            "automated": True,
        }

    matched = [skill for skill in wanted if skill.lower() in haystack]

    return {
        "status": True,  # preferred skills are informational, never blocking
        "reason": f"{len(matched)}/{len(wanted)} preferred skills matched",
        "matched": matched,
        "automated": True,
    }
