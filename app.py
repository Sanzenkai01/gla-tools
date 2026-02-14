# pip install pyinstaller
# executar quando o app estiver completo

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw
import os
import sys
import math
import json

# Pequenas utilidades
def _clamp(v, lo=0, hi=255):
    return max(lo, min(hi, int(v)))

def adjust_color(hexcolor, factor=1.08):
    """Ajusta um hex color multiplicando RGB por factor (simples)."""
    try:
        h = hexcolor.lstrip('#')
        lv = len(h)
        if lv == 3:
            r, g, b = [int(h[i]*2, 16) for i in range(3)]
        else:
            r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        r = _clamp(r * factor)
        g = _clamp(g * factor)
        b = _clamp(b * factor)
        return f"#{r:02x}{g:02x}{b:02x}"
    except Exception:
        return hexcolor

# ================= CONFIG =================
LARGURA = 700
ALTURA = 800
if getattr(sys, "frozen", False):
    # Executável PyInstaller: recursos extraídos para _MEIPASS
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def resource_path(filename):
    """Retorna o caminho absoluto para um recurso, procurando também em 'assets/'."""
    # procura no BASE_DIR
    path = os.path.join(BASE_DIR, filename)
    if os.path.exists(path):
        return path
    # procura em assets/
    alt = os.path.join(BASE_DIR, 'assets', filename)
    if os.path.exists(alt):
        return alt
    # fallback: devolve o path padrão (pode não existir)
    return path

# ================= SETTINGS (persistência simples) =================
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")
DEFAULT_SETTINGS = {
    "geometry": f"{LARGURA}x{ALTURA}",
    "state": "normal",
    "last_screen": "menu",
    "tier": "Diamante",
    "receita": None,
    "receita_qtd": "100",
    "receita_valor": "3200",
    "cristal_equip": "Emblema",
    "cristal_level": "0",
    "cristal_values": {}
}
settings = DEFAULT_SETTINGS.copy()

def load_settings():
    global settings
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            s = json.load(f)
            settings.update(s)
    except Exception:
        # keep defaults
        pass

# save_settings será usada mais tarde (quando a janela existir) — definimos uma versão básica aqui
def save_settings():
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

# carrega settings imediatamente
load_settings()

# Cores modernas
COR_PRIMARIA = "#1e3a8a"      # Azul escuro
COR_SECUNDARIA = "#0f766e"    # Teal escuro
COR_ACENTO = "#f59e0b"        # Âmbar
COR_FUNDO = "#0f172a"         # Preto azulado
COR_TEXTO = "#f1f5f9"         # Branco gelado
COR_CARD = "#1e293b"          # Cinza escuro

# ================= DADOS =================
receitas = {
    "Paella de Camarão": {
        # formato: (quantia_por_RECEITA, valor_unitario)
        "Camarão Cru": (8, 300),
        "Folhas Verdes": (1, 15),
        "Tomates": (1, 10),
        "Água": (3, 5),
        "Trufa Branca": (3, 250),
        "Sal": (1, 10),
        "Pimenta": (1, 15),
        "Arroz": (2, 10),
        "Azeite": (1, 15)
    },
    "Frango Teriyaki": {
        # formato: (quantia_por_RECEITA, valor_unitario)
        "Galinha": (5, 300),
        "Pimenta": (1, 15),
        "Tomates": (3, 10),
        "Sal": (2, 10),
        "Azeite": (6, 15),
        "Folhas Verdes": (3, 15),
        "Alho": (3, 10),
        "Trufa Branca": (3, 250),
        "Creme de Leite": (3, 20)
    }
}

# ================= FUNÇÕES UTILITÁRIAS =================
def criar_botao_moderno(parent, texto, comando, cor_fundo=COR_PRIMARIA, cor_texto=COR_TEXTO, largura=30, altura_fonte=11):
    """Cria um botão moderno com efeito hover e feedback visual."""
    btn = tk.Button(
        parent,
        text=texto,
        command=comando,
        bg=cor_fundo,
        fg=cor_texto,
        font=("Segoe UI", altura_fonte, "bold"),
        bd=0,
        padx=20,
        pady=1,
        width=largura,
        activebackground=adjust_color(cor_fundo, 0.9),
        activeforeground=COR_TEXTO,
        relief=tk.FLAT,
        cursor="hand2"
    )
    hover_bg = adjust_color(cor_fundo, 1.08)

    def _on_enter(e):
        try:
            btn.config(bg=hover_bg)
        except Exception:
            pass
    def _on_leave(e):
        try:
            btn.config(bg=cor_fundo)
        except Exception:
            pass
    def _on_press(e):
        try:
            btn.config(relief=tk.SUNKEN)
        except Exception:
            pass
    def _on_release(e):
        try:
            btn.config(relief=tk.FLAT)
        except Exception:
            pass

    btn.bind("<Enter>", _on_enter)
    btn.bind("<Leave>", _on_leave)
    btn.bind("<ButtonPress-1>", _on_press)
    btn.bind("<ButtonRelease-1>", _on_release)

    return btn

# Logo loader (definido aqui para ficar disponível ao construir a UI do menu)
# cache de imagens do logo por tamanho
imagem_logo_cache = {}

def carregar_logo(tamanho=(120,40)):
    """Carrega o logo do app para exibí-lo no rodapé do menu (cache por tamanho)."""
    global imagem_logo_cache
    key = tamanho
    if key in imagem_logo_cache:
        return imagem_logo_cache[key]
    caminho = resource_path("logo.png")
    try:
        img = Image.open(caminho).resize(tamanho)
        imagem_logo_cache[key] = ImageTk.PhotoImage(img)
        return imagem_logo_cache[key]
    except Exception:
        return None

class ToolTip:
    """Simples tooltip usando uma Toplevel pequena."""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)
    def show(self, event=None):
        if self.tipwindow:
            return
        x = (event.x_root + 10) if event else (self.widget.winfo_rootx() + 10)
        y = (event.y_root + 10) if event else (self.widget.winfo_rooty() + 10)
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, bg=COR_PRIMARIA, fg=COR_TEXTO, bd=0, font=("Segoe UI", 8))
        label.pack(padx=6, pady=3)
    def hide(self, event=None):
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None

# ================= JANELA PRINCIPAL =================
janela = tk.Tk()
janela.title("GLA Tools")
# Aplica geometria salva, se houver
janela.geometry(settings.get('geometry', f"{LARGURA}x{ALTURA}"))
if settings.get('state') == 'zoomed':
    try:
        janela.state('zoomed')
    except Exception:
        pass
janela.resizable(True, True)
janela.minsize(600, 400)
janela.config(bg=COR_FUNDO)
# tenta aplicar ícone do app (icon.ico se existir, senão usa logo.png)
try:
    icon_path = resource_path("icon.ico")
    if os.path.exists(icon_path):
        janela.iconbitmap(icon_path)
    else:
        logo_icon_path = resource_path("logo.png")
        if os.path.exists(logo_icon_path):
            try:
                logo_icon_img = ImageTk.PhotoImage(Image.open(logo_icon_path))
                janela.iconphoto(False, logo_icon_img)
                # mantém referência para evitar coleta de lixo
                janela._logo_icon = logo_icon_img
            except Exception:
                pass
except Exception:
    pass

# ========= Persistência: debounce de salvamento e handlers =========
save_job = None

def schedule_save(delay=800):
    global save_job
    try:
        if save_job:
            janela.after_cancel(save_job)
    except Exception:
        pass
    save_job = janela.after(delay, save_settings)

# Atualiza settings com geometria/state (debounced)
def _on_window_config(event):
    try:
        st = janela.state()
        settings['state'] = st
        if st == 'normal':
            settings['geometry'] = janela.geometry()
        schedule_save()
    except Exception:
        pass

janela.bind('<Configure>', _on_window_config)

def on_close():
    try:
        save_settings()
    except Exception:
        pass
    janela.destroy()

janela.protocol("WM_DELETE_WINDOW", on_close)

# ================= CONTAINER =================
container = tk.Frame(janela, bg=COR_FUNDO)
container.pack(fill=tk.BOTH, expand=True)

frames = {}

def mostrar_tela(nome):
    """Mostra a tela escondendo as demais e exibindo apenas a solicitada."""
    # Esconde todas as telas
    for frame in frames.values():
        try:
            frame.pack_forget()
        except Exception:
            pass
    # Mostra somente a tela solicitada e faz com que ela ocupe todo o container
    frames[nome].pack(fill=tk.BOTH, expand=True)
    try:
        frames[nome].lift()
    except Exception:
        pass
    # salva a tela atual nas configurações (persistência)
    try:
        settings['last_screen'] = nome
        schedule_save()
    except Exception:
        pass

# ================= TELA MENU =================
menu = tk.Frame(container, bg=COR_FUNDO)
menu.pack(fill=tk.BOTH, expand=True)
frames["menu"] = menu

# Título estilizado
titulo_frame = tk.Frame(menu, bg=COR_FUNDO)
titulo_frame.pack(pady=40)

tk.Label(
    titulo_frame,
    text="⚙️ GLA",
    bg=COR_FUNDO,
    fg=COR_ACENTO,
    font=("Segoe UI", 24, "bold")
).pack()

tk.Label(
    titulo_frame,
    text="TOOLS",
    bg=COR_FUNDO,
    fg=COR_TEXTO,
    font=("Segoe UI", 18, "normal")
).pack()

tk.Label(
    titulo_frame,
    text="Desenvolvido por Liniker",
    bg=COR_FUNDO,
    fg=COR_TEXTO,
    font=("Segoe UI", 6, "normal")
).pack()

# Cards de opções (sem scrollbar)
cards_frame = tk.Frame(menu, bg=COR_FUNDO)
cards_frame.pack(pady=30, padx=20, fill=tk.BOTH, expand=True)

# Crie os cards e organize em duas colunas (grid)
cards = []

card1 = tk.Frame(cards_frame, bg=COR_CARD, relief=tk.FLAT, bd=1)
cards.append((card1, {
    'title': '📊 CALCULADORA DE EXPERIÊNCIA',
    'desc': 'Calcule quantas poções você precisa\npara subir de nível por tier',
    'btn_text': 'ABRIR CALCULADORA',
    'btn_cmd': lambda: mostrar_tela('exp'),
    'btn_bg': COR_ACENTO,
    'btn_fg': '#000'
}))

card2 = tk.Frame(cards_frame, bg=COR_CARD, relief=tk.FLAT, bd=1)
cards.append((card2, {
    'title': '🍲 CALCULADORA DE RECEITAS',
    'desc': 'Calcule custo, lucro e ingredientes\npara suas receitas gourmet',
    'btn_text': 'ABRIR CALCULADORA',
    'btn_cmd': lambda: mostrar_tela('receitas'),
    'btn_bg': COR_SECUNDARIA,
    'btn_fg': COR_TEXTO
}))

card3 = tk.Frame(cards_frame, bg=COR_CARD, relief=tk.FLAT, bd=1)
cards.append((card3, {
    'title': '💎 CALCULADORA DE CRISTAIS',
    'desc': 'Calcule cristais necessários por equipamento\ncom opção de valor em berry',
    'btn_text': 'ABRIR CALCULADORA',
    'btn_cmd': lambda: mostrar_tela('cristais'),
    'btn_bg': '#06b6d4',
    'btn_fg': '#000'
}))

# Configure grid
cards_frame.grid_columnconfigure(0, weight=1)
cards_frame.grid_columnconfigure(1, weight=1)

for idx, (card, data) in enumerate(cards):
    r = idx // 2
    c = idx % 2
    card.grid(row=r, column=c, sticky='nsew', padx=8, pady=8)
    tk.Label(
        card,
        text=data['title'],
        bg=COR_CARD,
        fg=COR_ACENTO,
        font=("Segoe UI", 11, "bold")
    ).pack(pady=8, padx=10)
    tk.Label(
        card,
        text=data['desc'],
        bg=COR_CARD,
        fg="#cbd5e1",
        font=("Segoe UI", 9, "normal"),
        justify=tk.CENTER
    ).pack(pady=4, padx=10)
    criar_botao_moderno(
        card,
        data['btn_text'],
        data['btn_cmd'],
        cor_fundo=data['btn_bg'],
        cor_texto=data['btn_fg']
    ).pack(pady=8)

    # efeito hover: clareia levemente o card inteiro, mas NÃO altera botões/entradas para evitar flicker
    def _on_card_enter(e, c=card):
        try:
            newbg = adjust_color(COR_CARD, 1.06)
            c.config(bg=newbg)
            for child in c.winfo_children():
                try:
                    # evita alterar widgets interativos que possuem seu próprio estilo
                    cls = child.winfo_class()
                    if cls in ("Button", "TButton", "Entry", "Text", "Canvas", "Scrollbar", "Listbox", "Combobox"):
                        continue
                    child.config(bg=newbg)
                except Exception:
                    pass
        except Exception:
            pass
    def _on_card_leave(e, c=card):
        try:
            c.config(bg=COR_CARD)
            for child in c.winfo_children():
                try:
                    cls = child.winfo_class()
                    if cls in ("Button", "TButton", "Entry", "Text", "Canvas", "Scrollbar", "Listbox", "Combobox"):
                        continue
                    child.config(bg=COR_CARD)
                except Exception:
                    pass
        except Exception:
            pass
    card.bind("<Enter>", _on_card_enter)
    card.bind("<Leave>", _on_card_leave)

# Footer do menu com logo centralizado
footer_menu = tk.Frame(menu, bg=COR_FUNDO)
footer_menu.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
# logo com altura levemente maior
logo_img = carregar_logo((160,80))
if logo_img:
    logo_lbl = tk.Label(footer_menu, image=logo_img, bg=COR_FUNDO, cursor="hand2")
    logo_lbl.image = logo_img
    logo_lbl.pack()
    ToolTip(logo_lbl, "Desenvolvido por Liniker")
    # hover: aumenta o logo levemente
    big_logo = carregar_logo((180,90))
    def _logo_enter(e):
        try:
            if big_logo:
                logo_lbl.config(image=big_logo)
                logo_lbl.image = big_logo
        except Exception:
            pass
    def _logo_leave(e):
        try:
            logo_lbl.config(image=logo_img)
            logo_lbl.image = logo_img
        except Exception:
            pass
    logo_lbl.bind("<Enter>", _logo_enter)
    logo_lbl.bind("<Leave>", _logo_leave)
else:
    lbl = tk.Label(footer_menu, text="GLA", bg=COR_FUNDO, fg=COR_TEXTO, font=("Segoe UI", 10, "bold"))
    lbl.pack()
    ToolTip(lbl, "Desenvolvido por Liniker")

# ================= TELA EXPERIÊNCIA =================
tela_exp = tk.Frame(container, bg=COR_FUNDO)
tela_exp.pack(fill=tk.BOTH, expand=True)
frames["exp"] = tela_exp

# Header
header_exp = tk.Frame(tela_exp, bg=COR_PRIMARIA, height=70)
header_exp.pack(fill=tk.X)

tk.Label(
    header_exp,
    text="📊 CALCULADORA DE EXPERIÊNCIA",
    bg=COR_PRIMARIA,
    fg=COR_TEXTO,
    font=("Segoe UI", 14, "bold")
).pack(pady=15)

# Conteúdo — scrollable (mantém botões fixos no rodapé em monitores pequenos)
content_exp_container = tk.Frame(tela_exp, bg=COR_FUNDO)
content_exp_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
content_exp_canvas = tk.Canvas(content_exp_container, bg=COR_FUNDO, highlightthickness=0)
content_exp_scroll = tk.Scrollbar(content_exp_container, orient=tk.VERTICAL, command=content_exp_canvas.yview)
content_exp_canvas.configure(yscrollcommand=content_exp_scroll.set)
content_exp_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=10)
content_exp_scroll.pack(side=tk.RIGHT, fill=tk.Y)
content_exp = tk.Frame(content_exp_canvas, bg=COR_FUNDO)
content_exp_window = content_exp_canvas.create_window((0,0), window=content_exp, anchor='nw')
# Ajusta região de rolagem quando o frame interno muda
def _on_config_exp(event):
    content_exp_canvas.configure(scrollregion=content_exp_canvas.bbox("all"))
content_exp.bind("<Configure>", _on_config_exp)
# Faz o frame interno preencher toda a largura do canvas (corrige desalinhamento)
def _on_canvas_config_exp(event):
    try:
        content_exp_canvas.itemconfig(content_exp_window, width=event.width)
    except Exception:
        pass
content_exp_canvas.bind("<Configure>", _on_canvas_config_exp)
# Suporte a roda do mouse quando o cursor estiver sobre o conteúdo
def _bind_mousewheel_exp(event):
    content_exp_canvas.bind_all("<MouseWheel>", lambda e: content_exp_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
def _unbind_mousewheel_exp(event):
    content_exp_canvas.unbind_all("<MouseWheel>")
content_exp.bind("<Enter>", _bind_mousewheel_exp)
content_exp.bind("<Leave>", _unbind_mousewheel_exp)

# Seleção de Tier
tier_label = tk.Label(
    content_exp,
    text="Selecione o Tier do Personagem",
    bg=COR_FUNDO,
    fg=COR_TEXTO,
    font=("Segoe UI", 10, "bold")
)
tier_label.pack(anchor=tk.W, pady=(0, 10))

tier_selecionado = tk.StringVar(value=settings.get('tier', "Diamante"))
# atualiza settings quando o tier muda
def _on_tier_change(*args):
    try:
        settings['tier'] = tier_selecionado.get()
        schedule_save()
    except Exception:
        pass

try:
    # use trace_add em vez de trace (compatível com Tcl 9+)
    tier_selecionado.trace_add("write", _on_tier_change)
except Exception:
    pass

tier_frame = tk.Frame(content_exp, bg=COR_FUNDO)
tier_frame.pack(fill=tk.X, pady=10)

cores_tier = {
    "Diamante": "#06b6d4",
    "Ouro": "#eab308",
    "Prata": "#a78bfa",
    "Bronze": "#f97316"
}

for tier in ["Diamante", "Ouro", "Prata", "Bronze"]:
    btn_tier = tk.Button(
        tier_frame,
        text=f"⭐ {tier}",
        command=lambda t=tier: tier_selecionado.set(t),
        bg=cores_tier[tier],
        fg="#000" if tier in ["Ouro", "Prata"] else "#fff",
        font=("Segoe UI", 9, "bold"),
        bd=0,
        padx=12,
        pady=8,
        relief=tk.FLAT,
        cursor="hand2",
        activebackground=cores_tier[tier]
    )
    btn_tier.pack(side=tk.LEFT, padx=5)

# Inputs
input_frame = tk.Frame(content_exp, bg=COR_FUNDO)
input_frame.pack(fill=tk.X, pady=15)

tk.Label(
    input_frame,
    text="Nível Inicial",
    bg=COR_FUNDO,
    fg=COR_TEXTO,
    font=("Segoe UI", 9, "bold")
).pack(anchor=tk.W)

entry_nivel_ini = tk.Entry(
    input_frame,
    bg=COR_CARD,
    fg=COR_TEXTO,
    font=("Segoe UI", 10),
    bd=0,
    relief=tk.FLAT,
    insertbackground=COR_ACENTO
)
entry_nivel_ini.insert(0, "1")
entry_nivel_ini.pack(fill=tk.X, pady=(5, 10), ipady=8)

tk.Label(
    input_frame,
    text="Nível Final",
    bg=COR_FUNDO,
    fg=COR_TEXTO,
    font=("Segoe UI", 9, "bold")
).pack(anchor=tk.W)

entry_nivel_fin = tk.Entry(
    input_frame,
    bg=COR_CARD,
    fg=COR_TEXTO,
    font=("Segoe UI", 10),
    bd=0,
    relief=tk.FLAT,
    insertbackground=COR_ACENTO
)
entry_nivel_fin.insert(0, "70")
entry_nivel_fin.pack(fill=tk.X, pady=(5, 10), ipady=8)

# Canvas de resultado com poções
resultado_frame = tk.Frame(content_exp, bg=COR_CARD, relief=tk.FLAT, height=140)
resultado_frame.pack(fill=tk.BOTH, pady=10)

pocoes_canvas = tk.Canvas(
    resultado_frame,
    bg=COR_CARD,
    highlightthickness=0,
    height=180
)
# Reposiciona dinamicamente quando o canvas muda de tamanho
pocoes_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Flag para saber se já desenhamos um resultado de XP (usada para redraw no resize)
exp_drawn = False

def on_pocoes_resize(event):
    # Redesenha o resultado de XP se já tivermos um cálculo anterior
    global exp_drawn
    if exp_drawn:
        calcular_experiencia()

pocoes_canvas.bind('<Configure>', on_pocoes_resize)

imagens_pocoes = {}

def carregar_imagem_pocao(tipo):
    """Carrega imagem da poção"""
    if tipo in imagens_pocoes:
        return imagens_pocoes[tipo]
    
    mapa_imagens = {
        "grande": "Bigexppot.png",
        "média": "Medexppot.png",
        "pequena": "Smallexppot.png"
    }
    
    caminho = resource_path(mapa_imagens[tipo])
    try:
        img = Image.open(caminho).resize((60, 60))
        photo = ImageTk.PhotoImage(img)
        imagens_pocoes[tipo] = photo
        return photo
    except Exception as e:
        return None


# Config XP
XP_NECESSARIO = {
    (1, 70): 5246500,
    (1, 140): 43813000,
    (70, 140): 38566500
}

XP_POCAO_POR_TIER = {
    "Diamante": {"grande": 50000, "média": 5000, "pequena": 500},
    "Ouro": {"grande": 100000, "média": 10000, "pequena": 1000},
    "Prata": {"grande": 200000, "média": 20000, "pequena": 2000},
    "Bronze": {"grande": 300000, "média": 30000, "pequena": 3000}
}

TIERS = {
    "Diamante": 0.5,
    "Ouro": 1.0,
    "Prata": 2.0,
    "Bronze": 3.0
}

# Valores precisos por nível fornecidos pelo usuário
xpPerLevel = [
    0,
    98, 101, 189, 402, 708, 1067, 1611, 2221, 2833, 3726,
    4640, 5487, 6747, 7965, 9029, 10674, 12196, 13459, 15507, 17333,
    18777, 21246, 23376, 24983, 27891, 30325, 32077, 35442, 38180, 40059,
    43899, 46941, 48929, 53626, 56608, 58687, 63531, 67181, 69333, 74706,
    78660, 80867, 86787, 91045, 93289, 99774, 104336, 106599, 113667, 118533,
    120797, 128466, 133636, 135883, 144171, 149645, 151857, 160782, 166560, 168719,
    178299, 184381, 186469, 196722, 203108, 205107, 216051, 222741, 224633, 236286,
    243280, 245047, 257427, 264725, 266349, 279474, 287076, 288539, 302427, 310333,
    311617, 326286, 334496, 335583, 351051, 359565, 360437, 376722, 385540, 386179,
    403299, 412421, 412809, 430782, 440208, 440327, 459171, 468901, 468733, 488466,
    498500, 498027, 518667, 529005, 528209, 549774, 560416, 559279, 581787, 592733,
    591237, 614706, 625956, 624083, 648531, 660085, 657817, 683262, 695120, 692439,
    718899, 731061, 727949, 755442, 767908, 764347, 792891, 805661, 801633, 831246,
    844320, 839807, 870507, 883885, 878869, 910674, 924356, 918819, 951747,
    0
]

xpTotalByLevel = [
    0,
    0, 98, 199, 388, 790, 1498, 2565, 4176, 6397, 9230,
    12956, 17596, 23083, 29830, 37795, 46824, 57498, 69694, 83153, 98660,
    115993, 134770, 156016, 179392, 204375, 232266, 262591, 294668, 330110, 368290,
    408349, 452248, 499189, 548118, 601744, 658352, 717039, 780570, 847751, 917084,
    991790, 1070450, 1151317, 1238104, 1329149, 1422438, 1522212, 1626548, 1733147, 1846814,
    1965347, 2086144, 2214610, 2348246, 2484129, 2628300, 2777945, 2929802, 3090584, 3257144,
    3425863, 3604162, 3788543, 3975012, 4171734, 4374842, 4579949, 4796000, 5018741, 5243374,
    5479660, 5722940, 5967987, 6225414, 6490139, 6756488, 7035962, 7323038, 7611577, 7914004,
    8224337, 8535954, 8862240, 9196736, 9532319, 9883370, 10242935, 10603372, 10980094, 11365634,
    11751813, 12155112, 12567533, 12980342, 13411124, 13851332, 14291659, 14750830, 15219731, 15688464,
    16176930, 16675430, 17173457, 17692124, 18221129, 18749338, 19299112, 19859528, 20418807, 21000594,
    21593327, 22184564, 22799270, 23425226, 24049309, 24697840, 25357925, 26015742, 26699004, 27394124,
    28086563, 28805462, 29536523, 30264472, 31019914, 31787822, 32552169, 33345060, 34150721, 34952354,
    35783600, 36627920, 37467727, 38338234, 39222119, 40100988, 41011662, 41936018, 42854837, 43806584
]


def calcular_xp_necessaria(nivel_inicial, nivel_final):
    """Calcula XP necessária entre dois níveis usando as tabelas precisas.

    Usa os arrays `xpTotalByLevel` para retornar a diferença de XP acumulada
    entre níveis inteiros (1..140). Retorna None para entradas inválidas.
    """
    if nivel_inicial < 1 or nivel_inicial >= nivel_final or nivel_final > 140:
        return None

    # Ambos níveis são inteiros e estão dentro da tabela — diferença direta
    return xpTotalByLevel[nivel_final] - xpTotalByLevel[nivel_inicial]

def pocoes_para_xp(xp_necessaria, tier):
    """Converte XP em poções"""
    xp_valores = XP_POCAO_POR_TIER[tier]
    xp_necessaria = int(xp_necessaria)
    
    grandes = xp_necessaria // xp_valores["grande"]
    resto = xp_necessaria % xp_valores["grande"]
    
    medias = resto // xp_valores["média"]
    resto = resto % xp_valores["média"]
    
    pequenas = resto // xp_valores["pequena"]
    
    return grandes, medias, pequenas

def calcular_experiencia():
    """Calcula e exibe resultado"""
    global exp_drawn
    try:
        nivel_ini = int(entry_nivel_ini.get())
        nivel_fin = int(entry_nivel_fin.get())
        tier = tier_selecionado.get()
        
        if nivel_ini < 1 or nivel_fin > 140 or nivel_ini >= nivel_fin:
            exp_drawn = False
            pocoes_canvas.delete("all")
            pocoes_canvas.create_text(
                pocoes_canvas.winfo_width()//2,
                pocoes_canvas.winfo_height()//2,
                text="❌ Nível inválido!\n1 ≤ Inicial < Final ≤ 140",
                fill=COR_ACENTO,
                font=("Segoe UI", 11, "bold")
            )
            return
        
        xp_necessaria = calcular_xp_necessaria(nivel_ini, nivel_fin)
        grandes, medias, pequenas = pocoes_para_xp(xp_necessaria, tier)
        
        pocoes_canvas.delete("all")
        
        # Info header
        texto_info = f"⭐ {tier} | Nível {nivel_ini}→{nivel_fin}"
        # Posiciona title dinamicamente (no topo)
        pocoes_canvas.create_text(
            pocoes_canvas.winfo_width()//2,
            18,
            text=texto_info,
            fill=COR_ACENTO,
            font=("Segoe UI", 10, "bold")
        )
        
        # Poções — posições baseadas na largura do canvas (mais centralizadas)
        img_grande = carregar_imagem_pocao("grande")
        img_media = carregar_imagem_pocao("média")
        img_pequena = carregar_imagem_pocao("pequena")
        
        w = max(200, pocoes_canvas.winfo_width())
        h = max(120, pocoes_canvas.winfo_height())
        x_positions = [w * 0.25, w * 0.5, w * 0.75]
        y_image = h * 0.45
        y_count = y_image + 45
        y_label = y_count + 14
        
        pocoes_info = [
            (img_grande, grandes, "Grande"),
            (img_media, medias, "Média"),
            (img_pequena, pequenas, "Pequena")
        ]
        
        for idx, (img, qtd, nome) in enumerate(pocoes_info):
            x = int(x_positions[idx])
            
            if img:
                pocoes_canvas.create_image(x, int(y_image), image=img)
            
            pocoes_canvas.create_text(
                x, int(y_count),
                text=f"×{qtd}",
                fill=COR_ACENTO,
                font=("Segoe UI", 12, "bold")
            )
            
            pocoes_canvas.create_text(
                x, int(y_label),
                text=nome,
                fill="#cbd5e1",
                font=("Segoe UI", 8)
            )
        
        # XP Info
        pocoes_canvas.create_text(
            pocoes_canvas.winfo_width()//2,
            160,
            text=f"XP Total: {int(xp_necessaria):,}",
            fill=COR_TEXTO,
            font=("Segoe UI", 9)
        )
        # marca que existe um desenho de XP válido para redimensionamento
        exp_drawn = True
    except ValueError:
        exp_drawn = False
        pocoes_canvas.delete("all")
        pocoes_canvas.create_text(
            pocoes_canvas.winfo_width()//2,
            pocoes_canvas.winfo_height()//2,
            text="❌ Digite números válidos!",
            fill=COR_ACENTO,
            font=("Segoe UI", 11, "bold")
        )

# Botões experiência (fixos no rodapé)
btn_frame_exp = tk.Frame(tela_exp, bg=COR_FUNDO)
btn_frame_exp.pack(side=tk.BOTTOM, fill=tk.X, padx=15, pady=12)

criar_botao_moderno(
    btn_frame_exp,
    "⚓ CALCULAR",
    calcular_experiencia,
    cor_fundo=COR_ACENTO,
    cor_texto="#000"
).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

criar_botao_moderno(
    btn_frame_exp,
    "⬅ VOLTAR",
    lambda: mostrar_tela("menu"),
    cor_fundo=COR_SECUNDARIA
).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

# ================= TELA RECEITAS =================
tela_receitas = tk.Frame(container, bg=COR_FUNDO)
tela_receitas.pack(fill=tk.BOTH, expand=True)
frames["receitas"] = tela_receitas

# Header
header_receitas = tk.Frame(tela_receitas, bg=COR_SECUNDARIA, height=70)
header_receitas.pack(fill=tk.X)

tk.Label(
    header_receitas,
    text="🍲 CALCULADORA DE RECEITAS",
    bg=COR_SECUNDARIA,
    fg=COR_TEXTO,
    font=("Segoe UI", 14, "bold")
).pack(pady=15)

# Conteúdo — scrollable (mantém botões fixos no rodapé em monitores pequenos)
content_receitas_container = tk.Frame(tela_receitas, bg=COR_FUNDO)
content_receitas_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
content_receitas_canvas = tk.Canvas(content_receitas_container, bg=COR_FUNDO, highlightthickness=0)
content_receitas_scroll = tk.Scrollbar(content_receitas_container, orient=tk.VERTICAL, command=content_receitas_canvas.yview)
content_receitas_canvas.configure(yscrollcommand=content_receitas_scroll.set)
content_receitas_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=10)
content_receitas_scroll.pack(side=tk.RIGHT, fill=tk.Y)
content_receitas = tk.Frame(content_receitas_canvas, bg=COR_FUNDO)
content_receitas_window = content_receitas_canvas.create_window((0,0), window=content_receitas, anchor='nw')
# Ajusta região de rolagem quando o frame interno muda
def _on_config_receitas(event):
    content_receitas_canvas.configure(scrollregion=content_receitas_canvas.bbox("all"))
content_receitas.bind("<Configure>", _on_config_receitas)
# Faz o frame interno preencher toda a largura do canvas (corrige desalinhamento)
def _on_canvas_config_receitas(event):
    try:
        content_receitas_canvas.itemconfig(content_receitas_window, width=event.width)
    except Exception:
        pass
content_receitas_canvas.bind("<Configure>", _on_canvas_config_receitas)
def _bind_mousewheel_receitas(event):
    content_receitas_canvas.bind_all("<MouseWheel>", lambda e: content_receitas_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
def _unbind_mousewheel_receitas(event):
    content_receitas_canvas.unbind_all("<MouseWheel>")
content_receitas.bind("<Enter>", _bind_mousewheel_receitas)
content_receitas.bind("<Leave>", _unbind_mousewheel_receitas)

# Recipe selection
tk.Label(
    content_receitas,
    text="Selecione a Receita",
    bg=COR_FUNDO,
    fg=COR_TEXTO,
    font=("Segoe UI", 10, "bold")
).pack(anchor=tk.W, pady=(0, 5))

combo = ttk.Combobox(
    content_receitas,
    values=list(receitas.keys()),
    state="readonly",
    font=("Segoe UI", 10)
)
# restaura valor salvo
saved_receita = settings.get('receita')
if saved_receita and saved_receita in receitas:
    try:
        combo.set(saved_receita)
    except Exception:
        combo.current(0)
else:
    combo.current(0)
combo.pack(fill=tk.X, pady=(0, 15))
# atualiza settings quando o usuário escolher outra receita
combo.bind("<<ComboboxSelected>>", lambda e: (settings.update({'receita': combo.get()}), schedule_save()))
# restauração de entradas e bindings será aplicada após criar os widgets `entry_qtd` e `entry_valor` para evitar NameError

# Inputs
tk.Label(
    content_receitas,
    text="Quantidade",
    bg=COR_FUNDO,
    fg=COR_TEXTO,
    font=("Segoe UI", 9, "bold")
).pack(anchor=tk.W)

entry_qtd = tk.Entry(
    content_receitas,
    bg=COR_CARD,
    fg=COR_TEXTO,
    font=("Segoe UI", 10),
    bd=0,
    relief=tk.FLAT,
    insertbackground=COR_ACENTO
)
entry_qtd.insert(0, "100")
entry_qtd.pack(fill=tk.X, pady=(5, 10), ipady=8)

tk.Label(
    content_receitas,
    text="Valor Unitário",
    bg=COR_FUNDO,
    fg=COR_TEXTO,
    font=("Segoe UI", 9, "bold")
).pack(anchor=tk.W)

entry_valor = tk.Entry(
    content_receitas,
    bg=COR_CARD,
    fg=COR_TEXTO,
    font=("Segoe UI", 10),
    bd=0,
    relief=tk.FLAT,
    insertbackground=COR_ACENTO
)
entry_valor.insert(0, "3200")
entry_valor.pack(fill=tk.X, pady=(5, 15), ipady=8)

# Restaura valores salvos para quantidade/valor e cria bindings para persistir alterações
try:
    entry_qtd.delete(0, tk.END); entry_qtd.insert(0, settings.get('receita_qtd', entry_qtd.get()))
    entry_valor.delete(0, tk.END); entry_valor.insert(0, settings.get('receita_valor', entry_valor.get()))
except Exception:
    pass
entry_qtd.bind("<FocusOut>", lambda e: (settings.update({'receita_qtd': entry_qtd.get()}), schedule_save()))
entry_valor.bind("<FocusOut>", lambda e: (settings.update({'receita_valor': entry_valor.get()}), schedule_save()))

# Resultado
tk.Label(
    content_receitas,
    text="Resultado",
    bg=COR_FUNDO,
    fg=COR_TEXTO,
    font=("Segoe UI", 10, "bold")
).pack(anchor=tk.W, pady=(0, 5))

# Container para texto de resultado com scrollbar vertical ✅
resultado_frame_text = tk.Frame(content_receitas, bg=COR_FUNDO)
resultado_frame_text.pack(fill=tk.BOTH, pady=(0, 10), expand=True)

resultado = tk.Text(
    resultado_frame_text,
    width=40,
    bg=COR_CARD,
    fg=COR_TEXTO,
    font=("Segoe UI", 9),
    bd=0,
    relief=tk.FLAT,
    state="disabled",
    wrap="word"
)
scroll_result = tk.Scrollbar(resultado_frame_text, orient=tk.VERTICAL, command=resultado.yview)
resultado['yscrollcommand'] = scroll_result.set
resultado.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scroll_result.pack(side=tk.RIGHT, fill=tk.Y)

def calcular_receita():
    """Calcula receita"""
    receita = combo.get()
    qtd = int(entry_qtd.get())
    valor = int(entry_valor.get())

    texto = f"📋 {receita}\n"
    texto += f"{'─' * 32}\n\n"
    custo = 0

    for item, val in receitas[receita].items():
        # Novo formato: val = (quantia_por_unidade, valor_unitario)
        if isinstance(val, (tuple, list)) and len(val) >= 2:
            quantia_por_unidade, valor_unitario = val
            total_quantia = quantia_por_unidade * qtd
            try:
                custo_item = int(total_quantia * float(valor_unitario))
            except Exception:
                custo_item = 0
            custo += custo_item
            texto += f"• {item}: {total_quantia} unidades — Custo: {custo_item:,} berry (preço unitário: {valor_unitario})\n"
        else:
            # Compatibilidade com formato antigo (valor por unidade/porção)
            try:
                total = int(val) * qtd
            except Exception:
                total = 0
            custo += total
            texto += f"• {item}: {total}\n"

    venda = qtd * valor
    taxa = venda * 0.03
    lucro = venda - custo - taxa

    texto += f"\n{'─' * 32}\n"
    texto += f"Custo: {custo:,}\n"
    texto += f"Venda: {venda:,}\n"
    texto += f"Taxa (3%): {int(taxa):,}\n"
    texto += f"💰 Lucro: {int(lucro):,}"

    resultado.config(state="normal")
    resultado.delete("1.0", tk.END)
    resultado.insert(tk.END, texto)
    resultado.config(state="disabled")

# Botões receitas
btn_frame_receitas = tk.Frame(tela_receitas, bg=COR_FUNDO)
# fixa os botões no rodapé mesmo quando a janela crescer
btn_frame_receitas.pack(side=tk.BOTTOM, fill=tk.X, padx=15, pady=12)

criar_botao_moderno(
    btn_frame_receitas,
    "⚓ CALCULAR",
    calcular_receita,
    cor_fundo=COR_ACENTO,
    cor_texto="#000"
).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

criar_botao_moderno(
    btn_frame_receitas,
    "⬅ VOLTAR",
    lambda: mostrar_tela("menu"),
    cor_fundo=COR_SECUNDARIA
).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

# ================= TELA CRISTAIS ================= ✅
tela_cristais = tk.Frame(container, bg=COR_FUNDO)
tela_cristais.pack(fill=tk.BOTH, expand=True)
frames["cristais"] = tela_cristais

# Header
header_cristais = tk.Frame(tela_cristais, bg="#0b74a6", height=70)
header_cristais.pack(fill=tk.X)

tk.Label(
    header_cristais,
    text="💎 CALCULADORA DE CRISTAIS",
    bg="#0b74a6",
    fg=COR_TEXTO,
    font=("Segoe UI", 14, "bold")
).pack(pady=15)

# Conteúdo — scrollable (mantém botões fixos no rodapé em monitores pequenos)
content_cristais_container = tk.Frame(tela_cristais, bg=COR_FUNDO)
content_cristais_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
content_cristais_canvas = tk.Canvas(content_cristais_container, bg=COR_FUNDO, highlightthickness=0)
content_cristais_scroll = tk.Scrollbar(content_cristais_container, orient=tk.VERTICAL, command=content_cristais_canvas.yview)
content_cristais_canvas.configure(yscrollcommand=content_cristais_scroll.set)
content_cristais_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=10)
content_cristais_scroll.pack(side=tk.RIGHT, fill=tk.Y)
content_cristais = tk.Frame(content_cristais_canvas, bg=COR_FUNDO)
content_cristais_window = content_cristais_canvas.create_window((0,0), window=content_cristais, anchor='nw')
# Ajusta região de rolagem quando o frame interno muda
def _on_config_cristais(event):
    content_cristais_canvas.configure(scrollregion=content_cristais_canvas.bbox("all"))
content_cristais.bind("<Configure>", _on_config_cristais)
# Faz o frame interno preencher toda a largura do canvas (corrige desalinhamento)
def _on_canvas_config_cristais(event):
    try:
        content_cristais_canvas.itemconfig(content_cristais_window, width=event.width)
    except Exception:
        pass
content_cristais_canvas.bind("<Configure>", _on_canvas_config_cristais)
# Suporte a roda do mouse quando o cursor estiver sobre o conteúdo
def _bind_mousewheel_cristais(event):
    content_cristais_canvas.bind_all("<MouseWheel>", lambda e: content_cristais_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
def _unbind_mousewheel_cristais(event):
    content_cristais_canvas.unbind_all("<MouseWheel>")
content_cristais.bind("<Enter>", _bind_mousewheel_cristais)
content_cristais.bind("<Leave>", _unbind_mousewheel_cristais)

# Dados e imagens
cristais_tipos = ["Cristais do Céu", "Cristais do Sábio", "Cristais Carmesim", "Cristais Radiante"]
mapa_imagens_cristais = {
    "Cristais do Céu": "cristal do ceu.png",
    "Cristais do Sábio": "cristal do sabio.png",
    "Cristais Carmesim": "cristal carmesim.png",
    "Cristais Radiante": "cristal radiante.png"
}

MAX_CRISTAIS = {
    "Cristais do Céu": {"Emblema":36, "Capacete":36, "Calça":36, "Peito":72, "Arma":72, "Colar":72, "Total":324},
    "Cristais do Sábio": {"Emblema":60, "Capacete":60, "Calça":60, "Peito":120, "Arma":120, "Colar":120, "Total":540},
    "Cristais Carmesim": {"Emblema":102, "Capacete":102, "Calça":102, "Peito":204, "Arma":204, "Colar":204, "Total":918},
    "Cristais Radiante": {"Emblema":196, "Capacete":196, "Calça":196, "Peito":392, "Arma":392, "Colar":392, "Total":1764}
}

# Top controls — escolha de equipamento e nível alvo
controls_frame = tk.Frame(content_cristais, bg=COR_FUNDO)
controls_frame.grid(row=0, column=0, sticky='ew')
content_cristais.grid_rowconfigure(1, weight=1)
content_cristais.grid_columnconfigure(0, weight=1)

slots = ["Emblema", "Capacete", "Calça", "Peito", "Arma", "Colar"]

# Equipamento (escolha única)
tk.Label(controls_frame, text="Equipamento", bg=COR_FUNDO, fg=COR_TEXTO, font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w")
combo_equip = ttk.Combobox(controls_frame, values=slots, state="readonly", font=("Segoe UI", 10))
# restaura valor salvo
if settings.get('cristal_equip') in slots:
    combo_equip.set(settings.get('cristal_equip'))
else:
    combo_equip.current(0)
combo_equip.grid(row=1, column=0, sticky="we", pady=(5,8))
combo_equip.bind("<<ComboboxSelected>>", lambda e: (settings.update({'cristal_equip': combo_equip.get()}), schedule_save()))

# Nível atual (0..16)
tk.Label(controls_frame, text="Nível atual", bg=COR_FUNDO, fg=COR_TEXTO, font=("Segoe UI", 9, "bold")).grid(row=0, column=1, sticky="w", padx=(15,0))
combo_level = ttk.Combobox(controls_frame, values=[str(i) for i in range(0,17)], state="readonly", font=("Segoe UI", 10))
# restaura valor salvo
if settings.get('cristal_level') and settings.get('cristal_level') in [str(i) for i in range(0,17)]:
    try:
        combo_level.set(settings.get('cristal_level'))
    except Exception:
        combo_level.current(0)
else:
    combo_level.current(0)
combo_level.grid(row=1, column=1, sticky="we", pady=(5,8), padx=(15,0))
combo_level.bind("<<ComboboxSelected>>", lambda e: (settings.update({'cristal_level': combo_level.get()}), schedule_save()))

# Valor por cristal por tipo (Céu, Sábio, Carmesim, Radiante)
tk.Label(controls_frame, text="Valor por Cristal (berry)", bg=COR_FUNDO, fg=COR_TEXTO, font=("Segoe UI", 9, "bold")).grid(row=0, column=2, sticky="w", padx=(15,0))
valor_frame = tk.Frame(controls_frame, bg=COR_FUNDO)
valor_frame.grid(row=1, column=2, sticky="we", pady=(5,8), padx=(15,0))

# labels e entries compactos
labels = ["Céu", "Sábio", "Carmesim", "Radiante"]
crystal_keys = ["Cristais do Céu", "Cristais do Sábio", "Cristais Carmesim", "Cristais Radiante"]
valor_entries = {}
for i, (lbl, key) in enumerate(zip(labels, crystal_keys)):
    tk.Label(valor_frame, text=lbl, bg=COR_FUNDO, fg=COR_TEXTO, font=("Segoe UI", 8)).grid(row=0, column=i, padx=4)
    e = tk.Entry(valor_frame, bg=COR_CARD, fg=COR_TEXTO, font=("Segoe UI", 9), bd=0, relief=tk.FLAT, width=8, justify='center')
    # restaura valor salvo para cada tipo de cristal
    saved_vals = settings.get('cristal_values', {})
    e.insert(0, str(saved_vals.get(key, "0")))
    e.grid(row=1, column=i, padx=4)
    valor_entries[key] = e
    # atualiza settings ao perder foco
    e.bind("<FocusOut>", lambda ev, k=key: (settings.setdefault('cristal_values', {}).__setitem__(k, valor_entries[k].get()), schedule_save()))

# Ajuste de colunas
controls_frame.grid_columnconfigure(0, weight=1)
controls_frame.grid_columnconfigure(1, weight=0)
controls_frame.grid_columnconfigure(2, weight=0)

# Resultado (com scrollbar)
resultado_cristais_frame = tk.Frame(content_cristais, bg=COR_FUNDO)
resultado_cristais_frame.grid(row=1, column=0, sticky='nsew', pady=(10,5))

resultado_cristais = tk.Text(resultado_cristais_frame, bg=COR_CARD, fg=COR_TEXTO, font=("Segoe UI", 10), bd=0, relief=tk.FLAT, state="disabled", wrap="word")
scroll_cristais = tk.Scrollbar(resultado_cristais_frame, orient=tk.VERTICAL, command=resultado_cristais.yview)
resultado_cristais['yscrollcommand'] = scroll_cristais.set
resultado_cristais.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scroll_cristais.pack(side=tk.RIGHT, fill=tk.Y)

# Botões na parte inferior (calcular/voltar) — fixados no rodapé da tela
footer_cristais = tk.Frame(tela_cristais, bg=COR_FUNDO)
footer_cristais.pack(side=tk.BOTTOM, fill=tk.X, padx=15, pady=12)

criar_botao_moderno(
    footer_cristais,
    "⚓ CALCULAR",
    lambda: calcular_cristais(),
    cor_fundo=COR_ACENTO,
    cor_texto="#000"
).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

criar_botao_moderno(
    footer_cristais,
    "⬅ VOLTAR",
    lambda: mostrar_tela("menu"),
    cor_fundo=COR_SECUNDARIA
).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

# Imagens cache
imagens_cristais = {}
imagens_equip = {}
imagem_gema = None

def carregar_gema(tamanho=(20,20)):
    global imagem_gema
    if imagem_gema:
        return imagem_gema
    caminho = resource_path("gema.png")
    try:
        img = Image.open(caminho).resize(tamanho)
        imagem_gema = ImageTk.PhotoImage(img)
        return imagem_gema
    except Exception:
        return None

def carregar_imagem_cristal(nome, tamanho=(36,36)):
    if nome in imagens_cristais:
        return imagens_cristais[nome]
    caminho = resource_path(mapa_imagens_cristais.get(nome, ""))
    try:
        img = Image.open(caminho).resize(tamanho)
        photo = ImageTk.PhotoImage(img)
        imagens_cristais[nome] = photo
        return photo
    except Exception:
        return None

def carregar_imagem_equip(nome, tamanho=(28,28)):
    if nome in imagens_equip:
        return imagens_equip[nome]
    # map to files (same names as found)
    arquivos = {"Emblema":"emblema.png","Capacete":"capacete.png","Calça":"calça.png","Peito":"peito.png","Arma":"arma.png","Colar":"colar.png"}
    caminho = resource_path(arquivos.get(nome, ""))
    try:
        img = Image.open(caminho).resize(tamanho)
        photo = ImageTk.PhotoImage(img)
        imagens_equip[nome] = photo
        return photo
    except Exception:
        return None

# Lógica de cálculo
crystals_per_up = {"Emblema":2, "Capacete":2, "Calça":2, "Peito":4, "Arma":4, "Colar":4}

# Tabela de chance e tentativa garantida (pity)
SUCCESS_TABLE = {
    1: (0.35, 3),
    2: (0.30, 4),
    3: (0.25, 5),
    4: (0.20, 6),
    5: (0.22, 5),
    6: (0.18, 6),
    7: (0.14, 8),
    8: (0.10, 11),
    9: (0.10, 11),
    10: (0.09, 12),
    11: (0.08, 13),
    12: (0.07, 15),
    13: (0.06, 17),
    14: (0.05, 21),
    15: (0.04, 26),
    16: (0.03, 34)
}

# Tabela de custo de transferência (gemas) por nível alvo (baseada na imagem)
# As chaves representam o nível teto da faixa (4, 8, 12, 16)
TRANSFER_COSTS = {
    4: {
        "Capacete": 1,
        "Peito": 2,
        "Calça": 1,
        "Emblema": 1,
        "Arma": 2,
        "Colar": 2
    },
    8: {
        "Capacete": 3,
        "Peito": 5,
        "Calça": 3,
        "Emblema": 3,
        "Arma": 5,
        "Colar": 5
    },
    12: {
        "Capacete": 6,
        "Peito": 10,
        "Calça": 6,
        "Emblema": 6,
        "Arma": 10,
        "Colar": 10
    },
    16: {
        "Capacete": 10,
        "Peito": 15,
        "Calça": 10,
        "Emblema": 10,
        "Arma": 15,
        "Colar": 15
    }
}

def get_transfer_cost(slot, level):
    """Retorna o custo em gemas para transferir boost do equipamento dado seu nível atual."""
    if level <= 0:
        return 0
    if level <= 4:
        key = 4
    elif level <= 8:
        key = 8
    elif level <= 12:
        key = 12
    else:
        key = 16
    return TRANSFER_COSTS.get(key, {}).get(slot, 0)

# Mapeamento de níveis por cristal
TIERS_LEVELS = {
    "Cristais do Céu": range(1, 5),
    "Cristais do Sábio": range(5, 9),
    "Cristais Carmesim": range(9, 13),
    "Cristais Radiante": range(13, 17)
}

def expected_attempts(p, guarantee):
    """Calcula o número esperado de tentativas até o sucesso com pity garantido na tentativa 'guarantee'."""
    q = 1 - p
    E = 0.0
    # tentativa 1..guarantee-1 com prob p a cada tentativa
    for k in range(1, guarantee):
        E += k * (q ** (k - 1)) * p
    # se falhar até guarantee-1, a guarantee faz com que a tentativa guarantee resulte em sucesso
    E += guarantee * (q ** (guarantee - 1))
    return E

def expected_crystals_for_level(slot, level):
    if level < 1:
        return 0
    if level > 16:
        # limite na tabela
        level = 16
    p, guarantee = SUCCESS_TABLE[level]
    atts = expected_attempts(p, guarantee)
    return atts * crystals_per_up[slot]




def get_crystal_type_for_level(lvl):
    if 1 <= lvl <= 4:
        return "Cristais do Céu"
    if 5 <= lvl <= 8:
        return "Cristais do Sábio"
    if 9 <= lvl <= 12:
        return "Cristais Carmesim"
    return "Cristais Radiante"


def calcular_cristais():
    # Leitura de valores
    try:
        current = int(combo_level.get())
    except Exception:
        current = 1
    current = max(1, min(current, 16))

    slot = combo_equip.get()
    if slot not in crystals_per_up:
        resultado_cristais.config(state="normal")
        resultado_cristais.delete("1.0", tk.END)
        resultado_cristais.insert(tk.END, "❌ Selecione um equipamento válido!")
        resultado_cristais.config(state="disabled")
        return

    resultado_cristais.config(state="normal")
    resultado_cristais.delete("1.0", tk.END)

    # Cabeçalho
    imge = carregar_imagem_equip(slot)
    if imge:
        resultado_cristais.image_create(tk.END, image=imge)
        resultado_cristais.insert(tk.END, " ")
    resultado_cristais.insert(tk.END, f"{slot} — Nível atual +{current}\n")

    # Custo de transferência (gema)
    custo_gemas = get_transfer_cost(slot, current)
    gem = carregar_gema((18,18))
    if gem:
        resultado_cristais.image_create(tk.END, image=gem)
        resultado_cristais.insert(tk.END, " ")
    resultado_cristais.insert(tk.END, f"Custo para transferir o boost: {custo_gemas} gemas\n\n")

    total_avg = 0.0
    total_max = 0
    total_cost_low = 0
    total_cost_high = 0

    # Para cada nível alvo acima do atual até 16
    for lvl in range(current + 1, 17):
        p, guarantee = SUCCESS_TABLE[lvl]
        avg = expected_crystals_for_level(slot, lvl)
        max_cr = crystals_per_up[slot] * guarantee

        # Formato X a Y — X: piso da média, Y: máximo garantido
        low = int(math.floor(avg))
        high = int(max_cr)

        crystal_type = get_crystal_type_for_level(lvl)
        # obtém valor específico para o tipo de cristal
        try:
            valor_level = int(valor_entries[crystal_type].get())
        except Exception:
            valor_level = 0

        cost_low = low * valor_level
        cost_high = high * valor_level

        resultado_cristais.insert(tk.END, f"Média para o nível +{lvl}: {low} a {high} cristais (cristal equivalente ao nível: {crystal_type}) → {cost_low:,} a {cost_high:,} berry\n")

        total_avg += avg
        total_max += max_cr
        total_cost_low += cost_low
        total_cost_high += cost_high

    resultado_cristais.insert(tk.END, "\n")
    resultado_cristais.insert(tk.END, f"Total (Média somada): {int(math.floor(total_avg)):,} a {int(total_max):,} cristais → {int(total_cost_low):,} a {int(total_cost_high):,} berry\n")
    resultado_cristais.insert(tk.END, "\nNota: médias calculadas usando chance por nível e pity garantido.\n")
    resultado_cristais.config(state="disabled")



# ================= INICIAL =================
# mostra a tela que estava aberta na última execução
mostrar_tela(settings.get('last_screen', "menu"))

janela.mainloop()
