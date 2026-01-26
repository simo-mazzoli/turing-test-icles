const SHEET_ID = "1ycb4ujnnto4kGmMD-A_ulL9qS6qc8uc4TvBOLuGFoa4"; 
const API_KEY = "AIzaSyDdwXEIwDURNLqMhg5qVQH7xhqKXAUksTQ";

function doGet() {
  return HtmlService.createHtmlOutputFromFile("Giocatore");
}

function salvaDomanda(domanda, giocatoreId) {
  const sh = SpreadsheetApp.openById(SHEET_ID).getActiveSheet();
  const row = sh.appendRow([domanda, "", "", giocatoreId, "in_attesa"]);
  return sh.getLastRow();
}

function getRisposte(riga) {
  const sh = SpreadsheetApp.openById(SHEET_ID).getActiveSheet();
  const data = sh.getRange(riga, 1, 1, 5).getValues()[0];
  return {
    domanda: data[0],
    rispostaDestinatario: data[1],
    rispostaAI: data[2]
  };
}

function chiamaGemini(domanda, riga) {
  if (!riga) {
    console.log("Riga non valida. Gemini non viene chiamato.");
    return null;
  }

  const sh = SpreadsheetApp.openById(SHEET_ID).getActiveSheet();
  const rispostaDestinatario = sh.getRange(riga, 2).getValue(); // colonna B

  if (!rispostaDestinatario) {
    console.log("La risposta del destinatario non è ancora presente. Gemini non viene chiamato.");
    return null;
  }

  const lunghezza = rispostaDestinatario.length;

  const url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent?key=" + API_KEY;

  const testoPrompt = `
Il giocatore A sta giocando al turing test. Ha la possibilità di porre una domanda: "${domanda}". 
Tu devi rispondere in modo indistinguibile da un essere umano.
La tua risposta deve essere lunga circa ${lunghezza} caratteri (simile alla risposta del destinatario).
`;

  const payload = {
    contents: [
      { role: "user", parts: [{ text: testoPrompt }] }
    ]
  };

  const options = {
    method: "post",
    contentType: "application/json",
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };

  const response = UrlFetchApp.fetch(url, options);
  const json = JSON.parse(response.getContentText());

  const rispostaAI = json?.candidates?.[0]?.content?.parts?.[0]?.text || "⚠️ Nessuna risposta dal modello";

  sh.getRange(riga, 3).setValue(rispostaAI); // colonna C
  return {
    rispostaDestinatario: rispostaDestinatario,
    rispostaAI: rispostaAI
  };
}


function testGemini() {
  const url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent?key=" + API_KEY;

  const payload = {
    contents: [
      {
        role: "user",
        parts: [
          { text: "Ciao! Scrivi una frase breve per dimostrarmi che l'API funziona." }
        ]
      }
    ]
  };

  const options = {
    method: "post",
    contentType: "application/json",
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };

  const response = UrlFetchApp.fetch(url, options);
  const json = JSON.parse(response.getContentText());

  console.log("RAW RESPONSE:", response.getContentText());

  const answer = json?.candidates?.[0]?.content?.parts?.[0]?.text || "⚠️ Nessuna risposta dal modello";
  console.log("PARSED ANSWER:", answer);
}
