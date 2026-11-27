import uuid
from decimal import Decimal

from django.db import models


def new_grading_id():
    return f"grd_{uuid.uuid4().hex[:12]}"


class Grading(models.Model):
    """One record per submitted exam attempt."""

    class Status(models.TextChoices):
        PENDING_REVIEW = "PENDING_REVIEW"
        GRADED = "GRADED"

    grading_id = models.CharField(
        max_length=32, primary_key=True, default=new_grading_id, editable=False
    )
    attempt_id = models.CharField(max_length=64, unique=True)
    exam_id = models.CharField(max_length=64, db_index=True)
    student_id = models.CharField(max_length=64)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING_REVIEW
    )
    total_points_earned = models.DecimalField(
        max_digits=8, decimal_places=2, default=Decimal("0.00")
    )
    total_points_possible = models.DecimalField(
        max_digits=8, decimal_places=2, default=Decimal("0.00")
    )
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def percentage(self):
        if not self.total_points_possible:
            return Decimal("0.00")
        return (
            Decimal(self.total_points_earned)
            * 100
            / Decimal(self.total_points_possible)
        ).quantize(Decimal("0.01"))

    def __str__(self):
        return f"{self.attempt_id} ({self.status})"


class QuestionGrade(models.Model):
    """The score for one question inside one attempt."""

    class Status(models.TextChoices):
        AUTO_GRADED = "AUTO_GRADED"
        NEEDS_REVIEW = "NEEDS_REVIEW"
        MANUALLY_GRADED = "MANUALLY_GRADED"

    grading = models.ForeignKey(
        Grading, on_delete=models.CASCADE, related_name="question_grades"
    )
    question_id = models.CharField(max_length=64)
    student_answer = models.JSONField(null=True, blank=True)
    points_possible = models.DecimalField(max_digits=6, decimal_places=2)
    points_earned = models.DecimalField(
        max_digits=6, decimal_places=2, default=Decimal("0.00")
    )
    suggested_points = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.NEEDS_REVIEW
    )
    feedback = models.TextField(blank=True, default="")
    reason = models.TextField(blank=True, default="")
    graded_by = models.CharField(max_length=64, blank=True, default="")

    class Meta:
        ordering = ["id"]  # noqa: RUF012
        constraints = [  # noqa: RUF012
            models.UniqueConstraint(
                fields=["grading", "question_id"], name="unique_question_per_grading"
            )
        ]

    def __str__(self):
        return f"{self.grading_id}/{self.question_id} ({self.status})"
