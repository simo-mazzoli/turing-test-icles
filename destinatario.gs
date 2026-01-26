const SHEET_ID = "1ycb4ujnnto4kGmMD-A_ulL9qS6qc8uc4TvBOLuGFoa4"; 

function doGet() {
  return HtmlService.createHtmlOutputFromFile("Destinatario");
}

function getUltimaDomanda() {
  const sh = SpreadsheetApp.openById(SHEET_ID).getActiveSheet();
  const lastRow = sh.getLastRow();
  const data = sh.getRange(lastRow, 1, 1, 5).getValues()[0];
  return { domanda: data[0], riga: lastRow };
}

function salvaRisposta(riga, risposta) {
  const sh = SpreadsheetApp.openById(SHEET_ID).getActiveSheet();
  sh.getRange(riga, 2).setValue(risposta);
}
