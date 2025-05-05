from django.urls import path

from . import views

urlpatterns = [path("index", views.index, name="index"),
	       path('UserLogin', views.UserLogin, name="UserLogin"),
	       path('UserLoginAction', views.UserLoginAction, name="UserLoginAction"),	   
	       path('Signup', views.Signup, name="Signup"),
	       path('SignupAction', views.SignupAction, name="SignupAction"),
	       path('TrainNLP', views.TrainNLP, name="TrainNLP"),
	       path('GenerateSummary', views.GenerateSummary, name="GenerateSummary"),
	       path('GenerateSummaryAction', views.GenerateSummaryAction, name="GenerateSummaryAction"),	
	       path('Aboutus', views.Aboutus, name="Aboutus"),	       
]