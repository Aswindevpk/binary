from django.contrib import admin
from .models import CustomUser , PremiumSubscription,SubscriptionPlan,Payment

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(PremiumSubscription)
admin.site.register(SubscriptionPlan)
admin.site.register(Payment)

