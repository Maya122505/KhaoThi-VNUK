from django.shortcuts import render
from .views_common import ensure_actor_logged_in

def ldp_view(request):
    """
    Lãnh đạo phòng (LDP) Portal view.
    """
    ensure_actor_logged_in(request, 'ldp')
    return render(request, 'khaothi_app/ldp/giaodienLDP.html')
