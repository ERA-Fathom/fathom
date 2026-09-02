#!/usr/bin/env bash
# Repository boundary gate. Run before every push. Exits non-zero if the public tree carries anything
# that belongs to the hosted service or to internal documents.
set -e
cd "$(dirname "$0")"
PATTERN='B_rho|B_ρ|H_ext|reflexive burden|threshold|entropy|eigen|koopman|selector|attribution|pre-reg|planted|self-test|selftest|kill-test|retraction|substrate|oracle'
if grep -rniE "$PATTERN" --include='*.py' --include='*.md' --include='*.toml' --include='*.cff' --include='*.yml' . | grep -v scripts_boundary_check.sh; then
  echo "boundary check FAILED: internal vocabulary or scoring logic found above"; exit 1
fi
echo "boundary check passed"
