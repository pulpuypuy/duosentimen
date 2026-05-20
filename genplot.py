"""
genplot.py - Modul Visualisasi Data Sentimen

Modul ini menyediakan fungsi-fungsi untuk menghasilkan visualisasi
data sentimen menggunakan Plotly (chart interaktif) dan Matplotlib/
WordCloud (gambar statis).

Output berupa string HTML (Plotly div) atau base64 PNG string yang
dapat langsung di-embed di template HTML Flask.
"""

import base64
import io
import logging
from typing import Dict, List, Optional

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend untuk server
import matplotlib.pyplot as plt

import plotly.graph_objects as go
import plotly.express as px
from wordcloud import WordCloud

logger = logging.getLogger(__name__)

# Palet warna sentimen
COLOR_PALETTE = {
    'positif': '#00b894',
    'negatif': '#e17055',
    'netral': '#fdcb6e'
}

# Warna default untuk urutan sentimen
DEFAULT_COLORS = ['#00b894', '#e17055', '#fdcb6e']


def generate_pie_chart(label_counts_dict: Dict[str, int]) -> str:
    """
    Menghasilkan pie chart distribusi sentimen menggunakan Plotly.

    Args:
        label_counts_dict: Dictionary {label: jumlah} untuk setiap
                          kelas sentimen.
                          Contoh: {'positif': 2500, 'negatif': 1500, 'netral': 1000}

    Returns:
        String HTML div berisi pie chart Plotly interaktif
        (tanpa plotly.js, hanya div element).
    """
    if not label_counts_dict:
        logger.warning("Data label_counts kosong untuk pie chart")
        return '<div>Tidak ada data untuk ditampilkan</div>'

    labels = list(label_counts_dict.keys())
    values = list(label_counts_dict.values())
    colors = [COLOR_PALETTE.get(label, '#636e72') for label in labels]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=colors),
        textinfo='label+percent',
        textfont=dict(size=14),
        hovertemplate='<b>%{label}</b><br>'
                      'Jumlah: %{value}<br>'
                      'Persentase: %{percent}<extra></extra>',
        hole=0.3
    )])

    fig.update_layout(
        title=dict(
            text='Distribusi Sentimen',
            font=dict(size=18, color='#2d3436'),
            x=0.5
        ),
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.15,
            xanchor='center',
            x=0.5
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=60, b=60, l=40, r=40),
        height=450
    )

    return fig.to_html(full_html=False, include_plotlyjs=False)


def generate_bar_chart(
    categories: List[str],
    values: List[float],
    title: str = 'Bar Chart'
) -> str:
    """
    Menghasilkan bar chart menggunakan Plotly.

    Args:
        categories: List berisi nama kategori untuk sumbu X.
        values: List berisi nilai untuk setiap kategori.
        title: Judul chart (default: 'Bar Chart').

    Returns:
        String HTML div berisi bar chart Plotly interaktif.
    """
    if not categories or not values:
        logger.warning("Data kosong untuk bar chart")
        return '<div>Tidak ada data untuk ditampilkan</div>'

    colors = [
        COLOR_PALETTE.get(cat, '#0984e3')
        for cat in categories
    ]

    fig = go.Figure(data=[go.Bar(
        x=categories,
        y=values,
        marker_color=colors,
        text=[f'{v}' for v in values],
        textposition='auto',
        hovertemplate='<b>%{x}</b><br>'
                      'Jumlah: %{y}<extra></extra>'
    )])

    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=18, color='#2d3436'),
            x=0.5
        ),
        xaxis=dict(
            title='Kategori',
            tickfont=dict(size=12)
        ),
        yaxis=dict(
            title='Jumlah',
            tickfont=dict(size=12)
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=60, b=60, l=60, r=40),
        height=450
    )

    return fig.to_html(full_html=False, include_plotlyjs=False)


def generate_wordcloud_image(
    text: str,
    title: str = '',
    colormap: str = 'viridis'
) -> str:
    """
    Menghasilkan word cloud dari teks dan mengembalikan sebagai base64 PNG.

    Args:
        text: String teks yang akan divisualisasikan sebagai word cloud.
        title: Judul gambar word cloud (opsional).
        colormap: Nama colormap matplotlib (default: 'viridis').

    Returns:
        String base64-encoded PNG gambar word cloud.
        Dapat di-embed di HTML menggunakan:
        <img src="data:image/png;base64,{result}">
    """
    if not text or not text.strip():
        logger.warning("Teks kosong untuk word cloud")
        # Buat gambar kosong dengan pesan
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.text(
            0.5, 0.5, 'Tidak ada data teks',
            ha='center', va='center', fontsize=16, color='#636e72'
        )
        ax.axis('off')
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight',
                    dpi=100, facecolor='white')
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8')

    # Generate word cloud
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color='white',
        colormap=colormap,
        max_words=200,
        max_font_size=100,
        random_state=42,
        collocations=False
    ).generate(text)

    # Plot
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')

    if title:
        ax.set_title(title, fontsize=16, color='#2d3436', pad=15)

    # Konversi ke base64
    buf = io.BytesIO()
    fig.savefig(
        buf, format='png', bbox_inches='tight',
        dpi=150, facecolor='white'
    )
    plt.close(fig)
    buf.seek(0)

    encoded = base64.b64encode(buf.read()).decode('utf-8')
    logger.info(f"Word cloud berhasil di-generate (size: {len(encoded)} chars)")

    return encoded


def generate_confusion_matrix_chart(
    cm_dict: Dict[str, Dict[str, int]],
    labels: Optional[List[str]] = None
) -> str:
    """
    Menghasilkan heatmap confusion matrix menggunakan Plotly.

    Args:
        cm_dict: Dictionary confusion matrix
                 {label_asli: {label_prediksi: count}}.
                 Contoh: {'positif': {'positif': 90, 'negatif': 5, 'netral': 5}}
        labels: List label untuk sumbu (default: ['positif', 'negatif', 'netral']).

    Returns:
        String HTML div berisi heatmap Plotly interaktif.
    """
    if labels is None:
        labels = ['positif', 'negatif', 'netral']

    if not cm_dict:
        logger.warning("Data confusion matrix kosong")
        return '<div>Tidak ada data untuk ditampilkan</div>'

    # Bangun matriks 2D dari dictionary
    z_values = []
    for actual_label in labels:
        row = []
        for predicted_label in labels:
            value = cm_dict.get(actual_label, {}).get(predicted_label, 0)
            row.append(value)
        z_values.append(row)

    # Buat anotasi teks
    annotations = []
    for i, row in enumerate(z_values):
        for j, val in enumerate(row):
            annotations.append(
                dict(
                    x=labels[j],
                    y=labels[i],
                    text=str(val),
                    font=dict(
                        size=16,
                        color='white' if val > max(
                            max(r) for r in z_values
                        ) / 2 else 'black'
                    ),
                    showarrow=False
                )
            )

    fig = go.Figure(data=go.Heatmap(
        z=z_values,
        x=labels,
        y=labels,
        colorscale='Blues',
        showscale=True,
        hovertemplate='Label Asli: %{y}<br>'
                      'Label Prediksi: %{x}<br>'
                      'Jumlah: %{z}<extra></extra>'
    ))

    fig.update_layout(
        title=dict(
            text='Confusion Matrix',
            font=dict(size=18, color='#2d3436'),
            x=0.5
        ),
        xaxis=dict(
            title='Label Prediksi',
            tickfont=dict(size=13)
        ),
        yaxis=dict(
            title='Label Asli',
            tickfont=dict(size=13),
            autorange='reversed'
        ),
        annotations=annotations,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=60, b=60, l=80, r=40),
        height=500
    )

    return fig.to_html(full_html=False, include_plotlyjs=False)


def generate_accuracy_chart(metrics_dict: Dict) -> str:
    """
    Menghasilkan bar chart metrik evaluasi model.

    Menampilkan Accuracy, Macro Precision, Macro Recall, dan Macro F1
    dalam satu bar chart untuk overview performa model.

    Args:
        metrics_dict: Dictionary metrik evaluasi dari evaluate_model(),
                      harus memiliki keys: accuracy, macro_precision,
                      macro_recall, macro_f1.

    Returns:
        String HTML div berisi bar chart Plotly interaktif.
    """
    if not metrics_dict:
        logger.warning("Data metrik kosong untuk accuracy chart")
        return '<div>Tidak ada data untuk ditampilkan</div>'

    categories = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
    values = [
        round(metrics_dict.get('accuracy', 0) * 100, 2),
        round(metrics_dict.get('macro_precision', 0) * 100, 2),
        round(metrics_dict.get('macro_recall', 0) * 100, 2),
        round(metrics_dict.get('macro_f1', 0) * 100, 2)
    ]

    colors = ['#0984e3', '#00b894', '#e17055', '#6c5ce7']

    fig = go.Figure(data=[go.Bar(
        x=categories,
        y=values,
        marker_color=colors,
        text=[f'{v:.2f}%' for v in values],
        textposition='auto',
        hovertemplate='<b>%{x}</b><br>'
                      'Nilai: %{y:.2f}%<extra></extra>'
    )])

    fig.update_layout(
        title=dict(
            text='Metrik Evaluasi Model',
            font=dict(size=18, color='#2d3436'),
            x=0.5
        ),
        xaxis=dict(
            title='Metrik',
            tickfont=dict(size=13)
        ),
        yaxis=dict(
            title='Nilai (%)',
            tickfont=dict(size=12),
            range=[0, 105]
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=60, b=60, l=60, r=40),
        height=450
    )

    return fig.to_html(full_html=False, include_plotlyjs=False)


def generate_comparison_chart(
    label_asli_counts: Dict[str, int],
    label_prediksi_counts: Dict[str, int]
) -> str:
    """
    Menghasilkan grouped bar chart perbandingan label asli vs prediksi.

    Args:
        label_asli_counts: Dictionary {label: jumlah} dari label asli.
        label_prediksi_counts: Dictionary {label: jumlah} dari label prediksi.

    Returns:
        String HTML div berisi grouped bar chart Plotly interaktif.
    """
    if not label_asli_counts and not label_prediksi_counts:
        logger.warning("Data kosong untuk comparison chart")
        return '<div>Tidak ada data untuk ditampilkan</div>'

    # Gabungkan semua label
    all_labels = sorted(set(
        list(label_asli_counts.keys()) +
        list(label_prediksi_counts.keys())
    ))

    asli_values = [label_asli_counts.get(label, 0) for label in all_labels]
    prediksi_values = [
        label_prediksi_counts.get(label, 0) for label in all_labels
    ]

    fig = go.Figure(data=[
        go.Bar(
            name='Label Asli',
            x=all_labels,
            y=asli_values,
            marker_color='#0984e3',
            text=[str(v) for v in asli_values],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>'
                          'Label Asli: %{y}<extra></extra>'
        ),
        go.Bar(
            name='Label Prediksi',
            x=all_labels,
            y=prediksi_values,
            marker_color='#e17055',
            text=[str(v) for v in prediksi_values],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>'
                          'Label Prediksi: %{y}<extra></extra>'
        )
    ])

    fig.update_layout(
        title=dict(
            text='Perbandingan Label Asli vs Prediksi',
            font=dict(size=18, color='#2d3436'),
            x=0.5
        ),
        xaxis=dict(
            title='Label Sentimen',
            tickfont=dict(size=13)
        ),
        yaxis=dict(
            title='Jumlah',
            tickfont=dict(size=12)
        ),
        barmode='group',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.2,
            xanchor='center',
            x=0.5
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=60, b=80, l=60, r=40),
        height=500
    )

    return fig.to_html(full_html=False, include_plotlyjs=False)
