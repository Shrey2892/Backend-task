# from django.contrib.auth.models import User
# from django.db import models

# class ChatMessage(models.Model):
#     sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
#     receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_messages')
#     message = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.sender} -> {self.receiver}: {self.message[:20]}"
