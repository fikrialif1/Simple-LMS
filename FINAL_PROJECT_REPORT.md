# FINAL PROJECT REPORT

## Identitas

- **Nama:** Muhammad Fikri Alif Karim
- **NIM:** A11.2023.15180
- **Kelas:** A11.4602
- **Repository:** https://github.com/fikrialif1/Simple-LMS.git

---

## Deskripsi Project

Simple LMS merupakan aplikasi Learning Management System berbasis Django dan Django Ninja API yang memungkinkan instructor membuat course, student melakukan enrollment, mempelajari materi, serta memantau progress pembelajaran. Project ini menggunakan PostgreSQL sebagai database utama, Redis untuk caching, MongoDB untuk analytics, dan Celery untuk background task.

---

## Fitur Dasar yang Sudah Berjalan

- JWT Authentication
- Role-based Access Control (Admin, Instructor, Student)
- CRUD Course
- Enrollment System
- Progress Tracking
- Reports & Analytics
- Celery Background Tasks
- Redis Caching
- MongoDB Activity Logs
- Swagger API Documentation
- Docker Compose Deployment
- Flower Monitoring

---

## Fitur Tambahan yang Dipilih

| No | Fitur | Kategori | Poin | Status |
|----|--------|-----------|-------|---------|
| 1 | Course Announcement | Instructor Feature | 10 | ✅ Selesai |
| 2 | Student Dashboard | Dashboard | 12 | ✅ Selesai |
| 3 | Instructor Dashboard | Dashboard | 12 | ✅ Selesai |
| 4 | Consistent Response & Error Format | API Improvement | 10 | ✅ Selesai |
| 5 | Health Check dan API Changelog | Monitoring & Documentation | 8 | ✅ Selesai |

**Total Poin Tambahan: 52**

---

## Penjelasan Implementasi

### 1. Course Announcement

Instructor dapat membuat pengumuman pada course tertentu dan student dapat melihat daftar pengumuman tersebut.

Endpoint:

- `POST /api/courses/{course_id}/announcements`
- `GET /api/courses/{course_id}/announcements`

---

### 2. Student Dashboard

Dashboard student menampilkan:

- Jumlah course aktif
- Jumlah course selesai
- Progress setiap course
- Rekomendasi course sederhana

Endpoint:

```text
GET /api/dashboard/student
```

---

### 3. Instructor Dashboard

Dashboard instructor menampilkan:

- Total course yang dimiliki
- Total enrollment
- Course paling populer
- Progress belajar student

Endpoint:

```text
GET /api/dashboard/instructor
```

---

### 4. Consistent API Response & Error Format

Seluruh endpoint menggunakan helper:

```python
api_success(message, data)
api_error(status_code, message)
```

Format response berhasil:

```json
{
  "success": true,
  "message": "Request berhasil",
  "data": {}
}
```

Format error:

```json
{
  "detail": {
    "success": false,
    "message": "Course tidak ditemukan",
    "data": null
  }
}
```

---

### 5. Health Check & API Changelog

Endpoint health check digunakan untuk memastikan seluruh layanan berjalan dengan baik.

```text
GET /api/health
```

Melakukan pengecekan:

- PostgreSQL
- Redis
- MongoDB

Endpoint changelog:

```text
GET /api/changelog
```

Menampilkan daftar perubahan dan fitur yang tersedia pada API.

---

## Cara Menjalankan Project

### 1. Clone repository

```bash
git clone https://github.com/fikrialif1/Simple-LMS.git
cd simple-lms
```

### 2. Jalankan Docker Compose

```bash
docker compose up --build
```

### 3. Jalankan migrasi

```bash
docker compose exec web python manage.py migrate
```

### 4. Membuat superuser

```bash
docker compose exec web python manage.py createsuperuser
```

### 5. Akses aplikasi

| Service | URL |
|----------|------|
| API Docs | http://localhost:8000/api/docs |
| Django Admin | http://localhost:8000/admin |
| Flower Monitoring | http://localhost:5555 |

---

## Akun Demo

| Role | Username | Password |
|-------|-----------|------------|
| Admin | admin | admin123 |
| Instructor | instructor1 | instructor123 |
| Student | student1 | 123456 |

---

## Endpoint Penting

### Authentication

```text
POST /api/auth/register
POST /api/auth/login
POST /api/auth/refresh
GET  /api/auth/me
PUT  /api/auth/m
```

### Course

```text
GET    /api/courses
GET    /api/courses/{id}
POST   /api/courses
PATCH  /api/courses/{id}
DELETE /api/courses/{id}
```

### Enrollment

```text
POST /api/enrollments
GET  /api/enrollments/my-courses
POST /api/enrollments/{id}/progress
```

### Dashboard

```text
GET /api/dashboard/student
GET /api/dashboard/instructor
```

### Announcement

```text
POST /api/courses/{id}/announcements
GET  /api/courses/{id}/announcements
```
### Reports
```text
GET  /api/reports/enrollments
POST /api/reports/export
GET  /api/reports/analytics
```

### System

```text
GET /api/health
GET /api/changelog
```
---

## Screenshot / Bukti Pengujian

### Swagger API Documentation

![Swagger](Screenshots/final%20project/Swagger-api-docs.png)

### Authentication (JWT)

![Authentication](Screenshots/final%20project/Login.png)

### Course & Enrollment

![Course](Screenshots/final%20project/get-course.png)
![Enrollment](Screenshots/final%20project/mark-progress.png)

### Student Dashboard

![Student Dashboard](Screenshots/final%20project/student-dashboard.png)

### Instructor Dashboard

![Instructor Dashboard](Screenshots/final%20project/instructor-dashboard.png)

### Course Announcement

![Announcement](Screenshots/final%20project/create-announcement.png)
![Announcement](Screenshots/final%20project/melihat-announcement.png)

### Reports & Analytics

![Reports](Screenshots/final%20project/analytics-report.png)
![Reports](Screenshots/final%20project/export-report.png)

### System (Health Check & Changelog)

![Health](Screenshots/final%20project/health.png)
![Changelog](Screenshots/final%20project/changelog.png)

### Consistent API Response

![Success Response](Screenshots/final%20project/student-dashboard.png)
![Error Response](Screenshots/final%20project/error-response.png)

### Flower Monitoring
![Monitoring](Screenshots/final%20project/Flowermonitoring.png)

---

## Kendala dan Solusi

| Kendala | Solusi |
|----------|---------|
| Redis tidak dapat diakses dari container web | Melakukan rebuild Docker dan memastikan hostname redis sesuai dengan docker-compose |
| PostgreSQL tidak memiliki tabel setelah migrasi | Menjalankan kembali docker compose exec web python manage.py migrate pada container |
| Format error API tidak konsisten | Membuat helper api_success() dan api_error() |
| Response Swagger tidak sesuai schema | Mengubah seluruh response menjadi `dict` agar konsisten |
| Instructor tidak dapat membuat announcement | Memastikan instructor adalah pemilik course yang bersangkutan |

---

## Kesimpulan

Melalui final project ini, saya mempelajari pengembangan REST API menggunakan Django Ninja, implementasi autentikasi JWT, integrasi PostgreSQL, Redis, MongoDB, dan Celery dalam satu aplikasi. Selain fitur dasar LMS, saya juga menambahkan dashboard, announcement, health check, dan konsistensi format response untuk meningkatkan kualitas sistem. Pengalaman ini memberikan pemahaman yang lebih mendalam mengenai pengembangan backend modern, asynchronous task processing, caching, monitoring, serta pengelolaan aplikasi multi-container menggunakan Docker Compose.


