# Simple LMS - Django Docker Setup

Project ini merupakan setup environment development untuk aplikasi Simple LMS menggunakan Django, Docker, dan PostgreSQL sebagai database.

Project ini bertujuan untuk mempermudah proses development dengan environment yang konsisten menggunakan container Docker.

## Cara Menjalankan Project

1. Build Docker Image

```bash
docker compose build
```

2. Jalankan Container

```bash
docker compose up
```

3. Jalankan Migration Database

Buka terminal baru lalu jalankan:

```bash
docker compose exec web python manage.py migrate
```

4. Akses Aplikasi

Buka browser dan masuk ke:

```
http://localhost:8000
```

Jika berhasil maka halaman Django akan tampil.

---

## Environment Variables Explanation

Project ini menggunakan environment variables untuk konfigurasi database PostgreSQL.

Contoh isi file `.env.example`:

```
POSTGRES_DB=lms_db
POSTGRES_USER=lms_user
POSTGRES_PASSWORD=lms_password
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

Penjelasan Variabel

| Variable          | Deskripsi                |
| ----------------- | ------------------------ |
| POSTGRES_DB       | Nama database PostgreSQL |
| POSTGRES_USER     | Username PostgreSQL      |
| POSTGRES_PASSWORD | Password PostgreSQL      |
| POSTGRES_HOST     | Host database container  |
| POSTGRES_PORT     | Port PostgreSQL          |


Environment variables ini digunakan oleh Django untuk melakukan koneksi ke database PostgreSQL yang berjalan di dalam Docker container.

---

## Screenshot Django Welcome Page

Berikut tampilan halaman awal Django setelah project berhasil dijalankan:

![Django Welcome Page](screenshots/Djangowelcomepage.png)

Halaman ini dapat diakses melalui:
http://localhost:8000

Jika halaman tersebut muncul, berarti:

- Docker container berjalan dengan baik
- Django berhasil dijalankan
- Koneksi PostgreSQL berhasil