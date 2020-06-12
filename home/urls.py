from django.urls import path
from .views import *

app_name='home'

urlpatterns = [
    path('', PhotoListView.as_view(), name='list'),
    path('<int:list_num>/', PhotoListView.as_view(), name='list_order'),
    path('detail/<int:pk>/',PhotoDetailView.as_view(), name='photo_detail'),
    path('comment/<int:comment_id>/', CommentCreateView.as_view(), name="home_comment"),
    path('CCCcomment/<int:comment_id>/', CCCommentCreateView.as_view(), name="home_CCCcomment"),
]