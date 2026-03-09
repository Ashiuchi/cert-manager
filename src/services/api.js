// Exemplo de função para buscar o dólar comercial
async function getDollarRate() {
  try {
    const response = await fetch('https://economia.awesomeapi.com.br/json/last/USD-BRL');
    const data = await response.json();
    const rate = parseFloat(data.USDBRL.bid);
    return rate; // Ex: 5.12
  } catch (error) {
    console.error("Erro ao buscar cotação:", error);
    return null;
  }
}