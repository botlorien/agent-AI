from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ChatSerializer
from .agent_openai import Assistent
import os

instructions = """
Você é um Assitente pessoal responsavel por fornecer insights do mercado financeiro com base na resposta de consulta de  Apis
Além da habilidade de encaminhar emails
"""
OPENAI_API_KEY_PORTFOLIO = os.getenv('OPENAI_API_KEY_PORTFOLIO')
print(OPENAI_API_KEY_PORTFOLIO)
ass = Assistent(
    'portfolio',
    instructions=instructions,
    api_key=OPENAI_API_KEY_PORTFOLIO
)


class ChatAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ChatSerializer(data=request.data)
        if serializer.is_valid():
            user_message = serializer.validated_data['message']
            resp = ass.chat(user_message)
            return Response({'response':resp['message']}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def chat_view(request):
    return render(request, 'agentAI/chat.html')