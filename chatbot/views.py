"""
Chatbot Views - AI Chatbot with OpenAI integration
Only available for Professional and Enterprise plans
"""
import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings
from subscription.decorators import subscription_required, contract_required
from .decorators import chatbot_required
from django.contrib import messages

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None



@login_required
@subscription_required
@contract_required
@chatbot_required
def chatbot_view(request):
    """
    Main chatbot interface
    """
    # Get subscription and plan type explicitly
    subscription = None
    plan_type = None
    
    if hasattr(request, 'company') and request.company:
        subscription = request.company.active_subscription
        if subscription and subscription.plan:
            plan_type = subscription.plan.plan_type
    
    context = {
        'company_name': request.company.name if hasattr(request, 'company') else '',
        'subscription': subscription,
        'plan_type': plan_type,
    }
    return render(request, 'chatbot/chatbot.html', context)


@login_required
@subscription_required
@contract_required
@chatbot_required
@require_http_methods(["POST"])
def send_message(request):
    """
    Send message to OpenAI API and get AI response
    """
    try:
        # Check if OpenAI is available
        if OpenAI is None:
            return JsonResponse({
                'success': False,
                'error': 'OpenAI paketi quraşdırılmamışdır. Zəhmət olmasa openai paketini quraşdırın.'
            }, status=500)
        
        # Check if API key is configured
        if not hasattr(settings, 'OPENAI_API_KEY') or not settings.OPENAI_API_KEY:
            return JsonResponse({
                'success': False,
                'error': 'OpenAI API açarı təyin edilməyib. Zəhmət olmasa OPENAI_API_KEY təyin edin.'
            }, status=500)
        
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
        
        # Initialize OpenAI client
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Get conversation history from session
        conversation_history = request.session.get('chatbot_history', [])
        
        # Build system message with context
        company_name = request.company.name if hasattr(request, 'company') and request.company else 'Şirkət'
        system_message = f"""Sən tibbi idarəetmə sisteminin AI asistanısan. Şirkət adı: {company_name}

Sənə kömək edə biləcəyin əsas funksiyalar:
- Həkim məlumatları haqqında sorğular
- Qeydiyyat və resept məlumatları
- Satış və ödəniş statistikaları
- Hesabatlar haqqında məlumat
- Ümumi sistem istifadəsi məsləhətləri

Cavablarını Azərbaycan dilində ver. Qısa, dəqiq və faydalı ol.
"""
        
        # Prepare messages for OpenAI
        messages = [
            {"role": "system", "content": system_message}
        ]
        
        # Add conversation history
        messages.extend(conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Call OpenAI API
        try:
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL if hasattr(settings, 'OPENAI_MODEL') else "gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
            )
            
            # Get AI response
            ai_message = response.choices[0].message.content.strip()
            
            # Update conversation history (keep last 10 messages to avoid token limit)
            conversation_history.append({"role": "user", "content": user_message})
            conversation_history.append({"role": "assistant", "content": ai_message})
            if len(conversation_history) > 20:  # Keep last 10 exchanges (20 messages)
                conversation_history = conversation_history[-20:]
            request.session['chatbot_history'] = conversation_history
            request.session.modified = True
            
            logger.info(f"AI response generated successfully")
            
            return JsonResponse({
                'success': True,
                'message': ai_message,
            })
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'OpenAI API xətası: {str(e)}'
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Yanlış məlumat formatı'
        }, status=400)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Unexpected error in send_message: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Gözlənilməz xəta: {str(e)}'
        }, status=500)


@login_required
@subscription_required
@contract_required
@chatbot_required
@require_http_methods(["POST"])
def clear_history(request):
    """
    Clear chatbot conversation history from session
    """
    try:
        if 'chatbot_history' in request.session:
            del request.session['chatbot_history']
            request.session.modified = True
        
        return JsonResponse({
            'success': True,
            'message': 'Söhbət tarixçəsi təmizləndi'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Xəta: {str(e)}'
        }, status=500)
