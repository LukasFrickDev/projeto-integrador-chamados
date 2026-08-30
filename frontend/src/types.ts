export type TipoPerfil = 'SOLICITANTE' | 'MANUTENCAO'

export type StatusChamado = 'ABERTO' | 'EM_ANDAMENTO' | 'CONCLUIDO'

export type Perfil = {
  identificador: string
  nome: string
  tipo: TipoPerfil
}

export type Chamado = {
  id: number
  titulo: string
  descricao: string
  local: string
  solicitante: Perfil
  responsavel: Perfil | null
  status: StatusChamado
  criado_em: string
  historico: unknown[]
}
