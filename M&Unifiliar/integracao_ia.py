"""Controles discretos de copiar/importar, usando o mesmo núcleo do editor."""
import copy
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
from uuid import uuid4

from interface import botao, PAPEL, TINTA
from paineis import Cartao
from nucleo.documento import salvar, validar_dados
from nucleo.ia import gerar_contexto, preparar_importacao, resumo_projeto
from nucleo.validacao import LIMITES


class IntegracaoIA:
    def estado_para_ia(self):
        self.concluir_digitacao()
        estado = copy.deepcopy(self.dados)
        estado["vistas"] = {**self.cameras,self.aba.get():self.camera()}
        if self.posicao_mapa is not None:
            estado["minimapa"] = list(self.posicao_mapa)
        return estado

    def copiar_contexto_ia(self,atual=True):
        try:
            contexto = gerar_contexto(self.estado_para_ia(),atual=atual)
            self.root.clipboard_clear()
            self.root.clipboard_append(contexto)
            self.root.update_idletasks()
            self.status.set("Contexto copiado. Cole na sua IA e acrescente o pedido." if atual else
                            "Instruções copiadas para um projeto novo, sem o desenho atual.")
            return contexto
        except (OSError,ValueError,tk.TclError) as exc:
            messagebox.showerror("Contexto para IA",str(exc),parent=self.root)

    def importar_resposta_ia(self):
        self.concluir_digitacao()
        dialogo = DialogoImportacao(self)
        return dialogo

    def aplicar_documento_ia(self,data,substituir=False,pasta_recuperacao=None):
        """Só chamado pelos botões de aplicação depois da revisão. Sem gravação do destino."""
        data = validar_dados(data)
        if not substituir:
            janela = tk.Toplevel(self.root._root())
            editor = type(self)(janela)
            editor.substituir(copy.deepcopy(data),None)
            # Imported data is unsaved, including when the user closes the new window.
            editor.gravado = None
            editor.render()
            janela.editor = editor
            return editor
        anterior = self.estado_para_ia()
        pasta = Path(pasta_recuperacao) if pasta_recuperacao is not None else (
            self.path.parent if self.path else Path(__file__).resolve().parent)/".recuperacao"
        pasta.mkdir(parents=True,exist_ok=True)
        copia = pasta/f"antes-ia-{datetime.now():%Y%m%d-%H%M%S}-{uuid4().hex[:8]}.json"
        salvar(copia,anterior)  # Any failure aborts before replacing the document.
        caminho,gravado = self.path,copy.deepcopy(self.gravado)
        historico = copy.deepcopy(self.historico)
        try:
            self.substituir(copy.deepcopy(data),caminho)
        except Exception:
            self.substituir(anterior,caminho)
            self.gravado = gravado
            self.historico = historico
            raise
        self.historico = (historico+[anterior])[-80:]
        self.gravado = gravado
        self.ultima_recuperacao = copia
        self.render()
        self.status.set(f"Importação aplicada. Ctrl+Z desfaz. Cópia anterior: {copia}")
        return copia


def descrever_resumo(resumo):
    folhas = resumo["folhas"]
    totais = {k:sum(f[k] for f in folhas) for k in ("componentes","ligacoes","nos","formas")}
    nomes = ", ".join(f["nome"][:40] for f in folhas[:3])
    if len(folhas)>3:
        nomes += f" e mais {len(folhas)-3}"
    return (f"{len(folhas)} folha(s) ({nomes}): {totais['componentes']} componentes, "
            f"{totais['ligacoes']} ligações, {totais['nos']} nós, {totais['formas']} formas/textos")


class DialogoImportacao:
    def __init__(self,editor):
        self.editor = editor
        self.revisado = None
        self.janela = tk.Toplevel(editor.root)
        j = self.janela
        j.title("Importar resposta da IA")
        j.geometry("800x660")
        j.minsize(680,580)
        j.configure(bg=PAPEL)
        j.transient(editor.root)
        j.grab_set()
        j.bind("<Escape>",lambda e:self.cancelar())
        j.protocol("WM_DELETE_WINDOW",self.cancelar)
        cab = Cartao(j,padding=12)
        cab.pack(fill="x",padx=14,pady=(14,8))
        tk.Label(cab.conteudo,text="Importar resposta da IA",font=("Segoe UI",14,"bold"),bg="white",fg=TINTA).pack(anchor="w")
        tk.Label(cab.conteudo,text="Cole o JSON completo ou um único bloco Markdown. Valide antes de aplicar.",
                 bg="white",fg="#63756d").pack(anchor="w",pady=(4,0))
        comandos = tk.Frame(j,bg=PAPEL)
        comandos.pack(fill="x",padx=18)
        botao(comandos,"Colar",self.colar).pack(side="left",padx=(0,6))
        botao(comandos,"Abrir JSON…",self.abrir_arquivo).pack(side="left")
        area = tk.Frame(j,bg="white",highlightbackground="#d2dcd5",highlightthickness=1)
        area.pack(fill="both",expand=True,padx=18,pady=8)
        scroll = tk.Scrollbar(area)
        scroll.pack(side="right",fill="y")
        self.entrada = tk.Text(area,wrap="word",height=8,font=("Consolas",10),bg="white",fg=TINTA,
                               relief="flat",padx=10,pady=10,undo=True,yscrollcommand=scroll.set)
        self.entrada.pack(fill="both",expand=True)
        scroll.configure(command=self.entrada.yview)
        self.entrada.bind("<<Modified>>",self.alterado)
        self.resumo = tk.StringVar(value="Nenhuma alteração será aplicada durante a validação.")
        self.erro = tk.StringVar()
        tk.Label(j,textvariable=self.erro,bg=PAPEL,fg="#a33f36",justify="left",anchor="w",wraplength=640).pack(fill="x",padx=18)
        tk.Label(j,textvariable=self.resumo,bg=PAPEL,fg=TINTA,justify="left",anchor="w",wraplength=640).pack(fill="x",padx=18,pady=5)
        tk.Label(j,text="Validação estrutural não é aprovação elétrica. Não há mesclagem automática.",
                 bg=PAPEL,fg="#63756d").pack(anchor="w",padx=18)
        rodape = tk.Frame(j,bg=PAPEL)
        rodape.pack(fill="x",padx=18,pady=14)
        botao(rodape,"Cancelar",self.cancelar).pack(side="left")
        botao(rodape,"Validar e revisar",self.validar,"#d4eee0").pack(side="left",padx=6)
        self.botao_novo = botao(rodape,"Abrir em nova janela",lambda:self.aplicar(False))
        self.botao_novo.pack(side="right")
        self.botao_substituir = botao(rodape,"Substituir atual",lambda:self.aplicar(True))
        self.botao_substituir.pack(side="right",padx=6)
        self.bloquear()
        self.entrada.focus_set()

    def bloquear(self):
        self.revisado = None
        self.botao_novo.configure(state="disabled")
        self.botao_substituir.configure(state="disabled")

    def alterado(self,e=None):
        if self.entrada.edit_modified():
            self.bloquear()
            self.erro.set("")
            self.resumo.set("Texto alterado. Valide novamente antes de aplicar.")
            self.entrada.edit_modified(False)

    def preencher(self,texto):
        self.entrada.delete("1.0","end")
        self.entrada.insert("1.0",texto)
        self.alterado()

    def colar(self):
        try:
            self.preencher(self.janela.clipboard_get())
        except tk.TclError:
            self.erro.set("A área de transferência não contém texto.")

    def abrir_arquivo(self):
        nome = filedialog.askopenfilename(parent=self.janela,filetypes=[("Projeto JSON","*.json")])
        if nome:
            try:
                path = Path(nome)
                if path.stat().st_size>LIMITES["bytes_json"]:
                    raise ValueError("O arquivo excede 10 MiB.")
                self.preencher(path.read_text(encoding="utf-8-sig"))
            except (OSError,ValueError) as exc:
                self.erro.set(str(exc))

    def validar(self):
        self.alterado()
        self.bloquear()
        resposta = self.entrada.get("1.0","end-1c")
        try:
            data,resumo = preparar_importacao(resposta)
        except ValueError as exc:
            self.erro.set(str(exc))
            self.resumo.set("Importação recusada. O projeto atual foi preservado.")
            return False
        self.erro.set("")
        atual = resumo_projeto(self.editor.dados)
        libs = resumo["bibliotecas"]
        bibliotecas = ", ".join(r["id"] for r in libs[:3]) or "nenhuma"
        if len(libs)>3:
            bibliotecas += f" e mais {len(libs)-3}"
        self.resumo.set("Resposta válida — "+descrever_resumo(resumo)+
                        "\nBibliotecas: "+bibliotecas+
                        "\nProjeto atual — "+descrever_resumo(atual)+
                        "\nEscolha nova janela ou substituição com cópia recuperável e Ctrl+Z.")
        self.revisado = (resposta,data)
        self.botao_novo.configure(state="normal")
        self.botao_substituir.configure(state="normal")
        return True

    def aplicar(self,substituir):
        if self.revisado is None or self.revisado[0]!=self.entrada.get("1.0","end-1c"):
            self.bloquear()
            self.erro.set("Valide e revise o conteúdo antes de aplicar.")
            return False
        try:
            resultado = self.editor.aplicar_documento_ia(self.revisado[1],substituir)
        except (OSError,ValueError,tk.TclError) as exc:
            self.erro.set("Não foi possível aplicar: "+str(exc))
            return False
        self.cancelar()
        return resultado

    def cancelar(self):
        self.janela.grab_release()
        self.janela.destroy()
