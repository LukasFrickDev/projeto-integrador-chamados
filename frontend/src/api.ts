import type { Chamado, DadosCriacaoChamado } from './types'

const mensagemErroPadrao = 'Não foi possível carregar os chamados.'

async function obterMensagemErro(response: Response, mensagemPadrao: string) {
  const dados = await response.json().catch(() => null)
  if (dados && typeof dados.detail === 'string') {
    return dados.detail
  }

  if (dados && typeof dados === 'object') {
    const primeiraMensagem = Object.values(dados).flat()[0]
    if (typeof primeiraMensagem === 'string') {
      return primeiraMensagem
    }
  }

  return mensagemPadrao
}

async function verificarResposta(response: Response, mensagemPadrao: string) {
  if (!response.ok) {
    throw new Error(await obterMensagemErro(response, mensagemPadrao))
  }
}

export async function buscarChamados(identificador: string, signal?: AbortSignal) {
  const response = await fetch('/api/chamados/', {
    headers: {
      'X-Demo-User': identificador,
    },
    signal,
  })
  await verificarResposta(response, mensagemErroPadrao)
  return (await response.json()) as Chamado[]
}

export async function buscarChamado(
  identificador: string,
  id: number,
  signal?: AbortSignal,
) {
  const response = await fetch(`/api/chamados/${id}/`, {
    headers: {
      'X-Demo-User': identificador,
    },
    signal,
  })
  await verificarResposta(response, 'Não foi possível carregar o chamado.')
  return (await response.json()) as Chamado
}

export async function criarChamado(
  identificador: string,
  dados: DadosCriacaoChamado,
) {
  const response = await fetch('/api/chamados/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Demo-User': identificador,
    },
    body: JSON.stringify(dados),
  })
  await verificarResposta(response, 'Não foi possível criar o chamado.')
}
