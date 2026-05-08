from django.db import models


class PAIAssistanceSubmission(models.Model):
    victim_code = models.CharField(max_length=100, blank=True, null=True)
    victim_name = models.CharField(max_length=255, blank=True, null=True)
    assistance_type = models.CharField(max_length=255, blank=True, null=True)

    raw_data = models.JSONField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-submitted_at"]

    def __str__(self):
        return self.victim_code or f"PAI Submission #{self.id}"