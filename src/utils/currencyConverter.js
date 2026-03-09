/**
 * Utilitário de Conversão de Moedas - Cert-Manager
 * Consome a AwesomeAPI para cotação em tempo real.
 */

const BASE_URL = "https://economia.awesomeapi.com.br/json/last/USD-BRL";

export const currencyConverter = {
  /**
   * Busca a cotação atual do Dólar Comercial (bid)
   * @returns {Promise<number>} Valor do dólar em float
   */
  async getLatestRate() {
    try {
      const response = await fetch(BASE_URL);
      const data = await response.json();
      // 'bid' é o preço de compra, o mais comum para cálculos de conversão
      return parseFloat(data.USDBRL.bid);
    } catch (error) {
      console.error("Erro ao obter cotação do dólar:", error);
      return 0;
    }
  },

  /**
   * Converte um valor em Dólar para Real com base na cotação atual
   * @param {number} usdAmount - Valor da prova em dólares (ex: 99)
   * @returns {Promise<string>} Valor formatado em BRL (R$)
   */
  async convertToBRL(usdAmount) {
    const rate = await this.getLatestRate();
    if (rate === 0) return "Erro na cotação";
    
    const total = usdAmount * rate;
    
    // Retorna formatado para a moeda brasileira
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(total);
  }
};