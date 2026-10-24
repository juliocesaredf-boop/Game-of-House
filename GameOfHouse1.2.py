from datetime import datetime
import json
import os
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

ARQUIVO_DADOS = "pontos_filhos.json"

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

DADOS_PADRAO = {
    "ultima_semana": "",
    "pin_pais": "1234",
    "historico": [],
    "filhos": {
        "Maria Júlia": {
            "pontos_semana": 0,
            "saldo_recompensas": 0,
            "xp_total": 0,
            "titulos": 0,
            "avatar": "👧",
            "conquistas": [],
            "stats_semana": {"pts_tarefas": 0, "pts_bonus": 0, "pts_conseq": 0, "tarefas_qtd": 0, "bonus_qtd": 0, "conseq_qtd": 0}
        },
        "Joaquim": {
            "pontos_semana": 0,
            "saldo_recompensas": 0,
            "xp_total": 0,
            "titulos": 0,
            "avatar": "👦",
            "conquistas": [],
            "stats_semana": {"pts_tarefas": 0, "pts_bonus": 0, "pts_conseq": 0, "tarefas_qtd": 0, "bonus_qtd": 0, "conseq_qtd": 0}
        }
    },
    "tarefas": {
        "Arrumar a cama": {"pontos": 15, "xp": 20},
        "Fazer o dever de casa": {"pontos": 20, "xp": 25},
        "Ler 20 minutos": {"pontos": 15, "xp": 20},
        "Guardar brinquedos": {"pontos": 10, "xp": 10},
        "Guardar calçados": {"pontos": 10, "xp": 10},
        "Ajudar com a mesa": {"pontos": 15, "xp": 15},
        "Lavar a louça": {"pontos": 15, "xp": 25},
        "Varrer a casa": {"pontos": 15, "xp": 20},
    },
    "missoes_especiais": {
        "Completar 3 tarefas no dia": {"pontos": 30, "xp": 50},
        "Completar todas as tarefas": {"pontos": 50, "xp": 100},
        "Cumprir tarefas por 7 dias seguidos": {"pontos": 100, "xp": 200},
        "Ajudar espontaneamente": {"pontos": 20, "xp": 30}
    },
    "boas_acoes": {
        "🌟 Ajudar espontaneamente": {"pontos": 20, "xp": 20},
        "🤝 Compartilhar com irmão/irmã": {"pontos": 15, "xp": 15},
        "💖 Ajudar os pais sem pedir": {"pontos": 20, "xp": 20},
        "🕊️ Resolver conflito conversando": {"pontos": 25, "xp": 25}
    },
    "consequencias_regras": {
        "🧹 Deixar de realizar tarefa": {"nivel": "🟢 Leve", "pontos": 10},
        "🗣️ Responder aos pais": {"nivel": "🟡 Média", "pontos": 20},
        "😡 Brigar com irmão/irmã": {"nivel": "🔴 Grave", "pontos": 30},
        "🚫 Desobedecer regra combinada": {"nivel": "🟡 Média", "pontos": 20},
        "📱 Usar dispositivo sem autorização": {"nivel": "🔴 Grave", "pontos": 30},
        "❌ Recusar uma tarefa": {"nivel": "🟢 Leve", "pontos": 15}
    },
    "recompensas": {
        "30 min extra de gameplay": 150,
        "R$ 2,00 em dinheiro": 250,
        "1h extra de gameplay": 400,
        "R$ 5,00 em dinheiro": 500,
        "Sorvete": 600,
    }
}

def obter_info_nivel(xp_total):
    for min_xp, nome_nivel, max_xp in reversed(NIVEIS):
        if xp_total >= min_xp:
            progresso = min(1.0, (xp_total - min_xp) / (max_xp - min_xp)) if max_xp > min_xp else 1.0
            return nome_nivel, min_xp, max_xp, progresso
    return NIVEIS[0][1], 0, 500, 0.0

class GameOfHouseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎮 Game of House - Edição Avançada")
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

        self.dados = self.carregar_dados()
        self.criar_widgets()
        self.verificar_reset_semana()
        self.atualizar_interface()

    def carregar_dados(self):
        dados = json.loads(json.dumps(DADOS_PADRAO))
        if os.path.exists(ARQUIVO_DADOS):
            try:
                with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
                    dados_salvos = json.load(f)

                    if "filhos" in dados_salvos:
                        for nome, info_p in DADOS_PADRAO["filhos"].items():
                            if nome in dados_salvos["filhos"]:
                                f_old = dados_salvos["filhos"][nome]
                                pts_sem = f_old.get("pontos_semana", f_old.get("pontos", 0))
                                sal_rec = f_old.get("saldo_recompensas", pts_sem)
                                xp_tot = f_old.get("xp_total", pts_sem)
                                tit = f_old.get("titulos", 0)
                                av = f_old.get("avatar", info_p["avatar"])
                                conq = f_old.get("conquistas", [])
                                stats = f_old.get("stats_semana", {"pts_tarefas": 0, "pts_bonus": 0, "pts_conseq": 0, "tarefas_qtd": 0, "bonus_qtd": 0, "conseq_qtd": 0})
                                dados["filhos"][nome] = {
                                    "pontos_semana": pts_sem,
                                    "saldo_recompensas": sal_rec,
                                    "xp_total": xp_tot,
                                    "titulos": tit,
                                    "avatar": av,
                                    "conquistas": conq,
                                    "stats_semana": stats
                                }

                    for cat in ["tarefas", "missoes_especiais", "boas_acoes", "consequencias_regras", "recompensas"]:
                        if cat in dados_salvos:
                            dados[cat] = dados_salvos[cat]

                    for chave in ["ultima_semana", "pin_pais", "historico"]:
                        if chave in dados_salvos:
                            dados[chave] = dados_salvos[chave]
            except Exception as e:
                print(f"Erro ao carregar dados: {e}")
        return dados

    def salvar_dados(self):
        with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
            json.dump(self.dados, f, indent=4, ensure_ascii=False)

    def registrar_historico(self, filho, tipo, descricao, pontos, xp=0):
        data_hora = datetime.now().strftime("%d/%m %H:%M")
        registro = {
            "data": data_hora,
            "filho": filho,
            "tipo": tipo, # 'tarefa', 'bonus', 'consequencia', 'resgate'
            "descricao": descricao,
            "pontos": pontos,
            "xp": xp
        }
        self.dados["historico"].insert(0, registro) # Mais recentes primeiro
        if len(self.dados["historico"]) > 100: # Limite do histórico
            self.dados["historico"].pop()

    def verificar_conquistas(self, nome_filho):
        f = self.dados["filhos"][nome_filho]
        xp = f["xp_total"]
        titulos = f["titulos"]
        novas = []

        if xp >= 100 and "100_xp" not in f["conquistas"]:
            f["conquistas"].append("100_xp"); novas.append("100_xp")
        if xp >= 500 and "500_xp" not in f["conquistas"]:
            f["conquistas"].append("500_xp"); novas.append("500_xp")
        if xp >= 1000 and "1000_xp" not in f["conquistas"]:
            f["conquistas"].append("1000_xp"); novas.append("1000_xp")
        if titulos >= 1 and "1_vitoria" not in f["conquistas"]:
            f["conquistas"].append("1_vitoria"); novas.append("1_vitoria")
        if titulos >= 4 and "4_vitorias" not in f["conquistas"]:
            f["conquistas"].append("4_vitorias"); novas.append("4_vitorias")

        for key in novas:
            c = CONQUISTAS_DISPONIVEIS[key]
            messagebox.showinfo("🎖️ CONQUISTA DESBLOQUEADA!", f"Parabéns {f['avatar']} {nome_filho}!\n\nDesbloqueou: {c['nome']}\n({c['desc']})")

    def verificar_reset_semana(self):
        hoje = datetime.now().strftime("%Y-%U")
        if not self.dados.get("ultima_semana"):
            self.dados["ultima_semana"] = hoje
            self.salvar_dados()
            return

        if self.dados.get("ultima_semana") != hoje:
            ranking = sorted(self.dados["filhos"].items(), key=lambda x: x[1]["pontos_semana"], reverse=True)
            campeao_nome = None
            top_pts = ranking[0][1]["pontos_semana"] if ranking else 0

            if top_pts > 0:
                lideres = [n for n, info in ranking if info["pontos_semana"] == top_pts]
                if len(lideres) == 1:
                    campeao_nome = lideres[0]
                    self.dados["filhos"][campeao_nome]["titulos"] += 1
                    self.verificar_conquistas(campeao_nome)

            self.exibir_tela_fim_semana(ranking, campeao_nome)

            # Reset semanal
            for f in self.dados["filhos"]:
                self.dados["filhos"][f]["pontos_semana"] = 0
                self.dados["filhos"][f]["stats_semana"] = {"pts_tarefas": 0, "pts_bonus": 0, "pts_conseq": 0, "tarefas_qtd": 0, "bonus_qtd": 0, "conseq_qtd": 0}

            self.dados["ultima_semana"] = hoje
            self.salvar_dados()

    def exibir_tela_fim_semana(self, ranking, campeao):
        top = tk.Toplevel(self.root)
        top.title("🏆 RELATÓRIO DO CAMPEONATO SEMANAL")
        top.geometry("520x650")
        top.configure(bg=self.COR_FUNDO)
        top.grab_set()

        tk.Label(top, text="📊 RELATÓRIO DA SEMANA 🏆", font=("Impact", 20), bg=self.COR_FUNDO, fg=self.COR_AMARELO).pack(pady=15)

        canvas = tk.Canvas(top, bg=self.COR_FUNDO, highlightthickness=0)
        scrollbar = ttk.Scrollbar(top, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=self.COR_FUNDO)

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for nome, info in ranking:
            av = info.get("avatar", "👤")
            st = info.get("stats_semana", {"pts_tarefas": 0, "pts_bonus": 0, "pts_conseq": 0, "tarefas_qtd": 0, "bonus_qtd": 0, "conseq_qtd": 0})
            
            f_card = tk.LabelFrame(scroll_frame, text=f"{av} {nome}", font=("Helvetica", 12, "bold"), bg=self.COR_CARD, fg=self.COR_TEXTO, padx=12, pady=10)
            f_card.pack(fill="x", padx=20, pady=8)

            tk.Label(f_card, text=f"Tarefas ({st['tarefas_qtd']}): +{st['pts_tarefas']} pts", font=("Helvetica", 9), bg=self.COR_CARD, fg=self.COR_VERDE).pack(anchor="w")
            tk.Label(f_card, text=f"Bônus Atitudes ({st['bonus_qtd']}): +{st['pts_bonus']} pts", font=("Helvetica", 9), bg=self.COR_CARD, fg=self.COR_AZUL).pack(anchor="w")
            tk.Label(f_card, text=f"Consequências ({st['conseq_qtd']}): -{st['pts_conseq']} pts", font=("Helvetica", 9), bg=self.COR_CARD, fg=self.COR_VERMELHO).pack(anchor="w")
            
            tk.Frame(f_card, height=1, bg=self.COR_ROXO).pack(fill="x", pady=5)
            tk.Label(f_card, text=f"TOTAL SEMANAL: {info['pontos_semana']} pts", font=("Helvetica", 11, "bold"), bg=self.COR_CARD, fg=self.COR_AMARELO).pack(anchor="e")

        canvas.pack(side="left", fill="both", expand=True, padx=(10,0))
        scrollbar.pack(side="right", fill="y")

        if campeao:
            av_camp = self.dados["filhos"][campeao]["avatar"]
            tk.Label(top, text=f"🥇 CAMPEÃO DA SEMANA: {av_camp} {campeao}!", font=("Impact", 16), bg=self.COR_FUNDO, fg=self.COR_VERDE).pack(pady=10)

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
        self.combo_filhos = ttk.Combobox(f_sel, values=list(self.dados["filhos"].keys()), state="readonly", font=("Helvetica", 10))
        self.combo_filhos.pack(side="left", fill="x", expand=True, padx=5)
        self.combo_filhos.current(0)
        self.combo_filhos.bind("<<ComboboxSelected>>", lambda e: self.atualizar_interface())

        self.f_conteudo = tk.Frame(self.root, bg=self.COR_FUNDO)
        self.f_conteudo.pack(fill="both", expand=True, padx=15, pady=5)

        self.mudar_aba(1)

    def desenhar_cards_jogadores(self):
        for w in self.frame_jogadores.winfo_children():
            w.destroy()

        ranking = sorted(self.dados["filhos"].items(), key=lambda x: x[1]["pontos_semana"], reverse=True)
        lider_nome = ranking[0][0] if ranking and ranking[0][1]["pontos_semana"] > 0 else None

        for nome, info in self.dados["filhos"].items():
            f_card = tk.Frame(self.frame_jogadores, bg=self.COR_CARD, padx=8, pady=6, bd=1, relief="ridge")
            f_card.pack(side="left", expand=True, fill="both", padx=3)

            av = info.get("avatar", "👤")
            nome_niv, _, _, prog = obter_info_nivel(info["xp_total"])
            tag_lider = " 🏆" if nome == lider_nome else ""

            tk.Label(f_card, text=f"{av} {nome}{tag_lider}", font=("Helvetica", 10, "bold"), bg=self.COR_CARD, fg=self.COR_TEXTO).pack()
            tk.Label(f_card, text=f"{nome_niv}", font=("Helvetica", 8, "bold"), bg=self.COR_CARD, fg=self.COR_AMARELO).pack()

            pbar = ttk.Progressbar(f_card, value=prog*100, maximum=100)
            pbar.pack(fill="x", pady=2)

            tk.Label(f_card, text=f"Semana: {info['pontos_semana']} pts", font=("Impact", 11), bg=self.COR_CARD, fg=self.COR_VERDE).pack()
            tk.Label(f_card, text=f"Saldo: {info.get('saldo_recompensas', 0)} pts | XP: {info['xp_total']}", font=("Helvetica", 8), bg=self.COR_CARD, fg=self.COR_LARANJA).pack()

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
        f_t = tk.LabelFrame(self.f_conteudo, text="✅ Missões Diárias", bg=self.COR_CARD, fg=self.COR_VERDE, font=("Helvetica", 10, "bold"), padx=10, pady=8)
        f_t.pack(fill="x", pady=5)

        opcoes_t = [f"{t} (+{v['pontos']} pts | +{v['xp']} XP)" for t, v in self.dados["tarefas"].items()]
        self.combo_tarefas = ttk.Combobox(f_t, values=opcoes_t, state="readonly", font=("Helvetica", 9))
        self.combo_tarefas.pack(fill="x", pady=5)
        if opcoes_t: self.combo_tarefas.current(0)

        tk.Button(f_t, text="⚡ CUMPRIR TAREFA", bg=self.COR_VERDE, fg="#11111B", font=("Helvetica", 9, "bold"), relief="flat", command=self.concluir_tarefa).pack(fill="x")

        f_e = tk.LabelFrame(self.f_conteudo, text="⚔️ Missões Especiais", bg=self.COR_CARD, fg=self.COR_ROXO, font=("Helvetica", 10, "bold"), padx=10, pady=8)
        f_e.pack(fill="x", pady=5)

        opcoes_e = [f"{m} (+{v['pontos']} pts | +{v['xp']} XP)" for m, v in self.dados["missoes_especiais"].items()]
        self.combo_especiais = ttk.Combobox(f_e, values=opcoes_e, state="readonly", font=("Helvetica", 9))
        self.combo_especiais.pack(fill="x", pady=5)
        if opcoes_e: self.combo_especiais.current(0)

        tk.Button(f_e, text="🔥 CONCLUIR MISSÃO ESPECIAL", bg=self.COR_ROXO, fg="#11111B", font=("Helvetica", 9, "bold"), relief="flat", command=self.concluir_missao_especial).pack(fill="x")

    def desenhar_aba_loja(self):
        f_r = tk.LabelFrame(self.f_conteudo, text="🎁 Loja de Recompensas", bg=self.COR_CARD, fg=self.COR_LARANJA, font=("Helvetica", 10, "bold"), padx=10, pady=10)
        f_r.pack(fill="x", pady=5)

        filho = self.combo_filhos.get()
        saldo = self.dados["filhos"][filho].get("saldo_recompensas", 0)

        tk.Label(f_r, text=f"Saldo Disponível de {filho}: {saldo} pts", font=("Helvetica", 10, "bold"), bg=self.COR_CARD, fg=self.COR_AMARELO).pack(anchor="w", pady=(0, 5))

        opcoes_r = [f"{r} ({pts} pts)" for r, pts in self.dados["recompensas"].items()]
        self.combo_recompensas = ttk.Combobox(f_r, values=opcoes_r, state="readonly", font=("Helvetica", 9))
        self.combo_recompensas.pack(fill="x", pady=5)
        if opcoes_r: self.combo_recompensas.current(0)

        tk.Button(f_r, text="🛒 RESGATAR RECOMPENSA", bg=self.COR_LARANJA, fg="#11111B", font=("Helvetica", 9, "bold"), relief="flat", command=self.resgatar_recompensa).pack(fill="x", pady=5)

    def desenhar_aba_conduta(self):
        # Boas Ações
        f_b = tk.LabelFrame(self.f_conteudo, text="🌟 Boas Atitudes & Bônus", bg=self.COR_CARD, fg=self.COR_AZUL, font=("Helvetica", 10, "bold"), padx=10, pady=8)
        f_b.pack(fill="x", pady=5)

        opcoes_b = [f"{b} (+{v['pontos']} pts)" for b, v in self.dados["boas_acoes"].items()]
        self.combo_boas = ttk.Combobox(f_b, values=opcoes_b, state="readonly", font=("Helvetica", 9))
        self.combo_boas.pack(fill="x", pady=5)
        if opcoes_b: self.combo_boas.current(0)

        tk.Button(f_b, text="🌟 REGISTRAR BOA ATITUDE", bg=self.COR_AZUL, fg="#11111B", font=("Helvetica", 9, "bold"), relief="flat", command=self.registrar_boa_atitude).pack(fill="x")

        # Regras e Consequências
        f_c = tk.LabelFrame(self.f_conteudo, text="⚖️ Regras & Consequências", bg=self.COR_CARD, fg=self.COR_VERMELHO, font=("Helvetica", 10, "bold"), padx=10, pady=8)
        f_c.pack(fill="x", pady=5)

        tk.Label(f_c, text="Selecione a conduta para aplicar a consequência combinada:", font=("Helvetica", 8), bg=self.COR_CARD, fg=self.COR_TEXTO).pack(anchor="w")

        opcoes_c = [f"{c} [{v['nivel']}] (-{v['pontos']} pts)" for c, v in self.dados["consequencias_regras"].items()]
        self.combo_conseq = ttk.Combobox(f_c, values=opcoes_c, state="readonly", font=("Helvetica", 9))
        self.combo_conseq.pack(fill="x", pady=5)
        if opcoes_c: self.combo_conseq.current(0)

        tk.Button(f_c, text="⚠️ APLICAR CONSEQUÊNCIA (PIN)", bg=self.COR_VERMELHO, fg="#FFFFFF", font=("Helvetica", 9, "bold"), relief="flat", command=self.aplicar_consequencia).pack(fill="x", pady=5)

    def desenhar_aba_diario(self):
        tk.Label(self.f_conteudo, text="📜 Diário de Eventos do Campeonato", font=("Helvetica", 11, "bold"), bg=self.COR_FUNDO, fg=self.COR_AMARELO).pack(pady=2)

        f_hist = tk.Frame(self.f_conteudo, bg=self.COR_CARD, padx=5, pady=5)
        f_hist.pack(fill="both", expand=True, pady=3)

        listbox = tk.Listbox(f_hist, bg="#181825", fg=self.COR_TEXTO, font=("Courier", 9), selectbackground=self.COR_CARD)
        scrollbar = ttk.Scrollbar(f_hist, orient="vertical", command=listbox.yview)
        listbox.configure(yscrollcommand=scrollbar.set)

        listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for item in self.dados["historico"]:
            sinal = "+" if item["pontos"] >= 0 else ""
            txt = f"[{item['data']}] {item['filho']}: {sinal}{item['pontos']} pts ({item['descricao']})"
            listbox.insert("end", txt)

        tk.Button(self.f_conteudo, text="📊 Ver Relatório Semanal Detalhado", bg=self.COR_AZUL, fg="#11111B", font=("Helvetica", 9, "bold"), relief="flat", command=lambda: self.exibir_tela_fim_semana(sorted(self.dados["filhos"].items(), key=lambda x: x[1]["pontos_semana"], reverse=True), None)).pack(fill="x", pady=3)

    def autenticar_pais(self):
        pin = simpledialog.askstring("🔐 Área dos Pais", "Digite o PIN de Administrador:", show="*")
        if pin == self.dados.get("pin_pais", "1234"):
            self.desenhar_aba_pais()
        else:
            messagebox.showerror("Acesso Negado", "PIN Incorreto!")
            self.mudar_aba(1)

    def desenhar_aba_pais(self):
        tk.Label(self.f_conteudo, text="⚙️ Gerenciador Completo do Sistema", font=("Helvetica", 11, "bold"), bg=self.COR_FUNDO, fg=self.COR_VERMELHO).pack(pady=2)

        f_cont = tk.Frame(self.f_conteudo, bg=self.COR_CARD, padx=8, pady=8)
        f_cont.pack(fill="both", expand=True)

        tk.Button(f_cont, text="➕ Cadastrar Tarefa", bg=self.COR_AZUL, fg="#11111B", font=("Helvetica", 8, "bold"), command=self.admin_add_tarefa).pack(fill="x", pady=2)
        tk.Button(f_cont, text="⚖️ Cadastrar Regra de Consequência", bg=self.COR_VERMELHO, fg="#FFFFFF", font=("Helvetica", 8, "bold"), command=self.admin_add_consequencia).pack(fill="x", pady=2)
        tk.Button(f_cont, text="🌟 Cadastrar Boa Atitude (Bônus)", bg=self.COR_AZUL, fg="#11111B", font=("Helvetica", 8, "bold"), command=self.admin_add_boa_atitude).pack(fill="x", pady=2)
        tk.Button(f_cont, text="🎁 Cadastrar Recompensa", bg=self.COR_LARANJA, fg="#11111B", font=("Helvetica", 8, "bold"), command=self.admin_add_recompensa).pack(fill="x", pady=2)
        tk.Button(f_cont, text="👤 Cadastrar Novo Filho", bg=self.COR_VERDE, fg="#11111B", font=("Helvetica", 8, "bold"), command=self.admin_add_filho).pack(fill="x", pady=2)
        tk.Button(f_cont, text="🎯 Ajustar Pontos / Saldo / XP", bg=self.COR_AMARELO, fg="#11111B", font=("Helvetica", 8, "bold"), command=self.admin_ajustar_pontos).pack(fill="x", pady=2)
        tk.Button(f_cont, text="🔑 Alterar PIN dos Pais", bg=self.COR_ROXO, fg="#11111B", font=("Helvetica", 8, "bold"), command=self.admin_alterar_pin).pack(fill="x", pady=2)

    # --- AÇÕES DO JOGO ---
    def concluir_tarefa(self):
        filho = self.combo_filhos.get()
        sel = self.combo_tarefas.get()
        if not sel: return

        t_nome = sel.split(" (+")[0]
        info_t = self.dados["tarefas"].get(t_nome, {"pontos": 0, "xp": 0})
        pts = info_t.get("pontos", 0)
        xp = info_t.get("xp", 0)

        f = self.dados["filhos"][filho]
        f["pontos_semana"] += pts
        f["saldo_recompensas"] += pts
        f["xp_total"] += xp
        f["stats_semana"]["pts_tarefas"] += pts
        f["stats_semana"]["tarefas_qtd"] += 1

        self.registrar_historico(filho, "tarefa", t_nome, pts, xp)
        self.verificar_conquistas(filho)
        self.salvar_dados()
        self.atualizar_interface()
        messagebox.showinfo("Missão Cumprida! ⚡", f"{filho} recebeu:\n+ {pts} Pts no Campeonato\n+ {pts} Saldo na Loja\n+ {xp} XP")

    def concluir_missao_especial(self):
        filho = self.combo_filhos.get()
        sel = self.combo_especiais.get()
        if not sel: return

        m_nome = sel.split(" (+")[0]
        info_m = self.dados["missoes_especiais"].get(m_nome, {"pontos": 0, "xp": 0})
        pts = info_m.get("pontos", 0)
        xp = info_m.get("xp", 0)

        f = self.dados["filhos"][filho]
        f["pontos_semana"] += pts
        f["saldo_recompensas"] += pts
        f["xp_total"] += xp
        f["stats_semana"]["pts_tarefas"] += pts

        self.registrar_historico(filho, "missao_especial", m_nome, pts, xp)
        self.verificar_conquistas(filho)
        self.salvar_dados()
        self.atualizar_interface()
        messagebox.showinfo("BÔNUS ESPECIAL! ⚔️", f"{filho} recebeu:\n+ {pts} Pts\n+ {xp} XP")

    def registrar_boa_atitude(self):
        filho = self.combo_filhos.get()
        sel = self.combo_boas.get()
        if not sel: return

        b_nome = sel.split(" (+")[0]
        info_b = self.dados["boas_acoes"].get(b_nome, {"pontos": 0, "xp": 0})
        pts = info_b.get("pontos", 0)
        xp = info_b.get("xp", 0)

        f = self.dados["filhos"][filho]
        f["pontos_semana"] += pts
        f["saldo_recompensas"] += pts
        f["xp_total"] += xp
        f["stats_semana"]["pts_bonus"] += pts
        f["stats_semana"]["bonus_qtd"] += 1

        self.registrar_historico(filho, "bonus", f"Boa Atitude: {b_nome}", pts, xp)
        self.verificar_conquistas(filho)
        self.salvar_dados()
        self.atualizar_interface()
        messagebox.showinfo("BOA ATITUDE! 🌟", f"{filho} ganhou bônus de conduta:\n+ {pts} Pts\n+ {xp} XP")

    def aplicar_consequencia(self):
        pin = simpledialog.askstring("🔐 Confirmação dos Pais", "Digite o PIN para aplicar consequência:", show="*")
        if pin != self.dados.get("pin_pais", "1234"):
            messagebox.showerror("Negado", "PIN Incorreto!")
            return

        filho = self.combo_filhos.get()
        sel = self.combo_conseq.get()
        if not sel: return

        c_nome = sel.split(" [")[0]
        info_c = self.dados["consequencias_regras"].get(c_nome, {"pontos": 10})
        pts = info_c.get("pontos", 0)

        f = self.dados["filhos"][filho]
        f["pontos_semana"] = max(0, f["pontos_semana"] - pts)
        f["saldo_recompensas"] = max(0, f["saldo_recompensas"] - pts)
        f["stats_semana"]["pts_conseq"] += pts
        f["stats_semana"]["conseq_qtd"] += 1

        self.registrar_historico(filho, "consequencia", f"Consequência: {c_nome}", -pts, 0)
        self.salvar_dados()
        self.atualizar_interface()
        messagebox.showwarning("Consequência Aplicada ⚠️", f"Aplicado a {filho}:\n- {pts} Pts no Campeonato\n- {pts} Saldo na Loja\n(Nota: O XP Histórico permaneceu intacto)")

    def resgatar_recompensa(self):
        filho = self.combo_filhos.get()
        sel = self.combo_recompensas.get()
        if not sel: return

        r_nome = sel.split(" (")[0]
        custo = self.dados["recompensas"].get(r_nome, 0)
        saldo = self.dados["filhos"][filho].get("saldo_recompensas", 0)

        if saldo >= custo:
            self.dados["filhos"][filho]["saldo_recompensas"] -= custo
            self.registrar_historico(filho, "resgate", f"Resgatou: {r_nome}", -custo, 0)
            self.salvar_dados()
            self.atualizar_interface()
            messagebox.showinfo("Recompensa! 🎁", f"{filho} resgatou: {r_nome}!")
        else:
            messagebox.showwarning("Saldo Insuficiente", f"{filho} tem {saldo} pts de saldo, mas precisa de {custo} pts.")

    def atualizar_interface(self):
        self.desenhar_cards_jogadores()
        self.combo_filhos["values"] = list(self.dados["filhos"].keys())

    # --- ADMIN ---
    def admin_add_tarefa(self):
        nome = simpledialog.askstring("Nova Tarefa", "Nome da tarefa:")
        if nome:
            pts = simpledialog.askinteger("Pontos", "Pontos:", initialvalue=15)
            xp = simpledialog.askinteger("XP", "XP:", initialvalue=20)
            if pts and xp:
                self.dados["tarefas"][nome] = {"pontos": pts, "xp": xp}
                self.salvar_dados()

    def admin_add_consequencia(self):
        nome = simpledialog.askstring("Nova Consequência", "Nome do comportamento negativo:")
        if nome:
            pts = simpledialog.askinteger("Pontos a remover", "Pontos a deduzir:", initialvalue=20)
            if pts:
                self.dados["consequencias_regras"][nome] = {"nivel": "🟡 Média", "pontos": pts}
                self.salvar_dados()

    def admin_add_boa_atitude(self):
        nome = simpledialog.askstring("Nova Boa Atitude", "Nome do comportamento positivo:")
        if nome:
            pts = simpledialog.askinteger("Pontos Bônus", "Pontos bônus:", initialvalue=20)
            if pts:
                self.dados["boas_acoes"][nome] = {"pontos": pts, "xp": pts}
                self.salvar_dados()

    def admin_add_recompensa(self):
        nome = simpledialog.askstring("Nova Recompensa", "Nome do prêmio:")
        if nome:
            custo = simpledialog.askinteger("Custo", "Custo em Saldo:", initialvalue=200)
            if custo:
                self.dados["recompensas"][nome] = custo
                self.salvar_dados()

    def admin_add_filho(self):
        nome = simpledialog.askstring("Novo Filho", "Nome:")
        avatar = simpledialog.askstring("Avatar", "Emoji (ex: 👦, 👧):")
        if nome:
            self.dados["filhos"][nome] = {
                "pontos_semana": 0, "saldo_recompensas": 0, "xp_total": 0, "titulos": 0,
                "avatar": avatar if avatar else "👤", "conquistas": [],
                "stats_semana": {"pts_tarefas": 0, "pts_bonus": 0, "pts_conseq": 0, "tarefas_qtd": 0, "bonus_qtd": 0, "conseq_qtd": 0}
            }
            self.salvar_dados()
            self.atualizar_interface()

    def admin_ajustar_pontos(self):
        filho = self.combo_filhos.get()
        f = self.dados["filhos"][filho]
        pts = simpledialog.askinteger("Ajuste", f"Pontos SEMANA de {filho}:", initialvalue=f["pontos_semana"])
        saldo = simpledialog.askinteger("Ajuste", f"Saldo LOJA de {filho}:", initialvalue=f.get("saldo_recompensas", 0))
        xp = simpledialog.askinteger("Ajuste", f"XP TOTAL de {filho}:", initialvalue=f["xp_total"])
        if pts is not None and saldo is not None and xp is not None:
            f["pontos_semana"] = pts
            f["saldo_recompensas"] = saldo
            f["xp_total"] = xp
            self.salvar_dados()
            self.atualizar_interface()

    def admin_alterar_pin(self):
        novo = simpledialog.askstring("Novo PIN", "Digite o novo PIN:")
        if novo:
            self.dados["pin_pais"] = novo
            self.salvar_dados()

if __name__ == "__main__":
    root = tk.Tk()
    app = GameOfHouseApp(root)
    root.mainloop()