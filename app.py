
from flask import Flask, render_template_string
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io
import base64
import os

app = Flask(__name__)


# Membaca data 10 kelompok dari Excel
df_excel = pd.read_excel("pak wingdes.xlsx", header=None)

data_kelompok = df_excel.iloc[46:56, 2:12].apply(
    pd.to_numeric, errors="coerce"
)

data_kelompok.columns = [
    f"Column{i}" for i in range(1, 11)
]

# Menghitung statistik setiap kelompok
stat_kelompok = pd.DataFrame({
    "Jumlah": data_kelompok.count(),
    "Mean": data_kelompok.mean(),
    "Median": data_kelompok.median(),
    "Standar Deviasi": data_kelompok.std(),
    "Minimum": data_kelompok.min(),
    "Maximum": data_kelompok.max()
}).round(2)


# Data regresi dari file Excel tugas
# Data ini sama dengan 10 hari pada tabel Excel kamu
data = pd.DataFrame({
    "Hari": range(1, 11),
    "Pengunjung": [4, 3, 5, 8, 8, 9, 7, 10, 11, 12],
    "Penjualan": [5, 7, 7, 5, 7, 6, 6, 9, 11, 11]
})

def buat_grafik():
    gambar = io.BytesIO()
    plt.figure(figsize=(7, 4))
    plt.scatter(data["Pengunjung"], data["Penjualan"],
                label="Data aktual")
    m, b = __import__("numpy").polyfit(
        data["Pengunjung"], data["Penjualan"], 1
    )
    plt.plot(data["Pengunjung"], m * data["Pengunjung"] + b,
             color="red", label="Garis regresi")
    plt.xlabel("Pengunjung (X)")
    plt.ylabel("Penjualan (Y)")
    plt.title("Hubungan Pengunjung dan Penjualan")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(gambar, format="png")
    plt.close()
    gambar.seek(0)
    return base64.b64encode(gambar.getvalue()).decode("utf-8")

HTML = """
<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Dashboard Statistik</title>
<style>
* { box-sizing: border-box; }
body {
    margin: 0; font-family: Arial, sans-serif;
    background: #f1f5f9; color: #172033;
}
header {
    background: #172554; color: white;
    padding: 28px 6%;
}
header h1 { margin: 0 0 8px; }
main { max-width: 1150px; margin: 25px auto; padding: 0 18px; }
.cards {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
    gap: 16px; margin-bottom: 22px;
}
.card, section {
    background: white; border-radius: 12px;
    padding: 22px; box-shadow: 0 3px 12px #0000000c;
}
.card p { color: #64748b; margin: 0 0 10px; }
.card h2 { margin: 0; color: #1d4ed8; }
section { margin-bottom: 22px; overflow-x: auto; }
h2 { margin-top: 0; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 12px; border-bottom: 1px solid #e2e8f0; text-align: center; }
th { background: #e0e7ff; }
img { max-width: 100%; height: auto; }
.insight { line-height: 1.8; }
footer { text-align: center; color: #64748b; padding: 25px; }
</style>
</head>
<body>
<header>
    <h1>Dashboard Statistik Deskriptif</h1>
    <p>Analisis data pengunjung, penjualan, dan regresi linear</p>
</header>
<main>
    <div class="cards">
        <div class="card"><p>Total hari pengamatan</p><h2>{{ jumlah }}</h2></div>
        <div class="card"><p>Rata-rata pengunjung</p><h2>{{ mean_x }}</h2></div>
        <div class="card"><p>Rata-rata penjualan</p><h2>{{ mean_y }}</h2></div>
        <div class="card"><p>Korelasi X dan Y</p><h2>{{ korelasi }}</h2></div>
    </div>

    <section>
        <h2>Statistik Deskriptif</h2>
        <table>
        <tr><th>Variabel</th><th>Mean</th><th>Median</th>
        <th>Standar Deviasi</th><th>Minimum</th><th>Maximum</th></tr>
        {% for nama, row in statistik.iterrows() %}
        <tr>
        <td>{{ nama }}</td><td>{{ "%.2f"|format(row["mean"]) }}</td>
        <td>{{ "%.2f"|format(row["median"]) }}</td>
        <td>{{ "%.2f"|format(row["std"]) }}</td>
        <td>{{ "%.2f"|format(row["min"]) }}</td>
        <td>{{ "%.2f"|format(row["max"]) }}</td>
        </tr>
        {% endfor %}
        </table>
    </section>

    
<section>
    <h2>Statistik Deskriptif 10 Kelompok</h2>
    <table>
        <tr>
            <th>Kelompok</th>
            <th>Jumlah</th>
            <th>Mean</th>
            <th>Median</th>
            <th>Standar Deviasi</th>
            <th>Minimum</th>
            <th>Maximum</th>
        </tr>
        {% for nama, row in stat_kelompok.iterrows() %}
        <tr>
            <td>{{ nama }}</td>
            <td>{{ "%.0f"|format(row["Jumlah"]) }}</td>
            <td>{{ "%.2f"|format(row["Mean"]) }}</td>
            <td>{{ "%.2f"|format(row["Median"]) }}</td>
            <td>{{ "%.2f"|format(row["Standar Deviasi"]) }}</td>
            <td>{{ "%.2f"|format(row["Minimum"]) }}</td>
            <td>{{ "%.2f"|format(row["Maximum"]) }}</td>
        </tr>
        {% endfor %}
    </table>
</section>


    <section>
        <h2>Grafik Regresi Linear</h2>
        <img src="data:image/png;base64,{{ grafik }}" alt="Grafik regresi">
        <p>Persamaan regresi: <b>Y = {{ a }} + {{ b }}X</b></p>
        <p>Prediksi penjualan untuk 13 pengunjung: <b>{{ prediksi }}</b></p>
    </section>

    
<section>
    <h2>Multiple Linear Regression</h2>

    <p>Variabel target: <b>Penjualan (Y)</b></p>
    <p>Variabel bebas: <b>Hari (X1)</b> dan
    <b>Pengunjung (X2)</b></p>

    <h3>Persamaan Regresi Berganda</h3>
    <p>
        Y = {{ konstanta_multi }}
        + ({{ koef_hari }}) Hari
        + ({{ koef_pengunjung }}) Pengunjung
    </p>

    <h3>Koefisien Regresi</h3>
    <table>
        <tr>
            <th>Variabel</th>
            <th>Koefisien</th>
        </tr>
        <tr>
            <td>Konstanta</td>
            <td>{{ konstanta_multi }}</td>
        </tr>
        <tr>
            <td>Hari (X1)</td>
            <td>{{ koef_hari }}</td>
        </tr>
        <tr>
            <td>Pengunjung (X2)</td>
            <td>{{ koef_pengunjung }}</td>
        </tr>
    </table>

    <h3>Kualitas Model</h3>
    <p>R-kuadrat (R²): <b>{{ r2_multi }}</b></p>

    <h3>Hasil Prediksi</h3>
    <p>Hari ke-11 dengan 13 pengunjung:</p>
    <p>Prediksi penjualan:
        <b>{{ prediksi_multi }}</b>
    </p>

    <h3>Kesimpulan</h3>
    <div class="insight">
        <p>
            Model regresi linear berganda menggunakan
            hari dan jumlah pengunjung secara bersamaan
            untuk memperkirakan penjualan.
        </p>
        <p>
            Nilai R² menunjukkan proporsi variasi
            penjualan yang dapat dijelaskan oleh model
            pada data pengamatan ini.
        </p>
        <p>
            Hasil prediksi merupakan perkiraan berdasarkan
            data yang tersedia, bukan jaminan penjualan
            sebenarnya.
        </p>
    </div>
</section>


    <section>
        <h2>Insight Statistik</h2>
        <div class="insight">
        <p>1. Rata-rata pengunjung adalah {{ mean_x }}, sedangkan rata-rata penjualan adalah {{ mean_y }}.</p>
        <p>2. Hubungan pengunjung dan penjualan memiliki korelasi {{ korelasi }}.</p>
        <p>3. Persamaan regresi dapat digunakan untuk memperkirakan penjualan berdasarkan jumlah pengunjung.</p>
        <p>4. Prediksi merupakan perkiraan berdasarkan pola 10 hari pengamatan, bukan jaminan penjualan sebenarnya.</p>
        </div>
    </section>

    <section>
        <h2>Data Pengamatan</h2>
        {{ tabel|safe }}
    </section>
</main>
<footer>Dashboard Statistik • Flask Lokal</footer>
</body>
</html>
"""

@app.route("/")
def dashboard():
    import numpy as np

    x = data["Pengunjung"]
    y = data["Penjualan"]
    b, a = np.polyfit(x, y, 1)

    
    # Multiple Linear Regression: Hari dan Pengunjung -> Penjualan
    X_multi = data[["Hari", "Pengunjung"]].to_numpy(dtype=float)

    # Menambahkan konstanta untuk menghitung intercept
    X_desain = np.column_stack([
        np.ones(len(data)),
        X_multi
    ])

    # Menghitung konstanta dan koefisien regresi
    koef_multi = np.linalg.lstsq(
        X_desain, y.to_numpy(dtype=float), rcond=None
    )[0]

    konstanta_multi = koef_multi[0]
    koef_hari = koef_multi[1]
    koef_pengunjung = koef_multi[2]

    # Menghitung nilai prediksi pada data pengamatan
    prediksi_data = X_desain @ koef_multi

    # Menghitung R-kuadrat
    ss_res = np.sum((y.to_numpy() - prediksi_data) ** 2)
    ss_tot = np.sum((y.to_numpy() - y.mean()) ** 2)
    r2_multi = 1 - ss_res / ss_tot if ss_tot != 0 else 0

    # Contoh prediksi hari ke-11 dengan 13 pengunjung
    prediksi_multi = (
        konstanta_multi
        + koef_hari * 11
        + koef_pengunjung * 13
    )


    return render_template_string(
        HTML,
        jumlah=len(data),
        mean_x=round(x.mean(), 2),
        mean_y=round(y.mean(), 2),
        korelasi=round(x.corr(y), 3),
        statistik=data[["Pengunjung", "Penjualan"]].agg(
            ["mean", "median", "std", "min", "max"]
        ).T,

        stat_kelompok=stat_kelompok,
        
        grafik=buat_grafik(),
        a=round(a, 3),
        b=round(b, 3),
        prediksi=round(a + b * 13, 2),
        tabel=data.to_html(index=False, classes="data-table")
    )

if __name__ == "__main__":
    app.run(debug=True)
