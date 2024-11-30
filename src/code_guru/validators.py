from settings import CANDIDATE_LEVELS


def validate_candidate_level(candidate_level: str) -> None:
    if candidate_level not in CANDIDATE_LEVELS:
        raise ValueError(
            f"Candidate level must be "
            f"one of those - {', '.join(CANDIDATE_LEVELS)}"
        )
