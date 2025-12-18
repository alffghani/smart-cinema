import streamlit as st
import pandas as pd
import time
import qrcode
import random
from io import BytesIO
from datetime import datetime
from PIL import Image


# ================= DATA STRUCTURES =================

class Queue:
    def __init__(self):
        self.items = []

    def enqueue(self, x):
        self.items.append(x)

    def dequeue(self):
        return self.items.pop(0) if self.items else None


class Node:
    def __init__(self, value):
        self.value = value
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None

    def insert(self, value):
        node = Node(value)
        if not self.head:
            self.head = node
        else:
            cur = self.head
            while cur.next:
                cur = cur.next
            cur.next = node

    def to_list(self):
        res = []
        cur = self.head
        while cur:
            res.append(cur.value)
            cur = cur.next
        return res

# ================= CONFIG =================
st.set_page_config("Smart Cinema", layout="wide")

ROWS, COLS = 7, 10
PRICE = 50000
ADMIN_PASSWORD = "admin123"


# ================= HELPER =================
def nav_button(label, page_name):
    active = st.session_state.page == page_name
    if st.button(
        label,
        type="primary" if active else "secondary",
        use_container_width=True
    ):
        st.session_state.page = page_name
        st.rerun()


def init_state(key, value):
    if key not in st.session_state:
        st.session_state[key] = value


# ================= STYLE =================
st.markdown("""
<style>
.poster-img img {
    height: 280px;
    object-fit: cover;
    border-radius: 10px;
}
.film-card {
    background-color: #111;
    padding: 10px;
    border-radius: 12px;
    margin-bottom: 15px;
}
.seat-btn button {
    width:100%;
    height:45px;
    font-weight:bold;
}
.seat-btn button:hover {
    transform:scale(1.05);
    transition:0.2s;
}
</style>
""", unsafe_allow_html=True)


# ================= INIT SESSION STATE =================
init_state("page", "home")
init_state("film", None)
init_state("name", "")
init_state("selected_seats", [])
init_state("queue", Queue())
init_state("queue_number", 0)
init_state("is_admin", False)

# ================= TOP HEADER BAR =================
col_title, col_nav = st.columns([7, 3])

with col_title:
    st.markdown(
        "<h1 style='margin-bottom:0;'>Smart Cinema</h1>",
        unsafe_allow_html=True
    )

with col_nav:
    nav1, nav2, nav3 = st.columns(3)

    with nav1:
        nav_button("Home", "home")

    with nav2:
        nav_button("About", "about")

    with nav3:
        nav_button("Admin", "admin_login")

st.divider()


# ================= SESSION STATE =================

def init_state(key, value):
    if key not in st.session_state:
        st.session_state[key] = value


def random_schedule():
    studios = ["Studio 1", "Studio 2", "Studio 3"]
    times = ["10:00", "13:00", "16:30", "19:00", "21:30"]
    days = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]

    return {
        "studio": random.choice(studios),
        "time": random.sample(times, 3),
        "days": random.sample(days, 4)
    }


FILMS_DATA = {
    "Avengers": {
        "desc": "Avengers mengisahkan pertemuan para superhero terkuat Marvel seperti Iron Man, Captain America, Thor, dan Hulk yang harus bersatu untuk menghadapi ancaman global dari Loki. Dengan konflik ego, perbedaan prinsip, dan aksi spektakuler, film ini menunjukkan bahwa hanya dengan kerja sama mereka mampu menyelamatkan bumi dari kehancuran besar.",
        "actors": [
            "Robert Downey Jr.",
            "Chris Evans",
            "Chris Hemsworth",
            "Mark Ruffalo",
            "Scarlett Johansson"
        ],
        "rating": "8.0 / 10",
        "duration": "2 jam 23 menit",
        "genre": "Action, Sci-Fi",
        "poster": "https://image.tmdb.org/t/p/w500/RYMX2wcKCBAr24UyPD7xwmjaTn.jpg"
    },

    "Interstellar": {
        "desc": "Interstellar menceritakan perjalanan sekelompok astronot yang meninggalkan bumi demi mencari planet baru bagi kelangsungan umat manusia. Dengan pendekatan ilmiah yang kuat, emosi keluarga yang mendalam, dan visual luar angkasa yang megah, film ini mengeksplorasi waktu, relativitas, dan pengorbanan dalam skala kosmik.",
        "actors": [
            "Matthew McConaughey",
            "Anne Hathaway",
            "Jessica Chastain",
            "Michael Caine",
            "Matt Damon"
        ],
        "rating": "8.6 / 10",
        "duration": "2 jam 49 menit",
        "genre": "Sci-Fi, Drama",
        "poster": "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg"
    },

    "Dune": {
        "desc": "Dune mengisahkan Paul Atreides, pewaris keluarga bangsawan yang harus berpindah ke planet gurun Arrakis, satu-satunya sumber rempah paling berharga di alam semesta. Intrik politik, pengkhianatan, dan takdir besar membentuk perjalanan Paul menuju perannya sebagai pemimpin yang akan menentukan masa depan kekuasaan galaksi.",
        "actors": [
            "Timothée Chalamet",
            "Zendaya",
            "Oscar Isaac",
            "Rebecca Ferguson",
            "Jason Momoa"
        ],
        "rating": "8.1 / 10",
        "duration": "2 jam 35 menit",
        "genre": "Sci-Fi, Adventure",
        "poster": "https://image.tmdb.org/t/p/w500/d5NXSklXo0qyIYkgV94XAgMIckC.jpg"
    },

    "Oppenheimer": {
        "desc": "Oppenheimer mengangkat kisah J. Robert Oppenheimer, ilmuwan jenius di balik Proyek Manhattan yang menciptakan bom atom. Film ini menyoroti dilema moral, tekanan politik, dan konsekuensi besar dari penemuan ilmiah yang mengubah sejarah dunia secara permanen.",
        "actors": [
            "Cillian Murphy",
            "Emily Blunt",
            "Matt Damon",
            "Robert Downey Jr.",
            "Florence Pugh"
        ],
        "rating": "8.5 / 10",
        "duration": "3 jam",
        "genre": "Drama, History",
        "poster": "https://image.tmdb.org/t/p/w500/ptpr0kGAckfQkJeJIt8st5dglvd.jpg"
    },

    "Batman": {
        "desc": "Batman mengikuti perjalanan Bruce Wayne sebagai detektif gelap Gotham yang harus menghadapi kejahatan brutal dan korupsi yang merajalela. Dengan pendekatan realistis dan nuansa noir, film ini menggali sisi psikologis Batman dalam menghadapi musuh serta masa lalunya sendiri.",
        "actors": [
            "Robert Pattinson",
            "Zoë Kravitz",
            "Paul Dano",
            "Jeffrey Wright",
            "Colin Farrell"
        ],
        "rating": "7.9 / 10",
        "duration": "2 jam 56 menit",
        "genre": "Action, Crime",
        "poster": "https://image.tmdb.org/t/p/w500/74xTEgt7R36Fpooo50r9T25onhq.jpg"
    },

    "Inception": {
        "desc": "Inception bercerita tentang Dom Cobb, seorang pencuri profesional yang mencuri rahasia melalui alam bawah sadar manusia. Dengan konsep mimpi berlapis, film ini menyajikan teka-teki psikologis, aksi menegangkan, dan pertanyaan mendalam tentang realitas dan ingatan.",
        "actors": [
            "Leonardo DiCaprio",
            "Joseph Gordon-Levitt",
            "Elliot Page",
            "Tom Hardy",
            "Ken Watanabe"
        ],
        "rating": "8.8 / 10",
        "duration": "2 jam 28 menit",
        "genre": "Sci-Fi, Thriller",
        "poster": "https://image.tmdb.org/t/p/w500/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg"
    },

    "Spider-Man": {
        "desc": "Spider-Man mengisahkan Peter Parker, remaja biasa yang memperoleh kekuatan laba-laba dan harus belajar menyeimbangkan kehidupan pribadi dengan tanggung jawab sebagai pahlawan. Film ini menampilkan aksi seru, humor ringan, serta perjuangan moral seorang pahlawan muda.",
        "actors": [
            "Tom Holland",
            "Zendaya",
            "Jacob Batalon",
            "Marisa Tomei",
            "Michael Keaton"
        ],
        "rating": "8.2 / 10",
        "duration": "2 jam 28 menit",
        "genre": "Action, Fantasy",
        "poster": "https://image.tmdb.org/t/p/w500/5weKu49pzJCt06OPpjvT80efnQj.jpg"
    },

    "Parasite": {
        "desc": "Parasite adalah film satir sosial yang menggambarkan kesenjangan kelas antara keluarga miskin dan keluarga kaya. Dengan alur cerita penuh kejutan dan simbolisme kuat, film ini menyajikan kritik tajam terhadap struktur sosial modern yang penuh ketimpangan.",
        "actors": [
            "Song Kang-ho",
            "Lee Sun-kyun",
            "Cho Yeo-jeong",
            "Choi Woo-shik",
            "Park So-dam"
        ],
        "rating": "8.6 / 10",
        "duration": "2 jam 12 menit",
        "genre": "Thriller, Drama",
        "poster": "https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg"
    }
}

init_state("films", {film: LinkedList() for film in FILMS_DATA})
init_state("film_schedule", {film: random_schedule() for film in FILMS_DATA})
init_state("sales_log", [])

# ================= PROGRESS =================

def progress(step):
    steps = ["Pilih Film", "Pilih Kursi", "Pembayaran", "Selesai"]
    html = "<div style='display:flex;gap:10px;margin-bottom:20px;'>"
    for i, s in enumerate(steps):
        html += f"<b style='color:{'#ff4b8b' if i==step else '#777'}'>{s}</b>"
        if i < 3:
            html += " → "
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

# ================= HOME =================

if st.session_state.page == "home":

    st.subheader("Sedang Tayang")
    cols = st.columns(4)

    for i, film in enumerate(FILMS_DATA):
        with cols[i % 4]:
            st.markdown('<div class="film-card poster-img">', unsafe_allow_html=True)
            st.image(FILMS_DATA[film]["poster"])
            st.markdown(f"**{film}**")
            st.caption(FILMS_DATA[film]["genre"])

            if st.button("Pesan Tiket", key=film):
                st.session_state.film = film
                st.session_state.page = "detail"
                st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

# ================ FILM DETAIL ==================


elif st.session_state.page == "detail":

    film = st.session_state.film

    if film is None:
        st.info("Silakan pilih film terlebih dahulu")
    else:
        data = FILMS_DATA[film]
        schedule = st.session_state.film_schedule[film]

        st.subheader("Detail Film")

        col_poster, col_info = st.columns([1, 3])

        # ===== POSTER =====
        with col_poster:
            st.image(data["poster"], width=220)

            st.markdown("#### Info Film")
            st.markdown(
                f"""
                Durasi  : {data['duration']}  
                Rating  : {data['rating']}  
                Genre   : {data['genre']}
                """
            )

        # ===== INFO =====
        with col_info:
            st.markdown(f"## {film}")  # JUDUL LEBIH BESAR
            st.write(data["desc"])

            st.markdown("#### Aktor yang Memerankan")
            st.write(", ".join(data["actors"]))

            st.markdown("#### Jadwal Tayang")
            st.markdown(
                f"""
                Studio  : {schedule['studio']}  
                Jam     : {', '.join(schedule['time'])}  
                Hari    : {', '.join(schedule['days'])}
                """
            )

            st.divider()

            colA, colB = st.columns(2)
            with colA:
                if st.button("Kembali"):
                    st.session_state.page = "home"
                    st.rerun()

            with colB:
                if st.button("Pesan Tiket"):
                    st.session_state.page = "buyer"
                    st.rerun()

elif st.session_state.page == "about":
    st.subheader("Tentang Smart Cinema")

    st.markdown("""
    **Smart Cinema Booking System** adalah aplikasi pemesanan tiket bioskop
    berbasis web yang dirancang untuk memberikan pengalaman pemesanan yang
    cepat, modern, dan interaktif.

    ### Fitur Utama
    - Pemilihan film & jadwal
    - Pemilihan kursi real-time
    - Simulasi pembayaran
    - Dashboard admin
    - QR Code tiket

    Dibuat sebagai project sistem pemesanan modern menggunakan **Streamlit**.
    """)

    if st.button("Kembali ke Home"):
        st.session_state.page = "home"
        st.rerun()


# ================= ADMIN LOGIN =================

elif st.session_state.page == "admin_login":

    st.subheader("Login Admin")

    password = st.text_input("Password Admin", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Login"):
            if password == ADMIN_PASSWORD:
                st.session_state.is_admin = True
                st.session_state.page = "admin"
                st.rerun()
            else:
                st.error("Password salah")

    with col2:
        if st.button("Kembali"):
            st.session_state.page = "home"
            st.rerun()



# ================= ADMIN DASHBOARD =================

elif st.session_state.page == "admin":

    if not st.session_state.is_admin:
        st.warning("Akses admin ditolak")
        st.session_state.page = "admin_login"
        st.rerun()

    st.subheader("Dashboard Admin")

    if not st.session_state.sales_log:
        st.info("Belum ada transaksi")
    else:
        df = pd.DataFrame(st.session_state.sales_log)
        df["date"] = pd.to_datetime(df["date"])
        df["day"] = df["date"].dt.date
        df["month"] = df["date"].dt.to_period("M").astype(str)

        c1, c2, c3 = st.columns(3)
        c1.metric("Tiket Terjual", df["seats"].sum())
        c2.metric("Pendapatan", f"Rp {df['total'].sum():,}")
        c3.metric("Transaksi", len(df))

        st.divider()
        st.line_chart(df.groupby("day")["total"].sum())
        st.bar_chart(df.groupby("month")["total"].sum())
        st.dataframe(df)

    if st.button("Keluar Admin"):
        st.session_state.is_admin = False
        st.session_state.page = "home"
        st.rerun()


# ================= BUYER =================

elif st.session_state.page == "buyer":
    progress(0)
    st.subheader("Data Pemesan")
    name = st.text_input("Nama Pembeli")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Kembali"):
            st.session_state.page = "home"
            st.rerun()
    with col2:
        if st.button("Lanjut"):
            if name:
                st.session_state.name = name
                st.session_state.queue.enqueue(name)
                st.session_state.queue_number = len(st.session_state.queue.items)
                st.session_state.page = "seat"
                st.rerun()
            else:
                st.warning("Masukkan nama terlebih dahulu")

# ================= SEAT SELECTION =================
elif st.session_state.page == "seat":
    progress(1)
    st.subheader("Pilih Kursi")

    # ===== LAYOUT 2 KOLOM + PEMBATAS =====
    left, divider, right = st.columns([1.2, 0.05, 3])

    # ================= PANEL KIRI : INFO FILM =================
    with left:
        film = st.session_state.film
        data = FILMS_DATA[film]

        # Poster (diperkecil)
        st.image(data["poster"], width=220)

        st.markdown(f"### {film}")
        st.markdown(f"**Durasi:** {data['duration']}")
        st.markdown(f"**Rating:** {data['rating']}")
        st.markdown(f"**Genre:** {data['genre']}")

        # ===== HITUNG SISA KURSI =====
        occupied = [
            x[1]
            for x in st.session_state.films[film].to_list()
        ]
        sisa = (ROWS * COLS) - len(occupied)

        st.markdown("---")
        st.markdown(f"**Sisa Kursi:** `{sisa}`")

    # ================= PEMBATAS =================
    with divider:
        st.markdown(
            "<div style='height:100%; border-left:2px solid #444;'></div>",
            unsafe_allow_html=True
        )

    # ================= PANEL KANAN : SEAT SELECTION =================
    with right:

        # ===== LAYAR BIOSKOP =====
        st.markdown("""
        <div style="
            margin: 40px 0 80px 0;
            padding: 25px;
            background: linear-gradient(90deg, #222, #333);
            color: white;
            text-align: center;
            font-size: 26px;
            font-weight: bold;
            letter-spacing: 5px;
            border-radius: 15px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.6);
        ">
         L A Y A R
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='margin-bottom:60px'></div>", unsafe_allow_html=True)

        # ===== AMBIL KURSI YANG SUDAH TERISI =====
        occupied = [
        x[1]
        for x in st.session_state.films[st.session_state.film].to_list()
        ]

        # ===== GRID KURSI =====
        for r in range(ROWS):
            cols = st.columns(COLS)
            for c in range(COLS):
                seat = f"{chr(65+r)}{c+1}"

                with cols[c]:
                    # === STATUS KURSI ===
                    if seat in occupied:
                        label = f"⬜ {seat}"      # SUDAH TERISI
                        disabled = True
                    elif seat in st.session_state.selected_seats:
                        label = f"🟥 {seat}"      # DIPILIH USER
                        disabled = False
                    else:
                        label = f"⬛ {seat}"      # KOSONG
                        disabled = False

                    if st.button(label, key=seat, disabled=disabled):
                        if seat in st.session_state.selected_seats:
                            st.session_state.selected_seats.remove(seat)
                        else:
                            st.session_state.selected_seats.append(seat)
                        st.rerun()


        # ===== INFO =====
        st.divider()
        st.info(f"Kursi dipilih: {', '.join(st.session_state.selected_seats)}")
        st.success(f"Total: Rp {len(st.session_state.selected_seats) * PRICE:,}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Kembali"):
                st.session_state.page = "buyer"
                st.rerun()

        with col2:
            if st.button("Lanjut Pembayaran"):
                if st.session_state.selected_seats:
                    st.session_state.page = "payment"
                    st.rerun()
                else:
                    st.warning("Pilih minimal 1 kursi")

# ================= PAYMENT =================

elif st.session_state.page == "payment":
    progress(2)
    st.subheader("Konfirmasi & Pembayaran")

    film = st.session_state.film
    film_data = FILMS_DATA[film]
    total = len(st.session_state.selected_seats) * PRICE

    # ===== LAYOUT =====
    left, right = st.columns([1, 2])

    # ================= LEFT: POSTER & INFO FILM =================
    with left:
        st.image(film_data["poster"], width=220)

        st.markdown(f"### {film}")
        st.markdown(f"**Durasi:** {film_data['duration']}")
        st.markdown(f"**Rating:** {film_data['rating']}")
        st.markdown(f"**Genre:** {film_data['genre']}")

        st.divider()

    # ================= RIGHT: RINGKASAN & PEMBAYARAN =================
    with right:
        st.markdown(f"""
        <div style="
            background-color:#111;
            padding:20px;
            border-radius:12px;
            box-shadow:0 4px 12px rgba(0,0,0,0.4);
        ">
        <h4>Ringkasan Pesanan</h4>
        Nama Pembeli : <b>{st.session_state.name}</b><br>
        Film         : <b>{film}</b><br>
        Kursi        : {', '.join(st.session_state.selected_seats)}<br>
        Jumlah Tiket : {len(st.session_state.selected_seats)}<br>
        Nomor Antrian: {st.session_state.queue_number}
        <hr>
        <h3 style="color:#ff4b8b;">Total: Rp {total:,}</h3>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### Metode Pembayaran")
        method = st.radio("", ["Kartu", "E-Wallet", "Transfer Bank", "Cash"])
        agree = st.checkbox("Saya menyetujui detail pesanan")

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Kembali"):
            st.session_state.page = "seat"
            st.rerun()

    with col2:
        if st.button("Bayar Sekarang", disabled=not agree):
            with st.spinner("Memproses pembayaran..."):
                time.sleep(2)

            for seat in st.session_state.selected_seats:
                st.session_state.films[film].insert((st.session_state.name, seat))

            st.session_state.sales_log.append({
                "date": datetime.now(),
                "film": film,
                "seats": len(st.session_state.selected_seats),
                "total": total,
                "method": method
            })

            st.session_state.queue.dequeue()
            st.session_state.page = "success"
            st.rerun()

# ================= SUCCESS =================

elif st.session_state.page == "success":
    progress(3)
    st.success("Pembayaran Berhasil!")
    qr_text = f"{st.session_state.name} | {st.session_state.film} | {st.session_state.selected_seats}"
    qr = qrcode.make(qr_text)
    buf = BytesIO()
    qr.save(buf)
    buf.seek(0)
    st.image(buf, caption="Scan QR Code")

    if st.button("Kembali ke Home"):
        st.session_state.name = ""
        st.session_state.selected_seats = []
        st.session_state.page = "home"
        st.rerun()