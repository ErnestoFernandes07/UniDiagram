from formas import limites


class Navegacao:
    def agendar_movimento(self,acao,event):
        # Uma única posição pendente; não reproduzir o trajeto atrasado do mouse.
        self.movimento_pendente=(acao,event)
        if getattr(self,"timer_movimento",None) is None:
            self.timer_movimento=self.root.after_idle(self.processar_movimento)

    def cancelar_movimento(self):
        if getattr(self,"timer_movimento",None) is not None:
            self.root.after_cancel(self.timer_movimento)
        self.timer_movimento=None
        self.movimento_pendente=None

    def processar_movimento(self):
        pendente=getattr(self,"movimento_pendente",None)
        self.cancelar_movimento()
        if pendente:
            acao,event=pendente
            acao(event)

    def terminar_pan(self,event=None):
        self.processar_movimento()
        self.c.configure(cursor=self.cursor_ferramenta())

    def iniciar_arrasto_mapa(self,e):
        self.inicio_mapa = (e.x_root-self.cartao_mapa.winfo_rootx(),e.y_root-self.cartao_mapa.winfo_rooty())
        self.cartao_mapa.tk.call("raise",self.cartao_mapa)

    def arrastar_mapa(self,e):
        dx,dy = self.inicio_mapa
        x,y = e.x_root-self.area.winfo_rootx()-dx,e.y_root-self.area.winfo_rooty()-dy
        w = max(1,self.area.winfo_width()-self.cartao_mapa.winfo_width())
        h = max(1,self.area.winfo_height()-self.cartao_mapa.winfo_height())
        self.posicao_mapa = [min(1,max(0,x/w)),min(1,max(0,y/h))]
        self.limitar_mapa()

    def limitar_mapa(self):
        if self.posicao_mapa is None:
            return
        fx,fy = self.posicao_mapa
        x = round(fx*max(0,self.area.winfo_width()-self.cartao_mapa.winfo_width()))
        y = round(fy*max(0,self.area.winfo_height()-self.cartao_mapa.winfo_height()))
        self.cartao_mapa.place(x=x,y=y,relx=0,rely=0,anchor="nw")

    def vista(self):
        c = self.c
        x,y = c.canvasx(0)/self.zoom,c.canvasy(0)/self.zoom
        return x,y,x+c.winfo_width()/self.zoom,y+c.winfo_height()/self.zoom

    def camera(self):
        x,y,u,v = self.vista()
        return dict(x=(x+u)/2,y=(y+v)/2,zoom=self.zoom)

    def posicionar_vista(self,x,y):
        # Canvas sem confinamento. scan_dragto desloca a janela, inclusive antes de zero.
        self.c.scan_mark(0,0)
        self.c.scan_dragto(round(self.c.canvasx(0)-x),round(self.c.canvasy(0)-y),gain=1)

    def ir_camera(self,x,y,zoom):
        self.zoom = zoom
        self.indice_zoom.set(f"{zoom:.0%}")
        self.posicionar_vista(x*zoom-self.c.winfo_width()/2,y*zoom-self.c.winfo_height()/2)
        self.render()

    def marcar(self,numero):
        self.lembrar()
        self.dados.setdefault("waypoints",{})[str(numero)] = dict(self.camera(),folha=self.aba.get())
        self.status.set(f"Posição marcada. Pressione {numero} para voltar a esta vista.")
        self.render()

    def visitar(self,numero):
        destino = self.dados.get("waypoints",{}).get(str(numero))
        if not destino:
            self.status.set(f"Posição {numero} livre. Use o + do minimapa ou Shift + {numero} para marcar.")
            return
        self.aba.set(destino["folha"])
        self.trocar()
        self.ir_camera(destino["x"],destino["y"],destino["zoom"])

    def elementos_mapa(self):
        for item in self.folha["componentes"].values():
            x,y = item["x"],item["y"]
            yield "bloco",[(x-15,y-16),(x+15,y+16)]
        for fio in self.folha["ligacoes"].values():
            yield "fio",self.caminho(fio)
        for forma in self.folha.get("formas",{}).values():
            yield forma["tipo"],forma["pontos"]

    def desenhar_mapa(self):
        from canvas_retido import CanvasRetido
        if not hasattr(self,"mapa_retido"):
            self.mapa_retido=CanvasRetido(self.minimapa)
        m=self.mapa_retido
        m.iniciar(1)
        w,h = int(m.cget("width")),int(m.cget("height"))
        x,y,u,v = self.vista()
        elementos = list(self.elementos_mapa())
        marcas = {k:p for k,p in self.dados.get("waypoints",{}).items() if p["folha"]==self.aba.get()}
        pontos = [(x,y),(u,v),*((p["x"],p["y"]) for p in marcas.values())]
        for _,coords in elementos:
            pontos.extend(coords)
        a,b,d,e = limites(pontos)
        escala = min((w-22)/max(1,d-a),(h-22)/max(1,e-b))
        ox,oy = (w-(d-a)*escala)/2-a*escala,(h-(e-b)*escala)/2-b*escala
        self.plano_mapa = ox,oy,escala

        def tela(x,y):
            return (x*escala+ox,y*escala+oy)

        m.create_rectangle(*tela(x,y),*tela(u,v),fill="#dff1eb",outline="")
        for tipo,coords in elementos:
            mini = [tela(*p) for p in coords]
            if tipo in ("bloco","Retângulo","Losango","Elipse"):
                caixa = limites(mini)
                metodo = m.create_oval if tipo=="Elipse" else m.create_rectangle
                metodo(*caixa,outline="#538578",fill="#538578" if tipo=="bloco" else "")
            elif len(mini)>1:
                m.create_line(*mini,fill="#607d84")
            else:
                px,py = mini[0]
                m.create_line(px-2,py,px+2,py,fill="#607d84")
        m.create_rectangle(*tela(x,y),*tela(u,v),outline="#13836f",width=1.5)
        for k,p in marcas.items():
            px,py = tela(p["x"],p["y"])
            m.create_oval(px-6,py-6,px+6,py+6,fill="#146a59",outline="")
            m.create_text(px,py,text=k,font=("Segoe UI",-9,"bold"),fill="white")
        m.finalizar()
        for k,botao in self.slots.items():
            salvo = str(k) in self.dados.get("waypoints",{})
            botao.configure(bg="#d7eee5" if salvo else "#eff3f1",fg="#216653" if salvo else "#63766f")

    def navegar_mapa(self,e):
        ox,oy,k = self.plano_mapa
        self.ir_camera((e.x-ox)/k,(e.y-oy)/k,self.zoom)

    def arrastar_tela(self,e):
        self.c.scan_dragto(e.x,e.y,gain=1)
        self.render()
