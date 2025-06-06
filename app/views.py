import json
from django.shortcuts import render
from django.http import HttpResponse
from helpers.unitalk_requests import get_unitalk_data
from helpers.akc import get_new_call_requests, get_pending_orders_count, get_unanswered_messages_count
from dashboard.settings import API_TOKEN
from .models import CRMModel
import subprocess
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


def home(request):
    if request.method == "GET":
        unitalk = get_unitalk_data(API_TOKEN)
        missed_calls = unitalk['missed_calls']
        lost_calls = unitalk['lost_calls']
        unique_missed_phones = unitalk['unique_missed_phones']
        unique_lost_phones = unitalk['unique_lost_phones']
        crm_qs = CRMModel.objects.filter(unread_chats__gt=0)
        crm_data = [{obj.channel_name: obj.unread_chats} for obj in crm_qs]
        updated_at = CRMModel.objects.values_list('updated_at', flat=True).last()
        request_recall_akc = get_new_call_requests()
        pending_orders = get_pending_orders_count()
        unanswered_messages = get_unanswered_messages_count()
        telegram_messages = TelegramMSGS.objects.all().count()
        if request_recall_akc:
            crm_data.append({"Заявки на дзвінок(akumulyator.center)": request_recall_akc})
        if pending_orders:
            crm_data.append({"Замовлення на сайті(akumulyator.center)": pending_orders})
        if unanswered_messages:
            crm_data.append({"Повідомлення без відповіді(akumulyator.center)": unanswered_messages})
        if telegram_messages > 0:
            crm_data.append({"заявки з aku.lviv": telegram_messages})
            
        result = {
            "missed_calls": missed_calls,
            "lost_calls": lost_calls,
            "unique_missed_phones": unique_missed_phones,
            "unique_lost_phones": unique_lost_phones,
            "crm": crm_data,
            "updated_at": updated_at
        }
        return render(request, 'index.html', result)

def get_unread_report(request):
    if request.method == "GET":
        unitalk = get_unitalk_data(API_TOKEN)
        missed_calls = unitalk['missed_calls']
        lost_calls = unitalk['lost_calls']
        crm_qs = CRMModel.objects.filter(unread_chats__gt=0)
        crm_data = [{obj.channel_name: obj.unread_chats} for obj in crm_qs]
        updated_at = CRMModel.objects.values_list('updated_at', flat=True).last()
        
            
        result = {
            "missed_calls": missed_calls,
            "lost_calls": lost_calls,
            "crm": crm_data,
            "updated_at": updated_at,
        }
        return JsonResponse(result)


@csrf_exempt
def run_parser_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            if data.get("code") == "6start6":
                subprocess.Popen(["python", "manage.py", "update_crm"])
                return JsonResponse({"status": "started"})
            else:
                return JsonResponse({"error": "invalid code"}, status=403)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "invalid method"}, status=405)
