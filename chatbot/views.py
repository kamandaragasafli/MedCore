"""
Chatbot Views - AI Chatbot with n8n integration
Only available for Professional and Enterprise plans
"""
import json
import requests
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings
from subscription.decorators import subscription_required, contract_required
from .decorators import chatbot_required
from django.contrib import messages



@login_required
@subscription_required
@contract_required
@chatbot_required
def chatbot_view(request):
    """
    Main chatbot interface
    """
    context = {
        'n8n_webhook_url': settings.N8N_WEBHOOK_URL,
        'company_name': request.company.name if hasattr(request, 'company') else '',
    }
    return render(request, 'chatbot/chatbot.html', context)


@login_required
@subscription_required
@contract_required
@chatbot_required
@require_http_methods(["POST"])
def send_message(request):
    """
    Send message to n8n webhook and get AI response
    """
    try:
        # Debug: Log the request
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Chatbot message received from user {request.user.id}")
        
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        logger.info(f"User message: {user_message[:50]}...")
        
        if not user_message:
            return JsonResponse({
                'success': False,
                'error': 'Mesaj boş ola bilməz'
            }, status=400)
        
        # Prepare data to send to n8n webhook
        webhook_data = {
            'message': user_message,
            'user_id': request.user.id,
            'username': request.user.username,
            'company_id': request.company.id if hasattr(request, 'company') else None,
            'company_name': request.company.name if hasattr(request, 'company') else '',
            'session_id': request.session.session_key,
            # API endpoint for AI to query database
            'api_endpoint': request.build_absolute_uri('/chatbot/api/query/'),
            'api_available': True,
        }
        
        # Send to n8n webhook
        try:
            headers = {
                'Content-Type': 'application/json',
            }
            
            # Add API key if configured
            if hasattr(settings, 'N8N_API_KEY') and settings.N8N_API_KEY:
                headers['Authorization'] = f'Bearer {settings.N8N_API_KEY}'
            
            response = requests.post(
                settings.N8N_WEBHOOK_URL,
                json=webhook_data,
                headers=headers,
                timeout=30  # 30 second timeout
            )
            
            if response.status_code == 200:
                # Parse n8n response
                try:
                    n8n_response = response.json()
                    # Handle both dict and list responses from n8n
                    if isinstance(n8n_response, list):
                        # If n8n returns a list, take the first item or join them
                        if len(n8n_response) > 0:
                            first_item = n8n_response[0]
                            if isinstance(first_item, dict):
                                ai_message = first_item.get('response', first_item.get('message', str(first_item)))
                            else:
                                ai_message = str(first_item)
                        else:
                            ai_message = 'Cavab alına bilmədi.'
                    elif isinstance(n8n_response, dict):
                        ai_message = n8n_response.get('response', n8n_response.get('message', 'Cavab alına bilmədi.'))
                    else:
                        # If it's a string or other type
                        ai_message = str(n8n_response) if n8n_response else 'Cavab alına bilmədi.'
                except (json.JSONDecodeError, ValueError):
                    # If response is not JSON, use text
                    ai_message = response.text or 'Cavab alına bilmədi.'
                
                return JsonResponse({
                    'success': True,
                    'message': ai_message,
                    'timestamp': response.headers.get('Date', '')
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'n8n webhook xətası: {response.status_code}'
                }, status=response.status_code)
                
        except requests.exceptions.Timeout:
            return JsonResponse({
                'success': False,
                'error': 'Cavab gözləyərkən vaxt aşımı baş verdi. Zəhmət olmasa yenidən cəhd edin.'
            }, status=504)
        except requests.exceptions.ConnectionError:
            return JsonResponse({
                'success': False,
                'error': 'n8n serverinə qoşula bilmədi. Zəhmət olmasa daha sonra cəhd edin.'
            }, status=503)
        except requests.exceptions.RequestException as e:
            return JsonResponse({
                'success': False,
                'error': f'Xəta baş verdi: {str(e)}'
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Yanlış məlumat formatı'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Gözlənilməz xəta: {str(e)}'
        }, status=500)
