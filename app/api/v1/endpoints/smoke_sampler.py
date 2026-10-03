from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.v1.dtos.SmokeSamplerDTO import SmokeSamplerSubmitDTO
from app.api.v1.endpoints.auth import get_current_user
from app.core.deps import get_db
from app.models.userModel import UserModel
from app.models.SmokeSamplerModel import (
    SmokeSamplerSampleModel,
    SmokeSamplerSubmissionModel,
)

smoke_sampler_router = APIRouter()


@smoke_sampler_router.post("/", status_code=status.HTTP_201_CREATED)
@smoke_sampler_router.post("", status_code=status.HTTP_201_CREATED)
def submit_smoke_sampler(
    payload: SmokeSamplerSubmitDTO,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not payload.samples:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one smoke sample is required.",
        )

    try:
        submission = SmokeSamplerSubmissionModel(user_id=current_user.id)
        db.add(submission)
        db.flush()

        sample_rows = []

        for sample in payload.samples:
            chemical_name = sample.chemical_name.strip()

            if not chemical_name:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Chemical name cannot be empty.",
                )

            sample_rows.append(
                SmokeSamplerSampleModel(
                    submission_id=submission.submission_id,
                    chemical_name=chemical_name,
                    percentage_proportion=sample.percentage_proportion,
                )
            )

        db.add_all(sample_rows)
        db.commit()
        db.refresh(submission)

        return {
            "submission_id": str(submission.submission_id),
            "sample_count": len(sample_rows),
            "message": "Smoke sampler data saved successfully",
        }

    except HTTPException:
        db.rollback()
        raise

    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save smoke sampler data: {str(exc)}",
        ) from exc

    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected smoke sampler error: {str(exc)}",
        ) from exc