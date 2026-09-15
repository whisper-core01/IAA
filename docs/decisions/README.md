# Architecture decisions

Each decision record must preserve:

- context and problem;
- chosen decision;
- alternatives considered and rejected;
- consequences and migration impact;
- affected contracts and invariants;
- evidence required to revisit it.

Accepted decisions are append-only. A later decision supersedes an earlier one
without rewriting history.

