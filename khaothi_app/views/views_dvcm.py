from django.shortcuts import render
from .views_common import ensure_actor_logged_in

def dvcm_view(request):
    """
    Đơn vị chuyên môn (DVCM) Portal view.
    """
    ensure_actor_logged_in(request, 'dvcm')
    return render(request, 'khaothi_app/dvcm/giaodienDVCM.html')
