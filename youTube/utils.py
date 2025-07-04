# utils/download_tracker.py or views.py

from django.http import JsonResponse


download_progress = {}


def get_client_ip(request):
    """Utility to get client IP"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


download_progress = {}

def get_user_key(request):
    return str(request.user.id) if request.user.is_authenticated else get_client_ip(request)

import threading
import time

# def download_hook(user_key):
#     def hook(d):
#         if d['status'] == 'downloading':
#             percent = d.get('_percent_str', '').strip()
#             speed = d.get('_speed_str', '').strip()
#             eta = d.get('_eta_str', '').strip()
#             total = d.get('_total_bytes_str', '').strip() or d.get('_total_bytes_estimate_str', '').strip()

#             download_progress[user_key] = {
#                 'percent': percent,
#                 'speed': speed,
#                 'eta': eta,
#                 'total': total
#             }

#         elif d['status'] == 'finished':
#             download_progress[user_key] = {
#                 'percent': '100%',
#                 'speed': '0KiB/s',
#                 'eta': '00:00',
#                 'total': d.get('_total_bytes_str', '').strip() or 'Unknown'
#             }

#             # Clear progress after 5 seconds
#             def clear_later():
#                 time.sleep(5)
#                 download_progress.pop(user_key, None)

#             threading.Thread(target=clear_later).start()

#     return hook


import re

ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')

def clean_ansi(text):
    return ansi_escape.sub('', text)

def download_hook(user_key):
    def hook(d):
        if d['status'] == 'downloading':
            percent = clean_ansi(d.get('_percent_str', '').strip())
            speed = clean_ansi(d.get('_speed_str', '').strip())
            eta = clean_ansi(d.get('_eta_str', '').strip())
            total = clean_ansi(d.get('_total_bytes_str', '').strip() or d.get('_total_bytes_estimate_str', '').strip())

            download_progress[user_key] = {
                'percent': percent,
                'speed': speed,
                'eta': eta,
                'total': total
            }

        elif d['status'] == 'finished':
            download_progress[user_key] = {
                'percent': '100%',
                'speed': '0KiB/s',
                'eta': '00:00',
                'total': clean_ansi(d.get('_total_bytes_str', '').strip() or 'Unknown')
            }

            # Optionally clear progress after a delay
            import threading, time
            def clear_later():
                time.sleep(5)
                download_progress.pop(user_key, None)
            threading.Thread(target=clear_later).start()

    return hook


