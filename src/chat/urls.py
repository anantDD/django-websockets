from django.urls import path, re_path


from .views import ThreadView, InboxView, test_view

app_name = 'chat'
urlpatterns = [
    path("", InboxView.as_view()),
    path("test/<str:name>/<slug:slugname>/<int:num>", test_view),
    re_path(r"^(?P<username>[\w.@+-]+)", ThreadView.as_view()),
]
