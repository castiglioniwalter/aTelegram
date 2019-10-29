from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('inseriscinumero', views.index, name='InserisciNumero'),
    path('contatti', views.contatti, name='Contatti'),
    path('chat/<int:id>', views.chat, name='chat'),
    path('setcontatti/<int:num>/<int:id_contatto>', views.setcontatti, name='setcontatti'),
    path('setcontatti/', views.setcontatti, name='setcontatti'),
    path('setcontatti/<str:num>', views.setcontatti, name='setcontatti'),
    path('chatdebug/<int:id>/<int:idm>', views.chatdebug, name='chatdebug'),
    path('chatdebug/<int:id>', views.chatdebug, name='chatdebug'),
    path('contattidebug/', views.contattidebug, name='contattidebug'),
    path('chat/update', views.update, name='update'),
    #path('bottone',views.contatti_bottone, name='bottone'),
    #path('button_listener/<int:id>', views.button_listener, name='button_listener'),
    #path('button_listener/update_bottone', views.update_bottone, name='update_bottone')
]
