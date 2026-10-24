from datetime import datetime
import json
import os
import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

DB_FILE = "game_of_house.db"

# --- TABELA DE NÍVEIS ---
NIVEIS = [
    (0, "🥚 Novato", 500),
    (500, "🥉 Aprendiz", 1000),
    (1000, "🥈 Aventureiro", 2000),
    (2000, "🥇 Campeão", 5000),
    (5000, "🏆 Mestre", 10000),
    (10000, "👑 Lenda", 999999)
]

# --- TABELA DE CONQUISTAS ---
CONQUISTAS_DISPONIVEIS = {
    "100_xp": {"nome": "🥉 Primeiros Passos", "desc": "Alcançou 100 XP Total"},
    "500_xp": {"nome": "🥈 Aventureiro Dedicado", "desc": "Alcançou 500 XP Total"},
    "1000_xp": {"nome": "🥇 Mestre das Tarefas", "desc": "Alcançou 1.000 XP Total"},
    "1_vitoria": {"nome": "🏆 Campeão Semanal", "desc": "Venceu 1 campeonato semanal"},
    "4_vitorias": {"nome": "👑 Rei da Casa", "desc": "Venceu 4 campeonatos semanais"}
}

def conectar_bd():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def inicializar_bd():
    """Cria o esquema do banco de dados e insere os dados padrão na primeira execução."""
    conn = conectar_bd()
    cursor = conn.cursor()

    # 1. Configurações gerais
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS config (
            chave TEXT PRIMARY KEY,
            valor TEXT NOT NULL
        )
    """)

    # 2. Tabela de Jogadores
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jogadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE NOT NULL,
            avatar TEXT DEFAULT '👤',
            pontos_semana INTEGER DEFAULT 0,
            saldo_recompensas INTEGER DEFAULT 0,
            xp_total INTEGER DEFAULT 0,
            titulos INTEGER DEFAULT 0,
            conquistas TEXT DEFAULT '[]'
        )
    """)

    # 3. Tabela de Tarefas e Ações
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tarefas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE NOT NULL,
            pontos INTEGER DEFAULT 0,
            xp INTEGER DEFAULT 0,
            tipo TEXT CHECK(tipo IN ('diaria', 'especial', 'boa_acao')) DEFAULT 'diaria'
        )
    """)

    # 4. Tabela de Consequências / Regras
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS consequencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE NOT NULL,
            nivel TEXT NOT NULL,
            pontos INTEGER DEFAULT 10
        )
    """)

    # 5. Tabela de Recompensas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recompensas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE NOT NULL,
            custo INTEGER DEFAULT 100
        )
    """)

    # 6. Tabela de Histórico
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            jogador_nome TEXT NOT NULL,
            tipo_acao TEXT NOT NULL,
            descricao TEXT NOT NULL,
            pontos INTEGER DEFAULT 0,
            xp INTEGER DEFAULT 0,
            data_hora TEXT DEFAULT (datetime('now', 'localtime'))
        )
    """)

    # INSERÇÃO DE DADOS PADRÃO (Se o banco estiver limpo)
    cursor.execute("SELECT COUNT(*) FROM config WHERE chave = 'pin_pais'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO config (chave, valor) VALUES ('pin_pais', '1234')")
        cursor.execute("INSERT INTO config (chave, valor) VALUES ('ultima_semana', '')")

        # Jogadores Padrão
        cursor.executemany("""
            INSERT OR IGNORE INTO jogadores (nome, avatar, pontos_semana, saldo_recompensas, xp_total, titulos)
            VALUES (?, ?, 0, 0, 0, 0)
        """, [("Maria Júlia", "👧"), ("Joaquim", "👦")])

        # Tarefas Diárias
        cursor.executemany("""
            INSERT OR IGNORE INTO tarefas (nome, pontos, xp, tipo)
            VALUES (?, ?, ?, 'diaria')
        """, [
            ("Arrumar a cama", 15, 20),
            ("Fazer o dever de casa", 20, 25),
            ("Ler 20 minutos", 15, 20),
            ("Guardar brinquedos", 10, 10),
            ("Guardar calçados", 10, 10),
            ("Ajudar com a mesa", 15, 15),
            ("Lavar a louça", 15, 25),
            ("Varrer a casa", 15, 20)
        ])

        # Missões Especiais
        cursor.executemany("""
            INSERT OR IGNORE INTO tarefas (nome, pontos, xp, tipo)
            VALUES (?, ?, ?, 'especial')
        """, [
            ("Completar 3 tarefas no dia", 30, 50),
            ("Completar todas as tarefas", 50, 100),
            ("Cumprir tarefas por 7 dias seguidos", 100, 200),
            ("Ajudar espontaneamente", 20, 30)
        ])

        # Boas Atitudes
        cursor.executemany("""
            INSERT OR IGNORE INTO tarefas (nome, pontos, xp, tipo)
            VALUES (?, ?, ?, 'boa_acao')
        """, [
            ("🌟 Ajudar espontaneamente", 20, 20),
            ("🤝 Compartilhar com irmão/irmã", 15, 15),
            ("💖 Ajudar os pais sem pedir", 20, 20),
            ("🕊️ Resolver conflito conversando", 25, 25)
        ])

        # Consequências
        cursor.executemany("""
            INSERT OR IGNORE INTO consequencias (nome, nivel, pontos)
            VALUES (?, ?, ?)
        """, [
            ("🧹 Deixar de realizar tarefa", "🟢 Leve", 10),
            ("🗣️ Responder aos pais", "🟡 Média", 20),
            ("😡 Brigar com irmão/irmã", "🔴 Grave", 30),
            ("🚫 Desobedecer regra combinada", "🟡 Média", 20),
            ("📱 Usar dispositivo sem autorização", "🔴 Grave", 30),
            ("❌ Recusar uma tarefa", "🟢 Leve", 15)
        ])

        # Recompensas
        cursor.executemany("""
            INSERT OR IGNORE INTO recompensas (nome, custo)
            VALUES (?, ?)
        """, [
            ("30 min extra de gameplay", 150),
            ("R$ 2,00 em dinheiro", 250),
            ("1h extra de gameplay", 400),
            ("R$ 5,00 em dinheiro", 500),
            ("Sorvete", 600)
        ])

    conn.commit()
    conn.close()

def obter_info_nivel(xp_total):
    for min_xp, nome_nivel, max_xp in reversed(NIVEIS):
        if xp_total >= min_xp:
            progresso = min(1.0, (xp_total - min_xp) / (max_xp - min_xp)) if max_xp > min_xp else 1.0
            return nome_nivel, min_xp, max_xp, progresso
    return NIVEIS[0][1], 0, 500, 0.0

class GameOfHouseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎮 Game of House - SQLite Edition")
        self.root.geometry("680x850")
        self.root.resizable(False, False)

        # Temas / Cores
        self.COR_FUNDO = "#1E1E2E"
        self.COR_CARD = "#2A2A3D"
        self.COR_TEXTO = "#CDD6F4"
        self.COR_VERDE = "#A6E3A1"
        self.COR_LARANJA = "#FAB387"
        self.COR_ROXO = "#CBA6F7"
        self.COR_AZUL = "#89B4FA"
        self.COR_AMARELO = "#F9E2AF"
        self.COR_VERMELHO = "#F38BA8"

        self.root.configure(bg=self.COR_FUNDO)

        inicializar_bd()
        self.criar_widgets()
        self.verificar_reset_semana()
        self.atualizar_interface()

    def obter_config(self, chave, padrao=""):
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("SELECT valor FROM config WHERE chave = ?", (chave,))
        row = cursor.fetchone()
        conn.close()
        return row['valor'] if row else padrao

    def salvar_config(self, chave, valor):
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO config (chave, valor) VALUES (?, ?)", (chave, valor))
        conn.commit()
        conn.close()

    def registrar_historico(self, jogador_nome, tipo_acao, descricao, pontos, xp=0):
        data_fmt = datetime.now().strftime("%d/%m %H:%M")
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO historico (jogador_nome, tipo_acao, descricao, pontos, xp, data_hora)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (jogador_nome, tipo_acao, descricao, pontos, xp, data_fmt))
        conn.commit()
        conn.close()

    def verificar_conquistas(self, jogador_nome):
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("SELECT xp_total, titulos, conquistas, avatar FROM jogadores WHERE nome = ?", (jogador_nome,))
        j = cursor.fetchone()

        if not j:
            conn.close()
            return

        xp = j['xp_total']
        titulos = j['titulos']
        conquistas = json.loads(j['conquistas'])
        novas = []

        if xp >= 100 and "100_xp" not in conquistas:
            conquistas.append("100_xp"); novas.append("100_xp")
        if xp >= 500 and "500_xp" not in conquistas:
            conquistas.append("500_xp"); novas.append("500_xp")
        if xp >= 1000 and "1000_xp" not in conquistas:
            conquistas.append("1000_xp"); novas.append("1000_xp")
        if titulos >= 1 and "1_vitoria" not in conquistas:
            conquistas.append("1_vitoria"); novas.append("1_vitoria")
        if titulos >= 4 and "4_vitorias" not in conquistas:
            conquistas.append("4_vitorias"); novas.append("4_vitorias")

        if novas:
            cursor.execute("UPDATE jogadores SET conquistas = ? WHERE nome = ?", (json.dumps(conquistas), jogador_nome))
            conn.commit()

        conn.close()

        for key in novas:
            c = CONQUISTAS_DISPONIVEIS[key]
            messagebox.showinfo("🎖️ CONQUISTA DESBLOQUEADA!", f"Parabéns {j['avatar']} {jogador_nome}!\n\nDesbloqueou: {c['nome']}\n({c['desc']})")

    def verificar_reset_semana(self):
        hoje = datetime.now().strftime("%Y-%U")
        ultima = self.obter_config("ultima_semana")

        if not ultima:
            self.salvar_config("ultima_semana", hoje)
            return

        if ultima != hoje:
            conn = conectar_bd()
            cursor = conn.cursor()
            cursor.execute("SELECT nome, avatar, pontos_semana FROM jogadores ORDER BY pontos_semana DESC")
            ranking = cursor.fetchall()

            campeao_nome = None
            top_pts = ranking[0]['pontos_semana'] if ranking else 0

            if top_pts > 0:
                lideres = [r['nome'] for r in ranking if r['pontos_semana'] == top_pts]
                if len(lideres) == 1:
                    campeao_nome = lideres[0]
                    cursor.execute("UPDATE jogadores SET titulos = titulos + 1 WHERE nome = ?", (campeao_nome,))
                    conn.commit()
                    self.verificar_conquistas(campeao_nome)

            self.exibir_tela_fim_semana(ranking, campeao_nome)

            # Reset semanal
            cursor.execute("UPDATE jogadores SET pontos_semana = 0")
            conn.commit()
            conn.close()

            self.salvar_config("ultima_semana", hoje)

    def exibir_tela_fim_semana(self, ranking, campeao):
        top = tk.Toplevel(self.root)
        top.title("🏆 RELATÓRIO DO CAMPEONATO SEMANAL")
        top.geometry("520x600")
        top.configure(bg=self.COR_FUNDO)
        top.grab_set()

        tk.Label(top, text="📊 RELATÓRIO DA SEMANA 🏆", font=("Impact", 20), bg=self.COR_FUNDO, fg=self.COR_AMARELO).pack(pady=15)

        f_placar = tk.Frame(top, bg=self.COR_CARD, padx=15, pady=15)
        f_placar.pack(fill="x", padx=20)

        for r in ranking:
            av = r['avatar']
            nome = r['nome']
            pts = r['pontos_semana']
            tk.Label(f_placar, text=f"{av} {nome}: {pts} pontos na semana", font=("Helvetica", 12, "bold"), bg=self.COR_CARD, fg=self.COR_TEXTO).pack(anchor="w", pady=4)

        if campeao:
            tk.Label(top, text=f"🥇 CAMPEÃO DA SEMANA: {campeao}!", font=("Impact", 18), bg=self.COR_FUNDO, fg=self.COR_VERDE).pack(pady=15)

        tk.Button(top, text="⚡ INICIAR NOVA SEMANA", font=("Helvetica", 11, "bold"), bg=self.COR_VERDE, fg="#11111B", relief="flat", command=top.destroy).pack(pady=10)

    def criar_widgets(self):
        lbl_titulo = tk.Label(self.root, text="🎮 GAME OF HOUSE ⚔️", font=("Impact", 22), bg=self.COR_FUNDO, fg=self.COR_ROXO)
        lbl_titulo.pack(pady=(12, 2))

        self.frame_jogadores = tk.Frame(self.root, bg=self.COR_FUNDO)
        self.frame_jogadores.pack(fill="x", padx=15, pady=2)

        # BARRA DE NAVEGAÇÃO
        f_nav = tk.Frame(self.root, bg=self.COR_FUNDO)
        f_nav.pack(fill="x", padx=15, pady=8)

        btn_aba1 = tk.Button(f_nav, text="⚡ Missões", font=("Helvetica", 9, "bold"), bg=self.COR_AZUL, fg="#11111B", relief="flat", command=lambda: self.mudar_aba(1))
        btn_aba1.pack(side="left", expand=True, fill="x", padx=2)

        btn_aba2 = tk.Button(f_nav, text="🎁 Loja", font=("Helvetica", 9, "bold"), bg=self.COR_LARANJA, fg="#11111B", relief="flat", command=lambda: self.mudar_aba(2))
        btn_aba2.pack(side="left", expand=True, fill="x", padx=2)

        btn_aba3 = tk.Button(f_nav, text="⚖️ Conduta", font=("Helvetica", 9, "bold"), bg=self.COR_ROXO, fg="#11111B", relief="flat", command=lambda: self.mudar_aba(3))
        btn_aba3.pack(side="left", expand=True, fill="x", padx=2)

        btn_aba4 = tk.Button(f_nav, text="📜 Diário", font=("Helvetica", 9, "bold"), bg=self.COR_AMARELO, fg="#11111B", relief="flat", command=lambda: self.mudar_aba(4))
        btn_aba4.pack(side="left", expand=True, fill="x", padx=2)

        btn_aba5 = tk.Button(f_nav, text="🔐 Pais", font=("Helvetica", 9, "bold"), bg=self.COR_VERMELHO, fg="#11111B", relief="flat", command=lambda: self.mudar_aba(5))
        btn_aba5.pack(side="left", expand=True, fill="x", padx=2)

        f_sel = tk.Frame(self.root, bg=self.COR_CARD, padx=10, pady=6)
        f_sel.pack(fill="x", padx=15, pady=2)

        tk.Label(f_sel, text="Player Ativo:", font=("Helvetica", 10, "bold"), bg=self.COR_CARD, fg=self.COR_TEXTO).pack(side="left", padx=5)
        self.combo_filhos = ttk.Combobox(f_sel, state="readonly", font=("Helvetica", 10))
        self.combo_filhos.pack(side="left", fill="x", expand=True, padx=5)

        self.f_conteudo = tk.Frame(self.root, bg=self.COR_FUNDO)
        self.f_conteudo.pack(fill="both", expand=True, padx=15, pady=5)

        self.mudar_aba(1)

    def desenhar_cards_jogadores(self):
        for w in self.frame_jogadores.winfo_children():
            w.destroy()

        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM jogadores ORDER BY pontos_semana DESC")
        jogadores = cursor.fetchall()
        conn.close()

        lider_nome = jogadores[0]['nome'] if jogadores and jogadores[0]['pontos_semana'] > 0 else None

        for j in jogadores:
            f_card = tk.Frame(self.frame_jogadores, bg=self.COR_CARD, padx=8, pady=6, bd=1, relief="ridge")
            f_card.pack(side="left", expand=True, fill="both", padx=3)

            av = j['avatar']
            nome = j['nome']
            nome_niv, _, _, prog = obter_info_nivel(j['xp_total'])
            tag_lider = " 🏆" if nome == lider_nome else ""

            tk.Label(f_card, text=f"{av} {nome}{tag_lider}", font=("Helvetica", 10, "bold"), bg=self.COR_CARD, fg=self.COR_TEXTO).pack()
            tk.Label(f_card, text=f"{nome_niv}", font=("Helvetica", 8, "bold"), bg=self.COR_CARD, fg=self.COR_AMARELO).pack()

            pbar = ttk.Progressbar(f_card, value=prog*100, maximum=100)
            pbar.pack(fill="x", pady=2)

            tk.Label(f_card, text=f"Semana: {j['pontos_semana']} pts", font=("Impact", 11), bg=self.COR_CARD, fg=self.COR_VERDE).pack()
            tk.Label(f_card, text=f"Saldo: {j['saldo_recompensas']} pts | XP: {j['xp_total']}", font=("Helvetica", 8), bg=self.COR_CARD, fg=self.COR_LARANJA).pack()

    def mudar_aba(self, numero):
        for w in self.f_conteudo.winfo_children():
            w.destroy()

        if numero == 1:
            self.desenhar_aba_missoes()
        elif numero == 2:
            self.desenhar_aba_loja()
        elif numero == 3:
            self.desenhar_aba_conduta()
        elif numero == 4:
            self.desenhar_aba_diario()
        elif numero == 5:
            self.autenticar_pais()

    def desenhar_aba_missoes(self):
        conn = conectar_bd()
        cursor = conn.cursor()

        # Missões Diárias
        f_t = tk.LabelFrame(self.f_conteudo, text="✅ Missões Diárias", bg=self.COR_CARD, fg=self.COR_VERDE, font=("Helvetica", 10, "bold"), padx=10, pady=8)
        f_t.pack(fill="x", pady=5)

        cursor.execute("SELECT nome, pontos, xp FROM tarefas WHERE tipo = 'diaria'")
        diarias = cursor.fetchall()
        opcoes_t = [f"{t['nome']} (+{t['pontos']} pts | +{t['xp']} XP)" for t in diarias]

        self.combo_tarefas = ttk.Combobox(f_t, values=opcoes_t, state="readonly", font=("Helvetica", 9))
        self.combo_tarefas.pack(fill="x", pady=5)
        if opcoes_t: self.combo_tarefas.current(0)

        tk.Button(f_t, text="⚡ CUMPRIR TAREFA", bg=self.COR_VERDE, fg="#11111B", font=("Helvetica", 9, "bold"), relief="flat", command=self.concluir_tarefa).pack(fill="x")

        # Missões Especiais
        f_e = tk.LabelFrame(self.f_conteudo, text="⚔️ Missões Especiais", bg=self.COR_CARD, fg=self.COR_ROXO, font=("Helvetica", 10, "bold"), padx=10, pady=8)
        f_e.pack(fill="x", pady=5)

        cursor.execute("SELECT nome, pontos, xp FROM tarefas WHERE tipo = 'especial'")
        especiais = cursor.fetchall()
        opcoes_e = [f"{m['nome']} (+{m['pontos']} pts | +{m['xp']} XP)" for m in especiais]

        self.combo_especiais = ttk.Combobox(f_e, values=opcoes_e, state="readonly", font=("Helvetica", 9))
        self.combo_especiais.pack(fill="x", pady=5)
        if opcoes_e: self.combo_especiais.current(0)

        tk.Button(f_e, text="🔥 CONCLUIR MISSÃO ESPECIAL", bg=self.COR_ROXO, fg="#11111B", font=("Helvetica", 9, "bold"), relief="flat", command=self.concluir_missao_especial).pack(fill="x")

        conn.close()

    def desenhar_aba_loja(self):
        f_r = tk.LabelFrame(self.f_conteudo, text="🎁 Loja de Recompensas", bg=self.COR_CARD, fg=self.COR_LARANJA, font=("Helvetica", 10, "bold"), padx=10, pady=10)
        f_r.pack(fill="x", pady=5)

        filho = self.combo_filhos.get()
        conn = conectar_bd()
        cursor = conn.cursor()

        cursor.execute("SELECT saldo_recompensas FROM jogadores WHERE nome = ?", (filho,))
        row = cursor.fetchone()
        saldo = row['saldo_recompensas'] if row else 0

        tk.Label(f_r, text=f"Saldo Disponível de {filho}: {saldo} pts", font=("Helvetica", 10, "bold"), bg=self.COR_CARD, fg=self.COR_AMARELO).pack(anchor="w", pady=(0, 5))

        cursor.execute("SELECT nome, custo FROM recompensas")
        recompensas = cursor.fetchall()
        opcoes_r = [f"{r['nome']} ({r['custo']} pts)" for r in recompensas]

        self.combo_recompensas = ttk.Combobox(f_r, values=opcoes_r, state="readonly", font=("Helvetica", 9))
        self.combo_recompensas.pack(fill="x", pady=5)
        if opcoes_r: self.combo_recompensas.current(0)

        tk.Button(f_r, text="🛒 RESGATAR RECOMPENSA", bg=self.COR_LARANJA, fg="#11111B", font=("Helvetica", 9, "bold"), relief="flat", command=self.resgatar_recompensa).pack(fill="x", pady=5)

        conn.close()

    def desenhar_aba_conduta(self):
        conn = conectar_bd()
        cursor = conn.cursor()

        # Boas Ações
        f_b = tk.LabelFrame(self.f_conteudo, text="🌟 Boas Atitudes & Bônus", bg=self.COR_CARD, fg=self.COR_AZUL, font=("Helvetica", 10, "bold"), padx=10, pady=8)
        f_b.pack(fill="x", pady=5)

        cursor.execute("SELECT nome, pontos FROM tarefas WHERE tipo = 'boa_acao'")
        boas = cursor.fetchall()
        opcoes_b = [f"{b['nome']} (+{b['pontos']} pts)" for b in boas]

        self.combo_boas = ttk.Combobox(f_b, values=opcoes_b, state="readonly", font=("Helvetica", 9))
        self.combo_boas.pack(fill="x", pady=5)
        if opcoes_b: self.combo_boas.current(0)

        tk.Button(f_b, text="🌟 REGISTRAR BOA ATITUDE", bg=self.COR_AZUL, fg="#11111B", font=("Helvetica", 9, "bold"), relief="flat", command=self.registrar_boa_atitude).pack(fill="x")

        # Regras e Consequências
        f_c = tk.LabelFrame(self.f_conteudo, text="⚖️ Regras & Consequências", bg=self.COR_CARD, fg=self.COR_VERMELHO, font=("Helvetica", 10, "bold"), padx=10, pady=8)
        f_c.pack(fill="x", pady=5)

        cursor.execute("SELECT nome, nivel, pontos FROM consequencias")
        consequencias = cursor.fetchall()
        opcoes_c = [f"{c['nome']} [{c['nivel']}] (-{c['pontos']} pts)" for c in consequencias]

        self.combo_conseq = ttk.Combobox(f_c, values=opcoes_c, state="readonly", font=("Helvetica", 9))
        self.combo_conseq.pack(fill="x", pady=5)
        if opcoes_c: self.combo_conseq.current(0)

        tk.Button(f_c, text="⚠️ APLICAR CONSEQUÊNCIA (PIN)", bg=self.COR_VERMELHO, fg="#FFFFFF", font=("Helvetica", 9, "bold"), relief="flat", command=self.aplicar_consequencia).pack(fill="x", pady=5)

        conn.close()

    def desenhar_aba_diario(self):
        tk.Label(self.f_conteudo, text="📜 Diário de Eventos do Campeonato", font=("Helvetica", 11, "bold"), bg=self.COR_FUNDO, fg=self.COR_AMARELO).pack(pady=2)

        f_hist = tk.Frame(self.f_conteudo, bg=self.COR_CARD, padx=5, pady=5)
        f_hist.pack(fill="both", expand=True, pady=3)

        listbox = tk.Listbox(f_hist, bg="#181825", fg=self.COR_TEXTO, font=("Courier", 9), selectbackground=self.COR_CARD)
        scrollbar = ttk.Scrollbar(f_hist, orient="vertical", command=listbox.yview)
        listbox.configure(yscrollcommand=scrollbar.set)

        listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM historico ORDER BY id DESC LIMIT 100")
        registros = cursor.fetchall()
        conn.close()

        for item in registros:
            sinal = "+" if item['pontos'] >= 0 else ""
            txt = f"[{item['data_hora']}] {item['jogador_nome']}: {sinal}{item['pontos']} pts ({item['descricao']})"
            listbox.insert("end", txt)

    def autenticar_pais(self):
        pin = simpledialog.askstring("🔐 Área dos Pais", "Digite o PIN de Administrador:", show="*")
        if pin == self.obter_config("pin_pais", "1234"):
            self.desenhar_aba_pais()
        else:
            messagebox.showerror("Acesso Negado", "PIN Incorreto!")
            self.mudar_aba(1)

    def desenhar_aba_pais(self):
        tk.Label(self.f_conteudo, text="⚙️ Gerenciador Completo (Banco de Dados SQL)", font=("Helvetica", 11, "bold"), bg=self.COR_FUNDO, fg=self.COR_VERMELHO).pack(pady=2)

        f_cont = tk.Frame(self.f_conteudo, bg=self.COR_CARD, padx=8, pady=8)
        f_cont.pack(fill="both", expand=True)

        tk.Button(f_cont, text="➕ Cadastrar Tarefa", bg=self.COR_AZUL, fg="#11111B", font=("Helvetica", 8, "bold"), command=self.admin_add_tarefa).pack(fill="x", pady=2)
        tk.Button(f_cont, text="⚖️ Cadastrar Regra de Consequência", bg=self.COR_VERMELHO, fg="#FFFFFF", font=("Helvetica", 8, "bold"), command=self.admin_add_consequencia).pack(fill="x", pady=2)
        tk.Button(f_cont, text="🌟 Cadastrar Boa Atitude (Bônus)", bg=self.COR_AZUL, fg="#11111B", font=("Helvetica", 8, "bold"), command=self.admin_add_boa_atitude).pack(fill="x", pady=2)
        tk.Button(f_cont, text="🎁 Cadastrar Recompensa", bg=self.COR_LARANJA, fg="#11111B", font=("Helvetica", 8, "bold"), command=self.admin_add_recompensa).pack(fill="x", pady=2)
        tk.Button(f_cont, text="👤 Cadastrar Novo Filho", bg=self.COR_VERDE, fg="#11111B", font=("Helvetica", 8, "bold"), command=self.admin_add_filho).pack(fill="x", pady=2)
        tk.Button(f_cont, text="🎯 Ajustar Pontos / Saldo / XP", bg=self.COR_AMARELO, fg="#11111B", font=("Helvetica", 8, "bold"), command=self.admin_ajustar_pontos).pack(fill="x", pady=2)
        tk.Button(f_cont, text="🔑 Alterar PIN dos Pais", bg=self.COR_ROXO, fg="#11111B", font=("Helvetica", 8, "bold"), command=self.admin_alterar_pin).pack(fill="x", pady=2)

    # --- AÇÕES DO JOGO COM TRANSAÇÕES SQL ---
    def concluir_tarefa(self):
        filho = self.combo_filhos.get()
        sel = self.combo_tarefas.get()
        if not sel or not filho: return

        t_nome = sel.split(" (+")[0]

        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("SELECT pontos, xp FROM tarefas WHERE nome = ?", (t_nome,))
        tarefa = cursor.fetchone()

        if tarefa:
            pts, xp = tarefa['pontos'], tarefa['xp']
            cursor.execute("""
                UPDATE jogadores
                SET pontos_semana = pontos_semana + ?,
                    saldo_recompensas = saldo_recompensas + ?,
                    xp_total = xp_total + ?
                WHERE nome = ?
            """, (pts, pts, xp, filho))
            conn.commit()

            self.registrar_historico(filho, "tarefa", t_nome, pts, xp)
            self.verificar_conquistas(filho)
            self.atualizar_interface()
            messagebox.showinfo("Missão Cumprida! ⚡", f"{filho} recebeu:\n+ {pts} Pts no Campeonato\n+ {pts} Saldo na Loja\n+ {xp} XP")

        conn.close()

    def concluir_missao_especial(self):
        filho = self.combo_filhos.get()
        sel = self.combo_especiais.get()
        if not sel or not filho: return

        m_nome = sel.split(" (+")[0]

        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("SELECT pontos, xp FROM tarefas WHERE nome = ?", (m_nome,))
        missao = cursor.fetchone()

        if missao:
            pts, xp = missao['pontos'], missao['xp']
            cursor.execute("""
                UPDATE jogadores
                SET pontos_semana = pontos_semana + ?,
                    saldo_recompensas = saldo_recompensas + ?,
                    xp_total = xp_total + ?
                WHERE nome = ?
            """, (pts, pts, xp, filho))
            conn.commit()

            self.registrar_historico(filho, "missao_especial", m_nome, pts, xp)
            self.verificar_conquistas(filho)
            self.atualizar_interface()
            messagebox.showinfo("BÔNUS ESPECIAL! ⚔️", f"{filho} recebeu:\n+ {pts} Pts\n+ {xp} XP")

        conn.close()

    def registrar_boa_atitude(self):
        filho = self.combo_filhos.get()
        sel = self.combo_boas.get()
        if not sel or not filho: return

        b_nome = sel.split(" (+")[0]

        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("SELECT pontos, xp FROM tarefas WHERE nome = ?", (b_nome,))
        boa = cursor.fetchone()

        if boa:
            pts, xp = boa['pontos'], boa['xp']
            cursor.execute("""
                UPDATE jogadores
                SET pontos_semana = pontos_semana + ?,
                    saldo_recompensas = saldo_recompensas + ?,
                    xp_total = xp_total + ?
                WHERE nome = ?
            """, (pts, pts, xp, filho))
            conn.commit()

            self.registrar_historico(filho, "bonus", f"Boa Atitude: {b_nome}", pts, xp)
            self.verificar_conquistas(filho)
            self.atualizar_interface()
            messagebox.showinfo("BOA ATITUDE! 🌟", f"{filho} ganhou bônus:\n+ {pts} Pts\n+ {xp} XP")

        conn.close()

    def aplicar_consequencia(self):
        pin = simpledialog.askstring("🔐 Confirmação dos Pais", "Digite o PIN para aplicar consequência:", show="*")
        if pin != self.obter_config("pin_pais", "1234"):
            messagebox.showerror("Negado", "PIN Incorreto!")
            return

        filho = self.combo_filhos.get()
        sel = self.combo_conseq.get()
        if not sel or not filho: return

        c_nome = sel.split(" [")[0]

        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("SELECT pontos FROM consequencias WHERE nome = ?", (c_nome,))
        conseq = cursor.fetchone()

        if conseq:
            pts = conseq['pontos']
            cursor.execute("""
                UPDATE jogadores
                SET pontos_semana = MAX(0, pontos_semana - ?),
                    saldo_recompensas = MAX(0, saldo_recompensas - ?)
                WHERE nome = ?
            """, (pts, pts, filho))
            conn.commit()

            self.registrar_historico(filho, "consequencia", f"Consequência: {c_nome}", -pts, 0)
            self.atualizar_interface()
            messagebox.showwarning("Consequência Aplicada ⚠️", f"Aplicado a {filho}:\n- {pts} Pts no Campeonato\n- {pts} Saldo na Loja")

        conn.close()

    def resgatar_recompensa(self):
        filho = self.combo_filhos.get()
        sel = self.combo_recompensas.get()
        if not sel or not filho: return

        r_nome = sel.split(" (")[0]

        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("SELECT custo FROM recompensas WHERE nome = ?", (r_nome,))
        rec = cursor.fetchone()

        cursor.execute("SELECT saldo_recompensas FROM jogadores WHERE nome = ?", (filho,))
        j = cursor.fetchone()

        if rec and j:
            custo = rec['custo']
            saldo = j['saldo_recompensas']

            if saldo >= custo:
                cursor.execute("UPDATE jogadores SET saldo_recompensas = saldo_recompensas - ? WHERE nome = ?", (custo, filho))
                conn.commit()

                self.registrar_historico(filho, "resgate", f"Resgatou: {r_nome}", -custo, 0)
                self.atualizar_interface()
                messagebox.showinfo("Recompensa! 🎁", f"{filho} resgatou: {r_nome}!")
            else:
                messagebox.showwarning("Saldo Insuficiente", f"{filho} tem {saldo} pts de saldo, mas precisa de {custo} pts.")

        conn.close()

    def atualizar_interface(self):
        self.desenhar_cards_jogadores()

        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("SELECT nome FROM jogadores")
        nomes = [row['nome'] for row in cursor.fetchall()]
        conn.close()

        if nomes:
            self.combo_filhos['values'] = nomes
            if not self.combo_filhos.get() or self.combo_filhos.get() not in nomes:
                self.combo_filhos.current(0)

    # --- ADMIN VIA SQL ---
    def admin_add_tarefa(self):
        nome = simpledialog.askstring("Nova Tarefa", "Nome da tarefa:")
        if nome:
            pts = simpledialog.askinteger("Pontos", "Pontos:", initialvalue=15)
            xp = simpledialog.askinteger("XP", "XP:", initialvalue=20)
            if pts and xp:
                conn = conectar_bd()
                cursor = conn.cursor()
                cursor.execute("INSERT OR REPLACE INTO tarefas (nome, pontos, xp, tipo) VALUES (?, ?, ?, 'diaria')", (nome, pts, xp))
                conn.commit()
                conn.close()
                messagebox.showinfo("Sucesso", "Tarefa gravada no Banco de Dados!")

    def admin_add_consequencia(self):
        nome = simpledialog.askstring("Nova Consequência", "Nome do comportamento negativo:")
        if nome:
            pts = simpledialog.askinteger("Pontos a remover", "Pontos a deduzir:", initialvalue=20)
            if pts:
                conn = conectar_bd()
                cursor = conn.cursor()
                cursor.execute("INSERT OR REPLACE INTO consequencias (nome, nivel, pontos) VALUES (?, '🟡 Média', ?)", (nome, pts))
                conn.commit()
                conn.close()
                messagebox.showinfo("Sucesso", "Consequência gravada no Banco de Dados!")

    def admin_add_boa_atitude(self):
        nome = simpledialog.askstring("Nova Boa Atitude", "Nome do comportamento positivo:")
        if nome:
            pts = simpledialog.askinteger("Pontos Bônus", "Pontos bônus:", initialvalue=20)
            if pts:
                conn = conectar_bd()
                cursor = conn.cursor()
                cursor.execute("INSERT OR REPLACE INTO tarefas (nome, pontos, xp, tipo) VALUES (?, ?, ?, 'boa_acao')", (nome, pts, pts))
                conn.commit()
                conn.close()
                messagebox.showinfo("Sucesso", "Boa atitude gravada no Banco de Dados!")

    def admin_add_recompensa(self):
        nome = simpledialog.askstring("Nova Recompensa", "Nome do prêmio:")
        if nome:
            custo = simpledialog.askinteger("Custo", "Custo em Saldo:", initialvalue=200)
            if custo:
                conn = conectar_bd()
                cursor = conn.cursor()
                cursor.execute("INSERT OR REPLACE INTO recompensas (nome, custo) VALUES (?, ?)", (nome, custo))
                conn.commit()
                conn.close()
                messagebox.showinfo("Sucesso", "Recompensa gravada no Banco de Dados!")

    def admin_add_filho(self):
        nome = simpledialog.askstring("Novo Filho", "Nome:")
        avatar = simpledialog.askstring("Avatar", "Emoji (ex: 👦, 👧):")
        if nome:
            conn = conectar_bd()
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO jogadores (nome, avatar) VALUES (?, ?)", (nome, avatar if avatar else '👤'))
            conn.commit()
            conn.close()
            self.atualizar_interface()

    def admin_ajustar_pontos(self):
        filho = self.combo_filhos.get()
        if not filho: return

        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("SELECT pontos_semana, saldo_recompensas, xp_total FROM jogadores WHERE nome = ?", (filho,))
        j = cursor.fetchone()

        if j:
            pts = simpledialog.askinteger("Ajuste", f"Pontos SEMANA de {filho}:", initialvalue=j['pontos_semana'])
            saldo = simpledialog.askinteger("Ajuste", f"Saldo LOJA de {filho}:", initialvalue=j['saldo_recompensas'])
            xp = simpledialog.askinteger("Ajuste", f"XP TOTAL de {filho}:", initialvalue=j['xp_total'])

            if pts is not None and saldo is not None and xp is not None:
                cursor.execute("UPDATE jogadores SET pontos_semana = ?, saldo_recompensas = ?, xp_total = ? WHERE nome = ?", (pts, saldo, xp, filho))
                conn.commit()
                self.atualizar_interface()

        conn.close()

    def admin_alterar_pin(self):
        novo = simpledialog.askstring("Novo PIN", "Digite o novo PIN:")
        if novo:
            self.salvar_config("pin_pais", novo)
            messagebox.showinfo("Sucesso", "PIN alterado com sucesso!")

if __name__ == "__main__":
    root = tk.Tk()
    app = GameOfHouseApp(root)
    root.mainloop()