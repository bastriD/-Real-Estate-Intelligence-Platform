#!/bin/sh
# backend:validate / runtime-imports. Sourced by GitLab; run from the project checkout.

python - <<'PY'
import jwt
import numpy
import pandas
import psycopg

from pwdlib import PasswordHash

print("Runtime dependency validation:")
print(" - NumPy:", numpy.__version__)
print(" - Pandas:", pandas.__version__)
print(" - psycopg:", psycopg.__version__)
print(" - PyJWT:", jwt.__version__)
print(" - pwdlib: OK")

PasswordHash.recommended()

print(
    "Backend + matching + authentication runtime "
    "dependencies imported successfully."
)
PY
python - <<'PY'
from src.ai.matching.features import (
    MatchingWeights,
    build_matching_features,
    compute_matching_score,
    filter_candidates,
)

from src.ai.matching.repository import (
    load_candidate_biens,
    load_demande_version,
    load_ground_truth_references,
    load_matching_input,
)

from src.ai.matching.evaluate import (
    evaluate_demande_version,
)

weights = MatchingWeights()

print(
    "Backend-compatible matching modules "
    "imported successfully."
)
print("Matching weights:", weights)
PY
python - <<'PY'
from src.api.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)

password = "ci-validation-password"

hashed = hash_password(password)

assert hashed != password
assert verify_password(password, hashed)
assert not verify_password(
    "wrong-password",
    hashed,
)

token = create_access_token(
    subject="ci-validation@example.test",
    role="ADMIN",
    utilisateur_id=1,
)

payload = decode_access_token(token)

assert (
    payload["sub"]
    == "ci-validation@example.test"
)

assert payload["uid"] == 1
assert payload["role"] == "ADMIN"

print(
    "Authentication primitives "
    "validation successful."
)
PY
