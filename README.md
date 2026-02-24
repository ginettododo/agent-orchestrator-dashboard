# Sistema Agenti H24

Questa workspace contiene un prototipo di **catena di agenti orchestrati** e una dashboard per monitorarne lo stato. L’idea è quella di far girare agenti specializzati (Monitor, Analyst, Executor, Reviewer, Notifier) che comunicano tramite un task bus condiviso e tengono aggiornato un’interfaccia web.

## Cosa c’è qui

- `site/dashboard.html` + `site/style.css`: dashboard responsive che carica lo stato da `site/data/agent_state.json`
- `site/data/agent_state.json`: snapshot condiviso (agenti, queue, log e metriche)
- `site/scripts/task_bus.py`: script CLI per leggere lo stato, spawnare task (`spawn`), aggiornare il battito (`heartbeat`) e stampare lo stato (`status`)
- `site/scripts/auto_tasks.py`: simulazione di task automatici h24 per popolare la coda
- `site/scripts/heartbeat_runner.py`: loop che invoca `task_bus.py heartbeat` a intervalli regolari, utile da collegare a cron o un container di monitoraggio
- `multi_agent_plan.md`: mappa dettagliata degli agenti, orchestrazione e roadmap

## Come usare la dashboard

1. Avvia un server HTTP nel workspace:
   ```bash
   cd /root/.openclaw/workspace/site
   python3 -m http.server 8000 --bind 0.0.0.0
   ```
2. Dal tuo browser (anche mobile), visita `http://<IP-del-PC>:8000/dashboard.html`. Sostituisci `<IP-del-PC>` con l’indirizzo locale (`hostname -I`).
3. La pagina si aggiorna ogni 10 secondi leggendo `agent_state.json`. Ogni volta che esegui `task_bus.py`, la dashboard rifletterà i nuovi dati.

**Nota:** se usi il server solo localmente, puoi aprire il file direttamente via `file://`, ma alcune funzionalità (fetch) funzionano solo da server.

## Task bus (CLI)

Esempi:

```bash
cd /root/.openclaw/workspace
python3 site/scripts/task_bus.py status
python3 site/scripts/task_bus.py spawn --task "Aggiorna i checkpoint" --priority alta
python3 site/scripts/task_bus.py heartbeat
```

- `status`: stampa lo stato attuale e l’ultima coda
- `spawn`: aggiunge un task e genera log/aggiornamenti per gli agenti
- `heartbeat`: sincronizza tutti gli agenti e riduce la coda

Il file JSON viene riscritto automaticamente e la dashboard lo ricarica al prossimo polling.

## Simulatore automatico (per sviluppare l’idea h24)

Per generare task a intervalli regolari:

```bash
cd /root/.openclaw/workspace
python3 site/scripts/auto_tasks.py --iterations 10 --interval 20 --priority alta
```

Ogni iterazione invoca `task_bus.py spawn` con un messaggio casuale e aggiorna il file di stato. Puoi legare questo script a un cron (es. ogni 5 minuti) per simulare attività continuativa.

## Prossimi step suggeriti

1. Collegare sub-agent reali tramite `sessions_spawn` o webhook per eseguire task paralleli (es. `Monitor` ascolta mail, `Executor` modifica file).  
2. Espandere la dashboard con grafici del tempo e controlli per riavviare heartbeat oppure gestire le priorità.  
3. Containerizzare il sistema (Docker + supervisore) e agganciare un bot/cron che lancia `auto_tasks.py` e manda aggiornamenti.

Fammi sapere quando vuoi che implementi il passo successivo (es. orchestratore con cron e sub-agent). Altrimenti continuo da solo: ti aggiorno quando c’è qualcosa di nuovo pronto.
---

## CI/CD

- Il codice vive su <https://github.com/ginettododo/agent-orchestrator-dashboard> e viene pushato automaticamente al repository GitHub appena lo aggiorni.
- Una workflow `Deploy agent dashboard` (vedi `.github/workflows/deploy.yml`) installa Vercel CLI e invoca `vercel --cwd site --prod --confirm` dopo ogni push su `main`.
- Il workflow si affida al secret `VERCEL_TOKEN`, che dovrai impostare tu dal pannello Secrets per consentire al deploy di funzionare.
- `vercel.json` definisce il comportamento statico della pipeline: tutto il contenuto di `site/` viene servito direttamente e la route `/` punta alla dashboard.

> 🔐 Dopo aver collegato GitHub e Vercel ti consiglio di rigenerare i token (GitHub + Vercel) perché ora sono salvati temporaneamente nella workspace. Aggiorna i secret con i valori nuovi prima di riprendere il lavoro.
