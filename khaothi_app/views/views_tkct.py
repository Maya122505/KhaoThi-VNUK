from django.shortcuts import render
from .views_common import ensure_actor_logged_in

def tkct_view(request):
    """
    Thư ký Chấm thi (TKCT) Portal view.
    """
    ensure_actor_logged_in(request, 'tkct')
    return render(request, 'khaothi_app/tkct/giaodienTKCT.html')
