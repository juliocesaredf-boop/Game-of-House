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
    "historico_semanas": [],
    "filhos": {
        "Maria Júlia": {"pontos_semana": 0, "xp_total": 0, "titulos": 0, "avatar": "👧", "conquistas": []},
        "Joaquim": {"pontos_semana": 0, "xp_total": 0, "titulos": 0, "avatar": "👦", "conquistas": []}
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
        self.root.title("🎮 Game of House - Edição Campeonatos")
        self.root.geometry("620x820")
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
                                xp_tot = f_old.get("xp_total", pts_sem)
                                tit = f_old.get("titulos", 0)
                                av = f_old.get("avatar", info_p["avatar"])
                                conq = f_old.get("conquistas", [])
                                dados["filhos"][nome] = {
                                    "pontos_semana": pts_sem,
                                    "xp_total": xp_tot,
                                    "titulos": tit,
                                    "avatar": av,
                                    "conquistas": conq
                                }

                    for chave_cat in ["tarefas", "missoes_especiais"]:
                        if chave_cat in dados_salvos:
                            novos_itens = {}
                            for k, v in dados_salvos[chave_cat].items():
                                nome_limpo = k.split(" (+")[0].split(" (")[0]
                                if isinstance(v, int):
                                    novos_itens[nome_limpo] = {"pontos": v, "xp": v}
                                elif isinstance(v, dict):
                                    novos_itens[nome_limpo] = {
                                        "pontos": v.get("pontos", 10),
                                        "xp": v.get("xp", 10)
                                    }
                            dados[chave_cat] = novos_itens

                    if "recompensas" in dados_salvos:
                        novas_rec = {}
                        for k, v in dados_salvos["recompensas"].items():
                            nome_limpo = k.split(" (")[0]
                            novas_rec[nome_limpo] = v if isinstance(v, int) else 100
                        dados["recompensas"] = novas_rec

                    for chave in ["ultima_semana", "pin_pais", "historico", "historico_semanas"]:
                        if chave in dados_salvos:
                            dados[chave] = dados_salvos[chave]
            except Exception as e:
                print(f"Erro ao carregar dados: {e}")
        return dados

    def salvar_dados(self):
        with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
            json.dump(self.dados, f, indent=4, ensure_ascii=False)

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

            for f in self.dados["filhos"]:
                self.dados["filhos"][f]["pontos_semana"] = 0

            self.dados["ultima_semana"] = hoje
            self.salvar_dados()

    def exibir_tela_fim_semana(self, ranking, campeao):
        top = tk.Toplevel(self.root)
        top.title("🏆 FIM DO CAMPEONATO SEMANAL")
        top.geometry("450x550")
        top.configure(bg=self.COR_FUNDO)
        top.grab_set()

        tk.Label(top, text="🏆 FIM DO CAMPEONATO! 🏆", font=("Impact", 20), bg=self.COR_FUNDO, fg=self.COR_AMARELO).pack(pady=15)

        f_placar = tk.Frame(top, bg=self.COR_CARD, padx=15, pady=15)
        f_placar.pack(fill="x", padx=20)

        for nome, info in ranking:
            av = info.get("avatar", "👤")
            pts = info["pontos_semana"]
            tk.Label(f_placar, text=f"{av} {nome}: {pts} pontos na semana", font=("Helvetica", 12, "bold"), bg=self.COR_CARD, fg=self.COR_TEXTO).pack(anchor="w", pady=4)

        tk.Frame(top, height=2, bg=self.COR_ROXO).pack(fill="x", padx=20, pady=15)

        if campeao:
            av_camp = self.dados["filhos"][campeao]["avatar"]
            tk.Label(top, text="🥇 CAMPEÃO DA SEMANA", font=("Helvetica", 11, "bold"), bg=self.COR_FUNDO, fg=self.COR_LARANJA).pack()
            tk.Label(top, text=f"{av_camp} {campeao}!", font=("Impact", 22), bg=self.COR_FUNDO, fg=self.COR_VERDE).pack(pady=5)
            tk.Label(top, text="🎁 Recompensa: Escolher o filme do fim de semana!", font=("Helvetica", 11, "italic"), bg=self.COR_FUNDO, fg=self.COR_AMARELO).pack(pady=5)
        else:
            tk.Label(top, text="🤝 EMPATE NA SEMANA!", font=("Impact", 18), bg=self.COR_FUNDO, fg=self.COR_AZUL).pack(pady=10)

        tk.Label(top, text="🚀 NOVA SEMANA COMEÇOU!\nTodos começam com 0 pontos de campeonato.", font=("Helvetica", 10), bg=self.COR_FUNDO, fg=self.COR_TEXTO, justify="center").pack(pady=20)

        tk.Button(top, text="⚡ INICIAR NOVO CAMPEONATO", font=("Helvetica", 11, "bold"), bg=self.COR_VERDE, fg="#11111B", relief="flat", command=top.destroy).pack(pady=10)

    def criar_widgets(self):
        lbl_titulo = tk.Label(self.root, text="🎮 GAME OF HOUSE ⚔️", font=("Impact", 22), bg=self.COR_FUNDO, fg=self.COR_ROXO)
        lbl_titulo.pack(pady=(15, 5))

        self.frame_jogadores = tk.Frame(self.root, bg=self.COR_FUNDO)
        self.frame_jogadores.pack(fill="x", padx=20, pady=5)

        # BARRA DE NAVEGAÇÃO DE 4 ABAS
        f_nav = tk.Frame(self.root, bg=self.COR_FUNDO)
        f_nav.pack(fill="x", padx=20, pady=10)

        btn_aba1 = tk.Button(f_nav, text="🎯 Missões", font=("Helvetica", 9, "bold"), bg=self.COR_AZUL, fg="#11111B", relief="flat", command=lambda: self.mudar_aba(1))
        btn_aba1.pack(side="left", expand=True, fill="x", padx=2)

        btn_aba2 = tk.Button(f_nav, text="🎁 Loja", font=("Helvetica", 9, "bold"), bg=self.COR_LARANJA, fg="#11111B", relief="flat", command=lambda: self.mudar_aba(2))
        btn_aba2.pack(side="left", expand=True, fill="x", padx=2)

        btn_aba3 = tk.Button(f_nav, text="🏅 Conquistas", font=("Helvetica", 9, "bold"), bg=self.COR_AMARELO, fg="#11111B", relief="flat", command=lambda: self.mudar_aba(3))
        btn_aba3.pack(side="left", expand=True, fill="x", padx=2)

        btn_aba4 = tk.Button(f_nav, text="🔐 Área dos Pais", font=("Helvetica", 9, "bold"), bg=self.COR_VERMELHO, fg="#11111B", relief="flat", command=lambda: self.mudar_aba(4))
        btn_aba4.pack(side="left", expand=True, fill="x", padx=2)

        f_sel = tk.Frame(self.root, bg=self.COR_CARD, padx=10, pady=8)
        f_sel.pack(fill="x", padx=20, pady=5)

        tk.Label(f_sel, text="Player Ativo:", font=("Helvetica", 10, "bold"), bg=self.COR_CARD, fg=self.COR_TEXTO).pack(side="left", padx=5)
        self.combo_filhos = ttk.Combobox(f_sel, values=list(self.dados["filhos"].keys()), state="readonly", font=("Helvetica", 10))
        self.combo_filhos.pack(side="left", fill="x", expand=True, padx=5)
        self.combo_filhos.current(0)

        self.f_conteudo = tk.Frame(self.root, bg=self.COR_FUNDO)
        self.f_conteudo.pack(fill="both", expand=True, padx=20, pady=5)

        self.mudar_aba(1)

    def desenhar_cards_jogadores(self):
        for w in self.frame_jogadores.winfo_children():
            w.destroy()

        for nome, info in self.dados["filhos"].items():
            f_card = tk.Frame(self.frame_jogadores, bg=self.COR_CARD, padx=10, pady=8, bd=1, relief="ridge")
            f_card.pack(side="left", expand=True, fill="both", padx=4)

            av = info.get("avatar", "👤")
            nome_niv, _, _, prog = obter_info_nivel(info["xp_total"])

            tk.Label(f_card, text=f"{av} {nome}", font=("Helvetica", 11, "bold"), bg=self.COR_CARD, fg=self.COR_TEXTO).pack()
            tk.Label(f_card, text=f"{nome_niv}", font=("Helvetica", 9, "bold"), bg=self.COR_CARD, fg=self.COR_AMARELO).pack()

            pbar = ttk.Progressbar(f_card, value=prog*100, maximum=100)
            pbar.pack(fill="x", pady=4)

            tk.Label(f_card, text=f"Semana: {info['pontos_semana']} pts", font=("Impact", 12), bg=self.COR_CARD, fg=self.COR_VERDE).pack()
            tk.Label(f_card, text=f"Total: {info['xp_total']} XP | 🏆 {info['titulos']}x", font=("Helvetica", 8), bg=self.COR_CARD, fg=self.COR_LARANJA).pack()

    def mudar_aba(self, numero):
        for w in self.f_conteudo.winfo_children():
            w.destroy()

        if numero == 1:
            self.desenhar_aba_missoes()
        elif numero == 2:
            self.desenhar_aba_loja()
        elif numero == 3:
            self.desenhar_aba_conquistas()
        elif numero == 4:
            self.autenticar_pais()

    def desenhar_aba_missoes(self):
        # Missoes Diárias
        f_t = tk.LabelFrame(self.f_conteudo, text="✅ Missões Diárias", bg=self.COR_CARD, fg=self.COR_VERDE, font=("Helvetica", 10, "bold"), padx=10, pady=10)
        f_t.pack(fill="x", pady=8)

        opcoes_t = [f"{t} (+{v['pontos']} pts | +{v['xp']} XP)" for t, v in self.dados["tarefas"].items()]
        self.combo_tarefas = ttk.Combobox(f_t, values=opcoes_t, state="readonly", font=("Helvetica", 10))
        self.combo_tarefas.pack(fill="x", pady=8)
        if opcoes_t: self.combo_tarefas.current(0)

        tk.Button(f_t, text="⚡ CUMPRIR MISSÃO", bg=self.COR_VERDE, fg="#11111B", font=("Helvetica", 9, "bold"), relief="flat", command=self.concluir_tarefa).pack(fill="x")

        # Missoes Especiais
        f_e = tk.LabelFrame(self.f_conteudo, text="⚔️ Missões Especiais", bg=self.COR_CARD, fg=self.COR_ROXO, font=("Helvetica", 10, "bold"), padx=10, pady=10)
        f_e.pack(fill="x", pady=8)

        opcoes_e = [f"{m} (+{v['pontos']} pts | +{v['xp']} XP)" for m, v in self.dados["missoes_especiais"].items()]
        self.combo_especiais = ttk.Combobox(f_e, values=opcoes_e, state="readonly", font=("Helvetica", 10))
        self.combo_especiais.pack(fill="x", pady=8)
        if opcoes_e: self.combo_especiais.current(0)

        tk.Button(f_e, text="🔥 CONCLUIR MISSÃO ESPECIAL", bg=self.COR_ROXO, fg="#11111B", font=("Helvetica", 9, "bold"), relief="flat", command=self.concluir_missao_especial).pack(fill="x")

    def desenhar_aba_loja(self):
        # Loja de Recompensas
        f_r = tk.LabelFrame(self.f_conteudo, text="🎁 Loja de Recompensas", bg=self.COR_CARD, fg=self.COR_LARANJA, font=("Helvetica", 10, "bold"), padx=12, pady=15)
        f_r.pack(fill="x", pady=10)

        tk.Label(f_r, text="Escolha um prêmio para resgatar com seus pontos da semana:", font=("Helvetica", 9), bg=self.COR_CARD, fg=self.COR_TEXTO).pack(anchor="w", pady=(0, 5))

        opcoes_r = [f"{r} ({pts} pts)" for r, pts in self.dados["recompensas"].items()]
        self.combo_recompensas = ttk.Combobox(f_r, values=opcoes_r, state="readonly", font=("Helvetica", 10))
        self.combo_recompensas.pack(fill="x", pady=10)
        if opcoes_r: self.combo_recompensas.current(0)

        tk.Button(f_r, text="🛒 RESGATAR RECOMPENSA", bg=self.COR_LARANJA, fg="#11111B", font=("Helvetica", 10, "bold"), relief="flat", command=self.resgatar_recompensa).pack(fill="x", pady=5)

    def desenhar_aba_conquistas(self):
        filho = self.combo_filhos.get()
        f_data = self.dados["filhos"][filho]

        tk.Label(self.f_conteudo, text=f"🏅 Medalhas & Progresso de {f_data['avatar']} {filho}", font=("Helvetica", 12, "bold"), bg=self.COR_FUNDO, fg=self.COR_TEXTO).pack(pady=5)

        f_list = tk.Frame(self.f_conteudo, bg=self.COR_CARD, padx=10, pady=10)
        f_list.pack(fill="both", expand=True, pady=5)

        for key, info in CONQUISTAS_DISPONIVEIS.items():
            desbloqueada = key in f_data["conquistas"]
            cor = self.COR_AMARELO if desbloqueada else "#585B70"
            ic = "✅" if desbloqueada else "🔒"

            f_item = tk.Frame(f_list, bg="#181825", padx=8, pady=5, bd=1, relief="groove")
            f_item.pack(fill="x", pady=3)

            tk.Label(f_item, text=f"{ic} {info['nome']}", font=("Helvetica", 10, "bold"), bg="#181825", fg=cor).pack(anchor="w")
            tk.Label(f_item, text=info['desc'], font=("Helvetica", 8), bg="#181825", fg=self.COR_TEXTO).pack(anchor="w")

    def autenticar_pais(self):
        pin = simpledialog.askstring("🔐 Área dos Pais", "Digite o PIN de Administrador:", show="*")
        if pin == self.dados.get("pin_pais", "1234"):
            self.desenhar_aba_pais()
        else:
            messagebox.showerror("Acesso Negado", "PIN Incorreto!")
            self.mudar_aba(1)

    def desenhar_aba_pais(self):
        tk.Label(self.f_conteudo, text="⚙️ Gerenciador de Tarefas, Pontos e XP", font=("Helvetica", 12, "bold"), bg=self.COR_FUNDO, fg=self.COR_VERMELHO).pack(pady=5)

        f_cont = tk.Frame(self.f_conteudo, bg=self.COR_CARD, padx=10, pady=10)
        f_cont.pack(fill="both", expand=True)

        tk.Label(f_cont, text="--- GERENCIAR TAREFAS PRINCIPAIS ---", font=("Helvetica", 9, "bold"), bg=self.COR_CARD, fg=self.COR_AMARELO).pack(pady=(5, 2))
        tk.Button(f_cont, text="➕ Criar Nova Tarefa", bg=self.COR_AZUL, fg="#11111B", font=("Helvetica", 9, "bold"), command=self.admin_add_tarefa).pack(fill="x", pady=2)
        tk.Button(f_cont, text="✏️ Editar Pontos e XP de Tarefa", bg=self.COR_AMARELO, fg="#11111B", font=("Helvetica", 9, "bold"), command=self.admin_editar_tarefa).pack(fill="x", pady=2)
        tk.Button(f_cont, text="🗑️ Excluir Tarefa", bg=self.COR_VERMELHO, fg="#FFFFFF", font=("Helvetica", 9, "bold"), command=self.admin_excluir_tarefa).pack(fill="x", pady=2)

        tk.Label(f_cont, text="--- OUTRAS CONFIGURAÇÕES ---", font=("Helvetica", 9, "bold"), bg=self.COR_CARD, fg=self.COR_AMARELO).pack(pady=(12, 2))
        tk.Button(f_cont, text="⚔️ Criar Missão Especial", bg=self.COR_ROXO, fg="#11111B", font=("Helvetica", 9, "bold"), command=self.admin_add_especial).pack(fill="x", pady=2)
        tk.Button(f_cont, text="🎁 Criar Recompensa", bg=self.COR_LARANJA, fg="#11111B", font=("Helvetica", 9, "bold"), command=self.admin_add_recompensa).pack(fill="x", pady=2)
        tk.Button(f_cont, text="👤 Cadastrar Novo Filho", bg=self.COR_VERDE, fg="#11111B", font=("Helvetica", 9, "bold"), command=self.admin_add_filho).pack(fill="x", pady=2)
        tk.Button(f_cont, text="🎯 Ajustar Pontos/XP do Filho", bg=self.COR_AZUL, fg="#11111B", font=("Helvetica", 9, "bold"), command=self.admin_ajustar_pontos).pack(fill="x", pady=2)
        tk.Button(f_cont, text="🔑 Alterar PIN dos Pais", bg=self.COR_VERMELHO, fg="#FFFFFF", font=("Helvetica", 9, "bold"), command=self.admin_alterar_pin).pack(fill="x", pady=2)

    # --- AÇÕES DO JOGO ---
    def concluir_tarefa(self):
        filho = self.combo_filhos.get()
        sel = self.combo_tarefas.get()
        if not sel: return

        t_nome = sel.split(" (+")[0].split(" (")[0]
        info_t = self.dados["tarefas"].get(t_nome, {"pontos": 0, "xp": 0})
        pts = info_t.get("pontos", 0)
        xp = info_t.get("xp", 0)

        self.dados["filhos"][filho]["pontos_semana"] += pts
        self.dados["filhos"][filho]["xp_total"] += xp

        self.verificar_conquistas(filho)
        self.salvar_dados()
        self.atualizar_interface()
        messagebox.showinfo("Missão Cumprida! ⚡", f"{filho} recebeu:\n+ {pts} Pontos (Campeonato/Loja)\n+ {xp} XP (Subir de Nível)")

    def concluir_missao_especial(self):
        filho = self.combo_filhos.get()
        sel = self.combo_especiais.get()
        if not sel: return

        m_nome = sel.split(" (+")[0].split(" (")[0]
        info_m = self.dados["missoes_especiais"].get(m_nome, {"pontos": 0, "xp": 0})
        pts = info_m.get("pontos", 0)
        xp = info_m.get("xp", 0)

        self.dados["filhos"][filho]["pontos_semana"] += pts
        self.dados["filhos"][filho]["xp_total"] += xp

        self.verificar_conquistas(filho)
        self.salvar_dados()
        self.atualizar_interface()
        messagebox.showinfo("BÔNUS ESPECIAL! ⚔️", f"{filho} recebeu:\n+ {pts} Pontos Bônus\n+ {xp} XP Bônus")

    def resgatar_recompensa(self):
        filho = self.combo_filhos.get()
        sel = self.combo_recompensas.get()
        if not sel: return

        r_nome = sel.split(" (")[0]
        custo = self.dados["recompensas"].get(r_nome, 0)
        saldo = self.dados["filhos"][filho]["pontos_semana"]

        if saldo >= custo:
            self.dados["filhos"][filho]["pontos_semana"] -= custo
            self.salvar_dados()
            self.atualizar_interface()
            messagebox.showinfo("Recompensa! 🎁", f"{filho} resgatou: {r_nome}!")
        else:
            messagebox.showwarning("Pontos Insuficientes", f"{filho} tem {saldo} pts na semana, precisa de {custo} pts.")

    def atualizar_interface(self):
        self.desenhar_cards_jogadores()
        self.combo_filhos["values"] = list(self.dados["filhos"].keys())

    # --- AÇÕES ADMINISTRATIVAS ---
    def admin_add_tarefa(self):
        nome = simpledialog.askstring("Nova Tarefa", "Nome da tarefa (ex: 'Arrumar a cama'):")
        if nome:
            pts = simpledialog.askinteger("Pontos", f"Quantos PONTOS (para a Loja) vale '{nome}'?", initialvalue=15)
            xp = simpledialog.askinteger("XP", f"Quanto XP (para o Nível) vale '{nome}'?", initialvalue=20)
            if pts is not None and xp is not None:
                self.dados["tarefas"][nome] = {"pontos": pts, "xp": xp}
                self.salvar_dados()
                messagebox.showinfo("Sucesso", f"Tarefa '{nome}' criada:\n{pts} Pontos | {xp} XP")

    def admin_editar_tarefa(self):
        if not self.dados["tarefas"]:
            messagebox.showinfo("Aviso", "Nenhuma tarefa cadastrada.")
            return

        lista_tarefas = list(self.dados["tarefas"].keys())
        
        top = tk.Toplevel(self.root)
        top.title("✏️ Editar Tarefa")
        top.geometry("380x220")
        top.configure(bg=self.COR_FUNDO)
        top.grab_set()

        tk.Label(top, text="Selecione a Tarefa:", font=("Helvetica", 10, "bold"), bg=self.COR_FUNDO, fg=self.COR_TEXTO).pack(pady=(15, 5))
        combo = ttk.Combobox(top, values=lista_tarefas, state="readonly", font=("Helvetica", 10))
        combo.pack(fill="x", padx=20, pady=5)
        combo.current(0)

        def salvar_edicao():
            t_sel = combo.get()
            dados_atuais = self.dados["tarefas"][t_sel]
            novo_pts = simpledialog.askinteger("Pontos", f"Novos PONTOS para '{t_sel}':", initialvalue=dados_atuais["pontos"])
            novo_xp = simpledialog.askinteger("XP", f"Novo XP para '{t_sel}':", initialvalue=dados_atuais["xp"])
            if novo_pts is not None and novo_xp is not None:
                self.dados["tarefas"][t_sel] = {"pontos": novo_pts, "xp": novo_xp}
                self.salvar_dados()
                top.destroy()
                messagebox.showinfo("Sucesso", f"'{t_sel}' atualizada:\n{novo_pts} Pontos | {novo_xp} XP!")

        tk.Button(top, text="Atualizar Pontos e XP", bg=self.COR_VERDE, fg="#11111B", font=("Helvetica", 10, "bold"), command=salvar_edicao).pack(pady=15)

    def admin_excluir_tarefa(self):
        if not self.dados["tarefas"]:
            messagebox.showinfo("Aviso", "Nenhuma tarefa cadastrada.")
            return

        lista_tarefas = list(self.dados["tarefas"].keys())

        top = tk.Toplevel(self.root)
        top.title("🗑️ Excluir Tarefa")
        top.geometry("380x200")
        top.configure(bg=self.COR_FUNDO)
        top.grab_set()

        tk.Label(top, text="Selecione a Tarefa para Remover:", font=("Helvetica", 10, "bold"), bg=self.COR_FUNDO, fg=self.COR_TEXTO).pack(pady=(15, 5))
        combo = ttk.Combobox(top, values=lista_tarefas, state="readonly", font=("Helvetica", 10))
        combo.pack(fill="x", padx=20, pady=5)
        combo.current(0)

        def confirmar_exclusao():
            t_sel = combo.get()
            if messagebox.askyesno("Confirmar", f"Tem certeza que deseja excluir a tarefa '{t_sel}'?"):
                del self.dados["tarefas"][t_sel]
                self.salvar_dados()
                top.destroy()
                messagebox.showinfo("Sucesso", f"Tarefa '{t_sel}' excluída!")

        tk.Button(top, text="Excluir Tarefa", bg=self.COR_VERMELHO, fg="#FFFFFF", font=("Helvetica", 10, "bold"), command=confirmar_exclusao).pack(pady=15)

    def admin_add_especial(self):
        nome = simpledialog.askstring("Nova Missão Especial", "Nome da missão:")
        if nome:
            pts = simpledialog.askinteger("Pontos", "Pontos Bônus (Loja):", initialvalue=30)
            xp = simpledialog.askinteger("XP", "XP Bônus (Nível):", initialvalue=50)
            if pts is not None and xp is not None:
                self.dados["missoes_especiais"][nome] = {"pontos": pts, "xp": xp}
                self.salvar_dados()
                messagebox.showinfo("Sucesso", f"Missão especial '{nome}' cadastrada!")

    def admin_add_recompensa(self):
        nome = simpledialog.askstring("Nova Recompensa", "Nome da recompensa:")
        if nome:
            custo = simpledialog.askinteger("Custo", "Custo em Pontos da Semana:", initialvalue=200)
            if custo is not None:
                self.dados["recompensas"][nome] = custo
                self.salvar_dados()
                messagebox.showinfo("Sucesso", f"Recompensa '{nome}' cadastrada!")

    def admin_add_filho(self):
        nome = simpledialog.askstring("Novo Filho", "Nome da criança:")
        avatar = simpledialog.askstring("Avatar", "Emoji do avatar (ex: 👦, 👧, 🦁):")
        if nome:
            self.dados["filhos"][nome] = {
                "pontos_semana": 0,
                "xp_total": 0,
                "titulos": 0,
                "avatar": avatar if avatar else "👤",
                "conquistas": []
            }
            self.salvar_dados()
            self.atualizar_interface()
            messagebox.showinfo("Sucesso", f"Player {nome} cadastrado!")

    def admin_ajustar_pontos(self):
        filho = self.combo_filhos.get()
        pts_sem = simpledialog.askinteger("Ajuste", f"Novos Pontos da SEMANA para {filho}:", initialvalue=self.dados["filhos"][filho]["pontos_semana"])
        xp_tot = simpledialog.askinteger("Ajuste", f"Novo XP TOTAL para {filho}:", initialvalue=self.dados["filhos"][filho]["xp_total"])
        if pts_sem is not None and xp_tot is not None:
            self.dados["filhos"][filho]["pontos_semana"] = pts_sem
            self.dados["filhos"][filho]["xp_total"] = xp_tot
            self.salvar_dados()
            self.atualizar_interface()
            messagebox.showinfo("Sucesso", "Pontos ajustados com sucesso!")

    def admin_alterar_pin(self):
        novo_pin = simpledialog.askstring("Novo PIN", "Digite o novo PIN de 4 dígitos:")
        if novo_pin:
            self.dados["pin_pais"] = novo_pin
            self.salvar_dados()
            messagebox.showinfo("Sucesso", "PIN alterado com sucesso!")

if __name__ == "__main__":
    root = tk.Tk()
    app = GameOfHouseApp(root)
    root.mainloop()