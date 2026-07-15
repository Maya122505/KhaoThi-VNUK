from django.shortcuts import render
from .views_common import ensure_actor_logged_in

def cvht_view(request):
    """
    Chuyên viên Hệ thống (CVHT) Portal view.
    """
    ensure_actor_logged_in(request, 'cvht')
    return render(request, 'khaothi_app/cvht/giaodienCVHT.html')
