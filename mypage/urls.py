from django.urls import path
from .views import *

app_name='mypage'

urlpatterns = [
    path('', PhotoListView.as_view(), name='mypage'),
    path('detail/<int:pk>/',PhotoDetailView.as_view(), name='photo_detail'),
    path('upload/', PhotoUploadView.as_view(), name='photo_upload'),
    path('delete/<int:pk>/', PhotoDeleteView.as_view(), name='photo_delete'),
    path('update/<int:pk>/', PhotoUpdateView.as_view(), name='photo_update'),
    path('like/<int:post_id>/',PhotoLike.as_view(), name="like"),
    path('comment/<int:comment_id>/', CommentCreateView.as_view(), name="comment"),
    path('comment/<int:comment_id>/', CCCommentCreateView.as_view(), name="CCCcomment"),
    path('user/<str:user_id>/', UserPostListView.as_view(), name="userpage"),
    path('follow/<str:user_id>/',UserFollow.as_view(), name="follow"),
]