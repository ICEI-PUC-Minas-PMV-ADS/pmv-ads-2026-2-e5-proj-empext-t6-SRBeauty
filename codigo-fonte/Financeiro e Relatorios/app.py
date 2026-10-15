import io
from datetime import datetime, date
from typing import List, Optional
from enum import Enum
from collections import Counter
from fastapi import FastAPI, Query, Depends, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Date, Enum as SQLEnum
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Importações do ReportLab para PDF
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# -----------------------------------------------------------------------------
# Banco de Dados
# -----------------------------------------------------------------------------
DATABASE_URL = "sqlite:///./salao_financeiro.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# -----------------------------------------------------------------------------
# Modelos
# -----------------------------------------------------------------------------
class TipoMovimentacao(str, Enum):
    ENTRADA = "entrada"
    SAIDA = "saida"

class FormaPagamento(str, Enum):
    PIX = "pix"
    DINHEIRO = "dinheiro"
    CARTAO_DEBITO = "cartao_debito"
    CARTAO_CREDITO = "cartao_credito"

class Movimentacao(Base):
    __tablename__ = "movimentacoes"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(SQLEnum(TipoMovimentacao), nullable=False)
    profissional = Column(String, default="Salão")
    descricao = Column(String, nullable=False)
    categoria = Column(String, nullable=False)
    forma_pagamento = Column(SQLEnum(FormaPagamento), nullable=False)
    valor_bruto = Column(Float, nullable=False)
    taxa_cartao = Column(Float, default=0.0)
    valor_liquido = Column(Float, nullable=False)
    data = Column(DateTime, default=datetime.now)

class FechamentoCaixa(Base):
    __tablename__ = "fechamentos_caixa"

    id = Column(Integer, primary_key=True, index=True)
    data_fechamento = Column(Date, unique=True, nullable=False)
    total_entradas = Column(Float, default=0.0)
    total_saidas = Column(Float, default=0.0)
    total_taxas = Column(Float, default=0.0)
    saldo_liquido = Column(Float, default=0.0)
    data_hora_registro = Column(DateTime, default=datetime.now)

class ConfiguracaoTaxa(Base):
    __tablename__ = "configuracao_taxas"

    forma_pagamento = Column(SQLEnum(FormaPagamento), primary_key=True)
    percentual = Column(Float, nullable=False, default=0.0)

Base.metadata.create_all(bind=engine)

def inicializar_taxas_padrao():
    db = SessionLocal()
    try:
        if db.query(ConfiguracaoTaxa).count() == 0:
            taxas_iniciais = [
                ConfiguracaoTaxa(forma_pagamento=FormaPagamento.PIX, percentual=0.0),
                ConfiguracaoTaxa(forma_pagamento=FormaPagamento.DINHEIRO, percentual=0.0),
                ConfiguracaoTaxa(forma_pagamento=FormaPagamento.CARTAO_DEBITO, percentual=1.99),
                ConfiguracaoTaxa(forma_pagamento=FormaPagamento.CARTAO_CREDITO, percentual=3.99),
            ]
            db.add_all(taxas_iniciais)
            db.commit()
    finally:
        db.close()

inicializar_taxas_padrao()

# -----------------------------------------------------------------------------
# Schemas
# -----------------------------------------------------------------------------
class NovaMovimentacaoRequest(BaseModel):
    tipo: TipoMovimentacao
    profissional: Optional[str] = "Salão"
    descricao: str
    categoria: str
    forma_pagamento: FormaPagamento
    valor: float = Field(..., gt=0)

class MovimentacaoResponse(BaseModel):
    id: int
    tipo: TipoMovimentacao
    profissional: Optional[str] = "Salão"
    descricao: str
    categoria: str
    forma_pagamento: FormaPagamento
    valor_bruto: float
    taxa_cartao: float
    valor_liquido: float
    data: datetime

    class Config:
        from_attributes = True

class ResumoFechamentoResponse(BaseModel):
    data: date
    total_entradas: float
    total_saidas: float
    total_taxas: float
    saldo_liquido: float

class ItemServicoRelatorio(BaseModel):
    nome: str
    quantidade: int
    percentual: str

class RelatorioConsolidadoResponse(BaseModel):
    faturamento_mensal: float
    total_despesas: float
    saldo_liquido: float
    ticket_medio: float
    taxa_ocupacao: str
    total_atendimentos: int
    servicos_mais_realizados: List[ItemServicoRelatorio]
    faturamento_semanal: List[float]

class TaxaItemSchema(BaseModel):
    forma_pagamento: FormaPagamento
    percentual: float

class AtualizarTaxasRequest(BaseModel):
    taxas: List[TaxaItemSchema]

# -----------------------------------------------------------------------------
# Aplicação FastAPI
# -----------------------------------------------------------------------------
app = FastAPI(title="SR Beauty - Gestão Financeira")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def obter_taxa_percentual(forma: FormaPagamento, db: Session) -> float:
    conf = db.query(ConfiguracaoTaxa).filter(ConfiguracaoTaxa.forma_pagamento == forma).first()
    return conf.percentual if conf else 0.0

@app.get("/api/financeiro/taxas", response_model=List[TaxaItemSchema])
def listar_taxas(db: Session = Depends(get_db)):
    return db.query(ConfiguracaoTaxa).all()

@app.put("/api/financeiro/taxas", response_model=List[TaxaItemSchema])
def atualizar_taxas(payload: AtualizarTaxasRequest, db: Session = Depends(get_db)):
    for item in payload.taxas:
        conf = db.query(ConfiguracaoTaxa).filter(ConfiguracaoTaxa.forma_pagamento == item.forma_pagamento).first()
        if not conf:
            conf = ConfiguracaoTaxa(forma_pagamento=item.forma_pagamento)
        conf.percentual = max(0.0, item.percentual)
        db.add(conf)
    db.commit()
    return db.query(ConfiguracaoTaxa).all()

@app.post("/api/financeiro/movimentacao", response_model=MovimentacaoResponse)
def registrar_movimentacao(payload: NovaMovimentacaoRequest, db: Session = Depends(get_db)):
    taxa_perc = obter_taxa_percentual(payload.forma_pagamento, db)
    
    if payload.tipo == TipoMovimentacao.ENTRADA:
        taxa_cartao = round(payload.valor * (taxa_perc / 100), 2)
        valor_liquido = round(payload.valor - taxa_cartao, 2)
    else:
        taxa_cartao = 0.0
        valor_liquido = payload.valor

    nova_mov = Movimentacao(
        tipo=payload.tipo,
        profissional=payload.profissional or "Salão",
        descricao=payload.descricao,
        categoria=payload.categoria,
        forma_pagamento=payload.forma_pagamento,
        valor_bruto=payload.valor,
        taxa_cartao=taxa_cartao,
        valor_liquido=valor_liquido
    )

    db.add(nova_mov)
    db.commit()
    db.refresh(nova_mov)
    return nova_mov

@app.get("/api/financeiro/movimentacoes", response_model=List[MovimentacaoResponse])
def listar_movimentacoes(db: Session = Depends(get_db)):
    return db.query(Movimentacao).order_by(Movimentacao.data.desc()).all()

@app.post("/api/financeiro/fechamento", response_model=ResumoFechamentoResponse)
def fechar_caixa(data_ref: Optional[date] = None, db: Session = Depends(get_db)):
    alvo = data_ref or date.today()

    movs = db.query(Movimentacao).filter(
        Movimentacao.data >= datetime.combine(alvo, datetime.min.time()),
        Movimentacao.data <= datetime.combine(alvo, datetime.max.time())
    ).all()

    entradas = sum(m.valor_bruto for m in movs if m.tipo == TipoMovimentacao.ENTRADA)
    saidas = sum(m.valor_bruto for m in movs if m.tipo == TipoMovimentacao.SAIDA)
    taxas = sum(m.taxa_cartao for m in movs if m.tipo == TipoMovimentacao.ENTRADA)
    saldo_liquido = round(entradas - saidas - taxas, 2)

    fechamento = db.query(FechamentoCaixa).filter(FechamentoCaixa.data_fechamento == alvo).first()
    if not fechamento:
        fechamento = FechamentoCaixa(data_fechamento=alvo)

    fechamento.total_entradas = entradas
    fechamento.total_saidas = saidas
    fechamento.total_taxas = taxas
    fechamento.saldo_liquido = saldo_liquido

    db.add(fechamento)
    db.commit()

    return ResumoFechamentoResponse(
        data=alvo,
        total_entradas=entradas,
        total_saidas=saidas,
        total_taxas=taxas,
        saldo_liquido=saldo_liquido
    )

@app.get("/api/relatorios/consolidado", response_model=RelatorioConsolidadoResponse)
def obter_relatorio_consolidado(
    mes: int = Query(default=datetime.now().month, ge=1, le=12),
    ano: int = Query(default=datetime.now().year),
    db: Session = Depends(get_db)
):
    entradas = db.query(Movimentacao).filter(
        Movimentacao.tipo == TipoMovimentacao.ENTRADA,
        Movimentacao.data >= datetime(ano, mes, 1)
    ).all()

    saidas = db.query(Movimentacao).filter(
        Movimentacao.tipo == TipoMovimentacao.SAIDA,
        Movimentacao.data >= datetime(ano, mes, 1)
    ).all()

    total_faturamento = sum(m.valor_bruto for m in entradas)
    total_despesas = sum(m.valor_bruto for m in saidas)
    total_taxas = sum(m.taxa_cartao for m in entradas)
    saldo_liquido = round(total_faturamento - total_despesas - total_taxas, 2)

    total_atendimentos = len(entradas)
    ticket_medio = round(total_faturamento / total_atendimentos, 2) if total_atendimentos > 0 else 0.0

    capacidade_mensal = 176
    taxa_ocupacao_perc = min(round((total_atendimentos / capacidade_mensal) * 100, 1), 100.0)

    semanas = [0.0, 0.0, 0.0, 0.0]
    for m in entradas:
        dia = m.data.day
        if dia <= 7: semanas[0] += m.valor_bruto
        elif dia <= 14: semanas[1] += m.valor_bruto
        elif dia <= 21: semanas[2] += m.valor_bruto
        else: semanas[3] += m.valor_bruto

    contagem = Counter([m.categoria for m in entradas])
    servicos_mais_realizados = []
    for nome_servico, qtd in contagem.most_common(4):
        perc = round((qtd / total_atendimentos) * 100, 1) if total_atendimentos > 0 else 0
        servicos_mais_realizados.append(
            ItemServicoRelatorio(
                nome=nome_servico,
                quantidade=qtd,
                percentual=f"{perc}%"
            )
        )

    return RelatorioConsolidadoResponse(
        faturamento_mensal=total_faturamento,
        total_despesas=total_despesas,
        saldo_liquido=saldo_liquido,
        ticket_medio=ticket_medio,
        taxa_ocupacao=f"{taxa_ocupacao_perc}%",
        total_atendimentos=total_atendimentos,
        servicos_mais_realizados=servicos_mais_realizados,
        faturamento_semanal=semanas
    )

@app.get("/api/relatorios/exportar-pdf")
def exportar_relatorio_pdf(
    mes: int = Query(default=datetime.now().month, ge=1, le=12),
    ano: int = Query(default=datetime.now().year),
    db: Session = Depends(get_db)
):
    entradas = db.query(Movimentacao).filter(
        Movimentacao.tipo == TipoMovimentacao.ENTRADA,
        Movimentacao.data >= datetime(ano, mes, 1)
    ).all()

    saidas = db.query(Movimentacao).filter(
        Movimentacao.tipo == TipoMovimentacao.SAIDA,
        Movimentacao.data >= datetime(ano, mes, 1)
    ).all()

    total_faturamento = sum(m.valor_bruto for m in entradas)
    total_despesas = sum(m.valor_bruto for m in saidas)
    total_taxas = sum(m.taxa_cartao for m in entradas)
    saldo_liquido = round(total_faturamento - total_despesas - total_taxas, 2)
    total_atendimentos = len(entradas)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor("#8C4A5A"))
    subtitle_style = ParagraphStyle('SubTitleStyle', parent=styles['Normal'], fontSize=10, textColor=colors.gray)

    # Estilo de célula para quebra automática de linha na descrição
    cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#343434")
    )

    elements.append(Paragraph("SR Beauty — Relatório Gerencial Financeiro", title_style))
    elements.append(Paragraph(f"Referência: {mes:02d}/{ano} — Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", subtitle_style))
    elements.append(Spacer(1, 15))

    data_resumo = [
        ["Indicador", "Valor"],
        ["Faturamento Mensal (+)", f"R$ {total_faturamento:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')],
        ["Despesas do Mês (-)", f"R$ {total_despesas:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')],
        ["Taxas de Cartão (-)", f"R$ {total_taxas:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')],
        ["Saldo Líquido (=)", f"R$ {saldo_liquido:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')],
        ["Atendimentos Realizados", str(total_atendimentos)]
    ]
    t_resumo = Table(data_resumo, colWidths=[250, 200])
    t_resumo.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#8C4A5A")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E5E2DE")),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t_resumo)
    elements.append(Spacer(1, 15))

    elements.append(Paragraph("<b>Recebimentos (Entradas)</b>", styles['Heading2']))
    elements.append(Spacer(1, 6))

    data_entradas = [["Data", "Profissional", "Descrição", "Categoria", "Forma", "Valor Líquido"]]
    for m in entradas:
        data_entradas.append([
            m.data.strftime("%d/%m/%Y"),
            m.profissional or "Salão",
            Paragraph(m.descricao, cell_style),
            m.categoria,
            m.forma_pagamento.value.upper(),
            f"R$ {m.valor_liquido:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        ])
    if not entradas:
        data_entradas.append(["-", "-", "Sem entradas no período", "-", "-", "R$ 0,00"])

    t_entradas = Table(data_entradas, colWidths=[65, 85, 130, 85, 75, 80])
    t_entradas.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#8FA89A")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E5E2DE")),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    elements.append(t_entradas)
    elements.append(Spacer(1, 15))

    elements.append(Paragraph("<b>Despesas (Saídas)</b>", styles['Heading2']))
    elements.append(Spacer(1, 6))

    data_saidas = [["Data", "Profissional", "Descrição", "Categoria", "Forma", "Valor"]]
    for m in saidas:
        data_saidas.append([
            m.data.strftime("%d/%m/%Y"),
            m.profissional or "Salão",
            Paragraph(m.descricao, cell_style),
            m.categoria,
            m.forma_pagamento.value.upper(),
            f"R$ {m.valor_bruto:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        ])
    if not saidas:
        data_saidas.append(["-", "-", "Sem despesas registradas", "-", "-", "R$ 0,00"])

    t_saidas = Table(data_saidas, colWidths=[65, 85, 130, 85, 75, 80])
    t_saidas.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#A44848")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E5E2DE")),
        ('PADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    elements.append(t_saidas)

    doc.build(elements)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=Relatorio_SRBeauty_{mes:02d}_{ano}.pdf"}
    )