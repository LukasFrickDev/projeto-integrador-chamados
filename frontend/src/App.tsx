import { useEffect, useState } from 'react'

import { buscarChamados } from './api'
import './App.css'
import type { Chamado, Perfil, StatusChamado } from './types'

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

function App() {
  const [perfilAtivo, setPerfilAtivo] = useState(perfis[0])
  const [tentativa, setTentativa] = useState(0)
  const [chamados, setChamados] = useState<Chamado[]>([])
  const [carregando, setCarregando] = useState(true)
  const [erro, setErro] = useState<string | null>(null)

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

  const tituloLista = perfilAtivo.tipo === 'SOLICITANTE' ? 'Meus chamados' : 'Chamados'
  const mensagemListaVazia =
    perfilAtivo.tipo === 'SOLICITANTE'
      ? 'Você ainda não possui chamados registrados.'
      : 'Não há chamados registrados.'

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
                className={perfil.identificador === perfilAtivo.identificador ? 'active' : ''}
                key={perfil.identificador}
                onClick={() => setPerfilAtivo(perfil)}
                type="button"
              >
                <strong>{perfil.nome}</strong>
                <span>{perfil.tipo === 'SOLICITANTE' ? 'Solicitante' : 'Manutenção'}</span>
              </button>
            ))}
          </div>
        </div>
      </header>

      <main className="content">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Visão atual</p>
            <h2>{tituloLista}</h2>
          </div>
          <span className="profile-context">{perfilAtivo.nome}</span>
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
          <div className="ticket-list">
            {chamados.map((chamado) => (
              <article className="ticket-card" key={chamado.id}>
                <div className="ticket-card-header">
                  <span className="ticket-id">Chamado #{chamado.id}</span>
                  <span className={`status status-${chamado.status.toLowerCase()}`}>
                    {nomesStatus[chamado.status]}
                  </span>
                </div>
                <h3>{chamado.titulo}</h3>
                <p className="ticket-location">{chamado.local}</p>
              </article>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}

export default App
