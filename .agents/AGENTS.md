# Quy Chuẩn Lập Trình Dự Án Django (KhaoThi-VNUK)
> [!IMPORTANT]
> Đây là tài liệu quy chuẩn lập trình được tổng hợp trực tiếp từ giáo trình **"Web Development with Django 4"**. Mọi Agent khi thực hiện công việc lập trình, sửa đổi mã nguồn hoặc viết tính năng mới trên dự án này đều phải tuân thủ nghiêm ngặt các quy tắc dưới đây.

---

## 1. Kiến Trúc MVT & Tổ Chức Mã Nguồn

### 1.1. Nguyên lý Model-View-Template (MVT)
* **Model (M)**: Chỉ chứa định nghĩa dữ liệu, các quan hệ chéo, phương thức nghiệp vụ của riêng đối tượng và validation mức dữ liệu. Không chứa logic liên quan tới HTTP request/response hoặc hiển thị.
* **View (V)**: Đóng vai trò là bộ điều khiển xử lý HTTP Request và trả về HTTP Response. Phải giữ View ngắn gọn (Thin Views). Chuyển các logic nghiệp vụ phức tạp vào lớp **Services** (`services/`) hoặc phương thức của **Model** để tăng khả năng tái sử dụng và dễ viết unit test.
* **Template (T)**: Chỉ thực hiện hiển thị thông tin. Hạn chế tối đa logic phức tạp trong template; thay vào đó sử dụng Context Processors, Template Filters hoặc Template Tags.

### 1.2. Cấu trúc thư mục của ứng dụng
Đối với các ứng dụng lớn (như `khaothi_app`), cần phân chia mã nguồn thành các thư mục/file chuyên biệt thay vì viết tập trung:
* Các view được chia nhỏ theo chức năng (ví dụ: `views_common.py`, `views_tkt.py`, `views_gv.py` đặt trong thư mục `views/`).
* Các form được chia thành các file hoặc đặt trong thư mục `forms/` (ví dụ: `forms_tkt.py`).
* Các URL được tổ chức mạch lạc và liên kết tới URL chính của dự án (`urls_main.py` của app được include từ `urls.py` dự án).

---

## 2. Thiết Kế Models, Migrations & Tối Ưu Hóa Truy Vấn ORM

### 2.1. Thiết kế Model & Hành vi Khóa ngoại
* **on_delete**: Phải chọn kiểu xử lý phù hợp cho khóa ngoại:
  * Sử dụng `models.PROTECT` cho các thực thể quan trọng (như `Khoa`, `User`, `LopHanhChinh`) để tránh vô tình xóa mất dữ liệu liên quan.
  * Sử dụng `models.CASCADE` cho các bảng trung gian hoặc dữ liệu phụ thuộc hoàn toàn (như `DanhSachThiSinh` phụ thuộc vào `LichThi`).
  * Sử dụng `models.SET_NULL` (yêu cầu `null=True, blank=True`) nếu muốn giữ lại bản ghi khi thực thể liên kết bị xóa.
* **related_name**: Bắt buộc phải khai báo thuộc tính `related_name` có ý nghĩa cho mọi trường `ForeignKey` và `ManyToManyField` để dễ dàng truy vấn ngược từ thực thể đích.

### 2.2. Tối ưu hóa truy vấn ORM (Tránh lỗi N+1 Query)
> [!WARNING]
> Lỗi N+1 query xảy ra khi truy vấn một danh sách các đối tượng và tiếp tục gọi thuộc tính liên kết của từng đối tượng đó trong vòng lặp, tạo ra hàng chục truy vấn SQL không cần thiết.

* **select_related**: Sử dụng khi truy vấn các trường liên kết dạng **ForeignKey** hoặc **OneToOneField**. Django sẽ thực hiện truy vấn SQL JOIN để lấy dữ liệu đồng thời.
  ```python
  # TỐT: Chỉ thực hiện 1 câu truy vấn JOIN duy nhất
  lich_thi_list = LichThi.objects.select_related('ky_thi', 'phong_thi').all()
  ```
* **prefetch_related**: Sử dụng khi truy vấn các trường liên kết dạng **ManyToManyField** hoặc các quan hệ khóa ngoại ngược (Reverse Foreign Key). Django sẽ thực hiện truy vấn riêng biệt và gom nhóm lại bằng Python.
  ```python
  # TỐT: Lấy danh sách túi phách và danh sách mã phách của từng túi
  tui_phach_list = TuiPhach.objects.prefetch_related('danh_sach_phach').all()
  ```
* **exists() & count()**: 
  * Sử dụng `.exists()` thay cho `.count() > 0` hoặc kiểm tra độ dài `len(queryset)` nếu chỉ cần xác định xem bản ghi có tồn tại hay không.
  * Sử dụng `.count()` thay vì `len(queryset)` khi chỉ cần lấy số lượng bản ghi mà không cần dùng đến dữ liệu thực tế của các bản ghi.

### 2.3. Tác vụ Bulk (Số lượng lớn)
* Khi tạo nhiều bản ghi cùng lúc, hãy dùng `bulk_create` thay vì chạy vòng lặp gọi `.save()` để giảm tải cho database.
* Khi cập nhật nhiều bản ghi với các trường cụ thể, dùng `bulk_update` và truyền tham số `fields`.
  ```python
  SinhVien.objects.bulk_update(sinh_vien_list, ['is_eligible'])
  ```

---

## 3. Views & URL Routing

### 3.1. Phân chia FBVs và CBVs
* **Function-Based Views (FBVs)**: Sử dụng khi view có logic xử lý luồng HTTP phi tiêu chuẩn, hoặc yêu cầu nhiều bước trung gian đặc thù.
* **Class-Based Views (CBVs)**: Ưu tiên sử dụng cho các chức năng CRUD chuẩn mực. Kế thừa từ các view dựng sẵn của Django (`ListView`, `DetailView`, `CreateView`, `UpdateView`, `DeleteView`) để giảm trùng lặp mã nguồn.

### 3.2. URL Mapping & Namespacing
* Luôn sử dụng `app_name` trong file `urls.py` của ứng dụng để khai báo namespace.
* Mọi url pattern phải có thuộc tính `name` rõ ràng. Khi chuyển hướng hoặc gọi link trong template, bắt buộc sử dụng hàm `reverse()` hoặc tag `{% url %}` với định dạng `'namespace:url_name'`.
  ```html
  <a href="{% url 'khaothi_app:lich_thi_detail' ma_lich_thi=lich.ma_lich_thi %}">Chi tiết</a>
  ```

---

## 4. Forms & Advanced Validation

### 4.1. Bảo mật và Xử lý Request
* Mọi form gửi qua phương thức POST bắt buộc phải chứa thẻ `{% csrf_token %}` để phòng chống tấn công CSRF.
* Luôn kiểm tra tính hợp lệ của form bằng `form.is_valid()` trước khi thực hiện bất kỳ thao tác lưu trữ hay xử lý dữ liệu nào từ `form.cleaned_data`.

### 4.2. Validation Nâng cao (Custom Clean Methods)
* **Clean Field riêng lẻ**: Viết hàm `clean_<field_name>()` trong lớp Form để kiểm tra logic ràng buộc của riêng trường đó và trả về giá trị đã chuẩn hóa.
  ```python
  def clean_ma_sinh_vien(self):
      ma_sv = self.cleaned_data.get('ma_sinh_vien')
      if not ma_sv.startswith('SV'):
          raise ValidationError("Mã sinh viên phải bắt đầu bằng chữ 'SV'.")
      return ma_sv
  ```
* **Clean Đa trường (Multi-field validation)**: Viết hàm `clean()` của lớp Form khi cần so sánh, đối chiếu logic giữa nhiều trường dữ liệu khác nhau.
  ```python
  def clean(self):
      cleaned_data = super().clean()
      gio_bat_dau = cleaned_data.get('gio_bat_dau')
      gio_ket_thuc = cleaned_data.get('gio_ket_thuc')
      if gio_bat_dau and gio_ket_thuc and gio_bat_dau >= gio_ket_thuc:
          raise ValidationError("Giờ bắt đầu phải nhỏ hơn giờ kết thúc.")
      return cleaned_data
  ```

### 4.3. ModelForms
* Sử dụng `ModelForm` khi form đại diện trực tiếp cho một Model trong database để tránh định nghĩa lại các trường. Luôn khai báo danh sách thuộc tính `fields` cụ thể trong class `Meta`, không dùng `fields = '__all__'`.

---

## 5. Quản Lý Static & Media Files

### 5.1. Static Files (File Tĩnh)
* Lưu trữ các asset dùng chung cho toàn bộ dự án trong thư mục `static/` ở thư mục gốc (nếu được cấu hình trong `STATICFILES_DIRS`).
* Các asset của riêng app phải được đặt dưới cấu trúc namespace để tránh xung đột tên file: `khaothi_app/static/khaothi_app/css/style.css`.
* Sử dụng thẻ tag `{% static 'khaothi_app/css/style.css' %}` để tạo URL động.

### 5.2. Media Files (Ảnh/Tệp Tải lên)
* Cấu hình chính xác `MEDIA_ROOT` (thư mục vật lý lưu file) và `MEDIA_URL` (đường dẫn URL để truy cập).
* Trong môi trường phát triển (DEBUG=True), bắt buộc cấu hình serving media trong file `urls.py` của dự án:
  ```python
  from django.conf import settings
  from django.conf.urls.static import static

  urlpatterns = [
      # ... urls ...
  ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
  ```
* Sử dụng context processor `django.template.context_processors.media` để có thể sử dụng biến `{{ MEDIA_URL }}` trực tiếp trong template khi cần liên kết tới các file tải lên.

---

## 6. Sessions, Middleware & Authentication (Phân Quyền)

### 6.1. Bảo vệ Views bằng Authentication Decorators/Mixins
* Đối với FBVs, sử dụng decorator `@login_required` để giới hạn quyền truy cập cho người dùng đã đăng nhập.
* Đối với CBVs, kế thừa `LoginRequiredMixin` làm lớp cơ sở đầu tiên.
  ```python
  from django.contrib.auth.mixins import LoginRequiredMixin
  from django.views.generic import ListView

  class LichThiListView(LoginRequiredMixin, ListView):
      # ...
  ```

### 6.2. Phân quyền dựa trên vai trò (Role-Based Access Control)
* Dự án KhaoThi-VNUK sử dụng hệ thống vai trò được quy định trong trường `role` của custom model `User` (`ROLE_CHOICES`: `tkt`, `tkct`, `dvcm`, `gv`, `ldp`, `cvht`).
* Khi viết các chức năng cho từng nhóm người dùng, bắt buộc sử dụng decorator `@user_passes_test` hoặc xây dựng các Custom Mixin để kiểm tra giá trị của trường `request.user.role`.
  ```python
  from django.contrib.auth.decorators import user_passes_test

  def is_tkt(user):
      return user.is_authenticated and user.role == 'tkt'

  @user_passes_test(is_tkt)
  def quan_ly_ca_thi_view(request):
      # ... chỉ tổ khảo thí mới được vào
  ```

---

## 7. Tùy Biến Django Admin nâng cao

* Đăng ký model với admin bằng cách viết các lớp kế thừa từ `admin.ModelAdmin`.
* Sử dụng thuộc tính `list_display` để hiển thị các cột quan trọng, `list_filter` cho các bộ lọc thông minh, `search_fields` để hỗ trợ tìm kiếm nhanh, và `date_hierarchy` cho các dữ liệu thời gian.
* Sử dụng decorator `@admin.display` khi định nghĩa các cột hiển thị dữ liệu tính toán (custom columns).
  ```python
  @admin.display(description='Số lượng thí sinh')
  def show_so_luong_sv(self, obj):
      return obj.danh_sach_thi_sinh.count()
  ```

---

## 8. Django REST Framework (DRF) & REST API

Khi xây dựng các API endpoints:
* **Serializers**: Kế thừa `serializers.ModelSerializer` để tự động hóa việc tuần tự hóa dữ liệu từ models. Định nghĩa rõ ràng các trường cần lấy để tối ưu hóa hiệu năng.
* **ViewSets & Routers**: Sử dụng `viewsets.ModelViewSet` hoặc `viewsets.ReadOnlyModelViewSet` kết hợp với `DefaultRouter` để tự động tạo hệ thống định tuyến (URLs) chuẩn RESTful và giảm thiểu dòng mã.
* **Authentication**: Sử dụng xác thực Token Authentication cho các API tương tác với client bên ngoài bằng cách cấu hình `authentication_classes = [TokenAuthentication]`.

---

## 9. Kiểm Thử Tự Động (Testing)

* **TestCase**: Luôn kế thừa từ lớp `django.test.TestCase` để thực hiện test database cô lập. Mỗi method test sẽ được chạy trong một transaction riêng biệt và tự động rollback sau khi hoàn thành.
* **RequestFactory**: Khi kiểm thử trực tiếp logic của view hoặc các middleware mà không cần giả lập toàn bộ quá trình truyền tải HTTP thông qua Client mặc định, hãy dùng `RequestFactory`.
  ```python
  from django.test import RequestFactory
  # ... tạo request giả lập và truyền trực tiếp vào view ...
  request = RequestFactory().get('/path/')
  response = my_view(request)
  ```
* **Tách biệt và Tổ chức**: Viết test cases rõ ràng cho Models (kiểm tra validation, các phương thức tự định nghĩa) và Views (kiểm tra status code trả về, template được render và các tham số context truyền ra ngoài).

---

## 10. Các Thư Viện Bên Thứ Ba khuyên dùng

* **django-crispy-forms**: Luôn sử dụng thư viện này để kết xuất (render) form Bootstrap đẹp mắt và quản lý giao diện form trực tiếp trong mã nguồn Python thông qua class `FormHelper` thay vì can thiệp thủ công vào file HTML.
* **django-configurations**: Dùng để quản lý các lớp cài đặt cấu hình dự án tách biệt cho môi trường cục bộ (Dev) và sản xuất (Prod) một cách linh hoạt, thay vì sửa trực tiếp file `settings.py`.
* **django-debug-toolbar**: Kích hoạt công cụ này trong môi trường Dev để đo kiểm hiệu năng, đặc biệt là kiểm soát số lượng truy vấn SQL được tạo ra trên mỗi request nhằm phát hiện sớm lỗi N+1 query.
