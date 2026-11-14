"""Tracker tells: the one place the patterns live that mark a string as another tool's prompt rather than a person's.
Python standard library only. Imported by verify_tracked_set.py (on tracked prompts) and longtail_split.py (on a Search
Console export). longtail_split_bigquery.sql carries the same TRACKER_TELLS text; keep it identical.

The two scripts use the same TRACKER_TELLS, with two differences on purpose:
- LONG_PERSONA_TELLS (a first-person persona running 80+ characters) is used ONLY by longtail_split.py and the SQL. On a
  tracked prompt a persona row is allowed and counted by verify_tracked_set.py check 5 (one per page and per set);
  its length is held by check 2.
- verify_tracked_set.py flags LOCATION_CLAUSE too: a tracked prompt must never state the asker's location or market.
- longtail_split.py strips a trailing LOCATION_CLAUSE before matching, so one question run with and without a location
  is counted once; the clause alone does not make an export row a tracker.
"""

# A ranking instruction, an instruction addressed to the model, or a leading <tag> wrapper.
TRACKER_TELLS = (r"forced ranking|(?:rank|order)(?:ed)?(?: them)? from best to worst|you must (?:provide|rank|list|give|answer)"
                 r"|^\s*you are an? |search the web for|do not invent|^\s*<[a-z_ ]+>")

# A long first-person persona (export side only: longtail_split.py and the SQL).
LONG_PERSONA_TELLS = r"^i am an? .{80,}|^i'm an? .{80,}"

# A clause stating the asker's location or market.
LOCATION_CLAUSE = r"\b(?:my|our) (?:location|country|market|region) is\b"
