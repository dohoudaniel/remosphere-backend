from rest_framework import serializers
from .models import Application
from jobs.serializers import JobSerializer  # optional nested job view
from users.serializers import UserSerializer  # optional nested user view
from jobs.models import Job


class ApplicationCreateSerializer(serializers.ModelSerializer):
    # Accept job as ID
    # job = serializers.PrimaryKeyRelatedField(queryset=None)

    class Meta:
        model = Application
        fields = ["id", "job", "resume_url", "status", "applied_at"]
        read_only_fields = ["id", "status", "applied_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # avoid circular import at module load
        # from jobs.models import Job
        self.fields["job"].queryset = Job.objects.filter(
            is_active=True)  # Job.objects.all()

    def validate(self, attrs):
        user = self.context["request"].user
        job = attrs["job"]

        if not user or not user.is_authenticated:
            raise serializers.ValidationError("Authentication required.")

        # optionally: disallow applying if job is inactive
        if not job.is_active:
            raise serializers.ValidationError(
                "Cannot apply to an inactive job.")

        # check existing application
        if Application.objects.filter(job=job, user=user).exists():
            raise serializers.ValidationError(
                "You have already applied for this job.")

        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        return Application.objects.create(user=user, **validated_data)


class ApplicationDetailSerializer(serializers.ModelSerializer):
    # job = JobSerializer(read_only=True)
    # user = serializers.SerializerMethodField()
    job_title = serializers.CharField(source="job.title", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Application
        # fields = ["id", "job", "user", "resume_url", "status", "applied_at"]
        fields = "__all__"
        read_only_fields = ["id", "applied_at"]

    def get_user(self, obj):
        # keep small user representation (email + id)
        return {"id": obj.user_id, "email": getattr(obj.user, "email", None)}
