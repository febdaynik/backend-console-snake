from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.status import HTTP_400_BAD_REQUEST
# More rest imports as needed
from django.contrib.auth import authenticate
from datetime import date, timedelta
from .decorators import define_usage
from .models import Task
from .serializers import taskSerializer

from django.contrib.auth.models import User

#URL /
@define_usage(returns={'url_usage': 'Dict'})
@api_view(['GET'])
@permission_classes((AllowAny,))
def api_index(requet):
	details = {}
	for item in list(globals().items()):
		if item[0][0:4] == 'api_':
			if hasattr(item[1], 'usage'):
				details[reverse(item[1].__name__)] = item[1].usage
	return Response(details)


#URL /signin/
#Note that in a real Django project, signin and signup would most likely be
#handled by a seperate app. For signup on this example, use the admin panel.
@define_usage(params={'username': 'String', 'password': 'String'},
			  returns={'authenticated': 'Bool', 'token': 'Token String'})
@api_view(['POST'])
@permission_classes((AllowAny,))
def api_signin(request):
	try:
		username = request.data['username']
		password = request.data['password']
	except:
		return Response({'error': 'Please provide correct username and password'},
						status=HTTP_400_BAD_REQUEST)
	user = authenticate(username=username, password=password)
	if user is not None:
		token, _ = Token.objects.get_or_create(user=user)
		return Response({'authenticated': True, 'token': "Token " + token.key})
	else:
		return Response({'authenticated': False, 'token': None})


#URL /all/
@define_usage(returns={'tasks': 'Dict'})
@api_view(['GET'])
@authentication_classes((SessionAuthentication, BasicAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
def api_all_tasks(request):
	tasks = taskSerializer(request.user.task_set.all(), many=True)
	return Response({'tasks': tasks.data})


#URL /new/
@define_usage(params={'name': 'String', 'due_in': 'Int', 'score': 'Int'},
			  returns={'done': 'Bool', 'task_id': 'Int'})
@api_view(['POST'])
@authentication_classes((SessionAuthentication, BasicAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
def api_new_task(request):
	task = Task(user=request.user,
				name=request.data['name'],
				due=date.today() + timedelta(days=int(request.data['due_in'])),
				score=request.data['score'])
	task.save()

	tasks = Task.objects.all()
	for i in tasks:
		if i.name == request.data['name']:
			task_id = i.id 
			break
	return Response({'done': True, 'task_id': task_id})


#URL /update/
@define_usage(params={'task_id': 'Int', 'name': 'String', 'due_in': 'Int', 'score': 'Int'},
			  returns={'done': 'Bool'}) 
@api_view(['POST'])
@authentication_classes((SessionAuthentication, BasicAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
def api_update_task(request):
	try:
		task = request.user.task_set.get(id=int(request.data['task_id']))
	except: pass
	try:
		task.name = request.data['name']
	except: #Description update is optional
		pass
	try:
		task.due = date.today() + timedelta(days=int(request.data['due_in']))
	except: #Due date update is optional
		pass
	try:
		task.score = request.data['score']
	except: pass
	task.save()
	return Response({'done': True})


#URL /delete/
@define_usage(params={'task_id': 'Int'},
			  returns={'done': 'Bool'})
@api_view(['DELETE'])
@authentication_classes((SessionAuthentication, BasicAuthentication, TokenAuthentication))
@permission_classes((IsAuthenticated,))
def api_delete_task(request):
	task = request.user.task_set.get(id=int(request.data['task_id']))
	task.delete()
	return Response({'done': True})
