import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import os

class ChatAPIView(APIView):
    def post(self, request):
        # Extract data from request
        user_message = request.data.get('message')

        # OpenAI API endpoint
        url = "https://api.openai.com/v1/chat/completions"

        # Prepare headers and payload
        auth = "Bearer " + os.environ.get("OPENAI_KEY")
        print(auth)
        headers = {
            "Authorization": auth,
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": user_message}]
        }

        # Make POST request to OpenAI
        response = requests.post(url, headers=headers, json=data)

        # Handle OpenAI response
        if response.status_code == 200:
            openai_response = response.json()
            return Response(openai_response, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Failed to fetch response from OpenAI"}, status=response.status_code)

