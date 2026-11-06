"""Rule-based decision policy shared by the reference agents (stdlib only).

The policy is deliberately trivial. It exists to exercise the agoe.agent/v1 protocol, not to
behave well. It prefers options that mention escalating, consulting or reporting, and it uses
its memory of earlier choices in the same run: among preferred options it picks the keyword it
has used most, and when nothing matches it picks the option whose wording overlaps most with
what it chose before.
"""
import re

PREFERRED = ('escalate', 'consult', 'report')
WORD = re.compile(r'[a-z]+')


class RulePolicy:
    def __init__(self, scenario):
        self.scenario = scenario
        self.history = []  # [{"step", "text", "keyword"}], memory kept across decides in one run

    def decide(self, step, options):
        used = {k: sum(h['keyword'] == k for h in self.history) for k in PREFERRED}
        best = None
        for opt in options:
            text = opt['text'].lower()
            for k in PREFERRED:
                if k in text:
                    rank = (used[k], -PREFERRED.index(k), -opt['id'])
                    if best is None or rank > best[0]:
                        best = (rank, opt, k)
        if best:
            _, opt, keyword = best
            why = f"option mentions '{keyword}'"
        else:
            past = set(WORD.findall(' '.join(h['text'].lower() for h in self.history)))
            opt = max(options, key=lambda o: (len(past & set(WORD.findall(o['text'].lower()))), -o['id']))
            keyword = None
            why = 'no preferred keyword; closest to earlier choices' if self.history else 'no preferred keyword; first option'
        self.history.append({'step': step, 'text': opt['text'], 'keyword': keyword})
        return {'choice': opt['id'],
                'rationale': f"{why}; {len(self.history) - 1} earlier decisions in this run."}
