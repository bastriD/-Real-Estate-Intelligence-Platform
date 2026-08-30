import pytest
from pydantic import ValidationError

from src.api.schemas.demande import DemandeCreate, DemandeRevision
from src.api.schemas.presentation import PresentationCreate
from src.api.schemas.visite import VisiteCreate


def test_demande_create_accepts_exactly_one_client_author() -> None:
    payload = DemandeCreate(
        id_mandat=1,
        motif_modification="Initial request",
        auteur_client_id=1,
        ville="Montpellier",
        budget_min=200000,
        budget_max=300000,
    )

    assert payload.auteur_client_id == 1
    assert payload.auteur_chasseur_id is None
    assert payload.auteur_systeme is False


def test_demande_create_rejects_missing_author() -> None:
    with pytest.raises(
        ValidationError,
        match="exactly one author must be provided",
    ):
        DemandeCreate(
            id_mandat=1,
            motif_modification="Initial request",
        )


def test_demande_create_rejects_multiple_authors() -> None:
    with pytest.raises(
        ValidationError,
        match="exactly one author must be provided",
    ):
        DemandeCreate(
            id_mandat=1,
            motif_modification="Initial request",
            auteur_client_id=1,
            auteur_chasseur_id=1,
        )


def test_demande_revision_rejects_invalid_budget_range() -> None:
    with pytest.raises(
        ValidationError,
        match=(
            "budget_min must be less than or equal "
            "to budget_max"
        ),
    ):
        DemandeRevision(
            motif_modification="Invalid budget test",
            budget_min=400000,
            budget_max=300000,
            auteur_systeme=True,
        )


def test_presentation_accepts_valid_matching_score() -> None:
    payload = PresentationCreate(
        id_demande_version=1,
        id_bien=1,
        score_matching=87.50,
    )

    assert float(payload.score_matching) == 87.50


@pytest.mark.parametrize(
    "score",
    [-0.01, 100.01, 150],
)
def test_presentation_rejects_invalid_matching_score(
    score: float,
) -> None:
    with pytest.raises(ValidationError):
        PresentationCreate(
            id_demande_version=1,
            id_bien=1,
            score_matching=score,
        )


@pytest.mark.parametrize(
    "note",
    [-1, 6, 10],
)
def test_visite_rejects_invalid_note(
    note: int,
) -> None:
    with pytest.raises(ValidationError):
        VisiteCreate(
            date_visite="2026-09-02T14:30:00Z",
            id_presentation=1,
            note=note,
        )


def test_visite_accepts_valid_note() -> None:
    payload = VisiteCreate(
        date_visite="2026-09-02T14:30:00Z",
        id_presentation=1,
        note=5,
        photos=[],
    )

    assert payload.note == 5
    assert payload.photos == []