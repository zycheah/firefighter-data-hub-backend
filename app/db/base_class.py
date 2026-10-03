from app.db.base import Base

# Core auth/profile tables
from app.models.userModel import UserModel
from app.models.userProfileModel import UserProfileModel

# Frontend-required feature tables
from app.models.locationModel import LocationEntryModel
from app.models.LogEventModel import LogEventModel
from app.models.PpeModel import PpeModel
from app.models.SmokeSamplerModel import (
    SmokeSamplerSubmissionModel,
    SmokeSamplerSampleModel,
)

# Optional EC2/S3 proof-of-concept tables
from app.models.location_entry import LocationEntry
from app.models.uploaded_file import UploadedFile