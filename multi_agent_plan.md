# Sistema di Agenti e Dashboard permanente

## Obiettivo
Costruire un ecosistema di agenti specializzati che lavorano in catena per monitorare, generare contenuti e portare avanti task h24. Avere un'interfaccia web che mostra stati, input/output e metriche.

---

## 1. Mappa degli agenti

1. **Monitor Agent**
   - **Ruolo:** ascolta nuove richieste, messaggi, email, webhook.
   - **Input:** feed chat/cron, file changes, webhook.
   - **Output:** task nella coda centrale.
   - **Strumenti:** subagents (per ascolto), cron e trigger.
   - **Metriche:** tempo dall'ultimo trigger, numero di task rilevati.

2. **Analyst Agent**
   - **Ruolo:** processa il brief, analizza contesto, genera domande di follow-up.
   - **Input:** task dalla coda + memoria.
   - **Output:** sintetizza requisiti, stima complessità, passaggio successivo per coda.
   - **Strumenti:** modello LLM + memoria.
   - **Metriche:** tempo di risposta, percentuale di follow-up richiesti.

3. **Executor Agent**
   - **Ruolo:** produce artefatti (codice, documenti, risultati). usa strumenti (shell, editor, web).
   - **Input:** ordine dettagliato dall'Analyst.
   - **Output:** file/risultati + log.
   - **Strumenti:** shell, git, editor, screenshot.
   - **Metriche:** tasso di completamento, token usati per task.

4. **Reviewer Agent**
   - **Ruolo:** verifica lint, test, coerenza e qualità.
   - **Input:** output dell'Executor.
   - **Output:** report di qualità e correzioni da applicare.
   - **Metriche:** numero di revisioni, pass/fail.

5. **Notifier Agent**
   - **Ruolo:** aggiorna dashboard, invia notifiche (messaggi, webhook, cron reply).
   - **Input:** stato degli altri agenti.
   - **Output:** alert, log nell'interfaccia.
   - **Metriche:** latenza di notifica, messaggi inviati.

---

## 2. Orchestrazione

- **Task Bus:** una coda (file JSON/DB leggero) per memorizzare compiti e stato.
- **Trigger:** cron job + webhook per attivare Monitor Agent.
- **Subagents:** spawn quando servono attività parallele.
- **Stato persistente:** `memory/agent_state.json` con timestamp di ogni agente.

---

## 3. Dashboard mockup

- **Navbar:** nome progetto + status globale (verde/rosso).
- **Colonne:** agenti, queue, log, metriche.
- **Widget:** cerchi animati con % completamento, last run.
- **Log area:** feed streaming.
- **Controls:** bottone “Start Task”, filtro per priorità.
- **Data / Chart:** timeline delle attività.

---

## 4. Roadmap di implementazione h24

1. Generare i file di configurazione per gli agenti (JSON/Markdown) e documentazione.
2. Allestire la dashboard statica (HTML/CSS/JS + grafici fittizi).
3. Scrivere script di orchestrazione (es. `tasks.py`, cron job che popola la coda).
4. Setup dei subagent (template `sessions_spawn`).
5. Test finale: simulazione di un task completo.

---

## 5. Azioni immediate eseguite

- Creata la mappa agenti + note su orchestrazione e dashboard.
- Generata dashboard decisionale (es. `site/dashboard.html` + asset).
- Allestita la base dati e il task bus: `site/data/agent_state.json` mantiene lo stato condiviso, mentre `site/scripts/task_bus.py` permette di spawnare task fittizi, aggiornare i heartbeat e scrivere log.
- Documentato tutto in `README.md` e aggiunto gli script `site/scripts/auto_tasks.py` (simula task automatici h24) e `site/scripts/heartbeat_runner.py` (loop di heartbeat da cron).

Fammi sapere se vuoi che continui con il passo 2 (mockup funzionante) e poi col passo 3 (script/automation). La prossima consegna includerà il mockup e un file di configurazione per il bus di task.
