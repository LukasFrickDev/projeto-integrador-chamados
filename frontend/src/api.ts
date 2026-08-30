import type { Chamado } from './types'

const mensagemErroPadrao = 'Não foi possível carregar os chamados.'

export async function buscarChamados(identificador: string, signal?: AbortSignal) {
  const response = await fetch('/api/chamados/', {
    headers: {
      'X-Demo-User': identificador,
    },
    signal,
  })

  if (!response.ok) {
    const dados = await response.json().catch(() => null)
    const mensagem =
      dados && typeof dados.detail === 'string' ? dados.detail : mensagemErroPadrao
    throw new Error(mensagem)
  }

  return (await response.json()) as Chamado[]
}
