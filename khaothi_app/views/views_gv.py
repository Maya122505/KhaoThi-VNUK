from django.shortcuts import render
from .views_common import ensure_actor_logged_in

def gv_view(request):
    """
    Giảng viên / Cán bộ chấm thi Portal view.
    """
    ensure_actor_logged_in(request, 'GV001')
    return render(request, 'khaothi_app/gv/giaodienGV.html')
