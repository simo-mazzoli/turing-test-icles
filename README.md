Ciao Matte, ho pensato di caricarti qui tutti i file che avevo usato per l'applicazione (che dopo l'ultima modifica che avevo fatto manco funziona). Spero ti faciliti le cose.

Non so usare GitHub quindi avrei potuto far di meglio.

Il gioco in breve funziona così, un giocatore digita una domanda e la invia. A questa domanda rispondono una persona (da un'altra interfaccia) e un LLM. Il giocatore riceve le risposte e deve indovinare quale delle due è prodotta dal LLM.


Il gioco si compone in tre (boh forse 5) file(?):
- Giocatore: l'interfaccia da cui il giocatore digita la domanda e riceve le due risposte.
- Destinatario: l'interfaccia da cui la seconda persona risponde.
- Tramite: un csv che raccoglie le domande e le risposte. Quello che ti ho caricato probabilmente è inutile, contiene lo storico finora.

L'LLM è chiamato nel file .gs Giocatore solo quando la risposta del destinatario è stata ricevuta, in modo che entrambe vengano mostrate allo stesso momento e il giocatore non abbia l'indizio della velocità di ricezione.

Ti ringrazio molto per l'aiuto, se hai bisogno scrivimi 💕
