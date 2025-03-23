export function formatarMoeda(valor: number | null | undefined): string {
  if (valor === null || valor === undefined) return "R$ 0,00";
  return valor.toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
    minimumFractionDigits: 2
  });
}

export function formatarData(data: string | null | undefined): string {
  if (!data) return "-";
  return new Date(data).toLocaleDateString("pt-BR");
}

export function formatarDataHora(data: string | null | undefined): string {
  if (!data) return "-";
  return new Date(data).toLocaleString("pt-BR");
} 