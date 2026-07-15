from django.shortcuts import render

def tkcoithi_view(request):
    """
    Thư ký Coi thi Portal view.
    """
    return render(request, 'khaothi_app/tkcoithi/giaodienTKCOITHI.html')
