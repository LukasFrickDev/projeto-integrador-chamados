import { useEffect, useRef, useState } from 'react'

import {
  buscarChamado,
  buscarChamados,
  criarChamado,
  concluirChamado,
  iniciarChamado,
  registrarAtualizacao,
} from './api'
import './App.css'
import type {
  Chamado,
  DadosCriacaoChamado,
  HistoricoChamado,
  Perfil,
  StatusChamado,
  TipoEventoHistorico,
} from './types'

const perfis: Perfil[] = [
  {
    identificador: 'mariana',
    nome: 'Mariana Ribeiro',
    tipo: 'SOLICITANTE',
  },
  {
    identificador: 'rafael',
    nome: 'Rafael Martins',
    tipo: 'MANUTENCAO',
  },
]

const nomesStatus: Record<StatusChamado, string> = {
  ABERTO: 'Aberto',
  EM_ANDAMENTO: 'Em andamento',
  CONCLUIDO: 'Concluído',
}

const opcoesStatus: Array<{ valor: FiltroStatus; nome: string }> = [
  { valor: 'TODOS', nome: 'Todos os status' },
  { valor: 'ABERTO', nome: 'Aberto' },
  { valor: 'EM_ANDAMENTO', nome: 'Em andamento' },
  { valor: 'CONCLUIDO', nome: 'Concluído' },
]

const nomesEventos: Record<TipoEventoHistorico, string> = {
  CRIACAO: 'Criação do chamado',
  INICIO: 'Atendimento iniciado',
  ATUALIZACAO: 'Atualização',
  CONCLUSAO: 'Chamado concluído',
}

const formularioInicial: DadosCriacaoChamado = {
  titulo: '',
  local: '',
  descricao: '',
}

type Tela = 'lista' | 'novo' | 'detalhe'
type AcaoManutencao = 'iniciar' | 'atualizar' | 'concluir' | null
type FiltroStatus = 'TODOS' | StatusChamado

function formatarData(data: string) {
  return new Intl.DateTimeFormat('pt-BR', {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(new Date(data))
}

function App() {
  const [perfilAtivo, setPerfilAtivo] = useState(perfis[0])
  const [tentativa, setTentativa] = useState(0)
  const [tela, setTela] = useState<Tela>('lista')
  const [chamadoSelecionadoId, setChamadoSelecionadoId] = useState<number | null>(null)
  const [chamados, setChamados] = useState<Chamado[]>([])
  const [carregando, setCarregando] = useState(true)
  const [erro, setErro] = useState<string | null>(null)
  const [detalhe, setDetalhe] = useState<Chamado | null>(null)
  const [carregandoDetalhe, setCarregandoDetalhe] = useState(false)
  const [erroDetalhe, setErroDetalhe] = useState<string | null>(null)
  const [tentativaDetalhe, setTentativaDetalhe] = useState(0)
  const [formulario, setFormulario] = useState(formularioInicial)
  const [salvando, setSalvando] = useState(false)
  const [erroFormulario, setErroFormulario] = useState<string | null>(null)
  const [acaoEmAndamento, setAcaoEmAndamento] = useState<AcaoManutencao>(null)
  const [informacaoAtualizacao, setInformacaoAtualizacao] = useState('')
  const [erroAcao, setErroAcao] = useState<string | null>(null)
  const [busca, setBusca] = useState('')
  const [filtroStatus, setFiltroStatus] = useState<FiltroStatus>('TODOS')
  const [statusMenuAberto, setStatusMenuAberto] = useState(false)
  const filtroStatusRef = useRef<HTMLDivElement>(null)
  const filtroStatusBotaoRef = useRef<HTMLButtonElement>(null)
  const opcoesStatusRefs = useRef<Array<HTMLButtonElement | null>>([])

  useEffect(() => {
    const controller = new AbortController()

    async function carregarChamados() {
      setCarregando(true)
      setErro(null)

      try {
        const dados = await buscarChamados(perfilAtivo.identificador, controller.signal)
        setChamados(dados)
      } catch (error) {
        if (controller.signal.aborted) {
          return
        }
        setErro(error instanceof Error ? error.message : 'Não foi possível carregar os chamados.')
      } finally {
        if (!controller.signal.aborted) {
          setCarregando(false)
        }
      }
    }

    void carregarChamados()

    return () => controller.abort()
  }, [perfilAtivo, tentativa])

  useEffect(() => {
    if (tela !== 'detalhe' || chamadoSelecionadoId === null) {
      return
    }

    const id = chamadoSelecionadoId
    const controller = new AbortController()

    async function carregarDetalhe() {
      setCarregandoDetalhe(true)
      setErroDetalhe(null)

      try {
        const dados = await buscarChamado(
          perfilAtivo.identificador,
          id,
          controller.signal,
        )
        setDetalhe(dados)
      } catch (error) {
        if (controller.signal.aborted) {
          return
        }
        setDetalhe(null)
        setErroDetalhe(error instanceof Error ? error.message : 'Não foi possível carregar o chamado.')
      } finally {
        if (!controller.signal.aborted) {
          setCarregandoDetalhe(false)
        }
      }
    }

    void carregarDetalhe()

    return () => controller.abort()
  }, [chamadoSelecionadoId, perfilAtivo, tela, tentativaDetalhe])

  useEffect(() => {
    if (!statusMenuAberto) {
      return
    }

    const indiceSelecionado = opcoesStatus.findIndex((opcao) => opcao.valor === filtroStatus)
    opcoesStatusRefs.current[indiceSelecionado >= 0 ? indiceSelecionado : 0]?.focus()

    function fecharAoClicarFora(event: MouseEvent) {
      if (!filtroStatusRef.current?.contains(event.target as Node)) {
        setStatusMenuAberto(false)
      }
    }

    document.addEventListener('mousedown', fecharAoClicarFora)
    return () => document.removeEventListener('mousedown', fecharAoClicarFora)
  }, [filtroStatus, statusMenuAberto])

  function selecionarPerfil(perfil: Perfil) {
    setPerfilAtivo(perfil)
    setFormulario(formularioInicial)
    setErroFormulario(null)
    voltarParaLista()
  }

  function voltarParaLista() {
    setTela('lista')
    setChamadoSelecionadoId(null)
    setDetalhe(null)
    setErroDetalhe(null)
    setBusca('')
    setFiltroStatus('TODOS')
    setAcaoEmAndamento(null)
    setInformacaoAtualizacao('')
    setErroAcao(null)
  }

  function abrirDetalhe(id: number) {
    setChamadoSelecionadoId(id)
    setTela('detalhe')
  }

  function abrirFormulario() {
    setFormulario(formularioInicial)
    setErroFormulario(null)
    setTela('novo')
  }

  function atualizarCampo(campo: keyof DadosCriacaoChamado, valor: string) {
    setFormulario((atual) => ({ ...atual, [campo]: valor }))
  }

  async function enviarFormulario(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const camposVazios = Object.values(formulario).some((valor) => !valor.trim())
    if (camposVazios) {
      setErroFormulario('Preencha título, local e descrição para criar o chamado.')
      return
    }

    setSalvando(true)
    setErroFormulario(null)

    try {
      await criarChamado(perfilAtivo.identificador, formulario)
      setFormulario(formularioInicial)
      voltarParaLista()
      setTentativa((valor) => valor + 1)
    } catch (error) {
      setErroFormulario(error instanceof Error ? error.message : 'Não foi possível criar o chamado.')
    } finally {
      setSalvando(false)
    }
  }

  async function executarInicio() {
    if (!detalhe) {
      return
    }

    setAcaoEmAndamento('iniciar')
    setErroAcao(null)
    try {
      const chamadoAtualizado = await iniciarChamado(perfilAtivo.identificador, detalhe.id)
      setDetalhe(chamadoAtualizado)
      setTentativa((valor) => valor + 1)
    } catch (error) {
      setErroAcao(error instanceof Error ? error.message : 'Não foi possível iniciar o atendimento.')
    } finally {
      setAcaoEmAndamento(null)
    }
  }

  async function executarAtualizacao() {
    if (!detalhe) {
      return
    }
    if (!informacaoAtualizacao.trim()) {
      setErroAcao('Informe o texto da atualização.')
      return
    }

    setAcaoEmAndamento('atualizar')
    setErroAcao(null)
    try {
      const chamadoAtualizado = await registrarAtualizacao(
        perfilAtivo.identificador,
        detalhe.id,
        informacaoAtualizacao,
      )
      setDetalhe(chamadoAtualizado)
      setInformacaoAtualizacao('')
      setTentativa((valor) => valor + 1)
    } catch (error) {
      setErroAcao(error instanceof Error ? error.message : 'Não foi possível registrar a atualização.')
    } finally {
      setAcaoEmAndamento(null)
    }
  }

  async function executarConclusao() {
    if (!detalhe) {
      return
    }

    setAcaoEmAndamento('concluir')
    setErroAcao(null)
    try {
      const chamadoAtualizado = await concluirChamado(perfilAtivo.identificador, detalhe.id)
      setDetalhe(chamadoAtualizado)
      setTentativa((valor) => valor + 1)
    } catch (error) {
      setErroAcao(error instanceof Error ? error.message : 'Não foi possível concluir o chamado.')
    } finally {
      setAcaoEmAndamento(null)
    }
  }

  const tituloLista = perfilAtivo.tipo === 'SOLICITANTE' ? 'Meus chamados' : 'Chamados'
  const mensagemListaVazia =
    perfilAtivo.tipo === 'SOLICITANTE'
      ? 'Você ainda não possui chamados registrados.'
      : 'Não há chamados registrados.'
  const termoBusca = busca.trim().toLowerCase()
  const chamadosFiltrados = chamados.filter((chamado) => {
    const correspondeBusca =
      chamado.titulo.toLowerCase().includes(termoBusca) ||
      chamado.local.toLowerCase().includes(termoBusca)
    const correspondeStatus = filtroStatus === 'TODOS' || chamado.status === filtroStatus
    return correspondeBusca && correspondeStatus
  })

  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <p className="eyebrow">Prova de conceito</p>
          <h1>Chamados de Manutenção</h1>
          <p>Registro e acompanhamento de chamados.</p>
        </div>

        <div className="profile-switcher" aria-label="Perfil de demonstração">
          <span className="profile-label">Acessar como</span>
          <div className="profile-options">
            {perfis.map((perfil) => (
              <button
                aria-pressed={perfil.identificador === perfilAtivo.identificador}
                className={perfil.identificador === perfilAtivo.identificador ? 'active' : ''}
                key={perfil.identificador}
                onClick={() => selecionarPerfil(perfil)}
                type="button"
              >
                <strong>{perfil.nome}</strong>
                <span>{perfil.tipo === 'SOLICITANTE' ? 'Solicitante' : 'Manutenção'}</span>
              </button>
            ))}
          </div>
        </div>
      </header>

      {tela === 'lista' && (
        <main className="content">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Visão atual</p>
              <h2>{tituloLista}</h2>
            </div>
            {perfilAtivo.tipo === 'SOLICITANTE' && (
              <button className="primary-button" onClick={abrirFormulario} type="button">
                Novo chamado
              </button>
            )}
          </div>

          {carregando && <p className="feedback">Carregando chamados...</p>}

          {!carregando && erro && (
            <div className="feedback feedback-error" role="alert">
              <p>{erro}</p>
              <button type="button" onClick={() => setTentativa((valor) => valor + 1)}>
                Tentar novamente
              </button>
            </div>
          )}

          {!carregando && !erro && chamados.length === 0 && (
            <p className="feedback">{mensagemListaVazia}</p>
          )}

          {!carregando && !erro && chamados.length > 0 && (
            <div className="list-filters">
              <label>
                Buscar por título ou local
                <input
                  onChange={(event) => setBusca(event.target.value)}
                  type="search"
                  value={busca}
                />
              </label>
              <div className="status-filter-field">
                <label id="filtro-status-label" htmlFor="filtro-status-controle">
                  Filtrar por status
                </label>
                <div className="status-dropdown" ref={filtroStatusRef}>
                  <button
                    aria-controls="filtro-status-opcoes"
                    aria-expanded={statusMenuAberto}
                    aria-haspopup="listbox"
                    className="status-dropdown-trigger"
                    id="filtro-status-controle"
                    onClick={() => setStatusMenuAberto((aberto) => !aberto)}
                    onKeyDown={(event) => {
                      if (event.key === 'Escape') {
                        event.preventDefault()
                        setStatusMenuAberto(false)
                        filtroStatusBotaoRef.current?.focus()
                      }
                      if (event.key === 'ArrowDown' && !statusMenuAberto) {
                        event.preventDefault()
                        setStatusMenuAberto(true)
                      }
                      if ((event.key === 'Enter' || event.key === ' ') && statusMenuAberto) {
                        event.preventDefault()
                      }
                    }}
                    ref={filtroStatusBotaoRef}
                    type="button"
                  >
                    {opcoesStatus.find((opcao) => opcao.valor === filtroStatus)?.nome}
                    <span aria-hidden="true">⌄</span>
                  </button>
                  {statusMenuAberto && (
                    <div className="status-dropdown-menu" id="filtro-status-opcoes" role="listbox">
                      {opcoesStatus.map((opcao) => (
                        <button
                          aria-selected={opcao.valor === filtroStatus}
                          className={opcao.valor === filtroStatus ? 'selected' : ''}
                          key={opcao.valor}
                          onClick={() => {
                            setFiltroStatus(opcao.valor)
                            setStatusMenuAberto(false)
                            filtroStatusBotaoRef.current?.focus()
                          }}
                          onKeyDown={(event) => {
                            const indiceAtual = opcoesStatus.findIndex((item) => item.valor === opcao.valor)
                            if (event.key === 'Escape') {
                              event.preventDefault()
                              setStatusMenuAberto(false)
                              filtroStatusBotaoRef.current?.focus()
                            }
                            if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
                              event.preventDefault()
                              const deslocamento = event.key === 'ArrowDown' ? 1 : -1
                              const proximoIndice = (indiceAtual + deslocamento + opcoesStatus.length) % opcoesStatus.length
                              opcoesStatusRefs.current[proximoIndice]?.focus()
                            }
                            if (event.key === 'Home' || event.key === 'End') {
                              event.preventDefault()
                              const indiceDestino = event.key === 'Home' ? 0 : opcoesStatus.length - 1
                              opcoesStatusRefs.current[indiceDestino]?.focus()
                            }
                            if (event.key === 'Enter' || event.key === ' ') {
                              event.preventDefault()
                              setFiltroStatus(opcao.valor)
                              setStatusMenuAberto(false)
                              filtroStatusBotaoRef.current?.focus()
                            }
                          }}
                          role="option"
                          ref={(element) => {
                            opcoesStatusRefs.current[opcoesStatus.findIndex((item) => item.valor === opcao.valor)] = element
                          }}
                          type="button"
                        >
                          {opcao.nome}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {!carregando && !erro && chamados.length > 0 && chamadosFiltrados.length === 0 && (
            <p className="feedback">Nenhum chamado encontrado com os filtros selecionados.</p>
          )}

          {!carregando && !erro && chamadosFiltrados.length > 0 && (
            <div className="ticket-list">
              {chamadosFiltrados.map((chamado) => (
                <article className="ticket-card" key={chamado.id}>
                  <div className="ticket-card-header">
                    <span className="ticket-id">Chamado #{chamado.id}</span>
                    <span className={`status status-${chamado.status.toLowerCase()}`}>
                      {nomesStatus[chamado.status]}
                    </span>
                  </div>
                  <h3>{chamado.titulo}</h3>
                  <p className="ticket-location">{chamado.local}</p>
                  <button className="details-button" onClick={() => abrirDetalhe(chamado.id)} type="button">
                    Ver detalhes
                  </button>
                </article>
              ))}
            </div>
          )}
        </main>
      )}

      {tela === 'novo' && perfilAtivo.tipo === 'SOLICITANTE' && (
        <main className="content narrow-content">
          <button className="back-button" onClick={voltarParaLista} type="button">
            ← Voltar para chamados
          </button>
          <div className="page-heading">
            <p className="eyebrow">Novo registro</p>
            <h2>Novo chamado</h2>
            <p>Descreva o problema para que a manutenção possa atendê-lo.</p>
          </div>

          <form className="ticket-form" onSubmit={enviarFormulario}>
            <label>
              Título
              <input
                onChange={(event) => atualizarCampo('titulo', event.target.value)}
                required
                value={formulario.titulo}
              />
            </label>
            <label>
              Local
              <input
                onChange={(event) => atualizarCampo('local', event.target.value)}
                required
                value={formulario.local}
              />
            </label>
            <label>
              Descrição
              <textarea
                onChange={(event) => atualizarCampo('descricao', event.target.value)}
                required
                rows={5}
                value={formulario.descricao}
              />
            </label>

            {erroFormulario && <p className="form-error" role="alert">{erroFormulario}</p>}

            <div className="form-actions">
              <button className="secondary-button" onClick={voltarParaLista} type="button">
                Cancelar
              </button>
              <button className="primary-button" disabled={salvando} type="submit">
                {salvando ? 'Salvando...' : 'Criar chamado'}
              </button>
            </div>
          </form>
        </main>
      )}

      {tela === 'detalhe' && (
        <main className="content">
          <button className="back-button" onClick={voltarParaLista} type="button">
            ← Voltar para chamados
          </button>

          {carregandoDetalhe && <p className="feedback">Carregando chamado...</p>}

          {!carregandoDetalhe && erroDetalhe && (
            <div className="feedback feedback-error" role="alert">
              <p>{erroDetalhe}</p>
              <button type="button" onClick={() => setTentativaDetalhe((valor) => valor + 1)}>
                Tentar novamente
              </button>
            </div>
          )}

          {!carregandoDetalhe && !erroDetalhe && detalhe && (
            <DetalheChamado
              acaoEmAndamento={acaoEmAndamento}
              chamado={detalhe}
              erroAcao={erroAcao}
              informacaoAtualizacao={informacaoAtualizacao}
              onConcluir={executarConclusao}
              onIniciar={executarInicio}
              onInformacaoAtualizacao={setInformacaoAtualizacao}
              onRegistrarAtualizacao={executarAtualizacao}
              perfil={perfilAtivo}
            />
          )}
        </main>
      )}
    </div>
  )
}

type DetalheChamadoProps = {
  acaoEmAndamento: AcaoManutencao
  chamado: Chamado
  erroAcao: string | null
  informacaoAtualizacao: string
  onConcluir: () => void
  onIniciar: () => void
  onInformacaoAtualizacao: (valor: string) => void
  onRegistrarAtualizacao: () => void
  perfil: Perfil
}

function DetalheChamado({
  acaoEmAndamento,
  chamado,
  erroAcao,
  informacaoAtualizacao,
  onConcluir,
  onIniciar,
  onInformacaoAtualizacao,
  onRegistrarAtualizacao,
  perfil,
}: DetalheChamadoProps) {
  const podeExibirAcoes =
    perfil.tipo === 'MANUTENCAO' &&
    (chamado.status === 'ABERTO' ||
      (chamado.status === 'EM_ANDAMENTO' &&
        chamado.responsavel?.identificador === perfil.identificador))

  return (
    <div className="detail-layout">
      <div className="page-heading">
        <p className="eyebrow">Chamado #{chamado.id}</p>
        <div className="detail-title-row">
          <h2>{chamado.titulo}</h2>
          <span className={`status status-${chamado.status.toLowerCase()}`}>
            {nomesStatus[chamado.status]}
          </span>
                </div>
              </div>

      <section className="detail-card" aria-labelledby="informacoes-chamado">
        <h3 id="informacoes-chamado">Informações do chamado</h3>
        <dl className="detail-grid">
          <div>
            <dt>Local</dt>
            <dd>{chamado.local}</dd>
          </div>
          <div>
            <dt>Solicitante</dt>
            <dd>{chamado.solicitante.nome}</dd>
          </div>
          <div>
            <dt>Responsável</dt>
            <dd>{chamado.responsavel?.nome ?? 'Ainda não definido'}</dd>
          </div>
          <div>
            <dt>Criado em</dt>
            <dd>{formatarData(chamado.criado_em)}</dd>
          </div>
          <div className="description-block">
            <dt>Descrição</dt>
            <dd>{chamado.descricao}</dd>
          </div>
        </dl>
      </section>

      {podeExibirAcoes && (
        <section className="detail-card maintenance-actions" aria-labelledby="acoes-atendimento">
          <h3 id="acoes-atendimento">Ações de atendimento</h3>
          {erroAcao && <p className="action-error" role="alert">{erroAcao}</p>}

          {chamado.status === 'ABERTO' && (
            <button
              className="primary-button"
              disabled={acaoEmAndamento !== null}
              onClick={onIniciar}
              type="button"
            >
              {acaoEmAndamento === 'iniciar' ? 'Iniciando...' : 'Iniciar atendimento'}
            </button>
          )}

          {chamado.status === 'EM_ANDAMENTO' && chamado.responsavel?.identificador === perfil.identificador && (
            <>
              <label className="update-field">
                Atualização do atendimento
                <textarea
                  disabled={acaoEmAndamento !== null}
                  onChange={(event) => onInformacaoAtualizacao(event.target.value)}
                  rows={4}
                  value={informacaoAtualizacao}
                />
              </label>
              <div className="action-buttons">
                <button
                  className="secondary-button"
                  disabled={acaoEmAndamento !== null}
                  onClick={onRegistrarAtualizacao}
                  type="button"
                >
                  {acaoEmAndamento === 'atualizar' ? 'Registrando...' : 'Registrar atualização'}
                </button>
                <button
                  className="primary-button"
                  disabled={acaoEmAndamento !== null}
                  onClick={onConcluir}
                  type="button"
                >
                  {acaoEmAndamento === 'concluir' ? 'Concluindo...' : 'Concluir chamado'}
                </button>
              </div>
            </>
          )}
        </section>
      )}

      <section className="detail-card" aria-labelledby="historico-chamado">
        <h3 id="historico-chamado">Histórico</h3>
        <div className="history-list">
          {chamado.historico.map((evento: HistoricoChamado) => (
            <article className="history-item" key={evento.id}>
              <div className="history-marker" aria-hidden="true" />
              <div className="history-content">
                <div className="history-heading">
                  <h4>{nomesEventos[evento.tipo_evento]}</h4>
                  <time dateTime={evento.criado_em}>{formatarData(evento.criado_em)}</time>
                </div>
                <p className="history-author">Por {evento.autor.nome}</p>
                {evento.informacao && <p className="history-info">{evento.informacao}</p>}
              </div>
            </article>
          ))}
        </div>
      </section>
    </div>
  )
}

export default App
