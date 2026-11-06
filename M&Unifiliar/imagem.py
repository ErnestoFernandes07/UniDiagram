from functools import lru_cache
from pathlib import Path
import os
from math import hypot

from PIL import Image, ImageDraw, ImageFont

ARQUIVOS_FONTE = {"Segoe UI":("segoeui","segoeuib"), "Arial":("arial","arialbd"),
                  "Georgia":("georgia","georgiab"), "Consolas":("consola","consolab"),
                  "Times New Roman":("times","timesbd"), "Calibri":("calibri","calibrib")}


@lru_cache(maxsize=128)
def fonte(familia,tamanho,negrito):
    nome = ARQUIVOS_FONTE.get(familia,ARQUIVOS_FONTE["Segoe UI"])[int(negrito)]
    try:
        return ImageFont.truetype(str(Path(os.environ.get("WINDIR","C:/Windows"))/"Fonts"/(nome+".ttf")),tamanho)
    except OSError:
        return ImageFont.load_default(size=tamanho)


def rasterizar(canvas, caixa, escala, fundo, objetos):
    esquerda,topo,direita,base = caixa
    imagem = Image.new("RGB",(max(1,round((direita-esquerda)*escala)),
                              max(1,round((base-topo)*escala))),fundo)
    for obj in objetos:
        tipo = canvas.type(obj)
        if tipo not in ("line","oval","rectangle","polygon","text"):
            continue
        bbox = canvas.bbox(obj)
        if not bbox:
            continue
        x = max(0,int((bbox[0]-esquerda)*escala)-2)
        y = max(0,int((bbox[1]-topo)*escala)-2)
        u = min(imagem.width,int((bbox[2]-esquerda)*escala)+3)
        v = min(imagem.height,int((bbox[3]-topo)*escala)+3)
        if x>=u or y>=v:
            continue
        camada = Image.new("RGBA",(u-x,v-y))
        desenho = ImageDraw.Draw(camada)
        coords = canvas.coords(obj)
        pontos = [(round((a-esquerda)*escala)-x,round((b-topo)*escala)-y)
                  for a,b in zip(coords[::2],coords[1::2])]
        cor = canvas.itemcget(obj,"fill")
        if tipo=="text":
            familia,tamanho,*estilo = canvas.tk.splitlist(canvas.itemcget(obj,"font"))
            ft = fonte(familia,max(1,round(abs(int(tamanho))*escala)),"bold" in estilo)
            valor = canvas.itemcget(obj,"text")
            angulo = float(canvas.itemcget(obj,"angle"))
            if angulo:
                l,t,r,b = desenho.multiline_textbbox((0,0),valor,font=ft)
                texto = Image.new("RGBA",(max(1,r-l+6),max(1,b-t+6)))
                ImageDraw.Draw(texto).multiline_text((3-l,3-t),valor,font=ft,fill=cor,align="center")
                texto = texto.rotate(angulo,expand=True,resample=Image.Resampling.BICUBIC)
                a,b = pontos[0]
                camada.alpha_composite(texto,(a-texto.width//2,b-texto.height//2))
            else:
                desenho.multiline_text(pontos[0],valor,fill=cor,anchor="mm",align="center",font=ft)
        else:
            largura = max(1,round(float(canvas.itemcget(obj,"width"))*escala))
            if tipo=="line":
                padrao = canvas.itemcget(obj,"dash")
                if padrao:
                    tracos = [max(1,float(n)*escala) for n in canvas.tk.splitlist(padrao)]
                    if len(tracos)%2:
                        tracos *= 2
                    periodo = sum(tracos)
                    fase = 0
                    for (a,b),(c,d) in zip(pontos,pontos[1:]):
                        comprimento = hypot(c-a,d-b)
                        if not comprimento:
                            continue
                        # Clip the walked interval to the local image before splitting dashes.
                        lo,hi = 0.,1.
                        for origem,delta,limite in ((a,c-a,camada.width),(b,d-b,camada.height)):
                            if delta:
                                t0,t1 = sorted(((-largura-origem)/delta,(limite+largura-origem)/delta))
                                lo,hi = max(lo,t0),min(hi,t1)
                            elif not -largura<=origem<=limite+largura:
                                hi = -1
                        pos = max(0,lo*comprimento)
                        fim = min(comprimento,hi*comprimento)
                        while pos<fim:
                            resto = (fase+pos)%periodo
                            indice = 0
                            while indice<len(tracos)-1 and resto>=tracos[indice]:
                                resto -= tracos[indice]
                                indice += 1
                            proximo = min(fim,pos+max(.001,tracos[indice]-resto))
                            if indice%2==0:
                                desenho.line([(a+(c-a)*pos/comprimento,b+(d-b)*pos/comprimento),
                                              (a+(c-a)*proximo/comprimento,b+(d-b)*proximo/comprimento)],fill=cor,width=largura)
                            pos = proximo
                        fase = (fase+comprimento)%periodo
                else:
                    desenho.line(pontos,fill=cor,width=largura)
            elif tipo=="polygon":
                if cor:
                    desenho.polygon(pontos,fill=cor)
                desenho.line([*pontos,pontos[0]],fill=canvas.itemcget(obj,"outline"),width=largura)
            else:
                metodo = desenho.ellipse if tipo=="oval" else desenho.rectangle
                metodo(pontos,fill=cor or None,outline=canvas.itemcget(obj,"outline") or None,width=largura)
        alpha = next((int(tag[6:]) for tag in canvas.gettags(obj) if tag.startswith("alpha:")),100)
        mascara = camada.getchannel("A")
        if alpha!=100:
            mascara = mascara.point(lambda n:round(n*alpha/100))
        imagem.paste(camada,(x,y),mascara)
    return imagem


def gravar_png(canvas,destino):
    x,y,u,v = canvas.bbox("all") or (0,0,480,320)
    escala = min(2,6000/max(u-x+48,v-y+48))
    imagem = rasterizar(canvas,(x-24,y-24,u+24,v+24),escala,"white",canvas.find_all())
    imagem.save(destino,format="PNG")


def compor_tela(canvas):
    from PIL import ImageTk
    x,y = canvas.canvasx(0),canvas.canvasy(0)
    caixa = (x,y,x+canvas.winfo_width(),y+canvas.winfo_height())
    objetos = canvas.find_overlapping(*caixa)
    imagem = rasterizar(canvas,caixa,1,canvas.cget("bg"),objetos)
    canvas.composicao = ImageTk.PhotoImage(imagem,master=canvas)
    canvas.create_image(x,y,image=canvas.composicao,anchor="nw",tags="composicao")
